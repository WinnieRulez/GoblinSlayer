extends Area2D
## Oggetto da raccogliere: l'armatura (la rimette, o dà punti se ce l'hai già) oppure un cuore (+1 vita).

@export_enum("armor", "life") var kind := "armor"
@export var points := 500

@onready var sprite: Sprite2D = $Sprite


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	var y := sprite.position.y
	var tw := create_tween().set_loops()
	tw.tween_property(sprite, "position:y", y - 3.0, 0.6).set_trans(Tween.TRANS_SINE)
	tw.tween_property(sprite, "position:y", y, 0.6).set_trans(Tween.TRANS_SINE)


func _on_body_entered(body: Node2D) -> void:
	if body is Player and body.state == Player.State.NORMAL:
		if kind == "armor":
			body.restore_armor()
		else:
			Game.lives += 1
		Game.add_score(points)
		Game.play_sfx("pickup", 0.0)
		Fx.spawn(get_parent(), &"puff", sprite.global_position)
		queue_free()
