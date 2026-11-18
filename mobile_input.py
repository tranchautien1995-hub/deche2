"""Adapt the upstream touch controls and connect original Vietnamese voice lines."""


def replace_span(source, start, end, replacement):
    left = source.index(start)
    right = source.index(end, left + len(start))
    return source[:left] + replacement + source[right:]


CAMERA_BEHAVIOR = """\
func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventScreenTouch and event.pressed:
		_on_touch(event)
	elif event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			_zoom_at(event.position, 1.15)
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			_zoom_at(event.position, 1.0 / 1.15)


func _input(event: InputEvent) -> void:
	# A finger that started on the map keeps its gesture even if it ends over the HUD.
	if event is InputEventScreenTouch and not event.pressed and _touch.has(event.index):
		_on_touch(event)
		get_viewport().set_input_as_handled()
	elif event is InputEventScreenDrag and _touch.has(event.index):
		_on_drag(event)
		get_viewport().set_input_as_handled()


func _process(_delta: float) -> void:
	_begin_box_if_held()


func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		_touch.clear()
		_last_tap_ms = -100000
		_end_box()


func _on_touch(event: InputEventScreenTouch) -> void:
	if event.pressed:
		if ui_blocks.is_valid() and ui_blocks.call(event.position):
			return
		_touch[event.index] = event.position
		if _touch.size() == 1:
			_start_pos = event.position
			_start_ms = Time.get_ticks_msec()
			_moved = false
		else:
			_end_box()
			_moved = true
			_last_tap_ms = -100000
			if _touch.size() == 2:
				_begin_pinch()
		return

	if not _touch.has(event.index):
		return
	var last_finger := _touch.size() == 1
	_touch.erase(event.index)
	if _box_active:
		var area := _area(event.position)
		_end_box()
		if not event.canceled and event.position.distance_to(_start_pos) > TAP_SLOP:
			box_selected.emit(area)
	elif last_finger and not event.canceled and not _moved:
		var now := Time.get_ticks_msec()
		if now - _start_ms < HOLD_MS and event.position.distance_to(_start_pos) <= TAP_SLOP:
			_finish_tap(event.position, now)
	if _touch.size() == 2:
		_begin_pinch()


func _finish_tap(point: Vector2, now: int) -> void:
	var world_pos := screen_to_world(point)
	if now - _last_tap_ms <= DOUBLE_MS and point.distance_to(_last_tap_pos) <= DOUBLE_DIST:
		_last_tap_ms = -100000
		double_tapped.emit(world_pos)
	else:
		_last_tap_ms = now
		_last_tap_pos = point
		tapped.emit(world_pos)


func _begin_box_if_held() -> void:
	if _touch.size() != 1 or _moved or _box_active:
		return
	if Time.get_ticks_msec() - _start_ms < HOLD_MS:
		return
	if box_ok.is_valid() and not box_ok.call():
		return
	if ui_blocks.is_valid() and ui_blocks.call(_start_pos):
		return
	_box_active = true
	_last_tap_ms = -100000
	box_changed.emit(Rect2(_start_pos, Vector2.ONE))


func _area(end: Vector2) -> Rect2:
	return Rect2(_start_pos, end - _start_pos).abs()


func _end_box() -> void:
	if _box_active:
		_box_active = false
		box_changed.emit(Rect2())


func _on_drag(event: InputEventScreenDrag) -> void:
	if not _touch.has(event.index):
		return
	_touch[event.index] = event.position
	if _touch.size() == 1:
		_begin_box_if_held()
		if _box_active:
			box_changed.emit(_area(event.position))
			return
		if event.position.distance_to(_start_pos) > TAP_SLOP:
			_moved = true
			_last_tap_ms = -100000
		if _moved:
			position -= event.relative / zoom.x
			_clamp()
	elif _touch.size() == 2:
		var points: Array = _touch.values()
		var dist: float = points[0].distance_to(points[1])
		var mid: Vector2 = (points[0] + points[1]) * 0.5
		if _pinch_dist > 1.0:
			_zoom_at(mid, dist / _pinch_dist)
		position -= (mid - _pinch_mid) / zoom.x
		_pinch_dist = dist
		_pinch_mid = mid
		_clamp()


"""


