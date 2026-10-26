class_name Dagger
extends Area2D
## Pugnale da lancio del Goblin Slayer: vola dritto, uccide al contatto, si rompe sui muri.

@export var speed := 260.0
@export var max_distance := 240.0
@export var damage := 1

var direction := 1
var _travelled := 0.0

@onready var sprite: Sprite2D = $Sprite


func _ready() -> void:
	add_to_group("player_daggers")
	sprite.flip_h = direction < 0
	body_entered.connect(_on_body_entered)


func _physics_process(delta: float) -> void:
	var step := speed * delta
	position.x += step * direction
	_travelled += step
	if _travelled > max_distance:
		queue_free()


func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("oneway") or body.is_in_group("hazard"):
		return
	if body is Goblin:
		if not body.is_dangerous():
			return
		body.hit(damage, direction)
	Fx.spawn(get_parent(), &"spark", global_position)
	queue_free()
