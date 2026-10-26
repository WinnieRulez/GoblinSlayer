class_name Player
extends CharacterBody2D
## Goblin Slayer. Controlli alla Ghosts'n Goblins: salto "impegnato" (in aria non si
## cambia traiettoria), pugnali da lancio, l'armatura assorbe un colpo e poi vola via.

signal died
signal armor_changed(armored: bool)

@export var run_speed := 90.0
@export var jump_velocity := -360.0
@export var gravity := 900.0
@export var max_fall_speed := 360.0
## Come nell'originale: una volta staccati da terra la traiettoria non si può correggere.
@export var classic_jump := true
@export var max_daggers := 3
@export var throw_cooldown := 0.22
@export var invulnerable_time := 1.6

const DAGGER := preload("res://scenes/dagger.tscn")
const TEX_ARMOR := preload("res://assets/sprites/slayer_armor.png")
const TEX_NOARMOR := preload("res://assets/sprites/slayer_noarmor.png")
## Fotogrammi nello spritesheet 12x9 (celle 96x80, una riga per animazione: vedi tools/import_packs.py)
const ANIMS := {
	&"idle": {"frames": [0, 1, 2, 3], "fps": 6.0},
	&"run": {"frames": [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], "fps": 16.0},
	&"jump_up": {"frames": [36, 37], "fps": 10.0, "loop": false},
	&"jump_down": {"frames": [38, 39, 40], "fps": 10.0, "loop": false},
	&"throw": {"frames": [25, 27, 28], "fps": 16.0, "loop": false},
	&"crouch": {"frames": [49, 50], "fps": 14.0, "loop": false},
	&"crouch_throw": {"frames": [62], "fps": 1.0},
	&"hurt": {"frames": [72, 73], "fps": 8.0, "loop": false},
	&"dead": {"frames": [96], "fps": 1.0},
}

enum State { NORMAL, HURT, DEAD, WIN }

var state := State.NORMAL
var armored := true
var facing := 1
var crouching := false
var fall_limit := INF

var _throw_timer := 0.0
var _throw_anim := 0.0
var _invuln := 0.0
var _hurt_timer := 0.0
var _stand_shape := RectangleShape2D.new()
var _crouch_shape := RectangleShape2D.new()

@onready var sprite: FrameAnim = $Sprite
@onready var shape: CollisionShape2D = $Shape
@onready var hurtbox: Area2D = $Hurtbox
@onready var hurt_shape: CollisionShape2D = $Hurtbox/Shape


func _ready() -> void:
	add_to_group("player")
	sprite.animations = ANIMS
	sprite.play(&"idle")
	_stand_shape.size = Vector2(14, 36)
	_crouch_shape.size = Vector2(14, 24)
	_set_crouch(false)
	_invuln = 1.0  # breve protezione all'inizio/respawn


func _physics_process(delta: float) -> void:
	_throw_timer -= delta
	_throw_anim -= delta
	if _invuln > 0.0:
		_invuln -= delta
		sprite.visible = _invuln <= 0.0 or int(_invuln * 20.0) % 2 == 0
	velocity.y = min(velocity.y + gravity * delta, max_fall_speed)

	match state:
		State.NORMAL:
			_normal_state()
		State.HURT:
			_hurt_timer -= delta
			if _hurt_timer <= 0.0 and is_on_floor():
				state = State.NORMAL
		State.DEAD, State.WIN:
			if is_on_floor():
				velocity.x = move_toward(velocity.x, 0.0, 400.0 * delta)

	move_and_slide()
	if state != State.DEAD:
		_check_hurtbox()
		if global_position.y > fall_limit:
			die()
	_update_animation()


