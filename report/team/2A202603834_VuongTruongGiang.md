# Báo cáo cá nhân — Vương Trường Giang — 2A202603834

## 1. Thông tin thành viên

- Họ tên: Vương Trường Giang
- MSSV: 2A202603834
- Email: 26ai.giangvt@vinuni.edu.vn

## 2. Phần việc phụ trách

- Đọc run JSON, phân tích lỗi chọn tool và truyền tham số, đặc biệt với hội thoại nhiều lượt.
- Điều chỉnh `system_prompt.md` và `tools.yaml`, chạy eval và ghi lại bằng chứng cho các version v2–v5.

## 3. Đóng góp cụ thể

- **v2:** Làm rõ `lookup.query` chỉ chứa chủ đề, tách loại tin và thời gian sang tham số riêng; thêm quy tắc dùng giá trị mới nhất và giữ các ràng buộc còn hiệu lực trong hội thoại. Accuracy từ 0.65 lên 0.80; R03, R13, M02 pass, còn M03 và M05 fail.
- **v3:** Làm rõ định dạng `timeline.screenname`; thêm ví dụ giữ số lượng đã sửa qua nhiều lượt. Accuracy giữ ở 0.80; M03 pass nhưng M05 vẫn fail.
- **v4:** Giải thích cách chọn `lookup.topic` giữa `news` và `general` sau khi R03 v3 bỏ sót topic. Accuracy từ 0.80 lên 0.90; R03 pass. M05 cũng pass nhưng thay đổi v4 không trực tiếp nhắm vào số lượng.
- **v5:** Phân biệt `timeline` lấy bài từ tài khoản cụ thể với `social_search` tìm theo từ khóa; làm rõ thêm mô tả các tool khác. Accuracy từ 0.90 lên 0.95; M03 pass sau khi v4 gọi nhầm `social_search`.
- Viết mục **B2 — Failure Analysis** trong [báo cáo nhóm](group_report.md), đối chiếu lỗi, thay đổi và kết quả chạy lại theo từng version.

## 4. Bằng chứng

- Thay đổi kỹ thuật: commit `d0d4bee` (v2), `ab8e5e5` (v3), `07dcd61` (v4), `37c9ed9` (v5); commit `eb3b598` lưu run và version log.
- Artifact hiện tại: [system_prompt.md](../../starter_v0/artifacts/system_prompt.md), [tools.yaml](../../starter_v0/artifacts/tools.yaml), [version_log.csv](../../starter_v0/artifacts/version_log.csv).
- Kết quả: [run v1](../../starter_v0/runs/v1_B_base_openrouter_20261110T192535963510.json), [v2](../../starter_v0/runs/v2_B_base_openrouter_20261110T224459387016.json), [v3](../../starter_v0/runs/v3_B_base_openrouter_20261111T020747209566.json), [v4](../../starter_v0/runs/v4_B_base_openrouter_20261111T023343260878.json), [v5](../../starter_v0/runs/v5_B_base_openrouter_20261111T031733401977.json).
- Công cụ và cách kiểm tra: dùng kết quả eval lưu trong run JSON, đối chiếu `actual_tool_calls` và `failures` với `expect`, so sánh kết quả trước/sau và kiểm tra diff các commit. Thông tin về AI hỗ trợ viết hoặc phân tích cần thành viên bổ sung nếu có.

## 5. Tự đánh giá

- Thực hiện được nhiều thay đổi và chạy v2-v5 góp phần hoàn thiện CP01
- Cần đánh giá một giả thuyết trong nhiều lần chạy hơn, vì model có thể haluciation nên chạy 1 lần đúng vẫn chưa khẳng định những thay đổi là đúng và đủ.