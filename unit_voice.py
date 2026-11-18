"""Render short original Vietnamese responses into offline game audio."""

import json
import sys
import wave
from array import array
from pathlib import Path


LINES = {
    "select": ["Tôi đây.", "Bạn cần tôi làm gì?", "Vâng, tôi nghe."],
    "soldier_select": ["Có mặt!", "Chờ lệnh!", "Quân đã sẵn sàng!"],
    "move": ["Tôi đi ngay.", "Được, tôi tới đây."],
    "soldier_move": ["Tiến lên!", "Tuân lệnh!"],
    "wood": ["Tôi đi đốn gỗ.", "Để tôi chặt cây."],
    "food": ["Tôi đi hái quả.", "Tôi sẽ kiếm lương thực."],
    "gold": ["Tôi đi đào vàng.", "Đến mỏ vàng thôi."],
    "stone": ["Tôi đi khai thác đá.", "Tôi sẽ lấy đá."],
    "farm": ["Tôi đi làm ruộng.", "Để tôi lo ruộng này."],
    "fish": ["Tôi đi đánh cá.", "Chuẩn bị thả lưới."],
    "hunt": ["Tôi đi săn.", "Tôi sẽ săn con đó."],
    "build": ["Tôi xây ngay.", "Để tôi dựng công trình."],
    "repair": ["Tôi đi sửa ngay.", "Để tôi sửa lại."],
    "attack": ["Xông lên!", "Tấn công!", "Đánh vào mục tiêu!"],
    "relic": ["Tôi đi lấy thánh tích.", "Để tôi mang thánh tích về."],
    "deliver": ["Tôi mang về tu viện."],
    "garrison": ["Vào trong ngay.", "Tôi vào đồn trú."],
}


def render(project, model):
    from piper import PiperVoice, SynthesisConfig

    voice = PiperVoice.load(str(model))
    config = SynthesisConfig(length_scale=0.92, volume=0.85)
    assets = project / "assets" / "voice_vi"
    assets.mkdir(parents=True, exist_ok=True)
    rendered = 0
    for category, lines in LINES.items():
        for index, line in enumerate(lines):
            path = assets / f"{category}_{index}.wav"
            with wave.open(str(path), "wb") as audio:
                voice.synthesize_wav(line, audio, syn_config=config)
            with wave.open(str(path), "rb") as audio:
                assert audio.getnchannels() == 1 and audio.getsampwidth() == 2
                assert 0.2 < audio.getnframes() / audio.getframerate() < 5.0
                samples = array("h", audio.readframes(audio.getnframes()))
                assert max(samples) - min(samples) > 1000, f"Silent line: {category}/{index}"
            rendered += 1
    print(f"Verified {rendered} Vietnamese WAV clips")


def write_lines(project):
    data = json.dumps(LINES, ensure_ascii=False, indent="\t")
    path = project / "scripts" / "unit_speech.gd"
    path.write_text("class_name UnitSpeech\nextends RefCounted\n\nconst LINES := " + data + "\n", encoding="utf-8")


if __name__ == "__main__":
    game = Path(sys.argv[1])
    write_lines(game)
    render(game, Path(sys.argv[2]))
