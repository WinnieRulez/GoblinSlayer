class_name Hud
extends CanvasLayer
## Interfaccia: punteggio, vite, stato dell'armatura, messaggi a centro schermo e pausa.

@onready var score_label: Label = $Top/Score
@onready var lives_label: Label = $Top/Lives
@onready var armor_label: Label = $Top/Armor
@onready var message: Control = $Message
@onready var title_label: Label = $Message/Box/Title
@onready var sub_label: Label = $Message/Box/Sub
@onready var pause_label: Label = $Pause


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	message.visible = false
	Game.score_changed.connect(_on_score)
	Game.lives_changed.connect(_on_lives)
	_on_score(Game.score)
	_on_lives(Game.lives)


func bind_player(p: Player) -> void:
	p.armor_changed.connect(_on_armor)
	_on_armor(p.armored)


func _process(_delta: float) -> void:
	pause_label.visible = get_tree().paused


func _on_score(v: int) -> void:
	score_label.text = "PUNTI %06d" % v


func _on_lives(v: int) -> void:
	lives_label.text = "VITE %d" % v


func _on_armor(armored: bool) -> void:
	armor_label.text = "ARMATURA" if armored else "SENZA ARMATURA!"
	armor_label.modulate = Color(0.8, 0.85, 0.95) if armored else Color(1.0, 0.35, 0.3)


func show_message(title: String, sub: String) -> void:
	title_label.text = title
	sub_label.text = sub
	message.visible = true
