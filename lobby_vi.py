"""Extend the upstream translation catalog with the iOS Vietnamese UI."""

import json

from localize_vi import NAMES, TEXT, entries


LOBBY = {
    "New Game": "Đấu với máy",
    "Continue": "Chơi tiếp",
    "Load Game": "Tải trận đã lưu",
    "Options": "Cài đặt",
    "About": "Giới thiệu",
    "Quit": "Thoát",
    "Back": "Quay lại",
    "Cancel": "Hủy",
    "Civilization": "Nền văn minh",
    "Opponents": "Số người chơi máy",
    "Computer player %d": "Máy %d",
    "Your team": "Đội của bạn",
    "Game Type": "Kiểu trận đấu",
    "Starting Resources": "Tài nguyên ban đầu",
    "Victory": "Điều kiện thắng",
    "Map": "Tầm nhìn bản đồ",
    "Map Size": "Kích thước bản đồ",
    "Difficulty": "Độ khó",
    "Start Game": "Bắt đầu trận",
    "Random": "Ngẫu nhiên",
    "None": "Không đội",
    "Low": "Thấp",
    "Medium": "Trung bình",
    "High": "Cao",
    "Easy": "Dễ",
    "Hard": "Khó",
    "Tiny": "Rất nhỏ",
    "Small": "Nhỏ",
    "Normal": "Bình thường",
    "Large": "Lớn",
    "Giant": "Rất lớn",
    "Explored": "Đã khám phá",
    "All visible": "Hiện toàn bộ",
    "Random Map": "Bản đồ ngẫu nhiên",
    "Death Match": "Đấu sinh tử",
    "Standard": "Tiêu chuẩn",
    "Conquest": "Chinh phục",
    "No enemies: the game can only be won by a Wonder or the relics.":
        "Không có đối thủ. Bạn có thể thắng bằng Kỳ quan hoặc Thánh tích.",
    "The server cannot be reached.": "Không kết nối được máy chủ. Kiểm tra mạng và thử lại.",
    "Too many tries. Wait a moment.": "Bạn đã thử quá nhiều lần. Hãy chờ một lúc.",
    "The server is full.": "Máy chủ đã đầy. Hãy thử lại sau.",
    "You cannot connect to this server.": "Không thể đăng nhập vào máy chủ này.",
    "This version of the game is too old for the server. Please update.":
        "Phiên bản hiện tại đã cũ. Hãy cập nhật game.",
    "The server answered with an error (%s).": "Máy chủ trả về lỗi (%s).",
    "On My iPhone": "Trên iPhone của tôi",
    "Language": "Ngôn ngữ",
    "In Files, copy the unzipped game folder into On My iPhone > AoE2 HD Mobile. "
    "It must contain Data and Bin. Come back here to import it.":
        "Trong Tệp, chép thư mục game đã giải nén vào Trên iPhone của tôi > AoE2 HD Mobile. "
        "Thư mục cần có Data và Bin. Sau đó quay lại màn hình này để nhập.",
}


def localize(project, edit):
    originals = (line.split("|", 1) for line in TEXT.splitlines() if "|" in line)
    ui = {key.replace(r"\n", "\n"): value.replace(r"\n", "\n") for key, value in originals}
    names = entries(NAMES.splitlines())
    ui = {**names, **ui, **LOBBY}
    path = project / "scripts" / "lang_vi.gd"
    path.write_text(
        "class_name LangVi\nextends RefCounted\n\nconst UI := "
        + json.dumps(ui, ensure_ascii=False, indent="\t") + "\n", encoding="utf-8",
    )
    edit(project / "scripts" / "lang.gd", [
        ('const LANGUAGES := [', 'const LANGUAGES := [\n\t{"code": "vi", "name": "Tiếng Việt"},'),
        ('\tvar dev := OS.get_locale_language()\n\treturn dev if _known(dev) else "en"', '\treturn "vi"'),
        ('var table: Dictionary = (LangEs.UI if c == "es" else LangPt.UI)',
         'var table: Dictionary = LangVi.UI if c == "vi" else (LangEs.UI if c == "es" else LangPt.UI)'),
        ('\tif id < 0:\n\t\treturn fallback',
         '\tif code == "vi":\n\t\tfallback = t(fallback)\n\tif id < 0:\n\t\treturn fallback'),
    ])
