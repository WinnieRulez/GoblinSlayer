extends Node
## Stato globale della partita (autoload "Game"): punteggio, vite, effetti sonori.

signal score_changed(value: int)
signal lives_changed(value: int)

const START_LIVES := 3

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


func new_game() -> void:
	score = 0
	lives = START_LIVES


func add_score(points: int) -> void:
	score += points
	hi_score = max(hi_score, score)


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
