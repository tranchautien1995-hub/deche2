"""Vietnamese UI patch for the verified Age of Android 1.0.0 source."""

import json
import re


# Keys are the original GDScript string literals, including any escape sequences.
TEXT = r"""
[setup_wizard.gd]
AoE2HDBeta|AoE2 HD Mobile
On My iPhone|Thư mục của game trên iPhone
This app plays with the graphics, sounds and rules of your own copy of Age of Empires II HD. Nothing of the game is inside the app: it is imported from your game files once, on this device, and kept inside the app afterwards.|Nhập dữ liệu từ bản Age of Empires II HD của bạn để chơi. Bạn chỉ cần nhập một lần.
The import takes a while (about 5 to 50 minutes, depending on the device). You can pause it, and if it is interrupted it continues where it stopped.|Quá trình nhập mất khoảng 5 đến 50 phút tùy máy. Bạn có thể tạm dừng và tiếp tục sau.
In Files, copy the unzipped game folder into On My iPhone > AoE2 HD Mobile. It must contain Data and Bin. Come back here to import it.|Trong Tệp, giải nén dữ liệu vào Trên iPhone → AoE2 HD Mobile. Thư mục game phải có cả Data và Bin.
An earlier import was not finished.|Lần nhập trước vẫn chưa hoàn tất.
Import from the game folder|Chọn thư mục game
Import from a CD or ISO image|Nhập từ đĩa CD hoặc tệp ISO
Where is the game?|Chọn thư mục chứa dữ liệu game
Open the folder that holds the game (it contains the folders Data and Bin), a USB drive or SD card with it, or a folder one or two levels above.|Chọn thư mục chứa cả Data và Bin, rồi bấm nút Nhập dữ liệu ở góc dưới bên phải.
Game found: |Đã tìm thấy dữ liệu: 
This folder looks like the game but is missing: |Thư mục game còn thiếu: 
..  (up one folder)|..  (thư mục cấp trên)
This folder cannot be opened.|Không mở được thư mục này.
(no folders here)|(Chưa có thư mục)
Import the game from here|Nhập dữ liệu
Importing the game|Đang nhập dữ liệu
Keep the app open and the screen on. If the app closes, open it again and choose the same folder: the import continues where it stopped.|Giữ game mở và để màn hình sáng. Nếu game thoát, mở lại và chọn cùng thư mục để tiếp tục.
Pause|Tạm dừng
Stop|Dừng nhập
Continue|Tiếp tục
Back|Quay lại
   about %s left|   còn khoảng %s
Paused.|Đã tạm dừng.
Continuing an earlier import.|Đang tiếp tục lần nhập trước.
%d min|%d phút
a minute|một phút
The game is ready|Đã nhập xong
Everything was imported. You do not need the game folder any more; the app keeps its own copy.|Đã nhập toàn bộ dữ liệu cần thiết. Bạn có thể vào game ngay.
Start the game|Vào game
The import stopped|Quá trình nhập đã dừng
Check that the folder is a complete copy of the game, then try again; finished parts are not redone.|Kiểm tra thư mục game rồi thử lại. Phần đã nhập xong sẽ được giữ lại.
[hud.gd]
Economy|Kinh tế
Military|Quân sự
Defense|Phòng thủ
Dark Age|Thời Đen tối
Menu|Tùy chọn
Idle|Dân rảnh
All|Tất cả
Army|Quân đội
Clear|Bỏ chọn
Deconstruct|Tháo dỡ
Train |Tạo 
Trade|Giao dịch
buy and sell|Mua và bán
Unlock|Mở khóa
Lock|Khóa
shut to everybody|Chặn mọi đơn vị
open for your units|Quân ta có thể đi qua
Unload|Ra khỏi nhà
%d inside|%d đơn vị bên trong
Repair|Sửa chữa
%d%% health|%d%% máu
%d s|%d giây
Turn|Xoay
Cancel|Hủy
Place|Đặt
Paused|Tạm dừng
Resume|Tiếp tục
Save game|Lưu trận
Settings|Cài đặt
Debug|Công cụ kiểm thử
Debug logs|Nhật ký lỗi
New game|Trận mới
Start a new game?\nUnsaved progress is lost.|Bắt đầu trận mới?\nTiến độ chưa lưu sẽ mất.
Yes, choose a civilization|Chọn nền văn minh
Always log (also while a computer is attached with USB debugging)|Luôn ghi nhật ký
Off|Tắt
On|Bật
Delete all|Xóa tất cả
Delete every log?|Xóa tất cả nhật ký?
Yes, delete all|Xóa tất cả
Back|Quay lại
Log|Nhật ký
Save to Downloads|Xuất tệp
Share|Chia sẻ
Write a mail|Viết email
Delete|Xóa
Logging this session to |Đang ghi nhật ký vào 
Not logging this session|Phiên này chưa ghi nhật ký
No logs yet. Logs are written while the tablet is not attached to a computer.|Chưa có nhật ký.
%s   %d min   %d KB|%s   %d phút   %d KB
   %d errors|   %d lỗi
PROBLEM: |LỖI: 
Open|Mở
Saved to %s|Đã lưu vào %s
Could not write to Downloads: allow all files access for the app in the Android settings|Không xuất được tệp nhật ký
The log text is on the clipboard: paste it into a mail or a message|Đã sao chép nhật ký. Bạn có thể dán vào email hoặc tin nhắn.
Difficulty|Độ khó
Opponent (applies to the next new game)|Đối thủ (áp dụng từ trận sau)
Interface size|Cỡ giao diện
Small|Nhỏ
Normal|Vừa
Large|Lớn
Snarky comments|Lời thoại vui
Tombstones|Bia mộ
Sound|Âm thanh
Game data (imported from your copy of the game)|Dữ liệu game đã nhập
Delete it and import again|Xóa và nhập lại
Delete the imported game data?\nSaved games stay. You will be asked for the game folder again.|Xóa dữ liệu đã nhập?\nTrận đã lưu vẫn được giữ. Bạn sẽ cần chọn lại thư mục dữ liệu.
Yes, delete it|Xóa dữ liệu
Choose your civilization|Chọn nền văn minh
Start game|Vào trận
+500 of every\nresource|+500 mỗi loại\ntài nguyên
+500 of every resource|Đã thêm 500 mỗi loại tài nguyên
Raid now|Tấn công ngay
Next age\n(instant)|Lên đời ngay
Already in the Imperial Age|Đã ở thời Đế quốc
Spawn wild\nanimals here|Tạo thú hoang\nở đây
Wild animals appeared nearby|Thú hoang vừa xuất hiện gần đây
Game speed|Tốc độ trận
Close|Đóng
Market|Chợ
You have %d gold. Trading fee %d%%; prices move with every trade.|Bạn có %d vàng. Phí giao dịch %d%%. Giá thay đổi sau mỗi lần mua bán.
Sell 100\nget %d gold|Bán 100\nnhận %d vàng
Buy 100\npay %d gold|Mua 100\ntrả %d vàng
Attacks paused: raids and wild animals leave you alone|Đã tạm dừng các đợt tấn công và thú hoang
Attacks resumed|Đã bật lại các đợt tấn công
Load game\n%s|Tải trận\n%s
Load game\nno save yet|Tải trận\nChưa có bản lưu
Load autosave\n%s|Tải bản tự lưu\n%s
Load autosave\nnone yet|Tải bản tự lưu\nChưa có bản lưu
Attacks: PAUSED\n(tap to resume)|Tấn công: TẠM DỪNG\n(chạm để bật)
Attacks: ON\n(tap to pause)|Tấn công: BẬT\n(chạm để dừng)
Game saved|Đã lưu trận
Could not save the game|Không lưu được trận
No saved game found|Chưa có trận đã lưu
Are you sure?|Bạn có chắc không?
Yes|Đồng ý
No|Hủy
Deconstruct the %s?|Tháo dỡ %s?
\nYou get back %s.|\nBạn nhận lại %s.
\nNothing is refunded.|\nThao tác này không hoàn tài nguyên.
Yes, deconstruct|Tháo dỡ
Defeat|Thất bại
Your last Town Center has fallen.|Nhà chính cuối cùng của bạn đã thất thủ.
Load autosave|Tải bản tự lưu
Victory!|Chiến thắng!
The rival's base lies in ruins.|Căn cứ đối phương đã bị phá hủy.
Keep playing|Chơi tiếp
You won after %d:%02d, against %d attack waves.|Bạn thắng sau %d:%02d và vượt qua %d đợt tấn công.
You lasted %d:%02d and survived %d %s.|Bạn trụ được %d:%02d và vượt qua %d %s.
attacks|đợt tấn công
raids|đợt đột kích
attackers|quân địch
raiders|quân đột kích
You are under attack!|Bạn đang bị tấn công!
Attacks paused|Đã tạm dừng tấn công
Rival: %s|Đối thủ: %s
Raid %d in %d:%02d|Đợt đột kích %d sau %d:%02d
Fishing ship, %s.\nTap a school of fish to fish it, or open water to sail.|Thuyền đánh cá, %s.\nChạm đàn cá để đánh bắt hoặc chạm mặt nước để di chuyển.
Tap an enemy to attack, or the ground to move.|Chạm vào quân địch để tấn công, hoặc chạm mặt đất để di chuyển.
Monk, %s.\nHeals the wounded by himself. Tap an enemy to convert it, a relic to carry it, then your Monastery.|Tu sĩ, %s.\nTự chữa thương cho đồng đội. Chạm vào quân địch để cải đạo hoặc chọn thánh tích rồi đưa về tu viện.
%d units|%d đơn vị
%d villagers, %d soldiers.\nTap the ground to move, a resource or building site to work, an enemy to attack.|%d dân, %d lính.\nChạm đất để di chuyển, chạm tài nguyên hoặc công trình để làm việc, chạm quân địch để tấn công.
%d %s left.\nSelect a villager, then tap it to gather.|Còn %d %s.\nChọn dân rồi chạm vào tài nguyên để khai thác.
Under construction %d%%|Đang xây %d%%
Researching %s %d%%|Đang nghiên cứu %s %d%%
Training %s %d%%|Đang tạo %s %d%%
  (+%d queued)|  (+%d đang chờ)
Your village|Làng của bạn
Tap a villager, then a tree, bush, mine or the ground.\nDrag to scroll, pinch to zoom. Double-tap and draw a loop round units to select them. Build a Barracks and Towers before the raids.|Chọn dân, rồi chạm vào cây, bụi quả hoặc mỏ để khai thác.\nChạm đúp một đơn vị để chọn nhóm ở gần. Giữ rồi kéo để khoanh vùng chọn. Kéo nhanh để di chuyển bản đồ, chụm hai ngón để thu phóng.
%d villagers, %d soldiers, %d buildings.|%d dân, %d lính, %d công trình.
\nGarrison %d / %d|\nĐồn trú %d / %d
, +%d arrows|, +%d mũi tên
. Select soldiers, then tap it to garrison.|. Chọn lính rồi chạm công trình để đồn trú.
Send villagers to build it.|Cử dân đến xây công trình này.
Your units walk through it, enemies must break it down. %s|Quân ta có thể đi qua, quân địch phải phá cổng. %s
Locked: shut for everybody.|Đã khóa, mọi đơn vị đều bị chặn.
Lock it to keep your own units in.|Có thể khóa cổng để giữ quân trong thành.
%d food left.|Còn %d lương thực.
Trains fishing ships and warships; fishing ships bring their catch here. Research shipbuilding here.|Đóng thuyền cá và tàu chiến, nhận cá đánh bắt và nghiên cứu nâng cấp tàu.
Trains soldiers. Research upgrades here.|Tạo quân và nghiên cứu nâng cấp.
Attack and armor upgrades for your soldiers.|Nâng sức tấn công và giáp cho quân.
Tower and wall upgrades.|Nâng cấp tháp và tường.
Houses %d villagers.|Tăng %d giới hạn dân số.
%s. Houses %d. Research ages and economy technologies here.|%s. Tăng %d giới hạn dân số. Lên đời và nghiên cứu công nghệ kinh tế tại đây.
\nRelics inside: %d, +%.1f gold per second.|\nThánh tích: %d, +%.1f vàng mỗi giây.
Trains monks, who heal and convert. Research faith and healing here. A monk can bring a relic: it pays gold while it stays.|Tạo tu sĩ để chữa thương, cải đạo và mang thánh tích về tạo vàng.
Rams, mangonels and other siege. Research upgrades here.|Chế tạo và nâng cấp xe phá thành, máy bắn đá và các khí giới công thành khác.
Trade resources for gold and research commerce.|Đổi tài nguyên lấy vàng và nghiên cứu thương mại.
%d arrow%s per volley, range %d.|%d mũi tên%s mỗi loạt, tầm bắn %d.
Drop-off for %s. Research better tools here.|Nơi nộp %s. Có thể nghiên cứu nâng cấp công cụ tại đây.
[defs.gd]
Easy|Dễ
Medium|Vừa
Hard|Khó
Rival base|Căn cứ đối thủ
Raids only|Chỉ đột kích
Needs %s|Cần %s
Needs a Mill|Cần cối xay
Not available yet|Chưa mở khóa
Needs 2 %s buildings|Cần 2 công trình thuộc %s
more buildings|thêm công trình
[rules.gd]
Dark Age|Thời Đen tối
Feudal Age|Thời Phong kiến
Castle Age|Thời Lâu đài
Imperial Age|Thời Đế quốc
[main.gd]
Draw a loop round the units|Vẽ một vòng quanh nhóm quân để chọn
[controller.gd]
No idle villagers|Không có dân rảnh
You have no villagers|Bạn chưa có dân
You have no soldiers: build a Barracks|Bạn chưa có lính. Hãy xây trại lính.
No units there|Không có đơn vị ở đó
%d unit%s selected|Đã chọn %d đơn vị%s
A relic. Send a monk to carry it to your Monastery: it pays gold for as long as it stays there.|Thánh tích. Cử tu sĩ mang về tu viện để tạo vàng.
A monk goes for the relic|Tu sĩ đang đến lấy thánh tích
Select soldiers to attack|Chọn lính để tấn công
%s: %d of %d hit points. Select soldiers to attack it.|%s: %d / %d máu. Chọn lính để tấn công.
Repairing %s|Đang sửa %s
The relic goes to the Monastery|Đang mang thánh tích về tu viện
%s is full|%s đã đầy
%d to the %s (%d / %d)|Đã đưa %d đơn vị vào %s (%d / %d)
Gate %s|Cổng %s
%d units out of the %s|%d đơn vị đã ra khỏi %s
Not enough resources (%s)|Thiếu tài nguyên (%s)
Can't build there|Không thể xây ở đó
You need a villager to build|Cần dân để xây
Place Gate (%s). It turns to lie along a wall; your units pass, enemies do not. %s|Đặt cổng (%s). Cổng tự xoay theo tường cho quân ta đi qua. %s
Use Turn to rotate it.|Bấm Xoay để đổi hướng.
Blocked here, tap another spot.|Vị trí bị chặn. Chạm chỗ khác.
Place %s (%s). %s|Đặt %s (%s). %s
Tap the map to move it.|Chạm bản đồ để dời vị trí.
Stone Wall: tap where the wall should start.|Tường đá: chạm vào điểm bắt đầu.
Stone Wall: tap the next point. Walls run straight or diagonal; tap again to turn.|Tường đá: chạm điểm tiếp theo để vẽ tường thẳng hoặc chéo.
Stone Wall: %d pieces, %d stone. Tap to add a turn, tap the last point to undo. Place to build.|Tường đá: %d đoạn, %d đá. Chạm để thêm góc, chạm điểm cuối để hoàn tác. Bấm Đặt để xây.
Tap where the wall starts and where it turns first|Chạm vào điểm bắt đầu và điểm đổi hướng của tường
Not enough stone (%d each)|Thiếu đá (%d mỗi đoạn)
Only enough stone for %d pieces|Chỉ đủ đá cho %d đoạn
No villager to send|Không có dân để cử đi
A villager is on the way to repair the %s|Dân đang đến sửa %s
Researching %s|Đang nghiên cứu %s
[game_map.gd]
A new %s was found somewhere on the map|Đã phát hiện %s mới trên bản đồ
gold mine|mỏ vàng
stone mine|mỏ đá
berry bush|bụi quả
The rival's Town Center has fallen!|Nhà chính của đối thủ đã thất thủ!
Gold is the money|Vàng dùng làm tiền giao dịch
You need 100 %s to sell|Cần 100 %s để bán
You need %d gold|Cần %d vàng
Not finished yet|Công trình chưa hoàn thành
%s is busy researching|%s đang bận nghiên cứu
Already researched|Đã nghiên cứu xong
Already being researched|Đang được nghiên cứu
Not enough resources (%s)|Thiếu tài nguyên (%s)
%s reached! New buildings and technologies are open.|Đã lên %s! Công trình và công nghệ mới đã mở khóa.
%s researched|Đã nghiên cứu %s
Your %s was destroyed!|%s của bạn đã bị phá hủy!
%s deconstructed: +%s|Đã tháo dỡ %s: +%s
Queue is full|Hàng chờ đã đầy
%s cannot be trained here yet|Chưa thể tạo %s tại đây
Population limit reached: build Houses|Đã đạt giới hạn dân số. Hãy xây thêm nhà.
[director.gd]
Raid! %d enemy soldiers are coming from the %s.|Đột kích! %d quân địch đang tiến đến từ hướng %s.
Enemy warships are sailing in from the lake!|Tàu chiến địch đang đi vào từ hồ!
[rival.gd]
The rival has reached the %s.|Đối thủ đã lên %s.
The rival has no army yet.|Đối thủ chưa có quân.
Raid! The rival's army of %d is marching on you.|Đột kích! %d quân địch đang tiến về phía bạn.
[res_node.gd]
Berry bush|Bụi quả
Gold mine|Mỏ vàng
Stone mine|Mỏ đá
[villager.gd]
walking to work|đang đến chỗ làm
gathering|đang khai thác
building|đang xây
repairing|đang sửa chữa
carrying %d %s|đang mang %d %s
No drop-off for %s: build a Town Center%s|Thiếu chỗ nộp %s. Hãy xây nhà chính%s.
 or Mining Camp| hoặc trại khai mỏ
[ship.gd]
carrying %d food to the dock|đang mang %d lương thực về bến
fishing|đang đánh cá
[soldier.gd]
carrying a relic: tap your Monastery|đang mang thánh tích, hãy chạm tu viện
converting %s %d%%|đang cải đạo %s %d%%
a unit|một đơn vị
recharging his faith (%d s)|đang hồi đức tin (%d giây)
A monk takes the relic: tap your Monastery to have it pay gold|Tu sĩ đã lấy thánh tích. Chạm tu viện để mang về tạo vàng.
Relic in the Monastery: +%.1f gold per second|Đã cất thánh tích: +%.1f vàng mỗi giây
Converted: %s|Đã cải đạo: %s
[importer/importer.gd]
Reading the game rules|Đang đọc luật chơi
Terrain, trees, villagers and soldiers|Địa hình, cây cối, dân và lính
Units and buildings|Đơn vị và công trình
Terrain blending|Ghép lớp địa hình
Sounds and music|Hiệu ứng âm thanh và nhạc
Files are missing in |Các tệp còn thiếu trong 
The rules file (empires2_x1_p1.dat) could not be unpacked|Không giải nén được tệp luật chơi (empires2_x1_p1.dat)
The rules file has an unknown layout|Định dạng tệp luật chơi chưa được hỗ trợ
No sounds could be read|Không đọc được dữ liệu âm thanh
"""


