class_name RoomCodeScreen
extends MenuScreen

const ALPHABET := "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
const CODE_LENGTH := 8

var api: MpApi
var _input: LineEdit
var _status: Label
var _code_label: LineEdit
var _actions: HBoxContainer
var _waiting: HBoxContainer
var _start: Button
var _copy: Button
var _resume_button: Button
var _setup: VBoxContainer
var _settings_label: Label
var _resource_index := GameSetup.RESOURCES.find(GameSetup.DEFAULT_RESOURCES)
var _population_index := GameSetup.POPULATION_OPTIONS.find(GameSetup.MAX_POPULATION)
var _role := ""
var _code := ""
var _invite := 0
var _room_id := 0
var _joined_at := -10000
var _busy := false
var _launching := false


static func generate_code(pop_index := GameSetup.POPULATION_OPTIONS.size() - 1, resource_index := 1) -> String:
	var code := ""
	for byte: int in Crypto.new().generate_random_bytes(CODE_LENGTH - 1):
		code += ALPHABET[byte % ALPHABET.length()]
	return code + ALPHABET[pop_index * GameSetup.RESOURCES.size() + resource_index]


static func settings_from_code(code: String) -> Dictionary:
	if code.length() != CODE_LENGTH:
		return {}
	var combination := ALPHABET.find(code.right(1))
	var levels := GameSetup.RESOURCES.size()
	if combination < 0 or combination >= GameSetup.POPULATION_OPTIONS.size() * levels:
		return {}
	return {
		"population_limit": GameSetup.POPULATION_OPTIONS[floori(float(combination) / levels)],
		"resources": GameSetup.RESOURCES[combination % levels],
	}


static func normalize(raw: String) -> String:
	var code := raw.strip_edges().to_upper().replace("-", "").replace(" ", "")
	if code.length() != CODE_LENGTH:
		return ""
	for letter: String in code:
		if not ALPHABET.contains(letter):
			return ""
	return code


static func alias(code: String, role: String) -> String:
	var digest := ("aoe2hdmobile-room-v2:%s:%s" % [role, code]).sha256_text()
	return role.to_upper() + digest.substr(0, 14)


func _ready() -> void:
	var v := make_sheet(1730, 1400, "Chơi online bằng mã")
	v.add_child(MenuKit.label("Đấu 1v1 · Hai người dùng cùng bản cập nhật", 38 * u, MenuKit.INK, HORIZONTAL_ALIGNMENT_CENTER))
	_input = MenuKit.line_edit(u, "Nhập mã phòng 8 ký tự", 16)
	_input.text_submitted.connect(func(_value: String) -> void: _join())
	v.add_child(_input)
	_setup = VBoxContainer.new()
	_setup.add_child(MenuKit.label("Chủ phòng chọn trước khi tạo phòng", 34 * u, MenuKit.INK))
	_setup.add_child(MenuKit.label("Population Limit", 35 * u))
	_setup.add_child(MenuKit.segmented(GameSetup.POPULATION_OPTIONS, _population_index, _pick_population, u, 39.0, 72.0))
	_setup.add_child(MenuKit.label("Starting Resources", 35 * u))
	_setup.add_child(MenuKit.segmented(GameSetup.RESOURCE_NAMES, _resource_index, _pick_resources, u, 39.0, 72.0))
	v.add_child(_setup)
	_settings_label = MenuKit.label("", 37 * u, MenuKit.INK, HORIZONTAL_ALIGNMENT_CENTER)
	v.add_child(_settings_label)
	_code_label = MenuKit.line_edit(u, "", CODE_LENGTH)
	_code_label.editable = false
	_code_label.alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(_code_label)
	_actions = HBoxContainer.new()
	_actions.add_child(_button("Tạo phòng", _host))
	_actions.add_child(_button("Vào phòng", _join))
	v.add_child(_actions)
	_waiting = HBoxContainer.new()
	_copy = _button("Sao chép mã", _copy_code)
	_start = _button("Bắt đầu", _accept)
	_waiting.add_child(_copy)
	_waiting.add_child(_start)
	v.add_child(_waiting)
	_status = MenuKit.label("", 37 * u, MenuKit.INK, HORIZONTAL_ALIGNMENT_CENTER)
	_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(_status)
	_resume_button = _button("Tiếp tục trận online", _resume)
	v.add_child(_resume_button)
	var spacer := Control.new()
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(spacer)
	v.add_child(_button("Quay lại", back))
	_render()


func _button(label: String, action: Callable) -> Button:
	var b := MenuKit.button(label, action, u, 0.0, 90.0, 42.0)
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return b


func _render() -> void:
	_actions.visible = _role.is_empty()
	_setup.visible = _actions.visible
	var settings := settings_from_code(_code)
	_settings_label.visible = not settings.is_empty()
	if not settings.is_empty():
		_settings_label.text = "%d đơn vị mỗi bên · %d mỗi loại tài nguyên" % [settings.population_limit, GameSetup.resource_amount(settings.resources)]
	_input.visible = _actions.visible
	_input.editable = not _busy
	for b: Button in _actions.get_children():
		b.disabled = _busy
	_waiting.visible = _role == "h" and not _busy
	_code_label.visible = _waiting.visible
	_code_label.text = _code
	_start.disabled = _invite == 0 or _busy
	_resume_button.visible = _role.is_empty() and not MpMatch.resume_info().is_empty()
	_resume_button.disabled = _busy


func _host() -> void:
	if not _busy:
		_connect_room("h", generate_code(_population_index, _resource_index))


