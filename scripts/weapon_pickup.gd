class_name WeaponPickup
extends Area2D
## Arma da raccogliere: sostituisce quella in mano (come le armi nei vasi di Ghosts'n Goblins).

@export var weapon := "silverhalberd"
@export var points := 200
## Se > 0 l'arma sparisce dopo questo tempo (quelle lasciate dai nemici)
var life := 0.0

@onready var sprite: Sprite2D = $Sprite


static func drop(parent: Node, pos: Vector2, weapon_name: String) -> void:
	var w: WeaponPickup = load("res://scenes/weapon_pickup.tscn").instantiate()
	w.weapon = weapon_name
	w.life = 8.0
	w.position = pos
	parent.call_deferred("add_child", w)


func _ready() -> void:
	sprite.texture = load(Dagger.WEAPONS[weapon]["icon"])
	body_entered.connect(_on_body_entered)
	var y := sprite.position.y
	var tw := create_tween().set_loops()
	tw.tween_property(sprite, "position:y", y - 3.0, 0.5).set_trans(Tween.TRANS_SINE)
	tw.tween_property(sprite, "position:y", y, 0.5).set_trans(Tween.TRANS_SINE)


func _process(delta: float) -> void:
	$Glow.rotation += delta * 2.0
	if life > 0.0:
		life -= delta
		visible = life > 2.0 or int(life * 10.0) % 2 == 0
		if life <= 0.0:
			queue_free()


func _on_body_entered(body: Node2D) -> void:
	if body is Player and body.state in [Player.State.NORMAL, Player.State.CLIMB]:
		Game.weapon = weapon
		Game.add_score(points)
		Game.play_sfx("pickup", 0.0)
		Fx.spawn(get_parent(), &"puff", sprite.global_position)
		queue_free()
