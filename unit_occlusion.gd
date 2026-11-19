class_name UnitOcclusion
extends Node2D

const SCAN_INTERVAL := 0.08
const TREE_RADIUS := 5
const BODY_POINTS := [Vector2(0, -22), Vector2(-5, -18), Vector2(5, -18)]

var map: GameMap
var camera: RtsCamera
var _elapsed := SCAN_INTERVAL
var _shown: Dictionary = {}
var _tint: ShaderMaterial


func _ready() -> void:
	# Above entities and below the fog of war.
	z_index = 12
	var shader := Shader.new()
	shader.code = """shader_type canvas_item;
	render_mode unshaded;
	void fragment() {
		float mask = texture(TEXTURE, UV).a;
		COLOR = vec4(0.22, 1.0, 0.29, 0.78 * mask);
	}"""
	_tint = ShaderMaterial.new()
	_tint.shader = shader


func _process(delta: float) -> void:
	_elapsed += delta
	if _elapsed >= SCAN_INTERVAL:
		_elapsed = 0.0
		_scan()
	for unit in _shown.keys():
		if not is_instance_valid(unit) or not _eligible(unit):
			_remove(unit)
			continue
		var marker: Sprite2D = _shown[unit]
		marker.global_transform = unit.global_transform
		marker.texture = unit.texture
		marker.region_rect = unit.region_rect
		marker.offset = unit.offset
		marker.flip_h = unit.flip_h
		marker.flip_v = unit.flip_v


func _scan() -> void:
	var screen := camera.get_viewport_rect().grow(64.0)
	var scene_rect := Rect2(camera.screen_to_world(screen.position), screen.size / camera.zoom.x)
	var buildings: Array[Sprite2D] = []
	for list in [map.buildings, map.foes]:
		for b: Building in list:
			if b.alive and b.texture != null and b.is_visible_in_tree() \
					and b.get_rect().intersects(b.global_transform.affine_inverse() * scene_rect):
				buildings.append(b)
	var covered := {}
	for unit in map.mobs:
		if _eligible(unit) and screen.has_point(camera.world_to_screen(unit.position)) and _is_covered(unit, buildings):
			covered[unit] = true
			if not _shown.has(unit):
				var marker := Sprite2D.new()
				marker.centered = false
				marker.region_enabled = true
				marker.material = _tint
				add_child(marker)
				_shown[unit] = marker
	for unit in _shown.keys():
		if not covered.has(unit):
			_remove(unit)


func _remove(unit: Variant) -> void:
	_shown[unit].queue_free()
	_shown.erase(unit)


func _eligible(unit: Mob) -> bool:
	return unit.team == 0 and unit.alive and unit.garrisoned_in == null and unit.is_visible_in_tree() \
		and (unit is Villager or unit is Soldier) and unit.texture != null


func _is_covered(unit: Mob, buildings: Array[Sprite2D]) -> bool:
	for b in buildings:
		if _covers_unit(b, unit):
			return true
	var cell := unit.cell()
	for dx in range(-TREE_RADIUS, TREE_RADIUS + 1):
		for dy in range(-TREE_RADIUS, TREE_RADIUS + 1):
			var tree: ResNode = map.res_by_cell.get(cell + Vector2i(dx, dy))
			if is_instance_valid(tree) and tree.alive and tree.kind == "wood" and tree.is_visible_in_tree() \
					and _covers_unit(tree, unit):
				return true
	return false


static func _covers_unit(sprite: Sprite2D, unit: Mob) -> bool:
	if sprite.position.y < unit.position.y or (is_equal_approx(sprite.position.y, unit.position.y) and sprite.get_index() < unit.get_index()):
		return false
	for offset: Vector2 in BODY_POINTS:
		if sprite.is_pixel_opaque(sprite.to_local(unit.to_global(offset))):
			return true
	return false
