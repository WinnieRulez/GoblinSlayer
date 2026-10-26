extends Node
## Stato globale della partita (autoload "Game"): punteggio, record, vite, arma, tempo, effetti sonori.

signal score_changed(value: int)
signal lives_changed(value: int)
signal weapon_changed(weapon: String)

const START_LIVES := 3
## Tempo a disposizione per ogni vita, come in Ghosts'n Goblins (secondi)
const LEVEL_TIME := 180.0
const RECORD_FILE := "user://record.cfg"

# Livelli di collisione (vedi Impostazioni progetto > Nomi livelli > Fisica 2D)
const L_WORLD := 1
const L_PLAYER := 2
const L_ENEMY := 4
const L_PLAYER_WEAPON := 8
const L_PICKUP := 16
const L_HAZARD := 32

var score := 0:
	set(v):
		score = v
		score_changed.emit(score)
var lives := START_LIVES:
	set(v):
		lives = v
		lives_changed.emit(lives)
var hi_score := 0
## Arma in mano (chiave di Dagger.WEAPONS): resta anche dopo una morte, come nell'originale
var weapon := "dagger":
	set(v):
		weapon = v
		weapon_changed.emit(weapon)
var time_left := LEVEL_TIME
## Celle del livello con una scala a pioli (Vector2i -> true), riempite da level.gd
var ladders := {}

var _sfx := {}
var _players: Array[AudioStreamPlayer] = []


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for n in ["throw", "jump", "hit", "goblin_die", "armor_lost", "pickup", "death"]:
		_sfx[n] = load("res://assets/sfx/%s.wav" % n)
	for i in 8:
		var p := AudioStreamPlayer.new()
		p.volume_db = -6.0
		add_child(p)
		_players.append(p)
	var cfg := ConfigFile.new()
	if cfg.load(RECORD_FILE) == OK:
		hi_score = cfg.get_value("record", "punti", 0)


func new_game() -> void:
	score = 0
	lives = START_LIVES
	weapon = "dagger"


func add_score(points: int) -> void:
	score += points
	if score > hi_score:
		hi_score = score
		var cfg := ConfigFile.new()
		cfg.set_value("record", "punti", hi_score)
		cfg.save(RECORD_FILE)


func is_ladder(col: int, row: int) -> bool:
	return ladders.has(Vector2i(col, row))


func play_sfx(sfx_name: String, pitch_jitter := 0.08) -> void:
	if not _sfx.has(sfx_name):
		return
	for p in _players:
		if not p.playing:
			p.stream = _sfx[sfx_name]
			p.pitch_scale = 1.0 + randf_range(-pitch_jitter, pitch_jitter)
			p.play()
			return


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("pause"):
		get_tree().paused = not get_tree().paused