func _normal_state() -> void:
	var dir := Input.get_axis("move_left", "move_right")
	var on_floor := is_on_floor()
	_set_crouch(on_floor and Input.is_action_pressed("crouch"))

	if dir != 0.0 and (on_floor or not classic_jump or _throw_anim <= 0.0):
		facing = 1 if dir > 0.0 else -1
	if on_floor:
		velocity.x = 0.0 if crouching else dir * run_speed
		if Input.is_action_just_pressed("jump") and not crouching:
			velocity.y = jump_velocity
			Game.play_sfx("jump")
	elif not classic_jump:
		velocity.x = dir * run_speed
		if Input.is_action_just_released("jump") and velocity.y < 0.0:
			velocity.y *= 0.5

	if Input.is_action_just_pressed("attack"):
		_throw()


func _set_crouch(value: bool) -> void:
	crouching = value
	var s := _crouch_shape if value else _stand_shape
	if shape.shape == s:
		return
	shape.shape = s
	shape.position = Vector2(0, -s.size.y / 2.0)
	hurt_shape.shape = s
	hurt_shape.position = shape.position


func _throw() -> void:
	if _throw_timer > 0.0 or get_tree().get_nodes_in_group("player_daggers").size() >= max_daggers:
		return
	_throw_timer = throw_cooldown
	_throw_anim = 0.2
	sprite.play(&"crouch_throw" if crouching else &"throw", true)
	var d: Dagger = DAGGER.instantiate()
	d.direction = facing
	d.global_position = global_position + Vector2(14 * facing, -12 if crouching else -21)
	get_parent().add_child(d)
	Game.play_sfx("throw")


func _check_hurtbox() -> void:
	for body in hurtbox.get_overlapping_bodies():
		if body.is_in_group("hazard"):
			die()
			return
		if body is Goblin and body.is_dangerous():
			take_hit(body.global_position.x)
			return


func take_hit(from_x: float) -> void:
	if _invuln > 0.0 or state == State.DEAD or state == State.WIN:
		return
	if not armored:
		die()
		return
	set_armored(false)
	Game.play_sfx("armor_lost")
	_spawn_armor_bits()
	state = State.HURT
	_hurt_timer = 0.25
	_set_crouch(false)
	var away := signf(global_position.x - from_x)
	if away == 0.0:
		away = -facing
	velocity = Vector2(away * 90.0, -200.0)
	_invuln = invulnerable_time


func set_armored(value: bool) -> void:
	armored = value
	sprite.texture = TEX_ARMOR if value else TEX_NOARMOR
	armor_changed.emit(value)


func restore_armor() -> void:
	if not armored:
		set_armored(true)


func die() -> void:
	if state == State.DEAD:
		return
	state = State.DEAD
	if armored:
		set_armored(false)
	_set_crouch(false)
	sprite.visible = true
	_invuln = 0.0
	velocity = Vector2(-facing * 40.0, -180.0)
	Game.play_sfx("death", 0.0)
	await get_tree().create_timer(2.0).timeout
	died.emit()


func win() -> void:
	state = State.WIN
	velocity.x = 0.0


func _spawn_armor_bits() -> void:
	for i in 4:
		var bit := Debris.new()
		bit.texture = preload("res://assets/sprites/armor_bits.png")
		bit.hframes = 4
		bit.frame = i
		bit.velocity = Vector2(randf_range(-110, 110), randf_range(-260, -150))
		bit.global_position = global_position + Vector2(0, -26)
		get_parent().add_child(bit)


func _update_animation() -> void:
	var anim := &"idle"
	match state:
		State.DEAD:
			anim = &"dead"
		State.HURT:
			anim = &"hurt"
		State.WIN:
			anim = &"idle"
		_:
			if crouching:
				anim = &"crouch_throw" if _throw_anim > 0.0 else &"crouch"
			elif _throw_anim > 0.0:
				anim = &"throw"
			elif not is_on_floor():
				anim = &"jump_up" if velocity.y < 0.0 else &"jump_down"
			elif absf(velocity.x) > 1.0:
				anim = &"run"
	sprite.play(anim)
	sprite.flip_h = facing < 0
