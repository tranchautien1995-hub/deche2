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
	Rules.raw["civ_info"] = [{"id": 1, "name": "Britons", "text": "Civ test"}]
	var setup := NewGameScreen.new()
	add_child(setup)
	_check(Defs.DIFFICULTY_ORDER == ["easy", "medium", "hard"], "Three difficulty levels")
	setup._choice["difficulty"] = "hard"
	setup._choice["map_size"] = "tiny"
	setup._ai = [{"civ": 0, "team": 2}, {"civ": 0, "team": 1}]
	setup._player_team = 2
	setup._start()
	_check(Defs.load_difficulty() == "hard" and GameSetup.load_map_size() == "tiny", "Skirmish settings saved")
	_check(GameSetup.load_ai().size() == 2 and GameSetup.load_player_team() == 2, "Skirmish teams saved")
	setup.queue_free()

	var host := RoomCodeScreen.new()
	var guest := RoomCodeScreen.new()
	add_child(host)
	add_child(guest)
	var code := RoomCodeScreen.generate_code()
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