NAMES = """
food|lương thực
wood|gỗ
stone|đá
gold|vàng
health|máu
idle|đang rảnh
walking|đang đi
fishing|đang đánh cá
moving|đang di chuyển
attacking|đang tấn công
working|đang làm việc
farming|đang làm ruộng
hunting|đang săn
Master volume|Âm lượng tổng
Music|Nhạc nền
Fighting|Chiến đấu
Work and building|Lao động và xây dựng
Alerts and events|Cảnh báo và sự kiện
Town Center|Nhà chính
Feudal Town Center|Nhà chính Phong kiến
Castle Town Center|Nhà chính Lâu đài
Imperial Town Center|Nhà chính Đế quốc
House|Nhà dân
Lumber Camp|Trại gỗ
Mining Camp|Trại khai mỏ
Mill|Cối xay
Farm|Ruộng
Barracks|Trại lính bộ
Archery Range|Trại cung
Stable|Trại ngựa
Blacksmith|Lò rèn
University|Đại học
Siege Workshop|Xưởng công thành
Monastery|Tu viện
Market|Chợ
Castle|Lâu đài
Dock|Bến tàu
Watch Tower|Tháp canh
Guard Tower|Tháp phòng thủ
Keep|Tháp kiên cố
Stone Wall|Tường đá
Palisade Wall|Hàng rào gỗ
Fortified Wall|Tường thành kiên cố
Gate|Cổng thành
Relic|Thánh tích
Villager|Dân làng
Militia|Dân binh
Man-at-Arms|Kiếm binh
Long Swordsman|Lính trường kiếm
Two-Handed Swordsman|Lính kiếm hai tay
Champion|Kiếm binh tinh nhuệ
Spearman|Lính giáo
Pikeman|Lính trường thương
Halberdier|Lính kích
Archer|Cung thủ
Crossbowman|Lính nỏ
Arbalest|Lính nỏ tinh nhuệ
Skirmisher|Lính ném lao
Elite Skirmisher|Lính ném lao tinh nhuệ
Cavalry Archer|Kỵ cung
Heavy Cavalry Archer|Kỵ cung hạng nặng
Scout Cavalry|Kỵ binh trinh sát
Light Cavalry|Kỵ binh nhẹ
Hussar|Khinh kỵ tinh nhuệ
Knight|Kỵ sĩ
Cavalier|Kỵ sĩ hạng nặng
Paladin|Kỵ sĩ tinh nhuệ
Camel Rider|Kỵ binh lạc đà
Heavy Camel Rider|Kỵ binh lạc đà hạng nặng
Monk|Tu sĩ
Missionary|Nhà truyền giáo
Battering Ram|Xe phá thành
Capped Ram|Xe phá thành bọc giáp
Siege Ram|Xe công thành hạng nặng
Mangonel|Máy bắn đá
Onager|Máy bắn đá hạng nặng
Siege Onager|Máy bắn đá công thành
Scorpion|Nỏ xe
Heavy Scorpion|Nỏ xe hạng nặng
Trebuchet|Máy bắn đá đối trọng
Bombard Cannon|Pháo công thành
Hand Cannoneer|Lính hỏa mai
Fishing Ship|Thuyền cá
Transport Ship|Tàu vận tải
Trade Cog|Tàu buôn
Trade Cart|Xe buôn
Galley|Chiến thuyền nhẹ
War Galley|Chiến thuyền
Galleon|Chiến thuyền hạng nặng
Fire Ship|Tàu phun lửa
Fast Fire Ship|Tàu phun lửa nhanh
Demolition Ship|Tàu cảm tử
Cannon Galleon|Tàu pháo
Wolf|Sói
Wild Boar|Lợn rừng
Deer|Hươu
Britons|Anh
Franks|Frank
Goths|Goth
Teutons|Teuton
Japanese|Nhật Bản
Chinese|Trung Hoa
Byzantines|Byzantine
Persians|Ba Tư
Saracens|Saracen
Turks|Thổ Nhĩ Kỳ
Vikings|Viking
Mongols|Mông Cổ
Celts|Celt
Spanish|Tây Ban Nha
Aztecs|Aztec
Mayans|Maya
Huns|Hung Nô
Koreans|Triều Tiên
Dark Age|Thời Đen tối
Feudal Age|Thời Phong kiến
Castle Age|Thời Lâu đài
Imperial Age|Thời Đế quốc
Loom|Khung cửi
Wheelbarrow|Xe cút kít
Hand Cart|Xe kéo tay
Fletching|Đuôi tên
Bodkin Arrow|Mũi tên xuyên giáp
Bracer|Bao tay cung thủ
Forging|Rèn vũ khí
Iron Casting|Đúc sắt
Blast Furnace|Lò cao
Horse Collar|Ách ngựa
Heavy Plow|Cày nặng
Crop Rotation|Luân canh
Double-Bit Axe|Rìu hai lưỡi
Bow Saw|Cưa cung
Two-Man Saw|Cưa hai người
Gold Mining|Khai thác vàng
Gold Shaft Mining|Đào sâu mỏ vàng
Stone Mining|Khai thác đá
Stone Shaft Mining|Đào sâu mỏ đá
Ballistics|Đạn đạo
Chemistry|Hóa học
Masonry|Xây đá
Architecture|Kiến trúc
Conscription|Tòng quân
Spies|Do thám
Cartography|Bản đồ học
Coinage|Đúc tiền
Banking|Ngân hàng
Guilds|Phường hội
"""


