class_name FrameAnim
extends Sprite2D
## Sprite2D con animazioni a fotogrammi da uno spritesheet orizzontale.
## Ogni animazione: nome -> { "frames": [indici], "fps": float, "loop": bool }

signal finished(anim_name: StringName)

var animations: Dictionary = {}
var current: StringName = &""
var _index := 0
var _time := 0.0


func play(anim_name: StringName, restart := false) -> void:
	if anim_name == current and not restart:
		return
	current = anim_name
	_index = 0
	_time = 0.0
	frame = animations[anim_name]["frames"][0]


func _process(delta: float) -> void:
	if current == &"":
		return
	var a: Dictionary = animations[current]
	var frames: Array = a["frames"]
	var loop: bool = a.get("loop", true)
	if frames.size() < 2 or (not loop and _index >= frames.size() - 1):
		return
	_time += delta
	var step := 1.0 / float(a["fps"])
	while _time >= step:
		_time -= step
		_index += 1
		if _index >= frames.size():
			_index = 0
		if not loop and _index == frames.size() - 1:
			frame = frames[_index]
			finished.emit(current)
			return
	frame = frames[_index]
