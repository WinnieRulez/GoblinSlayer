class_name Goblin
extends CharacterBody2D
## Nemico di terra: goblin o lupo. Cammina avanti e indietro, si gira ai muri e ai bordi,
## a volte salta verso il giocatore. Il lupo corre quando il giocatore è vicino.

@export var speed := 32.0
@export var hp := 1
@export var points := 100
@export var hop_velocity := -230.0
@export var gravity := 900.0
@export_enum("goblin", "wolf") var kind := "goblin"
## Velocità quando il lupo carica il giocatore
@export var charge_speed := 0.0
## Probabilità di lasciare un'arma quando muore
@export var drop_chance := 0.12

const ANIMS := {
	"goblin": {
		&"walk": {"frames": [0, 1, 2, 3], "fps": 8.0},
		&"run": {"frames": [0, 1, 2, 3], "fps": 12.0},
		&"jump": {"frames": [4], "fps": 1.0},
		&"attack": {"frames": [6], "fps": 1.0},
	},
	# lupo: spritesheet 12 colonne (celle 72x48), disegnato rivolto a sinistra
	"wolf": {
		&"walk": {"frames": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], "fps": 12.0},
		&"run": {"frames": [12, 13, 14, 15, 16], "fps": 12.0},
		&"jump": {"frames": [26], "fps": 1.0},
		&"attack": {"frames": [12, 13, 14, 15, 16], "fps": 14.0},
	},
}

enum State { EMERGE, WALK, DEAD }

var state := State.WALK
var dir := -1
var _hop_timer := 0.0
var _flash := 0.0
var ledge_ahead := 7.0

@onready var sprite: FrameAnim = $Sprite
@onready var ledge: RayCast2D = $LedgeRay


func _ready() -> void:
	add_to_group("enemies")
	ledge_ahead = absf($Shape.shape.size.x) / 2.0 + 2.0
	sprite.animations = ANIMS[kind]
	sprite.play(&"walk")
	_hop_timer = randf_range(1.0, 3.0)
	var p := _player()
	if p:
		dir = 1 if p.global_position.x > global_position.x else -1


## Il goblin spunta dal terreno (usato dalle buche dei goblin).
func emerge() -> void:
	state = State.EMERGE
	sprite.scale.y = 0.0
	Fx.spawn(get_parent(), &"puff", global_position + Vector2(0, -4))
	var tw := create_tween()
	tw.tween_property(sprite, "scale:y", 1.0, 0.45).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_callback(func(): state = State.WALK)


func is_dangerous() -> bool:
	return state == State.WALK


func _player() -> Player:
	return get_tree().get_first_node_in_group("player") as Player


func _physics_process(delta: float) -> void:
	if state != State.WALK:
		return
	velocity.y += gravity * delta
	var p := _player()
	var near := p != null and absf(p.global_position.x - global_position.x) < 110.0 \
			and absf(p.global_position.y - global_position.y) < 40.0
	var spd := charge_speed if charge_speed > 0.0 and near else speed
	if is_on_floor():
		if charge_speed > 0.0 and near:
			dir = 1 if p.global_position.x > global_position.x else -1
		velocity.x = dir * spd
		ledge.position.x = ledge_ahead * dir
		ledge.force_raycast_update()
		if not ledge.is_colliding():
			dir = -dir
			velocity.x = dir * spd
		_hop_timer -= delta
		if _hop_timer <= 0.0:
			_hop_timer = randf_range(1.5, 3.5)
			if p and absf(p.global_position.x - global_position.x) < 90.0:
				velocity.y = hop_velocity
				velocity.x = dir * spd * 1.6
	move_and_slide()
	if is_on_wall():
		dir = 1 if get_wall_normal().x > 0.0 else -1
	if global_position.y > 2000.0:
		queue_free()

	_flash -= delta
	sprite.modulate = Color(3, 3, 3) if _flash > 0.0 else Color.WHITE
	if not is_on_floor():
		sprite.play(&"jump")
	else:
		var close := p != null and absf(p.global_position.x - global_position.x) < 28.0 \
				and absf(p.global_position.y - global_position.y) < 24.0
		sprite.play(&"attack" if close else (&"run" if spd > speed else &"walk"))
	sprite.flip_h = (dir < 0) if kind == "goblin" else (dir > 0)


func hit(damage: int, from_dir: int) -> void:
	hp -= damage
	Game.play_sfx("hit")
	if hp > 0:
		_flash = 0.1
		position.x += 4 * from_dir
		return
	state = State.DEAD
	Game.add_score(points)
	Game.play_sfx("goblin_die")
	Fx.spawn(get_parent(), &"puff", global_position + Vector2(0, -10))
	if randf() < drop_chance:
		var names := Dagger.WEAPONS.keys().filter(func(n): return n != Game.weapon)
		WeaponPickup.drop(get_parent(), global_position, names.pick_random())
	queue_free()
