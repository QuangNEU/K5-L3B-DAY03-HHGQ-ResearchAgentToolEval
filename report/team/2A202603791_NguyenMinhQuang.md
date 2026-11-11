# Báo cáo cá nhân — HoVaTen-MSSV

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Nguyễn Minh Quang
- MSSV: 2A202603791
- Email: 26ai.quangnm3@vinuni.edu.vn

## 2. Phần việc phụ trách
- Nghiên cứu & Triển khai Model: Phụ trách lựa chọn mô hình AI phù hợp với bài toán, thiết lập môi trường và chạy thử nghiệm phiên bản cơ sở (chạy log v0) để đánh giá hiệu năng (baseline performance).

- Tối ưu hóa (Prompt Engineering): Phân tích kết quả từ log v0, trực tiếp tinh chỉnh và tối ưu hóa cấu trúc prompt để khắc phục các hạn chế, sau đó chạy log v1 để nghiệm thu chất lượng.

- Quản lý mã nguồn (Source Control): Thiết lập và quản lý repository cho nhóm, áp dụng tiêu chuẩn quản lý version (VD: Conventional Commits), xử lý conflict và phân quyền nhánh (branch).

- Tài liệu hóa (Documentation): Ghi chép chi tiết quá trình thử nghiệm, tổng hợp log đầu ra (output logs) và so sánh các phiên bản để làm cơ sở cho báo cáo của toàn đội.
...

## 3. Đóng góp cụ thể
- Đã lựa chọn và tích hợp thành công model nvidia/nemotron-3.5-lightning:free.

- Thiết kế lại bộ prompt ở phiên bản v1 giúp cải thiện đáng kể độ chính xác của kết quả sinh ra so với v0, giảm thiểu tình trạng [điền lỗi của v0, ví dụ: hallucination / sai định dạng JSON].

- Đảm bảo luồng làm việc trên Git của nhóm diễn ra trơn tru, repository luôn giữ trạng thái "sạch" và code được review/merge đúng quy trình.
...

## 4. Bằng chứng

- File/commit/PR: system_prompt.md, version_log.csv, openrouter_provider.py, group_report, submission, readme, run/v0, run/v1
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: kiem tra kết quả bằng cách kiểm tra metric sau mỗi lần chạy log 

## 5. Tự đánh giá
Hoàn thành tốt vai trò kỹ thuật nòng cốt trong việc cấu hình model và prompt engineering. Kỹ năng quản lý source code và tài liệu hóa bài bản, hỗ trợ tốt cho teamwork.
...
