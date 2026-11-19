extends Node

var _failures := 0


func _ready() -> void:
	_run.call_deferred()


func _check(condition: bool, message: String) -> bool:
	if not condition:
		_failures += 1
		push_error(message)
	return condition


func _finish() -> void:
	print("LOBBY AND ROOM CODE: %d failures" % _failures)
	get_tree().quit(1 if _failures else 0)


func _run() -> void:
	_check(Lang.t("New Game") == "Đấu với máy", "Vietnamese skirmish title")
	_check(Lang.t("Easy") == "Dễ" and Lang.t("Medium") == "Trung bình" and Lang.t("Hard") == "Khó", "Vietnamese difficulty labels")
	_check(GameSetup.load_resources() == "medium", "Default starting resources")
	for mode in GameSetup.MODES:
		for level in GameSetup.RESOURCES:
			var amount := GameSetup.resource_amount(level)
			_check(GameSetup.stock(level, mode) == {"food": amount, "wood": amount, "gold": amount, "stone": amount}, "Resource tier applies in " + mode)
	_check(GameSetup.stock("medium").food == 500 and GameSetup.stock("low").food == 250 and GameSetup.stock("high").food == 1000, "Starting resource amounts")
	Rules.raw["civ_info"] = [{"id": 1, "name": "Britons", "text": "Civ test"}]
	var setup := NewGameScreen.new()
	add_child(setup)
	_check(Defs.DIFFICULTY_ORDER == ["easy", "medium", "hard"], "Three difficulty levels")
	setup._choice["difficulty"] = "hard"
	setup._choice["map_size"] = "tiny"
	setup._choice["population_limit"] = 75
	setup._choice["resources"] = "high"
	setup._ai = [{"civ": 0, "team": 2}, {"civ": 0, "team": 1}]
	setup._player_team = 2
	setup._start()
	_check(Defs.load_difficulty() == "hard" and GameSetup.load_map_size() == "tiny", "Skirmish settings saved")
	_check(GameSetup.load_ai().size() == 2 and GameSetup.load_player_team() == 2, "Skirmish teams saved")
	_check(GameSetup.load_population() == 75 and GameSetup.load_resources() == "high", "Skirmish population and resources saved")
	setup.queue_free()
	_check_world_overlay()

	var host := RoomCodeScreen.new()
	var guest := RoomCodeScreen.new()
	add_child(host)
	add_child(guest)
	var code := RoomCodeScreen.generate_code(3, 0)
	_check(RoomCodeScreen.settings_from_code(code) == {"population_limit": 100, "resources": "low"}, "Room code carries host settings")
	_check(RoomCodeScreen.normalize(code) == code, "Generated code is valid")
	_check(RoomCodeScreen.normalize("abcd-2345") == "ABCD2345", "Pasted code is normalized")
	_check(RoomCodeScreen.normalize("ABCD-0000").is_empty(), "Invalid code is rejected")

	await guest._connect_room("g", code)
	_check(guest.api == null and guest._role.is_empty(), "Room cannot be joined before the host opens it")
	await host._connect_room("h", code)
	if not _check(is_instance_valid(host.api) and host._code_label.visible and host._start.disabled, "Host sees a code and waits for a friend"):
		_finish()
		return
	await guest._connect_room("g", code)
	if not _check(is_instance_valid(guest.api) and guest._room_id > 0, "Guest joins using the room code"):
		await host.api.shutdown()
		_finish()
		return
	await get_tree().create_timer(1.6).timeout
	_check(host._invite == guest._room_id and not host._start.disabled, "Host receives guest and can start")
	_check(host._settings_label.text == guest._settings_label.text, "Host and guest see identical match settings")

	# Keep this test scene open while testing the server acceptance and relay.
	host._launching = true
	guest._launching = true
	await host._accept()
	await get_tree().create_timer(1.6).timeout
	var host_room: Variant = host.api.room
	var guest_room: Variant = guest.api.room
	if _check(host_room is Dictionary and guest_room is Dictionary, "Both players have a room"):
		_check(host_room.status == "playing" and guest_room.status == "playing", "Both players start the same match")
		_check(host_room.seed == guest_room.seed and host_room.you != guest_room.you, "Same map seed and distinct slots")
		var sent := await guest.api.send_relay("ping", "room-test")
		_check(sent.get("ok", false), "Guest can send a game message")
		var result := await host.api.call_api("relay", "poll", {"room": int(host_room.id), "since": 0, "wait": 0})
		var messages: Array = result.get("msgs", [])
		_check(messages.size() == 1 and messages[0].data == "room-test", "Host receives the guest's game message")
	await guest.api.shutdown()
	await host.api.shutdown()
	_finish()


func _check_world_overlay() -> void:
	Rules.civs = [{}, {"tech_tree": -1}]
	var map := GameMap.new()
	map.civ = 17
	map.population_limit = 125
	map.recalc_pop()
	_check(map.pop_cap == 125, "No-house civilizations honor population limit")
	var rival := Rival.new()
	rival.map = map
	rival.civ = 17
	_check(rival.pop_cap() == 125 and "POPULATION-CAP-125" in AiLoader.defines("medium", 17, 144, "standard", "conquest", 125), "AI honors population limit")
	rival.free()
	map.free()

	var unit := Villager.new()
	var blocker := Sprite2D.new()
	var art := Image.create(60, 80, false, Image.FORMAT_RGBA8)
	art.fill(Color.WHITE)
	blocker.texture = ImageTexture.create_from_image(art)
	add_child(unit)
	add_child(blocker)
	blocker.position = Vector2(0, 8)
	_check(UnitOcclusion._covers_unit(blocker, unit), "Opaque foreground tree or building covers the unit")
	blocker.position = Vector2(0, -8)
	_check(not UnitOcclusion._covers_unit(blocker, unit), "Background object does not cover the unit")
	blocker.position = Vector2(0, 8)
	art.fill(Color.TRANSPARENT)
	blocker.texture = ImageTexture.create_from_image(art)
	_check(not UnitOcclusion._covers_unit(blocker, unit), "Transparent areas do not trigger a silhouette")
	blocker.queue_free()
	unit.queue_free()
