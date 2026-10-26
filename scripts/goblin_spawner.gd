extends Node2D
## Buca dei goblin: quando il giocatore si avvicina, ne fa spuntare uno dal terreno ogni tanto
## (come gli zombi del cimitero in Ghosts'n Goblins). Con "from_sky" fa invece comparire
## spettri in volo davanti al giocatore.

@export var min_interval := 2.0
@export var max_interval := 4.0
@export var max_alive := 2
@export var activate_distance := 230.0
@export var min_distance := 40.0
@export var enemy: PackedScene = preload("res://scenes/goblin.tscn")
@export var from_sky := false

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
	var gob: Goblin = enemy.instantiate()
	if from_sky:
		var side := 1.0 if p.facing > 0 else -1.0
		gob.position = Vector2(p.global_position.x + side * randf_range(110, 150),
				p.global_position.y - randf_range(50, 70))
	else:
		gob.position = position + Vector2(randf_range(-8, 8), 0)
	get_parent().add_child(gob)
	gob.emerge()
	_alive.append(gob)
