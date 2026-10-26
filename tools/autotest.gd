extends SceneTree
## Test automatico: avvia il livello, simula input e salva screenshot in user://.
## Uso: godot --path . --script res://tools/autotest.gd

var frame := 0
var shots := 0
var script_steps := [
	[30, "shot"],
	[40, "tp", Vector2(33 * 16 + 8, 176)],       # ai piedi della prima scala
	[45, "press", "move_up"],
	[90, "shot"],                                # a metà scala
	[300, "release", "move_up"],
	[305, "shot"],                               # in cima alla collina
	[245, "weapon", "battlehammer"],
	[250, "press", "attack"],
	[252, "release", "attack"],
	[260, "shot"],
	[280, "tp", Vector2(97 * 16, 170)],
	[285, "weapon", "earthstaff"],
	[310, "press", "attack"],
	[312, "release", "attack"],
	[320, "shot"],
	[340, "tp", Vector2(160 * 16, 170)],
	[342, "weapon", "enchantedbow"],
	[380, "press", "attack"],
	[382, "release", "attack"],
	[390, "shot"],
	[480, "shot"],
	[560, "shot"],
	[640, "shot"],
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
			"weapon":
				root.get_node("Game").weapon = s[2]
				for d in get_nodes_in_group("player_daggers"):
					d.queue_free()
			"tp":
				var pl = current_scene.get_node("Entities/Player")
				pl._end_climb()
				pl.global_position = s[2]
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
				" enemies ", get_nodes_in_group("enemies").size(), " lives ", root.get_node("Game").lives, " fps ", Engine.get_frames_per_second())
	if frame >= 310 and frame <= 330 and frame % 4 == 2:
		for d in get_nodes_in_group("player_daggers"):
			print("  arma ", d.weapon, " ", d.global_position.round(), " vis ", d.visible)
	return frame > 650