func _pick_population(index: int) -> void:
	_population_index = index
	MenuKit.mark_segment(_setup.get_child(2), index, u)


func _pick_resources(index: int) -> void:
	_resource_index = index
	MenuKit.mark_segment(_setup.get_child(4), index, u)


func _join() -> void:
	if _busy:
		return
	var code := normalize(_input.text)
	if settings_from_code(code).is_empty():
		_status.text = "Kiểm tra mã phòng 8 ký tự và phiên bản của hai máy."
		return
	_input.release_focus()
	_connect_room("g", code)


func _connect_room(role: String, code: String) -> void:
	_role = role
	_code = code
	_busy = true
	_status.text = "Đang kết nối…"
	_render()
	_make_api()
	var result := await api.register(alias(code, role))
	if not result.get("ok", false):
		await _reset(_error(result))
		return
	api.set_beat_interval(1.0)
	if role == "g":
		result = await api.challenge_player(alias(code, "h"), randi_range(1, 2147483646))
		if not result.get("ok", false):
			await _reset(_error(result))
			return
		_room_id = int(result.room.id)
		_joined_at = Time.get_ticks_msec()
		_status.text = "Đang chờ chủ phòng bấm Bắt đầu…"
	else:
		_status.text = "Gửi mã này cho bạn chơi và giữ màn hình phòng mở."
	_busy = false
	_render()
	if role == "h":
		_on_challenge(api.challenge)
	else:
		_on_room(api.room)


func _make_api() -> void:
	api = MpApi.new()
	api.base = MpApi.server_url()
	add_child(api)
	api.room_changed.connect(_on_room)
	api.challenge_changed.connect(_on_challenge)
	api.lost.connect(_on_lost)


func _copy_code() -> void:
	DisplayServer.clipboard_set(_code)
	_status.text = "Đã sao chép mã phòng." if _invite == 0 else "Đã sao chép mã. Bạn có thể bắt đầu trận."


func _on_challenge(challenge: Variant) -> void:
	if _role != "h" or _busy or _launching:
		return
	_invite = 0
	if challenge is Dictionary:
		if String(challenge.get("nick", "")) == alias(_code, "g"):
			_invite = int(challenge.get("room", 0))
		else:
			api.defer(api.decline_challenge.bind(int(challenge.get("room", 0))))
	_status.text = "Bạn chơi đã vào phòng. Bấm Bắt đầu để vào trận." if _invite > 0 else "Đang chờ bạn chơi nhập mã…"
	_render()


func _accept() -> void:
	if _busy or _invite == 0:
		return
	_busy = true
	_room_id = _invite
	_status.text = "Đang bắt đầu trận…"
	_render()
	var result := await api.accept_challenge(_invite)
	_busy = false
	if result.get("ok", false):
		_on_room(api.room)
	else:
		_on_challenge(api.challenge)
		_status.text = _error(result)


func _on_room(room: Variant) -> void:
	if _busy or _launching or _room_id == 0:
		return
	if room is Dictionary and int(room.id) == _room_id and String(room.status) == "playing":
		_launching = true
		if not MpMatch.launch(api, get_tree(), settings_from_code(_code)):
			_launching = false
			_reset("Không thể mở trận. Hãy tạo phòng mới.")
	elif _role == "g" and Time.get_ticks_msec() - _joined_at > 2000 \
			and (not room is Dictionary or String(room.status) != "open"):
		_reset("Phòng đã đóng hoặc hết thời gian chờ.")


func _on_lost(_reason: String) -> void:
	if not _busy and not _launching:
		_reset("Mất kết nối với máy chủ. Hãy thử lại.")


func _error(result: Dictionary) -> String:
	var error := String(result.get("error", ""))
	match error:
		"player_gone", "player_busy", "room_unavailable":
			return "Phòng chưa mở hoặc đang bận. Kiểm tra mã với chủ phòng."
		"nick_taken":
			return "Mã phòng đang được sử dụng. Hãy thử lại hoặc tạo mã mới."
		"challenge_gone":
			return "Bạn chơi đã rời phòng hoặc hết thời gian chờ."
	return MpApi.error_text(error)


func _reset(message: String) -> void:
	_busy = true
	_status.text = message
	_render()
	if is_instance_valid(api):
		await api.shutdown()
		api.queue_free()
		api = null
	_busy = false
	_role = ""
	_room_id = 0
	_joined_at = -10000
	_invite = 0
	_code = ""
	_render()


func _resume() -> void:
	var info := MpMatch.resume_info()
	if _busy or info.is_empty():
		return
	_busy = true
	_status.text = "Đang kết nối lại…"
	_render()
	_make_api()
	var result := await api.resume_session(String(info.token), String(info.nick), String(info.cc), int(info.room), int(info.get("poll_wait", 8)))
	if not result.get("ok", false):
		var error := String(result.get("error", ""))
		if error == "match_over" or error == "auth":
			MpMatch.clear_resume()
			await _reset("Trận đấu đã kết thúc.")
		else:
			await _reset(_error(result))
		return
	_launching = true
	remove_child(api)
	get_tree().root.add_child(api)
	Main.mp_params = {"api": api, "slot": int(info.slot), "seed": int(info.seed), "resume": info, "next": int(info.next)}
	get_tree().change_scene_to_file(Main.SCENE)


func back() -> void:
	if _busy or _launching:
		return
	if is_instance_valid(api):
		await _reset("Đang rời phòng…")
	closed.emit()