CONTROLLER_SELECTION = """\
func on_tap(w: Vector2) -> void:
	_last_tapped_unit = null
	if placing != "":
		move_ghost(w)
		return
	var hit := pick(w)
	if hit is Relic:
		_relic_tap(hit)
	elif hit is Mob:
		if _selectable(hit):
			_last_tapped_unit = hit
			select_units([hit])
			Chatter.acknowledge(hit, "soldier_select" if hit is Soldier else "select")
		elif hit.team != 0:
			_attack(hit)
	elif hit is Building:
		_building_tap(hit)
	elif hit is ResNode:
		_gather(hit)
	else:
		_move_to(Iso.to_cell(w))


func on_double_tap(w: Vector2) -> void:
	var hit := pick(w)
	if placing != "" or not hit is Mob or not _selectable(hit) or hit != _last_tapped_unit:
		on_tap(w)
		return
	_last_tapped_unit = null
	select_units(nearby_units(hit))


func nearby_units(origin: Mob) -> Array[Mob]:
	var matches: Array[Mob] = [origin]
	for unit in map.mobs:
		if unit == origin or not _selectable(unit):
			continue
		if unit.tp.distance_squared_to(origin.tp) > GROUP_RADIUS * GROUP_RADIUS:
			continue
		if _selection_group(unit) == _selection_group(origin) and cam.get_viewport_rect().has_point(_screen_body(unit)):
			matches.append(unit)
	return matches


func _selection_group(unit: Mob) -> int:
	if unit is Villager:
		return 0
	return 1 if unit is Soldier else 2


func _selectable(unit: Mob) -> bool:
	return unit.team == 0 and unit.alive and unit.is_visible_in_tree() and unit.garrisoned_in == null \\
		and (unit is Villager or unit is Soldier or unit is Ship)


func _screen_body(unit: Mob) -> Vector2:
	return cam.world_to_screen(unit.position + Vector2(0, -22))


func select_in_box(area: Rect2) -> void:
	if not area.has_area() or placing != "":
		return
	var picked: Array[Mob] = []
	for unit in map.mobs:
		if _selectable(unit) and area.has_point(_screen_body(unit)):
			picked.append(unit)
	if picked.is_empty():
		toast("Không có đơn vị của bạn trong vùng chọn")
		return
	_last_tapped_unit = null
	select_units(picked)
	toast("Đã chọn %d đơn vị" % picked.size())


"""


CHATTER_BEHAVIOR = """\
static func acknowledge(unit: Mob, category: String) -> void:
	if not is_instance_valid(unit) or not unit.alive or unit.team != 0:
		return
	var lines: Array = UnitSpeech.LINES.get(category, [])
	if lines.is_empty():
		return
	var index := randi() % lines.size()
	Sfx.speak_unit(category, index, unit is Soldier)
	if not enabled:
		return
	var existing := unit.get_node_or_null("Chatter") as Chatter
	if existing != null:
		existing.text = lines[index]
		existing.t = 0.0
	else:
		_show(unit, lines[index])


static func say_some(units: Array, category: String, soldier_category := "") -> void:
	for member in units:
		if is_instance_valid(member) and member is Mob and member.alive and member.team == 0:
			var response := soldier_category if soldier_category != "" and member is Soldier else category
			acknowledge(member, response)
			return


"""


OVERLAY = """\
class_name LassoOverlay
extends Control
## Rectangle used by the hold-and-drag selection gesture.

var area := Rect2()
var scale_ui := 1.0


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_preset(Control.PRESET_FULL_RECT)


func set_area(value: Rect2) -> void:
	area = value
	queue_redraw()


func _draw() -> void:
	if not area.has_area():
		return
	var gold := Color(1.0, 0.86, 0.35)
	draw_rect(area, Color(gold, 0.14))
	draw_rect(area, gold, false, maxf(2.0, 4.0 * scale_ui))
"""


