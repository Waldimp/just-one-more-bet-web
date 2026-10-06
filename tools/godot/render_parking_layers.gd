## Renderiza el parqueo deco por capas, a resolucion nativa y con fondo transparente,
## para montar el hero de la web con parallax.
##
##   tools/godot.sh --path . --script <ruta>/render_parking_layers.gd -- <carpeta_salida>
extends SceneTree

const ROOM := "res://scenes/world/rooms/parking_lot_room_deco.tscn"
const TILE := 16

const SIGN := ["VegasSign", "Pylon"]
const FRONT := [
	"Planter1", "Planter2", "Palm1", "Palm2", "Palm3", "Palm4", "Bollard1", "Bollard2",
	"Bollard3", "Bollard4", "Bollard5", "Bollard6", "PlazaLamp1", "PlazaLamp2",
]

var _out := ""


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	_out = args[0] if not args.is_empty() else ProjectSettings.globalize_path("user://layers")
	DirAccess.make_dir_recursive_absolute(_out)
	var scene := load(ROOM) as PackedScene
	var probe := scene.instantiate()
	var rect: Rect2i = probe.call(&"compute_used_tile_rect")
	probe.free()
	print("rect ", rect)

	var passes := {
		"all": func(n: Node) -> bool: return true,
		"ground": func(n: Node) -> bool: return n is TileMapLayer,
		"facade": func(n: Node) -> bool: return n.name == "CasinoEntranceFacade",
		"sign": func(n: Node) -> bool: return SIGN.has(String(n.name)),
		"front": func(n: Node) -> bool: return FRONT.has(String(n.name)),
		"lot": func(n: Node) -> bool: return (
			n is Sprite2D and not SIGN.has(String(n.name)) and not FRONT.has(String(n.name))
			and n.name != "CasinoEntranceFacade"
		),
	}
	for pass_name: String in passes:
		await _render(scene, rect, pass_name, passes[pass_name])
	quit(0)


func _render(scene: PackedScene, rect: Rect2i, pass_name: String, keep: Callable) -> void:
	var viewport := SubViewport.new()
	viewport.size = rect.size * TILE
	viewport.disable_3d = true
	viewport.transparent_bg = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	viewport.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	root.add_child(viewport)
	var room := scene.instantiate() as Node2D
	room.position = -Vector2(rect.position * TILE)
	viewport.add_child(room)
	await process_frame
	for path: String in ["Crowd", "Entities"]:
		var n := room.get_node_or_null(path)
		if n != null:
			(n as Node2D).visible = false
	var map := room.get_node("Map")
	for child: Node in map.get_children():
		if child.name == "Props":
			for prop: Node in child.get_children():
				(prop as CanvasItem).visible = keep.call(prop)
		else:
			(child as CanvasItem).visible = keep.call(child)
	if pass_name != "all":
		pass
	await process_frame
	await process_frame
	await process_frame
	var image := viewport.get_texture().get_image()
	var path := _out.path_join("parking_%s.png" % pass_name)
	image.save_png(path)
	print("%s %dx%d" % [pass_name, image.get_width(), image.get_height()])
	viewport.queue_free()
	await process_frame
