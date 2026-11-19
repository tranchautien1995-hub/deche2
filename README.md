# AoE2 HD Mobile cho iPhone

Bản xuất iOS của Age of Android 1.2.0 từ Domotix, dành cho iPhone arm64 chạy iOS 15.1 trở lên. Tải IPA trong phần Artifacts của lượt build thành công tại [GitHub Actions](https://github.com/tranchautien1995-hub/deche2/actions). Giải nén gói tải về và mở IPA bằng TrollStore.

1. Mở AoE2 HD Mobile một lần để ứng dụng tạo thư mục.
2. Giải nén bộ dữ liệu Age of Empires II HD của bạn và chép thư mục chứa cả `Data` và `Bin` vào **Tệp → Trên iPhone → AoE2 HD Mobile**.
3. Trong game, bấm **Chọn thư mục game**, chọn thư mục rồi bấm **Nhập dữ liệu**. Để ứng dụng mở trong lúc nhập.

Cài bản 1.0.6 đè lên bản cũ để giữ dữ liệu đã nhập và trận đã lưu. Các mô tả văn minh lấy trực tiếp từ bản game và một số thuật ngữ chuyên biệt vẫn dùng tiếng Anh.

- **Đấu với máy** mở sảnh chỉnh độ khó Dễ, Trung bình hoặc Khó, nền văn minh, tài nguyên ban đầu, kích thước và tầm nhìn bản đồ, kiểu trận và điều kiện thắng. Có thể chọn đến bốn máy và xếp đội riêng cho từng máy.
- **Chơi online bằng mã** mở phòng đấu 1v1 qua máy chủ Domotix. Cả hai cài cùng bản. Một người tạo phòng và gửi mã 8 ký tự, người còn lại nhập mã rồi bấm **Vào phòng**. Chủ phòng bấm **Bắt đầu** khi bạn đã vào. Trận online dùng bản đồ nhỏ và luật Đấu sinh tử.
- Mỗi trận mới có thể đặt giới hạn 25, 50, 75, 100, 125 hoặc 150 đơn vị mỗi bên. Mức tài nguyên Ít, Trung bình, Nhiều cấp lần lượt 250, 500 và 1.000 mỗi loại. Mặc định là Trung bình. Khi chơi online, chủ phòng chọn hai thiết lập này trước khi tạo mã.
- Dân và lính của bạn hiện bóng xanh khi đứng sau cây hoặc công trình. Chấm màu trên bản đồ nhỏ đánh dấu căn cứ ban đầu của từng AI đối địch ngay từ đầu trận.
- Chọn công trình, chạm một ô để xem vị trí và chạm lại đúng ô đó để xây. Bấm **Hủy** để thoát. Với tường, chạm các điểm để nối dài rồi chạm lại điểm cuối để xây.
- Số trên ảnh dân hoặc lính là số đơn vị cùng loại đang chờ tuyển tại nhà đã chọn. Mỗi nhà có tối đa 15 đơn vị đang chờ, trong giới hạn dân số và tài nguyên của bạn.
- Chọn nhà tuyển quân, bấm **Cắm cờ**, rồi chạm một ô trống. Đơn vị mới sẽ tới đó khi ra nhà. Cờ được lưu cùng trận.
- Ruộng dùng được hình từ dữ liệu đã nhập bằng bản cũ, kể cả ruộng đang xây hoặc đã cạn.

- Chạm dân hoặc lính để nghe lời đáp tiếng Việt. Khi giao việc, đơn vị sẽ đáp theo việc được giao. Chỉnh âm lượng trong **Cài đặt > Âm thanh > Giọng dân và lính**.
- Chạm đúp dân để chọn dân ở gần, chạm đúp lính để chọn quân ở gần. Giữ khoảng một phần ba giây rồi kéo để vẽ khung chọn cả hai.

Xem [thông tin giọng tổng hợp](VOICE-CREDITS.md).

IPA chứa chương trình và giao diện của dự án cộng đồng. Dữ liệu Age of Empires II HD thuộc các chủ sở hữu tương ứng và được nhập trên thiết bị từ bản game của người dùng.

Mã nguồn Age of Android 1.2.0 do Domotix (© 2026) phát hành theo GPL‑3.0‑or‑later. Tải [mã nguồn gốc](https://domotix.co/download/9) cùng LICENSE và NOTICE. Tệp `prepare_ios.py` trong kho này thêm bản xuất iOS, nhập dữ liệu qua thư mục ứng dụng trong Tệp và vị trí xuất log trên iOS. Workflow dùng [Godot 4.7.2](https://github.com/godotengine/godot/releases/tag/4.7.2-stable) và Xcode để đóng gói. Đây là bản beta của dự án cộng đồng.

## Android

Tải gói **AoE2HDMobile-1.0.6-VI-Android** trong GitHub Actions, giải nén và mở tệp APK trên điện thoại. Bản APK thử nghiệm dùng khóa ký của lượt build. Chép thư mục chứa **Data** và **Bin** vào máy Android, cấp quyền truy cập tệp cho game rồi nhập như trên iOS.

Bản 1.0.6 phát chuông khi quân của bạn giao chiến và chọn vị trí căn cứ trên đất liền khi đấu máy. Trận online dùng cùng cách bố trí với bản 1.0.5 để hai hệ điều hành chơi chung qua mã phòng.