INPUT_TEST = """\
extends Node

var failures := 0
var camera: RtsCamera


func check(condition: bool, message: String) -> void:
	print(("PASS " if condition else "FAIL ") + message)
	if not condition:
		failures += 1


func _ready() -> void:
	call_deferred("_run")


func _run() -> void:
	var viewport := SubViewport.new()
	viewport.size = Vector2i(1600, 900)
	add_child(viewport)
	camera = RtsCamera.new()
	viewport.add_child(camera)
	var taps := [0, 0]
	var boxes: Array[Rect2] = []
	camera.tapped.connect(func(_point: Vector2) -> void: taps[0] += 1)
	camera.double_tapped.connect(func(_point: Vector2) -> void: taps[1] += 1)
	camera.box_selected.connect(func(area: Rect2) -> void: boxes.append(area))

	var origin := Vector2(320, 230)
	var end := origin - Vector2(140, 90)
	tap(origin)
	tap(origin + Vector2(8, 0))
	check(taps == [1, 1], "two quick taps are a tap followed by a double tap")
	tap(origin)
	tap(origin + Vector2(160, 0))
	check(taps == [3, 1], "far-apart taps remain separate commands")

	touch(0, origin, true)
	camera._start_ms -= RtsCamera.HOLD_MS + 1
	drag(0, origin, end)
	touch(0, end, false)
	check(boxes.size() == 1 and boxes[0] == Rect2(end, origin - end), "holding then dragging in reverse reports the exact rectangle")
	check(camera.position == Vector2.ZERO and taps == [3, 1], "box selection neither pans nor emits an order")

	touch(0, origin, true)
	drag(0, origin, end)
	touch(0, end, false)
	check(camera.position != Vector2.ZERO and boxes.size() == 1, "a quick drag pans the map")

	touch(0, origin, true)
	camera._start_ms -= RtsCamera.HOLD_MS + 1
	drag(0, origin, end)
	touch(1, origin + Vector2(95, 20), true)
	touch(1, origin + Vector2(95, 20), false)
	touch(0, end, false)
	check(boxes.size() == 1 and not camera._box_active, "a second finger cancels the rectangle")

	camera.position = Vector2.ZERO
	var controller := Controller.new()
	controller.cam = camera
	Rules.civs = [{}, {"tech_tree": -1}]
	controller.map = GameMap.new()
	add_child(controller)
	var villager := spawn(controller, Villager.new(), Vector2.ZERO)
	var near_villager := spawn(controller, Villager.new(), Vector2(2, 1))
	var far_villager := spawn(controller, Villager.new(), Vector2(30, 25))
	var soldier := spawn(controller, Soldier.new(), Vector2(1, 3))
	var near_soldier := spawn(controller, Soldier.new(), Vector2(2, 3))
	var enemy := spawn(controller, Soldier.new(), Vector2(1, 2), 1)
	var result := controller.nearby_units(villager)
	check(result.size() == 2 and result.has(near_villager) and not result.has(far_villager), "a village group contains only nearby villagers")
	result = controller.nearby_units(soldier)
	check(result.size() == 2 and result.has(near_soldier) and not result.has(enemy), "a military group excludes villagers and enemies")
	var area := Rect2(controller._screen_body(villager), Vector2.ZERO)
	for unit in [near_villager, soldier, near_soldier, enemy]:
		area = area.expand(controller._screen_body(unit))
	controller.select_in_box(area.grow(8))
	check(controller.sel_units.size() == 4 and not controller.sel_units.has(enemy), "a rectangle selects mixed friendly units only")
	controller.map.free()

	for category: String in UnitSpeech.LINES:
		for index in UnitSpeech.LINES[category].size():
			var wav := load("res://assets/voice_vi/%s_%d.wav" % [category, index]) as AudioStreamWAV
			check(wav != null and wav.get_length() > 0.2, "offline voice " + category + "/" + str(index))
	print("MOBILE INPUT AND VOICE: %d failures" % failures)
	get_tree().quit(failures)


func touch(index: int, point: Vector2, down: bool) -> void:
	var event := InputEventScreenTouch.new()
	event.index = index
	event.position = point
	event.pressed = down
	camera._on_touch(event)


func tap(point: Vector2) -> void:
	touch(0, point, true)
	touch(0, point, false)


func drag(index: int, from: Vector2, to: Vector2) -> void:
	var event := InputEventScreenDrag.new()
	event.index = index
	event.position = to
	event.relative = to - from
	camera._on_drag(event)


func spawn(controller: Controller, unit: Mob, point: Vector2, team := 0) -> Mob:
	unit.process_mode = Node.PROCESS_MODE_DISABLED
	unit.place(point)
	unit.team = team
	add_child(unit)
	controller.map.mobs.append(unit)
	return unit
"""


