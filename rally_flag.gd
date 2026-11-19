class_name RallyFlag
extends Node2D


func _ready() -> void:
	z_index = 45  # The player's own waypoint stays visible over unexplored ground.
	queue_redraw()


func _draw() -> void:
	var edge := Color(0.06, 0.10, 0.15, 0.95)
	draw_circle(Vector2.ZERO, 6.0, edge)
	draw_line(Vector2.ZERO, Vector2(0, -51), edge, 7.0, true)
	draw_line(Vector2.ZERO, Vector2(0, -51), Color(0.96, 0.84, 0.61), 3.0, true)
	var banner := PackedVector2Array([Vector2(2, -50), Vector2(31, -43), Vector2(20, -34), Vector2(2, -29)])
	draw_colored_polygon(banner, Color(0.24, 0.69, 1.0))
	banner.append(banner[0])
	draw_polyline(banner, edge, 2.5, true)
