class_name Level
extends Node2D
## Costruisce il livello da una mappa ASCII (vedi levels/level_1.gd), posiziona giocatore,
## goblin e oggetti, e gestisce tempo, morte, checkpoint e vittoria.

const TILE := 16
const LEVEL := preload("res://levels/level_1.gd")
const GOBLIN := preload("res://scenes/goblin.tscn")
const SPAWNER := preload("res://scenes/goblin_spawner.tscn")
const CHEST := preload("res://scenes/chest.tscn")
const HEART := preload("res://scenes/heart.tscn")
const WOLF := preload("res://scenes/wolf.tscn")
const GHOST := preload("res://scenes/ghost.tscn")
const WEAPON := preload("res://scenes/weapon_pickup.tscn")
## Armi per le cifre della mappa ("1" alabarda, "2" martello, ...)
const WEAPON_KEYS := ["silverhalberd", "battlehammer", "enchantedbow", "earthstaff", "machete"]
const TOMBS := 4
const TREES := 2
## Decorazioni per "t" (scelte in base alla posizione) e "x"
const DECOR_T := ["skull_pike", "mushrooms", "skull_totem", "rock", "pike", "mushroom", "skull_totem2", "candle"]
const DECOR_X := ["sword_rock", "rock", "skull_pike"]
const CAVE := preload("res://scenes/cave_exit.tscn")
const TILESET_TEX := preload("res://assets/tiles/tileset.png")

## Dove ricominciare dopo una morte (sopravvive al ricaricamento della scena)
static var checkpoint := Vector2.INF

@onready var backdrop: TileMapLayer = $Backdrop
@onready var ground: TileMapLayer = $Ground
@onready var platforms: TileMapLayer = $Platforms
@onready var hazards: TileMapLayer = $Hazards
@onready var decor_layer: Node2D = $Decor
@onready var entities: Node2D = $Entities
@onready var player: Player = $Entities/Player
@onready var hud: Hud = $Hud

var _map: Array = []
var _size := Vector2i.ZERO
var _over := false


func _ready() -> void:
	_map = LEVEL.MAP
	_size.y = _map.size()
	for line: String in _map:
		_size.x = max(_size.x, line.length())
	var ts := _build_tileset()
	for layer in [backdrop, ground, platforms, hazards]:
		layer.tile_set = ts
	platforms.add_to_group("oneway")
	hazards.add_to_group("hazard")
	_build_map()

	var cam: Camera2D = player.get_node("Camera")
	cam.limit_left = 0
	cam.limit_top = 0
	cam.limit_right = _size.x * TILE
	cam.limit_bottom = _size.y * TILE
	cam.reset_smoothing()
	player.fall_limit = _size.y * TILE + 32
	player.died.connect(_on_player_died)
	hud.bind_player(player)
	Game.time_left = Game.LEVEL_TIME


func _physics_process(delta: float) -> void:
	if _over or player.state == Player.State.DEAD or player.state == Player.State.WIN:
		return
	Game.time_left = maxf(Game.time_left - delta, 0.0)
	if Game.time_left <= 0.0:
		player.die()


func _cell(x: int, y: int) -> String:
	if y < 0 or y >= _map.size():
		return " "
	var line: String = _map[y]
	return line[x] if x >= 0 and x < line.length() else " "


