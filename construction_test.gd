extends Node

class PlacementProbe extends Controller:
	var confirmed := 0
	func confirm_place() -> void:
		confirmed += 1


var _errors := 0


func _ready() -> void:
	_run.call_deferred()


func _check(value: bool, message: String) -> void:
	if not value:
		_errors += 1
		push_error(message)


func _run() -> void:
	Rules.civs = [{}, {"tech_tree": -1}]
	var map := GameMap.new()
	add_child(map)
	map.set_process(false)
	map.civ = 17
	map.size = 24
	map.occ.resize(map.size * map.size)
	map.astar = AStarGrid2D.new()
	map.astar.region = Rect2i(0, 0, map.size, map.size)
	map.astar.update()
	map.tech.units[83] = {"cost": {0: 50}, "time": 25.0}
	map.stock.food = 1000
	var controller := PlacementProbe.new()
	controller.map = map
	add_child(controller)
	var preview := Building.new()
	add_child(preview)
	controller._ghost = preview
	controller.placing = "house"
	var first := Iso.to_world(Vector2(6, 6))
	var second := Iso.to_world(Vector2(9, 10))
	controller.on_tap(first)
	_check(controller.confirmed == 0 and preview.visible and controller.place_ok, "Initial tap previews without building")
	controller.on_tap(second)
	_check(controller.confirmed == 0, "Different tile moves the preview")
	controller.on_double_tap(second)
	_check(controller.confirmed == 1, "A repeated tap confirms the preview")
	controller.cancel_pressed()
	_check(controller.placing.is_empty(), "Cancel leaves placement mode")

	var town_center := Building.new()
	town_center.kind = "tc"
	town_center.def = Defs.BUILDINGS.tc
	town_center.done = true
	town_center.selected = true
	map.add_child(town_center)
	map.buildings.append(town_center)
	controller.sel_b = town_center
	var hud := Hud.new()
	hud.ctl = controller
	var card := hud._card(Control.new(), "Villager", {}, Callable(), Color.WHITE, "", "villager")
	map.training_changed.connect(hud._on_training_changed)
	for i in 15:
		_check(map.try_train(town_center, "villager").is_empty(), "Training slot %d accepts a villager" % (i + 1))
	var badge: Label = hud._training_badges["villager"]
	_check(badge.text == "15" and badge.visible and map.pop == 15, "Badge reports the exact queued count")
	var balance := map.stock.food
	_check(not map.try_train(town_center, "villager").is_empty() and map.stock.food == balance, "The 16th order is rejected without spending")
	town_center.queue.pop_front()
	map.training_changed.emit(town_center)
	_check(badge.text == "14", "The count falls when training completes")
	controller.start_rally()
	controller.on_tap(Iso.to_world(Vector2(12, 10)))
	_check(not controller.rally_mode and town_center.rally_cell == Vector2i(12, 10), "Rally mode sets a waypoint")
	_check(is_instance_valid(town_center._rally_flag) and town_center._rally_flag.visible, "Selected training building shows a flag")
	controller.start_rally()
	controller.cancel_pressed()
	_check(town_center.rally_cell == Vector2i(12, 10) and not controller.rally_mode, "Cancel preserves the previous flag")
	controller.clear_rally()
	_check(town_center.rally_cell == Building.NO_RALLY and not town_center._rally_flag.visible, "Removing a flag hides it")
	card.free()
	hud.free()

	var atlas := ImageTexture.create_from_image(Image.create(300, 180, false, Image.FORMAT_RGBA8))
	var descriptor := {"file": "legacy-test", "cols": 3, "frames": 9, "tw": 96, "th": 48, "cw": 100, "ch": 52, "pad": 2}
	Assets._tex["legacy-test"] = atlas
	Assets.man["terrain"] = {"farm_grown": descriptor, "farm_fresh": descriptor}
	_check(FarmArt.sheet("farm_full") == descriptor and FarmArt.sheet("farm_fallow") == descriptor, "Legacy farm art is used for grown and fallow farms")
	_check(FarmArt.region(descriptor, 4) == Rect2(102, 54, 96, 48), "Farm tiles select the right atlas row")
	Assets.man["terrain"] = {}
	_check(FarmArt.sheet("farm_full").is_empty(), "Missing farm art can fall back to drawn crop rows")
	print("CONSTRUCTION AND TRAINING: %d failures" % _errors)
	get_tree().quit(1 if _errors else 0)
