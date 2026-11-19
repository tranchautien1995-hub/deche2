extends Node

var _failures := 0


func _ready() -> void:
	_run.call_deferred()


func _check(condition: bool, note: String) -> void:
	if not condition:
		_failures += 1
		push_error(note)


func _run() -> void:
	Rules.civs = [{}, {"tech_tree": -1}]
	var map := GameMap.new()
	map.size = 120
	map.occ.resize(map.size * map.size)
	var positions := {}
	for seed_value in [1, 2, 3, 6, 12, 20, 31, 54, 75, 103, 174, 211]:
		map.world_seed = seed_value
		map._make_terrain_grid()
		map.astar = map._new_grid(map.size)
		for y in map.size:
			for x in map.size:
				var cell := Vector2i(x, y)
				if map.is_water(cell):
					map.astar.set_point_solid(cell, true)
		var base := map.pick_starting_base()
		positions[base] = true
		_check(map._starting_land(base), "Town Center and starting units have dry ground")
		_check(base == map.pick_starting_base(), "The same map seed preserves the player's starting site")
	_check(positions.size() >= 8, "Different seeds distribute bases across the map")

	var notifications := [0]
	map.battle_alert.connect(func() -> void: notifications[0] += 1)
	var opponent := Building.new()
	var player := Building.new()
	opponent.team = 1
	map.report_engagement(0, opponent)
	map.report_engagement(1, player)
	map.report_engagement(0, player)
	map.report_engagement(0, null)
	map.groups[1] = 0
	map.report_engagement(0, opponent)
	_check(notifications[0] == 2, "The alert sounds in both directions only for hostile player combat")
	Sfx.reset_battle_alert()
	Sfx.play_battle_alert()
	_check(Sfx._battle_player.stream is AudioStreamWAV and Sfx._last_battle_ms >= 0, "The battle bell has a playable fallback audio clip")
	opponent.free()
	player.free()
	map.free()
	print("BATTLE AND SPAWN: %d failures" % _failures)
	get_tree().quit(1 if _failures else 0)