func _build_map() -> void:
	var start := Vector2.ZERO
	Game.ladders.clear()
	for y in _size.y:
		for x in _size.x:
			var c := _cell(x, y)
			var cell := Vector2i(x, y)
			var pos := Vector2(x * TILE + TILE / 2.0, (y + 1) * TILE)  # centro in basso della cella
			match c:
				"#", "B":
					var above := _cell(x, y - 1)
					var top := above != "#" and above != "B"
					var v := (x * 7 + y * 13) % 3  # variante "casuale" ma sempre uguale
					if c == "#":
						ground.set_cell(cell, 0, _tile([0, 8, 0][v] if top else [1, 9, 1][v]))
					else:
						ground.set_cell(cell, 0, _tile([2, 10, 2][v] if top else [3, 11, 16][v]))
				"=":
					var l := _cell(x - 1, y) == "="
					var r := _cell(x + 1, y) == "="
					platforms.set_cell(cell, 0, _tile(4 if l and r else (12 if r else (13 if l else 4))))
				"^":
					hazards.set_cell(cell, 0, _tile(7))
				"h", "l":
					platforms.set_cell(cell, 0, _tile(19 if c == "l" else [5, 6, 5][(x * 7) % 3]))
					if c == "l":
						Game.ladders[cell] = true
					# fianco di terra della collina, dietro a tutto, fino al terreno sottostante
					var yy := y + 1
					while yy < _size.y and not "#B".contains(_cell(x, yy)):
						backdrop.set_cell(Vector2i(x, yy), 0, _tile([14, 15, 22, 23][(x * 5 + yy * 3) % 4]))
						yy += 1
				"L":
					platforms.set_cell(cell, 0, _tile(18))
					Game.ladders[cell] = true
				"T":
					_add_tomb((x * 3 + y) % TOMBS, pos)
				"Y":
					_add_decor("dead_tree_%d" % (x % TREES), pos + Vector2(0, 3))
				"G":
					var gs: Node2D = SPAWNER.instantiate()
					gs.enemy = GHOST
					gs.from_sky = true
					gs.max_alive = 1
					gs.min_interval = 4.0
					gs.max_interval = 7.0
					gs.min_distance = 0.0
					gs.activate_distance = 260.0
					gs.position = pos
					entities.add_child(gs)
				"1", "2", "3", "4", "5":
					var wp: WeaponPickup = WEAPON.instantiate()
					wp.weapon = WEAPON_KEYS[int(c) - 1]
					wp.position = pos
					entities.add_child(wp)
				"t":
					_add_decor(DECOR_T[(x * 5 + y) % DECOR_T.size()], pos)
				"x":
					_add_decor(DECOR_X[(x / 3) % DECOR_X.size()], pos)
				"w":
					var wolf: Goblin = WOLF.instantiate()
					wolf.position = pos
					entities.add_child(wolf)
				"H":
					var heart: Node2D = HEART.instantiate()
					heart.position = pos
					entities.add_child(heart)
				"P":
					start = pos
				"K":
					var k := Area2D.new()
					k.collision_layer = 0
					k.collision_mask = Game.L_PLAYER
					var sh := CollisionShape2D.new()
					var rect := RectangleShape2D.new()
					rect.size = Vector2(TILE, TILE * 8)
					sh.shape = rect
					k.add_child(sh)
					k.position = pos - Vector2(0, TILE * 4)
					k.body_entered.connect(func(_b): checkpoint = pos)
					entities.add_child(k)
				"g":
					var gob: Goblin = GOBLIN.instantiate()
					gob.position = pos
					entities.add_child(gob)
				"S":
					var sp: Node2D = SPAWNER.instantiate()
					sp.position = pos
					entities.add_child(sp)
				"C":
					var ch: Node2D = CHEST.instantiate()
					ch.position = pos
					entities.add_child(ch)
				"E":
					var cave: Area2D = CAVE.instantiate()
					cave.position = pos
					cave.body_entered.connect(_on_exit_reached)
					entities.add_child(cave)
					entities.move_child(cave, 0)
	player.position = start if checkpoint == Vector2.INF else checkpoint


## Indici delle tessere in assets/tiles/tileset.png (8 per riga), vedi tools/import_packs.py
const SOLID_TILES := [0, 1, 2, 3, 8, 9, 10, 11, 16, 17]
const PLANK_TILES := [4, 12, 13, 5, 6, 19]  # assi e cime delle colline: si attraversano dal basso
const BACK_TILES := [14, 15, 22, 23, 18]       # fianco delle colline e scale: solo grafica


func _tile(index: int) -> Vector2i:
	return Vector2i(index % 8, index / 8)


