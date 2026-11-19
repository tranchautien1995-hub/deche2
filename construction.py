"""Update the upstream game's construction and training controls."""

from pathlib import Path
from shutil import copyfile


def apply_construction(project, edit):
    scripts = project / "scripts"
    for name in ("farm_art.gd", "rally_flag.gd"):
        copyfile(Path(__file__).parent / name, scripts / name)

    edit(scripts / "controller.gd", [
        ('var placing := ""', 'var placing := ""\nvar rally_mode := false\nvar _preview_cell := Building.NO_RALLY'),
        ('func clear_selection() -> void:\n\tground_mode = false',
         'func clear_selection() -> void:\n\t_cancel_rally()\n\tground_mode = false'),
        ('\t\tsel_b = null\n\t\tgone = true', '\t\tsel_b = null\n\t\t_cancel_rally()\n\t\tgone = true'),
        ('\t\tmove_ghost(w)\n\t\treturn\n\tif ground_mode:',
         '\t\tmove_ghost(w)\n\t\treturn\n\tif rally_mode:\n\t\t_place_rally(w)\n\t\treturn\n\tif ground_mode:'),
        ('if placing != "" or ground_mode or not hit is Mob', 'if placing != "" or rally_mode or ground_mode or not hit is Mob'),
        ('# ------------------------------------------------------------------ placement\n', '''\
func start_rally() -> void:
	if not is_instance_valid(sel_b) or not sel_b.alive or not sel_b.done or not sel_b.def.has("train"):
		return
	rally_mode = true
	placing_changed.emit()


func clear_rally() -> void:
	if is_instance_valid(sel_b):
		sel_b.set_rally(Building.NO_RALLY)
		selection_changed.emit()


func _cancel_rally() -> void:
	if rally_mode:
		rally_mode = false
		placing_changed.emit()


func _place_rally(world: Vector2) -> void:
	if not is_instance_valid(sel_b) or not sel_b.alive:
		_cancel_rally()
		return
	var target := Iso.to_cell(world)
	if not map.in_bounds(target):
		return
	var naval := sel_b.kind == "dock"
	if map.blocked(target, naval):
		toast("Choose a free tile for the rally flag")
		return
	sel_b.set_rally(target)
	_cancel_rally()


# ------------------------------------------------------------------ placement
'''),
        ('\tmap.entities.add_child(_ghost)\n\t_ghost.show_range(true)',
         '\tmap.entities.add_child(_ghost)\n\t_ghost.hide()\n\t_ghost.show_range(true)'),
        ('''\
	if placing == "wall":
		_wall_tap(Iso.to_cell(w))
		return
	_set_origin(Iso.to_cell(w))
	_refresh_ghost()
''', '''\
	var at := Iso.to_cell(w)
	if not map.in_bounds(at):
		return
	if placing == "wall":
		if not wall_cells.is_empty() and (at == _preview_cell or at == wall_pts.back()):
			confirm_place()
		else:
			_preview_cell = at
			_wall_tap(at)
			placing_changed.emit()
		return
	if at == _preview_cell:
		confirm_place()
		return
	_preview_cell = at
	_set_origin(at)
	_ghost.show()
	_refresh_ghost()
	placing_changed.emit()
'''),
        ('func cancel_place() -> void:\n\t_clear_wall_ghosts()',
         'func cancel_place() -> void:\n\t_preview_cell = Building.NO_RALLY\n\t_clear_wall_ghosts()'),
        ('\tvar kind := placing\n\tvar cost: Dictionary = Defs.BUILDINGS[kind].cost',
         '\tif _preview_cell == Building.NO_RALLY:\n\t\treturn\n\t_refresh_ghost()\n'
         '\tvar kind := placing\n\tvar cost: Dictionary = Defs.BUILDINGS[kind].cost'),
        ('''\
	if placing == "gate":
		return tr("Place Gate (%s). It turns to lie along a wall; your units pass, enemies do not. %s") % [Defs.cost_text(d.cost), tr("Use Turn to rotate it.") if place_ok else tr("Blocked here, tap another spot.")]
	if placing != "wall":
		return tr("Place %s (%s). %s") % [d.name, Defs.cost_text(d.cost), tr("Tap the map to move it.") if place_ok else tr("Blocked here, tap another spot.")]
	if wall_pts.is_empty():
		return tr("Stone Wall: tap where the wall should start.")
	if wall_cells.size() <= 1:
		return tr("Stone Wall: tap the next point. Walls run straight or diagonal; tap again to turn.")
	var n := _wall_valid().size()
	return tr("Stone Wall: %d pieces, %d stone. Tap to add a turn, tap the last point to undo. Place to build.") % [n, n * int(d.cost.stone)]
''', '''\
	if placing != "wall":
		var hint := tr("Tap the map to choose a site.")
		if _preview_cell != Building.NO_RALLY:
			hint = tr("Tap the same tile again to build.") if place_ok else tr("Blocked here, tap another spot.")
		return tr("Place %s (%s). %s") % [Lang.t(d.name), Defs.cost_text(d.cost), hint]
	if wall_cells.is_empty():
		return tr("Stone Wall: tap where the wall should start.")
	var n := _wall_valid().size()
	return tr("Stone Wall: %d pieces, %d stone. Tap the endpoint again to build or tap elsewhere to extend.") % [n, n * int(d.cost.stone)]
'''),
        ('''\
	if not wall_pts.is_empty() and c == wall_pts.back():
		wall_pts.pop_back()
	elif wall_pts.is_empty():
''', '''\
	if wall_pts.is_empty():
'''),
        ('''\
## The Cancel button: first clears a planned wall, then leaves wall mode.
func cancel_pressed() -> void:
	if placing == "wall" and (not wall_cells.is_empty() or wall_pts.size() > 1):
		wall_pts.clear()
		_clear_wall_ghosts()
		placing_changed.emit()
	else:
		cancel_place()
''', '''\
func cancel_pressed() -> void:
	if rally_mode:
		_cancel_rally()
	else:
		cancel_place()
'''),
    ])

    edit(scripts / "main.gd", [
        ('return ctl.placing == "" and not ctl.ground_mode', 'return ctl.placing == "" and not ctl.rally_mode and not ctl.ground_mode'),
    ])

    edit(scripts / "building.gd", [
        ('var queue: Array[String] = []', 'const TRAIN_QUEUE_LIMIT := 15\nconst NO_RALLY := Vector2i(-1, -1)\n\n'
         'var queue: Array[String] = []\nvar rally_cell := NO_RALLY\nvar _rally_flag: RallyFlag'),
        ('map.spawn_unit(queue.pop_front(), self)', 'map.spawn_unit(queue.pop_front(), self)\n\t\t\tmap.training_changed.emit(self)'),
        ('func set_selected(v: bool) -> void:\n\tselected = v',
         'func set_rally(cell: Vector2i) -> void:\n'
         '\trally_cell = cell\n'
         '\t_sync_rally()\n\n\n'
         'func _sync_rally() -> void:\n'
         '\tif selected and rally_cell != NO_RALLY:\n'
         '\t\tif _rally_flag == null:\n'
         '\t\t\t_rally_flag = RallyFlag.new()\n'
         '\t\t\tadd_child(_rally_flag)\n'
         '\t\t_rally_flag.position = Iso.to_world(Vector2(rally_cell)) - position\n'
         '\t\t_rally_flag.show()\n'
         '\telif _rally_flag != null:\n'
         '\t\t_rally_flag.hide()\n\n\n'
         'func set_selected(v: bool) -> void:\n\tselected = v\n\t_sync_rally()'),
        ('''\
@warning_ignore("integer_division")
func _draw() -> void:
	if kind != "farm":
		return
	var t: Dictionary = Assets.man.terrain[farm_stage()]
	var tx: Texture2D = Assets.tex(t.file)
	var tw := float(t.tw)
	var th := float(t.th)
	for j in bsize:
		for i in bsize:
			var frame := i + j * 3
			var src := Rect2(float(t.pad) + (frame % 3) * float(t.cw), float(t.pad) + (frame / 3) * float(t.ch), tw, th)
			var c := Iso.to_world(Vector2(i, j) - Vector2.ONE * ((bsize - 1) * 0.5))
			draw_texture_rect_region(tx, Rect2(c - Vector2(tw, th) * 0.5, Vector2(tw, th)), src)
''', '''\
func _draw() -> void:
	if kind != "farm":
		return
	var art := FarmArt.sheet(farm_stage())
	var tx: Texture2D = Assets.tex(String(art.file)) if not art.is_empty() else null
	for j in bsize:
		for i in bsize:
			var centre := Iso.to_world(Vector2(i, j) - Vector2.ONE * ((bsize - 1) * 0.5))
			if tx != null:
				var src := FarmArt.region(art, (i + j * 3) % int(art.frames))
				draw_texture_rect_region(tx, Rect2(centre - src.size * 0.5, src.size), src)
			else:
				FarmArt.draw_missing_tile(self, centre, done and food > 0.0)
'''),
    ])

    edit(scripts / "villager.gd", [
        ('\t\t\t\tfarm.food = maxf(0.0, farm.food - 1.0)\n\t\t\t\tcarry_n += 1',
         '\t\t\t\tfarm.food = maxf(0.0, farm.food - 1.0)\n\t\t\t\tif farm.food == 0.0:\n'
         '\t\t\t\t\tfarm.queue_redraw()\n\t\t\t\tcarry_n += 1'),
    ])

    edit(scripts / "game_map.gd", [
        ('signal building_finished(b: Building)', 'signal building_finished(b: Building)\nsignal training_changed(b: Building)'),
        ('if b.queue.size() >= 5:\n\t\treturn tr("Queue is full")',
         'if b.queue.size() >= Building.TRAIN_QUEUE_LIMIT:\n\t\treturn tr("Training queue is full (%d)") % Building.TRAIN_QUEUE_LIMIT'),
        ('\tb.queue.append(ukind)\n\treturn ""', '\tb.queue.append(ukind)\n\trecalc_pop()\n\ttraining_changed.emit(b)\n\treturn ""'),
        ('\t\tif ship is Ship:\n\t\t\tvar f := nearest_fish',
         '\t\tif ship is Ship and from.rally_cell != Building.NO_RALLY:\n'
         '\t\t\t(ship as Ship).order_move(free_water_near(from.rally_cell, 8))\n'
         '\t\telif ship is Ship:\n\t\t\tvar f := nearest_fish'),
        ('var out := free_cell_near(c + Vector2i(2, 2), 4)',
         'var target := c + Vector2i(2, 2) if from.rally_cell == Building.NO_RALLY else from.rally_cell\n'
         '\tvar out := free_cell_near(target, 4)'),
    ])

    edit(scripts / "save_game.gd", [
        ('"rel": b.relics.size(), "rs": b.reseeds}', '"rel": b.relics.size(), "rs": b.reseeds, "rally": [b.rally_cell.x, b.rally_cell.y]}'),
        ('\t\tb.queue.assign(e.q)\n\t\tb.qt = float(e.qt)',
         '\t\tb.queue.assign(e.q)\n'
         '\t\tvar rally: Array = e.get("rally", [-1, -1])\n'
         '\t\tvar target := Vector2i(int(rally[0]), int(rally[1]))\n'
         '\t\tif map.in_bounds(target):\n\t\t\tb.set_rally(target)\n'
         '\t\tb.qt = float(e.qt)'),
    ])

    edit(scripts / "hud.gd", [
        ('var place_label: Label', 'var place_label: Label\nvar _training_badges: Dictionary = {}'),
        ('map.attacked.connect(_on_attacked)', 'map.attacked.connect(_on_attacked)\n\tmap.training_changed.connect(_on_training_changed)'),
        ('\t_cost_labels.clear()\n\tvar b := ctl.sel_b', '\t_cost_labels.clear()\n\t_training_badges.clear()\n\tvar b := ctl.sel_b'),
        ('\tif ctl.placing != "":\n\t\t_show_page()', '\tif ctl.placing != "" or ctl.rally_mode:\n\t\t_show_page()'),
        ('\t\t\t\t_cmd_items.append(_card(_unit_icon(uk), tr("Train %s") % String(u.name), u.cost, ctl.train.bind(uk), Color(0.3, 0.26, 0.14)))',
         '\t\t\t\t_cmd_items.append(_card(_unit_icon(uk), tr("Train %s") % Lang.t(String(u.name)), u.cost, ctl.train.bind(uk), Color(0.3, 0.26, 0.14), "", uk))\n'
         '\t\t\t_cmd_items.append(_card(Glyph.make("rally", 80 * s), "Set rally flag", {}, ctl.start_rally, Color(0.15, 0.31, 0.37)))\n'
         '\t\t\tif b.rally_cell != Building.NO_RALLY:\n'
         '\t\t\t\t_cmd_items.append(_card(Glyph.make("cross", 80 * s), "Clear rally flag", {}, ctl.clear_rally, Color(0.33, 0.23, 0.14)))\n'
         '\t\t\t_on_training_changed(b)'),
        ('func _card(icon: Control, title: String, cost: Dictionary, cb: Callable, fill: Color, sub := "") -> Button:',
         'func _card(icon: Control, title: String, cost: Dictionary, cb: Callable, fill: Color, sub := "", unit_kind := "") -> Button:'),
        ('\tholder.add_child(icon)\n\tvar name := _label(title, 24)',
         '\tholder.add_child(icon)\n'
         '\tif unit_kind != "":\n'
         '\t\tvar count := _label("", 38, Color.WHITE, true)\n'
         '\t\tcount.set_anchors_preset(Control.PRESET_FULL_RECT)\n'
         '\t\tcount.offset_right = -10 * s\n'
         '\t\tcount.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT\n'
         '\t\tholder.add_child(count)\n'
         '\t\t_training_badges[unit_kind] = count\n'
         '\tvar name := _label(title, 24)'),
        ('## Shrinks a label\'s font until', '''\
func _on_training_changed(b: Building) -> void:
	if ctl.sel_b != b:
		return
	for kind: String in _training_badges:
		var total := b.queue.count(kind)
		var badge: Label = _training_badges[kind]
		badge.text = str(total)
		badge.visible = total > 0


## Shrinks a label's font until'''),
        ('''\
		var t: Dictionary = Assets.man.terrain["farm_full"]
		var frame := 4
		var at := AtlasTexture.new()
		at.atlas = Assets.tex(t.file)
		at.region = Rect2(float(t.pad) + (frame % 3) * float(t.cw), float(t.pad) + (frame / 3) * float(t.ch), float(t.tw), float(t.th))
		return _tex_rect(at)
''', '''\
		var art := FarmArt.sheet("farm_full")
		if art.is_empty():
			return Glyph.make("food", 92 * s)
		var at := AtlasTexture.new()
		at.atlas = Assets.tex(String(art.file))
		at.region = FarmArt.region(art, mini(4, int(art.frames) - 1))
		return _tex_rect(at)
'''),
        ('\trow.add_child(_primary("Place", ctl.confirm_place, 300, 124, 36))\n', ''),
        ('var on := ctl.placing != ""', 'var on := ctl.placing != "" or ctl.rally_mode'),
        ('\tif on:\n\t\tplace_label.text = ctl.place_text()',
         '\tif on:\n\t\tplace_label.text = tr("Tap a free tile to set the rally flag.") if ctl.rally_mode else ctl.place_text()'),
        ('elif ctl.placing != "":\n\t\tctl.cancel_pressed()', 'elif ctl.placing != "" or ctl.rally_mode:\n\t\tctl.cancel_pressed()'),
    ])
    edit(scripts / "glyph.gd", [
        ('\t\t"cross":', '''\
		"rally":
			draw_line(Vector2(21, 84) * u, Vector2(21, 15) * u, OUTLINE, 11 * u, true)
			draw_line(Vector2(21, 84) * u, Vector2(21, 15) * u, Color(0.96, 0.84, 0.61), 5 * u, true)
			draw_colored_polygon(PackedVector2Array([Vector2(25, 17) * u, Vector2(82, 30) * u, Vector2(60, 43) * u, Vector2(25, 52) * u]), Color(0.24, 0.69, 1.0))
		"cross":'''),
    ])
