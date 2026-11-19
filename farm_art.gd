class_name FarmArt
extends RefCounted

const LEGACY := {
	"farm_cnst1": "farm_fresh", "farm_cnst2": "farm_fresh", "farm_cnst3": "farm_grown",
	"farm_full": "farm_grown", "farm_fallow": "farm_fresh",
}


static func sheet(stage: String) -> Dictionary:
	var terrain: Dictionary = Assets.man.get("terrain", {})
	for key: String in [stage, LEGACY[stage]]:
		var record: Dictionary = terrain.get(key, {})
		if int(record.get("frames", 0)) > 0 and int(record.get("cols", 0)) > 0 and Assets.tex(String(record.file)) != null:
			return record
	return {}


static func region(art: Dictionary, frame: int) -> Rect2:
	var cols := int(art.cols)
	var pad := float(art.pad)
	return Rect2(pad + (frame % cols) * float(art.cw), pad + floori(float(frame) / cols) * float(art.ch), float(art.tw), float(art.th))


static func draw_missing_tile(canvas: CanvasItem, centre: Vector2, green: bool) -> void:
	# Older or incomplete imports can still show the farm footprint and crop rows.
	var top := centre + Vector2(0, -Iso.HH)
	var right := centre + Vector2(Iso.HW, 0)
	var bottom := centre + Vector2(0, Iso.HH)
	var left := centre + Vector2(-Iso.HW, 0)
	canvas.draw_colored_polygon(PackedVector2Array([top, right, bottom, left]), Color(0.43, 0.29, 0.14))
	var row_color := Color(0.51, 0.65, 0.25) if green else Color(0.30, 0.19, 0.09)
	for i in range(1, 6):
		var at := float(i) / 6.0
		canvas.draw_line(top.lerp(left, at), right.lerp(bottom, at), row_color, 2.5, true)
