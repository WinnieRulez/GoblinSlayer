class_name Ghost
extends Goblin
## Spettro incappucciato: compare dal nulla, vola verso il giocatore ondeggiando come i
## cavalieri volanti di Ghosts'n Goblins, e svanisce se lo supera di molto.

@export var fly_speed := 48.0
@export var bob := 10.0
@export var life_time := 14.0

const GHOST_ANIMS := {
	&"walk": {"frames": [0, 1, 2, 3, 4, 5, 6], "fps": 9.0},
	&"appear": {"frames": [7, 8, 9, 10, 11, 12], "fps": 10.0, "loop": false},
	&"vanish": {"frames": [14, 15, 16, 17, 18, 19, 20], "fps": 12.0, "loop": false},
	&"shriek": {"frames": [21, 22, 23, 24], "fps": 10.0},
}

var _t := 0.0
var _y := 0.0


func _ready() -> void:
	add_to_group("enemies")
	sprite.animations = GHOST_ANIMS
	sprite.play(&"walk")
	_y = global_position.y
	var p := _player()
	if p:
		dir = 1 if p.global_position.x > global_position.x else -1


func emerge() -> void:
	state = State.EMERGE
	sprite.play(&"appear")
	await sprite.finished
	if state == State.EMERGE:
		state = State.WALK
		sprite.play(&"walk")


func _physics_process(delta: float) -> void:
	_flash -= delta
	sprite.modulate = Color(3, 3, 3) if _flash > 0.0 else Color(1, 1, 1, 0.92)
	sprite.flip_h = dir < 0
	if state != State.WALK:
		return
	_t += delta
	var p := _player()
	if p:
		var dx := p.global_position.x - global_position.x
		# scende lentamente verso l'altezza del giocatore
		_y = move_toward(_y, p.global_position.y - 20.0, 22.0 * delta)
		var close := absf(dx) < 40.0
		sprite.play(&"shriek" if close else &"walk")
		if dx * dir < -170.0 or _t > life_time:
			_vanish()
			return
	global_position.x += dir * fly_speed * delta
	global_position.y = _y + sin(_t * 3.0) * bob


func _vanish() -> void:
	state = State.EMERGE
	sprite.play(&"vanish")
	await sprite.finished
	queue_free()
