## Capturas de las mesas EN JUEGO (carretes girando, carrera, mano repartida) para la web.
##
##   tools/godot.sh --path . --script <ruta>/capture_action.gd -- <carpeta_salida> [semilla]
extends SceneTree

const WORLD := "res://scenes/world/casino_world.tscn"
const ROULETTE_BET := "res://scripts/minigames/roulette/roulette_bet.gd"

var _out := ""
var _world: Node = null
var _runs: Node
var _router: Node


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	_out = args[0]
	var run_seed := int(args[1]) if args.size() > 1 else 777
	DirAccess.make_dir_recursive_absolute(_out)
	_runs = root.get_node(^"/root/RunManager")
	_router = root.get_node(^"/root/SceneRouter")
	root.get_node(^"/root/RngService").call(&"start_run", run_seed)
	_world = (load(WORLD) as PackedScene).instantiate()
	root.add_child(_world)
	current_scene = _world
	await _wait(120)

	var layout: Object = _world.call(&"get_layout")
	var keys := {}
	for key: StringName in layout.call(&"get_room_keys"):
		var def_id: StringName = layout.call(&"get_room", key).get(&"definition_id")
		if not keys.has(def_id):
			keys[def_id] = key

	# Mas dinero: con 500 las apuestas son de calderilla y la mesa se ve vacia.
	var state: Object = _runs.call(&"get_run_state")
	state.set(&"money", 4800)
	root.get_node(^"/root/GameEvents").emit_signal(&"money_changed", 4800)

	var games := String(args[2]).split(",") if args.size() > 2 else PackedStringArray(
		["slots", "blackjack", "roulette"]
	)
	for g: String in games:
		match g:
			"slots": await _slots(keys)
			"blackjack": await _blackjack(keys)
			"roulette": await _roulette(keys)
			"horses": await _horses(keys)
	quit(0)


func _open(keys: Dictionary, room: StringName, id: StringName) -> Node:
	if not keys.has(room):
		print("falta ", room)
		return null
	_world.call(&"_enter_room", keys[room], &"")
	await _wait(60)
	_world.call(&"_try_open_minigame", id)
	await _wait(90)
	return _router.call(&"get_closeup")


func _close() -> void:
	if _router.call(&"has_closeup"):
		_router.call(&"pop_to_world")
	_runs.call(&"end_minigame")
	await _wait(20)


func _slots(keys: Dictionary) -> void:
	var c := await _open(keys, &"slots_room", &"slots")
	if c == null:
		return
	c.call(&"_on_stake_pressed", 2)
	await _wait(5)
	c.call(&"_on_confirm_pressed")
	await _wait(20)
	c.call(&"_on_spin_pressed")
	for i: int in 14:
		await _wait(10)
		await _shot("act_slots_%02d" % i)
	await _close()


func _blackjack(keys: Dictionary) -> void:
	var c := await _open(keys, &"blackjack_room", &"blackjack")
	if c == null:
		return
	c.call(&"_on_stake_pressed", 1)
	await _wait(5)
	c.call(&"_on_confirm_pressed")
	for i: int in 6:
		await _wait(20)
		await _shot("act_bj_deal_%02d" % i)
	c.call(&"_on_hit_pressed")
	for i: int in 4:
		await _wait(20)
		await _shot("act_bj_hit_%02d" % i)
	await _close()


func _roulette(keys: Dictionary) -> void:
	var c := await _open(keys, &"roulette_room", &"roulette")
	if c == null:
		return
	c.call(&"_on_stake_pressed", 1)
	await _wait(5)
	c.call(&"_on_confirm_pressed")
	await _wait(10)
	var bet_script: Variant = load(ROULETTE_BET)
	c.call(&"_on_cloth_cell_activated", bet_script.of_number(17))
	c.call(&"_on_cloth_cell_activated", bet_script.of_kind(&"red"))
	c.call(&"_on_cloth_cell_activated", bet_script.of_number(17))
	await _wait(20)
	await _shot("act_rl_place")
	c.call(&"_on_spin_pressed")
	for i: int in 16:
		await _wait(12)
		await _shot("act_rl_spin_%02d" % i)
	await _close()


func _horses(keys: Dictionary) -> void:
	var c := await _open(keys, &"horse_room", &"horses")
	if c == null:
		return
	c.call(&"_on_horse_pressed", 2)
	c.call(&"_on_stake_pressed", 1)
	await _wait(5)
	c.call(&"_on_confirm_pressed")
	await _wait(10)
	await _shot("act_hr_confirm")
	c.call(&"skip_countdown")
	for i: int in 16:
		await _wait(30)
		await _shot("act_hr_race_%02d" % i)
	await _close()


func _wait(frames: int) -> void:
	for i: int in frames:
		await process_frame


func _shot(name: String) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	image.save_png(_out.path_join(name + ".png"))
	print("  ", name)
