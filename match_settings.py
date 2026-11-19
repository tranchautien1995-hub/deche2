"""Apply the iPhone match settings to the pinned upstream game."""

from pathlib import Path
from shutil import copyfile


def apply_match_settings(project, edit):
    scripts = project / "scripts"
    source = Path(__file__).parent
    copyfile(source / "unit_occlusion.gd", scripts / "unit_occlusion.gd")

    edit(scripts / "game_setup.gd", [
        ('const RESOURCE_NAMES := ["Low", "Medium", "High"]',
         'const RESOURCE_NAMES := ["Low (250)", "Medium (500)", "High (1000)"]\n'
         'const RESOURCE_AMOUNTS := {"low": 250, "medium": 500, "high": 1000}\n'
         'const DEFAULT_RESOURCES := "medium"\n'
         'const MAX_POPULATION := 150\n'
         'const POPULATION_OPTIONS := [25, 50, 75, 100, 125, MAX_POPULATION]'),
        ('## What each stockpile opens at (the lobby\'s figures): {food, wood, stone, gold}. Death Match is 20,000 of everything.\n'
         'static func stock(level: String, mode: String) -> Dictionary:\n'
         '\tif mode == "deathmatch":\n'
         '\t\treturn {"food": 20000, "wood": 20000, "stone": 20000, "gold": 20000}\n'
         '\tmatch level:\n'
         '\t\t"medium":\n'
         '\t\t\treturn {"food": 500, "wood": 500, "stone": 300, "gold": 300}\n'
         '\t\t"high":\n'
         '\t\t\treturn {"food": 1000, "wood": 1000, "stone": 700, "gold": 700}\n'
         '\treturn {"food": 200, "wood": 200, "stone": 100, "gold": 100}',
         'static func stock(level: String, _mode := "standard") -> Dictionary:\n'
         '\tvar amount := resource_amount(level)\n'
         '\treturn {"food": amount, "wood": amount, "stone": amount, "gold": amount}\n\n\n'
         'static func resource_amount(level: String) -> int:\n'
         '\treturn int(RESOURCE_AMOUNTS.get(level, RESOURCE_AMOUNTS[DEFAULT_RESOURCES]))\n\n\n'
         'static func load_population() -> int:\n'
         '\tvar value := int(_load("population_limit", POPULATION_OPTIONS.map(func(n: int) -> String: return str(n)), str(MAX_POPULATION)))\n'
         '\treturn value\n\n\n'
         'static func save_population(value: int) -> void:\n'
         '\t_save("population_limit", str(value))'),
        ('static func _load(key: String, options: Array, default: String) -> String:',
         'static func _load(key: String, options: Array, default: String, section := "game") -> String:'),
        ('var v := String(cf.get_value("game", key, default))', 'var v := String(cf.get_value(section, key, default))'),
        ('static func _save(key: String, value: String) -> void:',
         'static func _save(key: String, value: String, section := "game") -> void:'),
        ('cf.set_value("game", key, value)', 'cf.set_value(section, key, value)'),
        ('_load("resources", RESOURCES, "low")', '_load("resources", RESOURCES, DEFAULT_RESOURCES, "match_rules")'),
        ('_save("resources", v)', '_save("resources", v, "match_rules")'),
    ])

    edit(scripts / "ui/new_game_screen.gd", [
        ('"victory": GameSetup.load_victory(), "reveal": GameSetup.load_reveal(), "map_size": GameSetup.load_map_size()}',
         '"victory": GameSetup.load_victory(), "reveal": GameSetup.load_reveal(), "map_size": GameSetup.load_map_size(),\n'
         '\t\t"population_limit": GameSetup.load_population()}'),
        ('\t_add_choice(col, "Starting Resources", "resources", GameSetup.RESOURCES, GameSetup.RESOURCE_NAMES)',
         '\t_add_choice(col, "Starting Resources", "resources", GameSetup.RESOURCES, GameSetup.RESOURCE_NAMES)\n'
         '\t_add_choice(col, "Population Limit", "population_limit", GameSetup.POPULATION_OPTIONS, GameSetup.POPULATION_OPTIONS)'),
        ('\tGameSetup.save_resources(_choice.resources)',
         '\tGameSetup.save_resources(_choice.resources)\n\tGameSetup.save_population(_choice.population_limit)'),
    ])
    edit(scripts / "ui/menu_kit.gd", [
        ('button(String(options[i]),', 'button(str(options[i]),'),
    ])

    edit(scripts / "main.gd", [
        ('\tvar loading := not is_mp and not pending.is_empty()',
         '\tvar loading := not is_mp and not pending.is_empty()\n'
         '\tmap.population_limit = GameSetup.load_population() if not is_mp else int(matchp.get("population_limit", GameSetup.MAX_POPULATION))'),
        ('tcs = _new_game_mp(int(matchp.slot), st)',
         'tcs = _new_game_mp(int(matchp.slot), st, String(matchp.get("resources", GameSetup.DEFAULT_RESOURCES)))'),
        ('\tcam.box_selected.connect(ctl.select_in_box)',
         '\tcam.box_selected.connect(ctl.select_in_box)\n\tvar silhouettes := UnitOcclusion.new()\n'
         '\tsilhouettes.map = map\n\tsilhouettes.camera = cam\n\tmap.add_child(silhouettes)'),
        ('\tmap.start_rivals(centre, ais if not ais.is_empty() else [{"civ": 0, "team": 0}], GameSetup.load_player_team())\n'
         '\t\tfor r in map.rivals:\n\t\t\tif map.mode == "deathmatch" or GameSetup.load_resources() != "low":\n'
         '\t\t\t\tr.stock = start_stock.duplicate()',
         '\tmap.start_rivals(centre, ais if not ais.is_empty() else [{"civ": 0, "team": 0}], GameSetup.load_player_team(), start_stock)'),
        ('func _new_game_mp(slot: int, st: Array) -> Array:',
         'func _new_game_mp(slot: int, st: Array, resources: String) -> Array:'),
        ('GameSetup.stock("low", "deathmatch")', 'GameSetup.stock(resources)'),
    ])
    # The chosen amount is the actual starting stock for every civilization.
    main = scripts / "main.gd"
    body = main.read_text(encoding="utf-8")
    bonus = '\tfor r: String in ["wood", "food", "gold", "stone"]:\n\t\tmap.stock[r] = maxi(0, int(map.stock[r]) + int(start.get(r, 0)))\n'
    if body.count(bonus) != 2:
        raise RuntimeError("Expected both match starts to award civilization resource bonuses")
    main.write_text(body.replace(bonus, ''), encoding="utf-8")

    edit(scripts / "game_map.gd", [
        ('var pop_cap := 0', 'var pop_cap := 0\nvar population_limit := GameSetup.MAX_POPULATION'),
        ('func start_rivals(player_centre: Vector2i, specs: Array, player_team := 0) -> bool:',
         'func start_rivals(player_centre: Vector2i, specs: Array, player_team := 0, starting_stock := {}) -> bool:'),
        ('\t\tr.want_civ = int(specs[i].civ)',
         '\t\tr.want_civ = int(specs[i].civ)\n'
         '\t\tif not starting_stock.is_empty():\n'
         '\t\t\tr.start_stock = starting_stock.duplicate()\n\t\t\tr.stock = starting_stock.duplicate()'),
        ('pop_cap = 200 if Defs.CIV_START.get(civ, {}).get("no_houses", false) else mini(cap, 200)',
         'pop_cap = population_limit if Defs.CIV_START.get(civ, {}).get("no_houses", false) else mini(cap, population_limit)'),
        ('\tif pop >= pop_cap:\n\t\treturn tr("Population limit reached: build Houses")',
         '\tif pop >= population_limit:\n\t\treturn tr("Match population limit reached (%d)") % population_limit\n'
         '\tif pop >= pop_cap:\n\t\treturn tr("Population limit reached: build Houses")'),
    ])

    edit(scripts / "soldier.gd", [
        ('\tif takes:\n\t\tvar t := convert_target',
         '\tif takes:\n\t\tvar t := convert_target\n'
         '\t\tif t is Mob and not (their != null and their.is_researched(HERESY)):\n'
         '\t\t\tvar rival := map.rival_of(team)\n'
         '\t\t\tvar used := rival.pop() if rival != null else 0\n'
         '\t\t\tif rival != null:\n'
         '\t\t\t\tfor building in rival.own():\n\t\t\t\t\tused += building.queue.size()\n'
         '\t\t\tif team == 0:\n\t\t\t\tmap.recalc_pop()\n\t\t\t\tused = map.pop\n'
         '\t\t\tif used >= map.population_limit:\n'
         '\t\t\t\tconvert_target = null\n\t\t\t\t_end_convert()\n\t\t\t\tstand()\n'
         '\t\t\t\tif team == 0:\n'
         '\t\t\t\t\tmap.message.emit("Match population limit reached (%d)", [map.population_limit], "")\n'
         '\t\t\t\treturn true'),
    ])

    edit(scripts / "director.gd", [
        ('\tfor i in total:\n\t\tvar kind := _pick_kind()',
         '\tfor i in mini(total, _raid_slots()):\n\t\tvar kind := _pick_kind()'),
        ('\tfor i in count:\n\t\tvar c := map.free_water_near',
         '\tfor i in mini(count, _raid_slots()):\n\t\tvar c := map.free_water_near'),
        ('\tmap.message.emit("Enemy warships are sailing in from the lake!", [], "")',
         '\tmap.message.emit("Enemy warships are sailing in from the lake!", [], "")\n\n\n'
         'func _raid_slots() -> int:\n'
         '\tvar units := 0\n'
         '\tfor mob in map.mobs:\n\t\tif mob.team == 1 and mob.alive:\n\t\t\tunits += 1\n'
         '\treturn maxi(0, map.population_limit - units)'),
    ])

    edit(scripts / "rival.gd", [
        ('var limit := Defs.RIVAL_POP_LIMIT if ai != null else 200', 'var limit := map.population_limit'),
        ('AiLoader.make(ai_host, map.difficulty, civ, map.size, ai_seed, map.mode)',
         'AiLoader.make(ai_host, map.difficulty, civ, map.size, ai_seed, map.mode, "conquest", map.population_limit)'),
        ('return pop_cap() < 200 and', 'return pop_cap() < map.population_limit and'),
        ('"age": age, "stock": stock, "wave": wave', '"age": age, "stock": stock, "start_stock": start_stock, "wave": wave'),
        ('\twave = int(e.wave)', '\tstart_stock = e.get("start_stock", start_stock).duplicate()\n\twave = int(e.wave)'),
    ])
    edit(scripts / "ai/ai_loader.gd", [
        ('"POPULATION-CAP-%d" % Defs.RIVAL_POP_LIMIT', '"POPULATION-CAP-%d" % population_limit'),
        ('mode := "standard", victory := "conquest") -> Array:',
         'mode := "standard", victory := "conquest", population_limit := GameSetup.MAX_POPULATION) -> Array:'),
        ('mode := "standard", victory := "conquest") -> AiEngine:',
         'mode := "standard", victory := "conquest", population_limit := GameSetup.MAX_POPULATION) -> AiEngine:'),
        ('defines(difficulty, civ, map_size, mode, victory)', 'defines(difficulty, civ, map_size, mode, victory, population_limit)'),
    ])
    host = scripts / 'ai/rival_host.gd'
    data = host.read_text(encoding='utf-8')
    key = 'mini(Defs.RIVAL_POP_LIMIT, 200)'
    if data.count(key) != 2:
        raise RuntimeError('Expected two AI population checks')
    host.write_text(data.replace(key, 'r.map.population_limit'), encoding='utf-8')
    edit(scripts / "defs.gd", [
        ('# The population limit the scripts are told (their unit and villager targets scale with it: 25, 50, 75, 100, 125, 150, 175, 200).\n'
         'const RIVAL_POP_LIMIT := 100\n', ''),
    ])

    edit(scripts / "save_game.gd", [
        ('"stock": map.stock, "wave":', '"stock": map.stock, "population_limit": map.population_limit, "wave":'),
        ('\tmap.difficulty = String(d.difficulty)',
         '\tmap.difficulty = String(d.difficulty)\n'
         '\tmap.population_limit = clampi(int(d.get("population_limit", GameSetup.MAX_POPULATION)), 25, GameSetup.MAX_POPULATION)'),
    ])

    edit(scripts / "minimap.gd", [
        ('\tfor p in _pings:\n\t\tvar k: float = p.t / 3.0',
         '\t# Initial AI bases are announced on the minimap even in unexplored territory.\n'
         '\tfor rival in map.rivals:\n'
         '\t\tif rival.base.x < 0 or not map.hostile(0, rival.seat):\n\t\t\tcontinue\n'
         '\t\tvar q := _p(Vector2(rival.base))\n'
         '\t\tvar team_color: Color = FoeBuilding.OWNER_COLOURS[clampi(rival.seat - 1, 0, 3)]\n'
         '\t\tdraw_circle(q, dot * 1.95, Color(0.05, 0.05, 0.05, 0.95), true, -1.0, true)\n'
         '\t\tdraw_circle(q, dot * 1.6, Color(0.98, 0.94, 0.78), true, -1.0, true)\n'
         '\t\tdraw_circle(q, dot * 1.22, team_color, true, -1.0, true)\n'
         '\tfor p in _pings:\n\t\tvar k: float = p.t / 3.0'),
    ])

    edit(scripts / "net/mp_match.gd", [
        ('static func launch(api: MpApi, tree: SceneTree) -> bool:',
         'static func launch(api: MpApi, tree: SceneTree, settings := {}) -> bool:'),
        ('Main.mp_params = {"api": api, "slot": slot, "seed": int(api.room.seed)}',
         'Main.mp_params = {"api": api, "slot": slot, "seed": int(api.room.seed)}\n'
         '\tMain.mp_params.merge(settings)'),
    ])
