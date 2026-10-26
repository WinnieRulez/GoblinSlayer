class_name Hud
extends CanvasLayer
## Interfaccia alla Ghosts'n Goblins: punteggio, record, tempo, arma in mano, vite, armatura,
## messaggi a centro schermo e pausa.

@onready var score_label: Label = $Top/Player/Score
@onready var record_label: Label = $Top/Record/Score
@onready var time_label: Label = $Top/Player/Time
@onready var lives_label: Label = $Bottom/Lives
@onready var armor_label: Label = $Top/Armor
@onready var weapon_icon: TextureRect = $Bottom/WeaponFrame/Icon
@onready var weapon_label: Label = $Bottom/WeaponName
@onready var message: Control = $Message
@onready var title_label: Label = $Message/Box/Title
@onready var sub_label: Label = $Message/Box/Sub
@onready var pause_label: Label = $Pause


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	message.visible = false
	Game.score_changed.connect(_on_score)
	Game.lives_changed.connect(_on_lives)
	Game.weapon_changed.connect(_on_weapon)
	_on_score(Game.score)
	_on_lives(Game.lives)
	_on_weapon(Game.weapon)


func bind_player(p: Player) -> void:
	p.armor_changed.connect(_on_armor)
	_on_armor(p.armored)


func _process(_delta: float) -> void:
	pause_label.visible = get_tree().paused
	var t := ceili(Game.time_left)
	time_label.text = "TEMPO %d:%02d" % [t / 60, t % 60]
	# negli ultimi 30 secondi il tempo lampeggia
	time_label.modulate = Color(1, 0.35, 0.3) if t <= 30 and int(Game.time_left * 4.0) % 2 == 0 else Color.WHITE


func _on_score(v: int) -> void:
	score_label.text = "%06d" % v
	record_label.text = "%06d" % max(v, Game.hi_score)


func _on_lives(v: int) -> void:
	lives_label.text = "VITE %d" % v


func _on_weapon(w: String) -> void:
	weapon_icon.texture = load(Dagger.WEAPONS[w]["icon"])
	weapon_label.text = Dagger.WEAPONS[w]["name"]


func _on_armor(armored: bool) -> void:
	armor_label.text = "ARMATURA" if armored else "SENZA ARMATURA!"
	armor_label.modulate = Color(0.8, 0.85, 0.95) if armored else Color(1.0, 0.35, 0.3)


func show_message(title: String, sub: String) -> void:
	title_label.text = title
	sub_label.text = sub
	message.visible = true
