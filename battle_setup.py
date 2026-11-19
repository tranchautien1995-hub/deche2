"""Prepare combat notifications and safe starting positions for mobile."""

import math
import struct
import wave


def write_bell(path):
    """Synthesize a short two-strike alert for imports without the interface sound."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rate = 24_000
    partials = ((1.0, 1.0, 4.7), (1.49, .36, 6.4), (2.02, .28, 7.1), (2.64, .24, 11.0), (3.87, .16, 15.0))
    samples = bytearray()
    for i in range(round(rate * 1.55)):
        now = i / rate
        sound = 0.0
        for onset, pitch, volume in ((0.0, 435.0, .76), (.33, 521.0, .66)):
            t = now - onset
            if t >= 0.0:
                attack = min(1.0, t / .012)
                sound += volume * attack * sum(
                    strength * math.exp(-falloff * t) * math.sin(math.tau * pitch * ratio * t)
                    for ratio, strength, falloff in partials
                )
        samples.extend(struct.pack("<h", round(12500 * sound * min(1.0, (1.55 - now) / .15))))
    with wave.open(str(path), "wb") as target:
        target.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        target.writeframes(samples)


def apply_battle_setup(project, edit):
    scripts = project / "scripts"
    write_bell(project / "assets/mobile/battle_bell.wav")

    edit(scripts / "main.gd", [
        ('\telif not loading:\n\t\t_new_game(centre)',
         '\telif not loading:\n\t\tcentre = map.pick_starting_base()\n\t\tmap.player_base = centre\n\t\t_new_game(centre)'),
        ('\tSfx.cam = cam', '\tSfx.cam = cam\n\tSfx.reset_battle_alert()\n\tmap.battle_alert.connect(Sfx.play_battle_alert)'),
    ])
    edit(scripts / "game_map.gd", [
        ('signal building_finished(b: Building)', 'signal building_finished(b: Building)\nsignal battle_alert'),
        ('func _new_grid(n: int) -> AStarGrid2D:', '''\
## The starting base follows the map seed, including when the player restarts the same match.
func pick_starting_base() -> Vector2i:
	const MARGIN := 12
	var centre := Vector2i(size / 2, size / 2)
	if size <= MARGIN * 2:
		return centre
	var starting_rng := RandomNumberGenerator.new()
	starting_rng.seed = world_seed ^ 0x5EED21
	for attempt in 256:
		var at := Vector2i(starting_rng.randi_range(MARGIN, size - MARGIN - 1), starting_rng.randi_range(MARGIN, size - MARGIN - 1))
		if _starting_land(at) and not find_path(Vector2(centre), at).is_empty():
			return at
	return centre  # The terrain generator always reserves dry ground here.


func _starting_land(at: Vector2i) -> bool:
	for dy in range(-6, 7):
		for dx in range(-6, 7):
			var cell := at + Vector2i(dx, dy)
			var t := terrain_at(cell)
			if t in [TerrainBlend.WATER, TerrainBlend.SHALLOWS, TerrainBlend.BEACH] or is_occupied(cell):
				return false
	return true


func _new_grid(n: int) -> AStarGrid2D:'''),
        ('## Called when something of ours takes a hit from an enemy; the interface pings the minimap.', '''\
## Ring only for hostile player combat. Wildlife and allied splash retain their ordinary sounds.
func report_engagement(target_team: int, attacker: Object) -> void:
	if not is_instance_valid(attacker):
		return
	var source_team: Variant = attacker.get("team")
	if source_team is int and (target_team == 0 or source_team == 0) and hostile(target_team, source_team):
		battle_alert.emit()


## Called when something of ours takes a hit from an enemy; the interface pings the minimap.'''),
    ])
    for file in ("mob.gd", "building.gd", "foe_building.gd"):
        edit(scripts / file, [
            ('func take_damage(amount: float, attacker: Object = null) -> void:\n\tif not alive:\n\t\treturn',
             'func take_damage(amount: float, attacker: Object = null) -> void:\n\tif not alive:\n\t\treturn\n'
             '\tif amount > 0.0:\n\t\tmap.report_engagement(team, attacker)'),
        ])
    edit(scripts / "net/mp_match.gd", [
        ('target.take_damage(dmg, by)\n\t\tmap.report_attack(target.tp)',
         'target.take_damage(dmg, by)\n\t\tif not is_instance_valid(by):\n\t\t\tmap.battle_alert.emit()\n\t\tmap.report_attack(target.tp)'),
    ])
    edit(scripts / "sfx.gd", [
        ('var _music: AudioStreamPlayer', 'var _battle_player: AudioStreamPlayer\nvar _last_battle_ms := -8000\nvar _music: AudioStreamPlayer'),
        ('\t_music = AudioStreamPlayer.new()',
         '\t_battle_player = AudioStreamPlayer.new()\n\t_battle_player.bus = "Alerts"\n\tadd_child(_battle_player)\n'
         '\t_music = AudioStreamPlayer.new()'),
        ('func reload_data() -> void:\n\t_streams.clear()',
         'func reload_data() -> void:\n\t_streams.clear()\n'
         '\t_battle_player.stream = GameData.audio("snd/attack_warning_general.wav")\n'
         '\tvar fallback := "res://assets/mobile/battle_bell.wav"\n'
         '\tif _battle_player.stream == null and ResourceLoader.exists(fallback):\n'
         '\t\t_battle_player.stream = load(fallback) as AudioStream'),
        ('# ------------------------------------------------------------------ effects', '''\
func reset_battle_alert() -> void:
	_last_battle_ms = -8000
	_battle_player.stop()


func play_battle_alert() -> void:
	var now := Time.get_ticks_msec()
	if now - _last_battle_ms >= 8000:
		_last_battle_ms = now
		_battle_player.play()


# ------------------------------------------------------------------ effects'''),
    ])
    edit(scripts / "importer/sound_extract.gd", [
        ('\tstep.call("Sound effects")\n\tvar n := 0', '''\
	step.call("Sound effects")
	var n := 0
	var original := game.path_join("resources/_common/drs/interface/attack_warning_general.wav")
	if FileAccess.file_exists(original):
		if DirAccess.copy_absolute(original, out.path_join("snd/attack_warning_general.wav")) == OK:
			n += 1'''),
    ])
    edit(scripts / "save_game.gd", [
        ('\t\td["player_base"] = [map.player_base.x, map.player_base.y]\n', ''),
        ('\tif map.rival:\n\t\td["rivals"]',
         '\td["player_base"] = [map.player_base.x, map.player_base.y]\n\tif map.rival:\n\t\td["rivals"]'),
    ])
