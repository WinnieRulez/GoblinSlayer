class_name Dagger
extends Area2D
## Arma da lancio del Goblin Slayer. Come in Ghosts'n Goblins se ne porta una alla volta:
## il pugnale all'inizio, poi quella raccolta per ultima (vedi WEAPONS).

## Caratteristiche di ogni arma. arc = vola a parabola, pierce = attraversa i nemici,
## wave = ondeggia, max = quante ce ne possono essere in volo, cooldown = pausa tra due lanci.
const WEAPONS := {
	"dagger": {"name": "PUGNALE", "tex": "res://assets/sprites/dagger.png", "icon": "res://assets/sprites/dagger.png",
		"speed": 260.0, "damage": 1, "range": 240.0, "max": 3, "cooldown": 0.22},
	"machete": {"name": "MACHETE", "tex": "res://assets/sprites/weapons/machete_shot.png", "icon": "res://assets/sprites/weapons/machete.png",
		"speed": 340.0, "damage": 1, "range": 170.0, "max": 4, "cooldown": 0.12},
	"silverhalberd": {"name": "ALABARDA", "tex": "res://assets/sprites/weapons/silverhalberd_shot.png", "icon": "res://assets/sprites/weapons/silverhalberd.png",
		"speed": 230.0, "damage": 2, "range": 300.0, "max": 2, "cooldown": 0.3},
	"battlehammer": {"name": "MARTELLO", "tex": "res://assets/sprites/weapons/battlehammer_shot.png", "icon": "res://assets/sprites/weapons/battlehammer.png",
		"speed": 140.0, "damage": 2, "range": 320.0, "max": 2, "cooldown": 0.35, "arc": -250.0, "pierce": true, "spin": 14.0},
	"enchantedbow": {"name": "ARCO", "tex": "res://assets/sprites/weapons/arrow.png", "icon": "res://assets/sprites/weapons/enchantedbow.png",
		"speed": 300.0, "damage": 1, "range": 260.0, "max": 4, "cooldown": 0.28, "spread": true},
	"earthstaff": {"name": "BASTONE", "tex": "res://assets/sprites/fireball.png", "icon": "res://assets/sprites/weapons/earthstaff.png",
		"speed": 170.0, "damage": 1, "range": 220.0, "max": 1, "cooldown": 0.4, "pierce": true, "wave": 18.0, "frames": 3},
}

@export var speed := 260.0
@export var max_distance := 240.0
@export var damage := 1

var weapon := "dagger"
var direction := 1
## Inclinazione verso l'alto (per la seconda freccia dell'arco)
var rise := 0.0
var _travelled := 0.0
var _vy := 0.0
var _gravity := 0.0
var _wave := 0.0
var _spin := 0.0
var _pierce := false
var _hit: Array[Node] = []
var _base_y := 0.0
var _time := 0.0

@onready var sprite: Sprite2D = $Sprite


func _ready() -> void:
	add_to_group("player_daggers")
	var w: Dictionary = WEAPONS[weapon]
	sprite.texture = load(w["tex"])
	sprite.hframes = w.get("frames", 1)
	speed = w["speed"]
	damage = w["damage"]
	max_distance = w["range"]
	_pierce = w.get("pierce", false)
	_wave = w.get("wave", 0.0)
	_spin = w.get("spin", 0.0)
	if w.has("arc"):
		_vy = w["arc"]
		_gravity = 700.0
	_vy += rise * speed
	sprite.flip_h = direction < 0
	if rise != 0.0:
		sprite.rotation = atan2(rise, 1.0) * direction
	_base_y = position.y
	body_entered.connect(_on_body_entered)


func _physics_process(delta: float) -> void:
	_time += delta
	var step := speed * delta
	position.x += step * direction
	_vy += _gravity * delta
	_base_y += _vy * delta
	position.y = _base_y + sin(_time * 14.0) * _wave * minf(_time * 4.0, 1.0)
	_travelled += step
	if _spin != 0.0:
		sprite.rotation += _spin * delta * direction
	if sprite.hframes > 1:
		sprite.frame = int(_time * 12.0) % sprite.hframes
	if _travelled > max_distance or position.y > 2000.0:
		queue_free()


func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("oneway") or body.is_in_group("hazard"):
		return
	if body is Goblin:
		if not body.is_dangerous() or body in _hit:
			return
		body.hit(damage, direction)
		if _pierce:
			_hit.append(body)
			Fx.spawn(get_parent(), &"spark", global_position)
			return
	elif _pierce and _gravity == 0.0:
		return  # la magia del bastone attraversa anche lapidi e muri
	Fx.spawn(get_parent(), &"spark", global_position)
	queue_free()
