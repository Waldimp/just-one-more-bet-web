## Plano entero de un casino generado: todas sus salas a la vez, cada una en su sitio.
##
## En el juego solo existe la sala en la que esta el jugador; aqui se instancian todas en su
## `grid_offset` dentro de un SubViewport y se saca una sola imagen a resolucion nativa.
##
##   tools/godot.sh --path . --script <ruta>/render_casino_map.gd -- <carpeta_salida> [semilla]
##
## Deja `casino_map_<semilla>.png` y `casino_map_<semilla>.txt` (rect de cada sala en pixeles,
## para poner etiquetas encima en la web).
extends SceneTree

const WORLD := "res://scenes/world/casino_world.tscn"
const TILE := 16


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var out: String = args[0]
	var run_seed := int(args[1]) if args.size() > 1 else 777
	DirAccess.make_dir_recursive_absolute(out)
	root.get_node(^"/root/RngService").call(&"start_run", run_seed)
	var world := (load(WORLD) as PackedScene).instantiate()
	root.add_child(world)
	await _wait(30)
	var layout: Object = world.call(&"get_layout")
	var library: Object = world.get_script().get_script_constant_map()["ROOM_LIBRARY"]

	var union := Rect2i()
	var first := true
	var rooms: Array = layout.call(&"get_rooms")
	for room: Object in rooms:
		var r: Rect2i = room.get(&"rect")
		union = r if first else union.merge(r)
		first = false
	# Margen arriba por las paredes de fondo, que viven en filas negativas.
	union = union.grow_individual(1, 4, 1, 1)
	print("union ", union)

	var viewport := SubViewport.new()
	viewport.size = union.size * TILE
	viewport.disable_3d = true
	viewport.transparent_bg = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	viewport.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	root.add_child(viewport)
	var holder := Node2D.new()
	holder.y_sort_enabled = true
	holder.position = -Vector2(union.position * TILE)
	viewport.add_child(holder)

	var lines: PackedStringArray = []
	for room: Object in rooms:
		var def_id: StringName = room.get(&"definition_id")
		var definition: Object = library.call(&"get_definition", def_id)
		var scene: PackedScene = definition.get(&"scene")
		var node := scene.instantiate() as Node2D
		var offset: Vector2i = room.get(&"grid_offset")
		node.position = Vector2(offset * TILE)
		holder.add_child(node)
		var r: Rect2i = room.get(&"rect")
		var px := Rect2i((r.position - union.position) * TILE, r.size * TILE)
		lines.append("%s %s %d %d %d %d" % [room.get(&"key"), def_id, px.position.x,
				px.position.y, px.size.x, px.size.y])
	await _wait(10)
	await RenderingServer.frame_post_draw
	var image := viewport.get_texture().get_image()
	image.save_png(out.path_join("casino_map_%d.png" % run_seed))
	var f := FileAccess.open(out.path_join("casino_map_%d.txt" % run_seed), FileAccess.WRITE)
	f.store_string("\n".join(lines))
	f.close()
	print("mapa %dx%d" % [image.get_width(), image.get_height()])
	quit(0)


func _wait(frames: int) -> void:
	for i: int in frames:
		await process_frame
