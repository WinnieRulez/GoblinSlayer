class_name Debris
extends Sprite2D
## Frammento che vola via con un arco (pezzi di armatura, ossa...) e poi sparisce.

var velocity := Vector2.ZERO
var gravity := 700.0
var life := 1.2
var spin := 0.0


func _ready() -> void:
	spin = randf_range(-12.0, 12.0)
	z_index = 5


func _process(delta: float) -> void:
	velocity.y += gravity * delta
	position += velocity * delta
	rotation += spin * delta
	life -= delta
	if life < 0.4:
		visible = int(life * 20.0) % 2 == 0
	if life <= 0.0:
		queue_free()
