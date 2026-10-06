## Capturas para la web: monta el casino de verdad y saca PNG a 640x360 nativos.
##
## Corre con ventana (sin rasterizador no hay imagen):
##   tools/godot.sh --path . --script <ruta>/capture_web.gd -- <carpeta_salida> [semilla]
##
## Bajo --script el guardado va aislado a user://test_runs/ y la telemetria no toca la red
## (ver scripts/persistence/save_store.gd). No escribe nada en el repo.
extends SceneTree

const WORLD := "res://scenes/world/casino_world.tscn"
const INTRO := "res://scenes/ui/screens/intro_scene.tscn"
const MENU := "res://scenes/ui/screens/main_menu.tscn"

const PINS: Array[StringName] = [
	&"trebol_torcido", &"moneda_al_aire", &"reloj_de_bolsillo", &"vela_del_brujo",
	&"alfiler_de_un_colon",
]

var _out := ""
var _world: Node = null


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	if DisplayServer.get_name() == "headless":
		printerr("necesita ventana")
		quit(1)
		return
	var args := OS.get_cmdline_user_args()
	_out = args[0] if not args.is_empty() else ProjectSettings.globalize_path("user://web")
	var run_seed := int(args[1]) if args.size() > 1 else 777
	var only := String(args[2]) if args.size() > 2 else "all"
	DirAccess.make_dir_recursive_absolute(_out)

	if only == "all" or only == "world":
		await _world_shots(run_seed)
	if only == "all" or only == "intro":
		await _intro_shots()
	if only == "all" or only == "menu":
		await _menu_shot()
	quit(0)


func _world_shots(run_seed: int) -> void:
	var rng_service := root.get_node(^"/root/RngService")
	var runs := root.get_node(^"/root/RunManager")
	var router := root.get_node(^"/root/SceneRouter")
	if runs.call(&"has_active_run"):
		runs.call(&"end_run")
	rng_service.call(&"start_run", run_seed)

	_world = (load(WORLD) as PackedScene).instantiate()
	root.add_child(_world)
	current_scene = _world
	await _wait(120)
	await _shot("s%d_parking" % run_seed)

	var layout: Object = _world.call(&"get_layout")
	var wanted: Array[StringName] = [
		&"lounge", &"slots_room", &"roulette_room", &"blackjack_room", &"horse_room",
		&"bar_room", &"brujo_room", &"smoking_room", &"restroom", &"cashier_room",
	]
	var keys_by_id := {}
	for key: StringName in layout.call(&"get_room_keys"):
		var room: Object = layout.call(&"get_room", key)
		var def_id: StringName = room.get(&"definition_id")
		if not keys_by_id.has(def_id):
			keys_by_id[def_id] = key
	print("salas en la semilla %d: %s" % [run_seed, keys_by_id.keys()])

	# Dinero y pines para que el HUD y la camisa no salgan vacios.
	for pin: StringName in PINS:
		runs.call(&"try_equip_amulet", pin)

	for def_id: StringName in wanted:
		if not keys_by_id.has(def_id):
			print("  falta %s" % def_id)
			continue
		_world.call(&"_enter_room", keys_by_id[def_id], &"")
		await _wait(90)
		await _shot("s%d_room_%s" % [run_seed, def_id])
		match def_id:
			&"slots_room":
				await _minigame(&"slots", run_seed, runs, router)
			&"roulette_room":
				await _minigame(&"roulette", run_seed, runs, router)
			&"blackjack_room":
				await _minigame(&"blackjack", run_seed, runs, router)
			&"horse_room":
				await _minigame(&"horses", run_seed, runs, router)
			&"brujo_room":
				_world.call(&"_try_open_brujo_shop")
				await _wait(90)
				if router.call(&"has_closeup"):
					await _shot("s%d_closeup_brujo" % run_seed)
					router.call(&"pop_to_world")
					runs.call(&"end_service_visit")
					await _wait(20)
			&"bar_room":
				_world.call(&"_try_open_closeup", &"bar")
				await _wait(90)
				if router.call(&"has_closeup"):
					await _shot("s%d_closeup_bar" % run_seed)
					router.call(&"pop_to_world")
					await _wait(20)
			&"lounge":
				var shirt := _world.get_node_or_null(^"AmuletView")
				if shirt != null:
					shirt.call(&"open")
					await _wait(60)
					await _shot("s%d_shirt" % run_seed)
					shirt.call(&"close")
					await _wait(20)

	# El cobrador al final del dia.
	_world.call(&"_on_collector_arrived", 0)
	await _wait(120)
	await _shot("s%d_collector" % run_seed)
	if router.call(&"has_closeup"):
		router.call(&"pop_to_world")
	await _wait(10)
	_world.queue_free()
	_world = null
	await _wait(10)


func _minigame(id: StringName, run_seed: int, runs: Node, router: Node) -> void:
	_world.call(&"_try_open_minigame", id)
	await _wait(60)
	if not router.call(&"has_closeup"):
		print("  no abrio %s por el mundo; se empuja directo" % id)
		var scenes: Dictionary = _world.get(&"MINIGAME_CLOSEUPS")
		router.call(&"push_closeup", id, scenes[id])
		await _wait(60)
	await _wait(60)
	await _shot("s%d_closeup_%s" % [run_seed, id])
	if router.call(&"has_closeup"):
		router.call(&"pop_to_world")
	runs.call(&"end_minigame")
	await _wait(20)


func _intro_shots() -> void:
	var intro := (load(INTRO) as PackedScene).instantiate()
	intro.set(&"playing", false)
	intro.set(&"play_music", false)
	root.add_child(intro)
	(intro as Control).set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _wait(5)
	var moments := [
		[0, [1.2, 3.6, 6.0, 7.5]],
		[1, [1.6, 4.8, 6.4, 8.6]],
		[2, [1.5, 3.5, 5.8, 7.0]],
		[3, [1.2, 2.5, 5.2, 8.0]],
		[4, [3.5, 7.0, 10.0]],
	]
	for entry: Array in moments:
		for moment: float in entry[1]:
			var start: float = intro.call(&"shot_start", entry[0])
			intro.call(&"seek", start + moment)
			await _wait(2)
			await _shot("intro_%d_%04.1f" % [entry[0], moment])
			# Version limpia, sin narracion ni expediente: la web pone su propio texto en ES/EN.
			for path: String in ["Narracion", "Saltar", "Expediente"]:
				var n := intro.get_node_or_null(path) as CanvasItem
				if n != null:
					n.visible = false
			await _wait(1)
			await _shot("clean_intro_%d_%04.1f" % [entry[0], moment])
			for path: String in ["Narracion", "Saltar", "Expediente"]:
				var n := intro.get_node_or_null(path) as CanvasItem
				if n != null:
					n.visible = true
	intro.queue_free()
	await _wait(5)


func _menu_shot() -> void:
	var menu := (load(MENU) as PackedScene).instantiate()
	root.add_child(menu)
	await _wait(120)
	await _shot("menu")
	menu.queue_free()
	await _wait(5)


func _wait(frames: int) -> void:
	for i: int in frames:
		await process_frame


func _shot(name: String) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	var path := _out.path_join(name + ".png")
	if image.save_png(path) != OK:
		printerr("no se pudo guardar %s" % path)
	else:
		print("  %s  %dx%d" % [name, image.get_width(), image.get_height()])
