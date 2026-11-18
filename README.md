# AoE2 HD Mobile cho iPhone

Bản xuất iOS của Age of Android 1.0.0 từ Domotix, mục tiêu iPhone arm64 chạy iOS 15.1 trở lên. Bản 1.0.1 thêm giao diện tiếng Việt. Tải IPA trong phần Artifacts của lượt build thành công tại [GitHub Actions](https://github.com/tranchautien1995-hub/deche2/actions). Giải nén gói tải về và mở IPA bằng TrollStore.

1. Mở AoE2 HD Mobile một lần để ứng dụng tạo thư mục.
2. Giải nén bộ dữ liệu Age of Empires II HD của bạn và chép thư mục chứa cả `Data` và `Bin` vào **Tệp → Trên iPhone → AoE2 HD Mobile**.
3. Trong game, bấm **Chọn thư mục game**, chọn thư mục rồi bấm **Nhập dữ liệu**. Để ứng dụng mở trong lúc nhập.

Cài bản 1.0.2 đè lên bản cũ để giữ dữ liệu đã nhập và trận đã lưu. Các mô tả văn minh lấy trực tiếp từ bản game và một số thuật ngữ chuyên biệt vẫn dùng tiếng Anh.

- Chạm dân hoặc lính để nghe lời đáp tiếng Việt. Khi giao việc, đơn vị sẽ đáp theo việc được giao. Chỉnh âm lượng trong **Cài đặt > Âm thanh > Giọng dân và lính**.
- Chạm đúp dân để chọn dân ở gần, chạm đúp lính để chọn quân ở gần. Giữ khoảng một phần ba giây rồi kéo để vẽ khung chọn cả hai.

Xem [thông tin giọng tổng hợp](VOICE-CREDITS.md).

IPA chứa chương trình và giao diện của dự án cộng đồng. Dữ liệu Age of Empires II HD thuộc các chủ sở hữu tương ứng và được nhập trên thiết bị từ bản game của người dùng.

Mã nguồn Age of Android 1.0.0 do Domotix (© 2026) phát hành theo GPL‑3.0‑or‑later. Tải [mã nguồn gốc](https://domotix.co/download/3) cùng LICENSE và NOTICE. Tệp `prepare_ios.py` trong kho này thêm bản xuất iOS, nhập dữ liệu qua thư mục ứng dụng trong Tệp và vị trí xuất log trên iOS. Workflow dùng [Godot 4.7.2](https://github.com/godotengine/godot/releases/tag/4.7.2-stable) và Xcode để đóng gói. Đây là bản beta của dự án cộng đồng.