func _add_decor(decor_name: String, pos: Vector2) -> void:
	var spr := Sprite2D.new()
	spr.texture = load("res://assets/decor/%s.png" % decor_name)
	spr.centered = false
	spr.position = (pos - Vector2(spr.texture.get_width() / 2.0, spr.texture.get_height())).round()
	decor_layer.add_child(spr)


## Lapide: solida come in Ghosts'n Goblins (ferma le armi, ci si può salire sopra)
func _add_tomb(index: int, pos: Vector2) -> void:
	var tex: Texture2D = load("res://assets/decor/tomb_%d.png" % index)
	var body := StaticBody2D.new()
	body.collision_layer = Game.L_WORLD
	body.collision_mask = 0
	body.position = pos + Vector2(0, 1)
	var spr := Sprite2D.new()
	spr.texture = tex
	spr.centered = false
	spr.position = Vector2(-tex.get_width() / 2, -tex.get_height())
	body.add_child(spr)
	var sh := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(tex.get_width() - 4, tex.get_height() - 4)
	sh.shape = rect
	sh.position = Vector2(0, -rect.size.y / 2.0 - 1)
	body.add_child(sh)
	decor_layer.add_child(body)


func _build_tileset() -> TileSet:
	var ts := TileSet.new()
	ts.tile_size = Vector2i(TILE, TILE)
	# livello fisico 0: terreno solido e assi; livello fisico 1: punte (solo pericolo, non solide)
	ts.add_physics_layer()
	ts.set_physics_layer_collision_layer(0, Game.L_WORLD)
	ts.set_physics_layer_collision_mask(0, 0)
	ts.add_physics_layer()
	ts.set_physics_layer_collision_layer(1, Game.L_HAZARD)
	ts.set_physics_layer_collision_mask(1, 0)

	var src := TileSetAtlasSource.new()
	src.texture = TILESET_TEX
	src.texture_region_size = Vector2i(TILE, TILE)
	ts.add_source(src, 0)
	var h := TILE / 2.0
	var full := PackedVector2Array([Vector2(-h, -h), Vector2(h, -h), Vector2(h, h), Vector2(-h, h)])
	for i in SOLID_TILES + PLANK_TILES + BACK_TILES + [7]:
		src.create_tile(_tile(i))
	for i in SOLID_TILES:
		var td := src.get_tile_data(_tile(i), 0)
		td.add_collision_polygon(0)
		td.set_collision_polygon_points(0, 0, full)
	# assi sottili e attraversabili dal basso
	for i in PLANK_TILES:
		var plank := src.get_tile_data(_tile(i), 0)
		plank.add_collision_polygon(0)
		plank.set_collision_polygon_points(0, 0, PackedVector2Array(
				[Vector2(-h, -h), Vector2(h, -h), Vector2(h, -h + 5), Vector2(-h, -h + 5)]))
		plank.set_collision_polygon_one_way(0, 0, true)
	# punte: zona letale nella metà bassa della cella
	var spikes := src.get_tile_data(_tile(7), 0)
	spikes.add_collision_polygon(1)
	spikes.set_collision_polygon_points(1, 0, PackedVector2Array(
			[Vector2(-h, 1), Vector2(h, 1), Vector2(h, h), Vector2(-h, h)]))
	return ts


func _on_player_died() -> void:
	Game.lives -= 1
	if Game.lives > 0:
		get_tree().reload_current_scene()
	else:
		_over = true
		hud.show_message("GAME OVER", "Premi SALTO per ricominciare")


func _on_exit_reached(body: Node2D) -> void:
	if body != player or _over:
		return
	_over = true
	player.win()
	Game.add_score(1000 * (2 if player.armored else 1))
	hud.show_message("LIVELLO COMPLETATO!", "I goblin della collina sono stati sterminati.\nPremi SALTO per rigiocare")


func _unhandled_input(event: InputEvent) -> void:
	if _over and event.is_action_pressed("jump"):
		checkpoint = Vector2.INF
		Game.new_game()
		get_tree().reload_current_scene()