# These expressions pass through internal names that must remain stable in game data.
DISPLAY_CALLS = {
    "hud.gd": [
        ("String(u.name)", "ViNames.label(u.name)"),
        ("String(d.name)", "ViNames.label(d.name)"),
        ("String(t.name)", "ViNames.label(t.name)"),
        ("String(c.name)", "ViNames.label(c.name)"),
        ("String(Sfx.LABELS[key])", "ViNames.label(Sfx.LABELS[key])"),
        ('String(u.def.get("name", u.kind))', 'ViNames.label(u.def.get("name", u.kind))'),
        ("b.title()", "ViNames.label(b.title())"),
        ("_cap(u.status_text())", "_cap(ViNames.label(u.status_text()))"),
        ("% u.status_text()", "% ViNames.label(u.status_text())"),
        ("[r.amount, r.kind]", "[r.amount, ViNames.label(r.kind)]"),
        ("[Rules.techs[b.res_tech].name,", "[ViNames.label(Rules.techs[b.res_tech].name),"),
        ("[u.name, int(prog", "[ViNames.label(u.name), int(prog"),
        ('" and ".join(b.def.drop)', '" và ".join(b.def.drop.map(ViNames.label))'),
        ('"s" if b.tower_shots() > 1 else ""', '""'),
        ('if "raid!" in t or', 'if "đột kích!" in t or "bị phá hủy" in t or "bị tấn công" in t or "raid!" in t or'),
        ('if "not enough" in t or', 'if "thiếu " in t or "chưa " in t or "cần " in t or "not enough" in t or'),
        ('if "ready" in t or', 'if "đã lưu" in t or "đã tháo dỡ" in t or "phát hiện" in t or "ready" in t or'),
    ],
    "defs.gd": [
        ('return String(Rules.raw.civ_info[c - 1].name)', 'return ViNames.label(Rules.raw.civ_info[c - 1].name)'),
        ('[cost[r], r]', '[cost[r], ViNames.label(r)]'),
        ('Rules.techs[r].name', 'ViNames.label(Rules.techs[r].name)'),
    ],
    "rules.gd": [('[cost[r], RES_NAMES[r]]', '[cost[r], ViNames.label(RES_NAMES[r])]')],
    "controller.gd": [
        ('"" if picked.size() == 1 else "s"', '""'),
        ('[b.title(),', '[ViNames.label(b.title()),'),
        ('[sent.size(), b.title(),', '[sent.size(), ViNames.label(b.title()),'),
        ('% b.title()', '% ViNames.label(b.title())'),
        ('[n, sel_b.title()]', '[n, ViNames.label(sel_b.title())]'),
        ('"locked" if sel_b.locked else "unlocked"', '"đã khóa" if sel_b.locked else "đã mở khóa"'),
        ('[d.name, Defs.cost_text(d.cost)', '[ViNames.label(d.name), Defs.cost_text(d.cost)'),
        ('% Rules.techs[id].name', '% ViNames.label(Rules.techs[id].name)'),
    ],
    "game_map.gd": [
        ('% b.def.name', '% ViNames.label(b.def.name)'),
        ('var nm: String = Rules.techs[id].name', 'var nm := ViNames.label(Rules.techs[id].name)'),
        ('var name := b.title()', 'var name := ViNames.label(b.title())'),
    ],
    "villager.gd": [('[carry_n, carry_kind]', '[carry_n, ViNames.label(carry_kind)]')],
}


