class_name Fx
extends FrameAnim
## Effetto animato che si distrugge alla fine (fumo, scintille).

const PUFF := preload("res://assets/sprites/puff.png")
const SPARK := preload("res://assets/sprites/spark.png")


static func spawn(parent: Node, kind: StringName, pos: Vector2) -> void:
	var fx := Fx.new()
	match kind:
		&"puff":
			fx.texture = PUFF
			fx.hframes = 5
			fx.animations = {&"play": {"frames": [0, 1, 2, 3, 4], "fps": 14.0, "loop": false}}
		&"spark":
			fx.texture = SPARK
			fx.hframes = 3
			fx.animations = {&"play": {"frames": [0, 1, 2], "fps": 20.0, "loop": false}}
	fx.position = pos
	fx.z_index = 6
	parent.add_child(fx)
	fx.play(&"play")
	fx.finished.connect(func(_n): fx.get_tree().create_timer(0.06).timeout.connect(fx.queue_free))