def apply_mobile(project, edit):
    scripts = project / "scripts"
    cam = scripts / "rts_camera.gd"
    source = cam.read_text(encoding="utf-8")
    source = replace_span(source, "## Touch camera:", "const MIN_ZOOM", """\
## Quick taps give orders, holding then dragging selects units, pinching zooms.

signal tapped(world_pos: Vector2)
signal double_tapped(world_pos: Vector2)
signal box_changed(area: Rect2)
signal box_selected(area: Rect2)

""")
    source = replace_span(source, "const TAP_SLOP", "var bounds", """\
const TAP_SLOP := 18.0
const HOLD_MS := 330
const DOUBLE_MS := 300
const DOUBLE_DIST := 72.0

""")
    source = source.replace(
        "## Optional callable() -> bool: whether a lasso may start now (not while a building is being placed).\n"
        "var lasso_ok: Callable = Callable()",
        "## Returns false during a building placement.\nvar box_ok: Callable = Callable()",
    )
    source = replace_span(source, "var _ignored", "func screen_to_world", """\
var _last_tap_ms := -100000
var _last_tap_pos := Vector2.ZERO
var _box_active := false


""")
    source = replace_span(source, "func _unhandled_input", "## Centres the view", CAMERA_BEHAVIOR)
    cam.write_text(source, encoding="utf-8")
    (scripts / "lasso_overlay.gd").write_text(OVERLAY, encoding="utf-8")
    (project / "tests" / "lasso.gd").write_text(INPUT_TEST, encoding="utf-8")

    controller = scripts / "controller.gd"
    source = controller.read_text(encoding="utf-8")
    source = replace_span(source, "var _pending_move", "func toast", """\
const GROUP_RADIUS := 14.0
var _last_tapped_unit: Mob


""")
    source = replace_span(source, "func on_tap(", "## Villagers that", CONTROLLER_SELECTION)
    controller.write_text(source, encoding="utf-8")
    edit(controller, [
        ("if m.get_rect().grow(8.0).has_point", "if m.alive and m.is_visible_in_tree() and m.get_rect().grow(8.0).has_point"),
        ('Chatter.say(best, "relic")', 'Chatter.acknowledge(best, "relic")'),
        ('Chatter.say_some(hunters, "food")', 'Chatter.say_some(hunters, "hunt")'),
        ('Chatter.say(vills[0], "farm")', 'Chatter.acknowledge(vills[0], "farm")'),
        ('Chatter.say(best, "repair")', 'Chatter.acknowledge(best, "repair")'),
        ('\t\t\tb.flash()\n\t\t\ttoast("The relic goes', '\t\t\tb.flash()\n\t\t\tChatter.say_some(carriers, "deliver")\n\t\t\ttoast("The relic goes'),
        ('\tb.flash()\n\ttoast("%d to the', '\tb.flash()\n\tChatter.say_some(sent, "garrison")\n\ttoast("%d to the'),
        ('\t\tif r.kind != "fish":\n\t\t\tChatter.say_some(workers, r.kind)',
         '\t\tif r.kind == "fish":\n\t\t\tChatter.say_some(sel_units.filter(func(u: Mob) -> bool: return u is Ship), "fish")\n'
         '\t\telse:\n\t\t\tChatter.say_some(workers, r.kind)'),
    ])

    main = scripts / "main.gd"
    source = main.read_text(encoding="utf-8")
    source = replace_span(source, '\tcam.lasso_ok', '\n\nvar _auto_t', """\
	cam.box_ok = func() -> bool: return ctl.placing == ""
	cam.double_tapped.connect(ctl.on_double_tap)
	cam.box_changed.connect(func(area: Rect2) -> void: hud.lasso.set_area(area))
	cam.box_selected.connect(ctl.select_in_box)
""")
    main.write_text(source, encoding="utf-8")

    chatter = scripts / "chatter.gd"
    edit(chatter, [
        ('\tvar c := Chatter.new()\n\tc.name = "Chatter"\n\tc.text = lines[randi() % lines.size()]',
         '\t_show(unit, lines[randi() % lines.size()])\n\n\nstatic func _show(unit: Node2D, line: String) -> void:\n'
         '\tvar c := Chatter.new()\n\tc.name = "Chatter"\n\tc.text = line'),
    ])
    source = chatter.read_text(encoding="utf-8")
    source = replace_span(source, "## A few of the ordered units speak", "func _ready", CHATTER_BEHAVIOR)
    chatter.write_text(source, encoding="utf-8")

    edit(scripts / "sfx.gd", [
        ('const BUSES := ["Music", "Combat", "Work", "Alerts"]', 'const BUSES := ["Music", "Combat", "Work", "Alerts", "Voice"]'),
        ('"Alerts": "Alerts and events"}', '"Alerts": "Alerts and events", "Voice": "Giọng dân và lính"}'),
        ('"Alerts": 0.9}', '"Alerts": 0.9, "Voice": 0.85}'),
        ('var _music: AudioStreamPlayer', 'var _voice: AudioStreamPlayer\nvar _music: AudioStreamPlayer'),
        ('\t_music = AudioStreamPlayer.new()', '\t_voice = AudioStreamPlayer.new()\n\t_voice.bus = "Voice"\n\tadd_child(_voice)\n\t_music = AudioStreamPlayer.new()'),
        ('## (Re)loads the music;', """\
func speak_unit(category: String, index: int, soldier: bool) -> void:
	if _voice == null or get_volume("Voice") <= 0.001 or get_volume("Master") <= 0.001:
		return
	var effect := "res://assets/voice_vi/%s_%d.wav" % [category, index]
	if not ResourceLoader.exists(effect, "AudioStream"):
		return
	_voice.stream = load(effect) as AudioStream
	_voice.pitch_scale = 0.87 if soldier else 1.0
	_voice.play()


## (Re)loads the music;"""),
    ])
    hud = scripts / "hud.gd"
    edit(hud, [
        ('["Master", "Music", "Combat", "Work", "Alerts"]', '["Master", "Music", "Combat", "Work", "Alerts", "Voice"]'),
    ])