def entries(lines):
    return dict(line.split("|", 1) for line in lines if line)


def localize(project):
    scripts = project / "scripts"
    catalog = {}
    for line in TEXT.splitlines():
        if line.startswith("[") and line.endswith("]"):
            messages = catalog.setdefault(line[1:-1], {})
        elif line:
            original, translated = line.split("|", 1)
            if original in messages:
                raise ValueError(f"Duplicate Vietnamese translation: {original}")
            messages[original] = translated

    names = entries(NAMES.splitlines())
    encoded = json.dumps({k.casefold(): v for k, v in names.items()}, ensure_ascii=False, indent="\t")
    (scripts / "vi_names.gd").write_text(
        "class_name ViNames\nextends RefCounted\n\nconst NAMES := " + encoded + "\n\n\n"
        "static func label(value: Variant) -> String:\n"
        "\tvar original := str(value)\n"
        "\treturn NAMES.get(original.strip_edges().to_lower(), original)\n",
        encoding="utf-8",
    )

    literal = re.compile(r'"((?:\\.|[^"\\\r\n])*)"')
    total = 0
    for name, strings in catalog.items():
        path = scripts / name
        original = path.read_text(encoding="utf-8")
        for before, after in DISPLAY_CALLS.get(name, []):
            original = original.replace(before, after)
        used = set()

        def translate(match):
            key = match.group(1)
            if key not in strings:
                return match.group(0)
            used.add(key)
            return '"' + strings[key].replace('"', '\\"') + '"'

        localized = literal.sub(translate, original)
        path.write_text(localized, encoding="utf-8")
        total += len(used)
        if name in {"setup_wizard.gd", "hud.gd"} and len(used) < 20:
            raise RuntimeError(f"Vietnamese UI patch did not match {name}")
    print(f"Localized {total} UI strings and {len(names)} display names")
