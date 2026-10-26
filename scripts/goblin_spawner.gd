extends Node2D
## Buca dei goblin: quando il giocatore si avvicina, ne fa spuntare uno dal terreno ogni tanto
## (come gli zombi del cimitero in Ghosts'n Goblins).

@export var min_interval := 2.0
@export var max_interval := 4.0
@export var max_alive := 2
@export var activate_distance := 230.0
@export var min_distance := 40.0

const GOBLIN := preload("res://scenes/goblin.tscn")

var _timer := 1.0
var _alive: Array[Node] = []


func _physics_process(delta: float) -> void:
	var p := get_tree().get_first_node_in_group("player") as Player
	if p == null or p.state != Player.State.NORMAL:
		return
	var dx := absf(p.global_position.x - global_position.x)
	if dx > activate_distance or dx < min_distance:
		return
	_timer -= delta
	if _timer > 0.0:
		return
	_timer = randf_range(min_interval, max_interval)
	_alive = _alive.filter(func(g): return is_instance_valid(g))
	if _alive.size() >= max_alive:
		return
	var gob: Goblin = GOBLIN.instantiate()
	gob.position = position + Vector2(randf_range(-8, 8), 0)
	get_parent().add_child(gob)
	gob.emerge()
	_alive.append(gob)
