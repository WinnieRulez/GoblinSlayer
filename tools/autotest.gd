extends SceneTree
## Test automatico: avvia il livello, simula input e salva screenshot in user://.
## Uso: godot --path . --script res://tools/autotest.gd

var frame := 0
var shots := 0
var script_steps := [
	[20, "tp", Vector2(40 * 16, 150)],
	[80, "shot"],
	[100, "tp", Vector2(158 * 16, 150)],
	[101, "press", "move_right"],
	[240, "shot"],
]


func _initialize() -> void:
	change_scene_to_file("res://scenes/main.tscn")


func _process(_delta: float) -> bool:
	frame += 1
	for s in script_steps:
		if s[0] != frame:
			continue
		match s[1]:
			"press":
				Input.action_press(s[2])
			"release":
				Input.action_release(s[2])
			"tp":
				current_scene.get_node("Entities/Player").global_position = s[2]
			"shot":
				var img := root.get_texture().get_image()
				img.save_png("user://shot_%02d.png" % shots)
				var p = current_scene.get_node_or_null("Entities/Player")
				print("shot ", shots, " frame ", frame, " player ", p.global_position if p else null,
					" state ", p.state if p else -1, " armored ", p.armored if p else null,
					" score ", root.get_node("Game").score, " lives ", root.get_node("Game").lives)
				shots += 1
	if frame % 40 == 0:
		var pl = current_scene.get_node_or_null("Entities/Player")
		if pl:
			print("f", frame, " pos ", pl.global_position.round(), " st ", pl.state, " arm ", pl.armored,
				" goblins ", get_nodes_in_group("enemies").size(), " lives ", root.get_node("Game").lives, " fps ", Engine.get_frames_per_second())
	return frame > 260
