"""Prepare the published portable project for an iPhone export."""

import sys
from shutil import copyfile
from pathlib import Path

from lobby_vi import localize
from match_settings import apply_match_settings
from mobile_input import apply_mobile


def edit(path, replacements):
    source = path.read_text(encoding="utf-8")
    for before, after in replacements:
        if source.count(before) != 1:
            raise RuntimeError(f"Expected one match in {path}: {before!r}")
        source = source.replace(before, after, 1)
    path.write_text(source, encoding="utf-8")


def prepare(project):
    source = Path(__file__).parent
    copyfile(source / "room_code_screen.gd", project / "scripts/ui/room_code_screen.gd")
    copyfile(source / "room_code_test.gd", project / "tests/room_code_test.gd")
    (project / "tests/room_code_test.tscn").write_text(
        '[gd_scene load_steps=2 format=3]\n\n'
        '[ext_resource type="Script" path="res://tests/room_code_test.gd" id="1"]\n\n'
        '[node name="RoomCodeTest" type="Node"]\nscript = ExtResource("1")\n', encoding="utf-8",
    )

    edit(project / "project.godot", [
        ('config/name="Age of Android"', 'config/name="AoE2 HD Mobile"'),
    ])

    edit(project / "scripts" / "setup_wizard.gd", [
        (
            'if OS.has_feature("android"):\n\t\tout.append',
            'if OS.has_feature("ios"):\n'
            '\t\treturn [["On My iPhone", ProjectSettings.globalize_path("user://").simplify_path()]]\n'
            '\tif OS.has_feature("android"):\n\t\tout.append',
        ),
        (
            '\tvar b2 := _button("Import from a CD or ISO image", _iso_browse)\n\tb2.disabled = not storage_ok()\n\tcol.add_child(b2)',
            '\tif OS.has_feature("ios"):\n'
            '\t\tcol.add_child(_label("In Files, copy the unzipped game folder into On My iPhone > AoE2 HD Mobile. '
            'It must contain Data and Bin. Come back here to import it.", 28, DIM))\n'
            '\telse:\n'
            '\t\tvar b2 := _button("Import from a CD or ISO image", _iso_browse)\n'
            '\t\tb2.disabled = not storage_ok()\n\t\tcol.add_child(b2)',
        ),
        (
            '\tif _path != "/" and _path != "":',
            '\tvar local_root: String = _roots()[0][1]\n'
            '\tif _path != "/" and _path != "" and (not OS.has_feature("ios") or _path != local_root):',
        ),
        (
            'If Android closes the app,',
            'If the app closes,',
        ),
    ])

    title = project / "scripts/ui/title_menu.gd"
    edit(title, [
        ('var _mp: MpApi                       # the connection to the multiplayer lobby, made when the player first opens that page\n', ''),
        ('m.title_text = "Age of Android"', 'm.title_text = "AoE2 HD Mobile"'),
        ('"text": "Multiplayer"', '"text": "Chơi online bằng mã"'),
        ('func _multiplayer() -> MpNickScreen:\n'
         '\tif _mp == null:\n\t\t_mp = MpApi.new()\n\t\tadd_child(_mp)\n'
         '\tvar s := MpNickScreen.new()\n\ts.api = _mp\n\treturn s',
         'func _multiplayer() -> RoomCodeScreen:\n\treturn RoomCodeScreen.new()'),
    ])

    edit(project / "scripts" / "game_log.gd", [
        (
            '\tvar dir := folder if folder != "" else OS.get_system_dir(OS.SYSTEM_DIR_DOWNLOADS) + "/AoE2HDBeta/logs"',
            '\tvar downloads := OS.get_system_dir(OS.SYSTEM_DIR_DOWNLOADS)\n'
            '\tvar export_dir := "user://Log exports" if OS.has_feature("ios") else downloads.path_join("AoE2HDBeta/logs")\n'
            '\tvar dir := folder if folder != "" else export_dir',
        ),
    ])

    with (project / "export_presets.cfg").open("a", encoding="utf-8") as presets:
        presets.write("""
[preset.2]

name="iOS Portable"
platform="iOS"
runnable=true
export_filter="all_resources"
include_filter="*.json"
exclude_filter="assets/aoe/*,tests/*"
script_export_mode=2

[preset.2.options]

application/app_store_team_id="0000000000"
application/bundle_identifier="io.github.tranchautien1995.aoe2hdmobile"
application/short_version="1.0.4"
application/version="5"
application/min_ios_version="15.1"
application/targeted_device_family=0
application/export_project_only=true
application/additional_plist_content="<key>UIFileSharingEnabled</key><true/><key>LSSupportsOpeningDocumentsInPlace</key><true/>"
architectures/arm64=true
""")
    apply_mobile(project, edit)
    apply_match_settings(project, edit)
    localize(project, edit)


if __name__ == "__main__":
    prepare(Path(sys.argv[1]))
