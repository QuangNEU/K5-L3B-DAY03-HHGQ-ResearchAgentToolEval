# Báo cáo cá nhân — DoanAnhHung-2A202603880

## 1. Thông tin thành viên

- Họ tên: Đoàn Anh Hùng
- MSSV: 2A202603880
- Email: hungdoan772@gmail.com
- GitHub: doananhhung
- Nhánh làm việc (Branch): `doananhhung`

---

## 2. Phần việc phụ trách

- **Phụ trách Checkpoint 3 (CP3 — Tool mới & Unit Test)**: Thiết kế, cài đặt công cụ tóm tắt trích xuất [summarize](../../starter_v0/tools/summarize/tool.py), xây dựng tài liệu mô tả [TOOL.md](../../starter_v0/tools/summarize/TOOL.md) và triển khai bộ unit tests ngoại tuyến [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py).
- **Phụ trách Checkpoint 4 (CP4 — Eval nhóm 10 cases)**: Thiết kế 5 trường hợp kiểm thử (2 single-turn và 3 multi-turn) trong [eval_group.json](../../starter_v0/data/eval_group.json), kiểm tra năng lực routing của mô hình vào tool mới `summarize` và các ranh giới xử lý ngữ cảnh đa lượt.
- **Tích hợp Git & Giải quyết xung đột (Integration & Conflict Resolution)**: Nhận nhánh `huydn8816` của đồng đội Đặng Nhật Huy, xử lý hợp nhất (merge) để bảo toàn cả 2 công cụ (`summarize` và `translate`) cùng 15 trường hợp kiểm thử nhóm, xác minh test suite xanh và đẩy nhánh lên GitHub.

---

## 3. Đóng góp cụ thể

### 3.1. Xây dựng Tool mới `summarize` (CP3)
- Cài đặt thuật toán Extractive Summarization thuần Python tại [tool.py](../../starter_v0/tools/summarize/tool.py) mà không phụ thuộc vào API bên ngoài, đảm bảo khả năng chạy offline 100%.
- Thuật toán bóc tách câu bằng biểu thức chính quy (Regex Positive Lookbehind), tính điểm trọng số câu dựa trên 3 yếu tố:
  1. Tần suất xuất hiện của từ khóa (Term Frequency).
  2. Vị trí mở đầu đoạn văn (Lead Bias).
  3. Từ khóa trọng tâm được chỉ định (`focus`).
- Cài đặt rào chắn an toàn: kiểm tra hợp lệ `max_sentences > 0`, bắt mọi ngoại lệ và trả về dictionary báo lỗi `{ "error": "...", "message": "..." }` thay vì làm sập tiến trình Agent.
- Khai báo metadata chuẩn tại [TOOL.md](../../starter_v0/tools/summarize/TOOL.md), đăng ký vào `TOOL_FUNCTIONS` trong [tools/\_\_init\_\_.py](../../starter_v0/tools/__init__.py) và schema tham số trong [tools.yaml](../../starter_v0/artifacts/tools.yaml).

### 3.2. Viết Unit Tests kiểm thử Tool mới (CP3)
- Triển khai 3 bài unit test độc lập trong [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py) theo đúng tiêu chí Rubric C4:
  - `test_summarize_happy_path_extracts_key_points`: Kiểm tra trường hợp chuẩn, trích xuất chính xác số câu $\le \text{max\_sentences}$ và đầy đủ các trường cấu trúc `tool`, `summary`, `key_points`.
  - `test_summarize_bad_input_from_model_handles_empty_or_whitespace`: Kiểm tra khả năng chống chịu khi mô hình gửi chuỗi rỗng `"   "` hoặc văn bản ngắn, đảm bảo không gặp lỗi mảng hoặc sập chương trình.
  - `test_summarize_failure_invalid_max_sentences_returns_error_dict`: Kiểm tra khi tham số biên không hợp lệ (`max_sentences = 0`), tool trả về error dictionary `{ "error": "ValueError" }` mà không văng unhandled exception.

### 3.3. Xây dựng 5 Cases Kiểm Thử Nhóm (CP4)
Đóng góp 5 trường hợp kiểm thử vào [eval_group.json](../../starter_v0/data/eval_group.json):
1. `G06_missing_text_clarify` (Single-turn): Kiểm tra mô hình gọi `clarify` khi người dùng yêu cầu tóm tắt nhưng không cung cấp nội dung văn bản.
2. `G07_arxiv_search_sort` (Single-turn): Kiểm tra khả năng trích xuất tham số `sort_by="submittedDate"` khi tìm kiếm bài báo nghiên cứu khoa học trên arXiv.
3. `M06G_read_then_summarize` (Multi-turn - 3 turns): Kiểm tra khả năng đọc ngữ cảnh từ URL ở lượt trước rồi chuyển tiếp sang gọi tool mới `summarize` với `max_sentences=2`.
4. `M07G_clarify_then_summarize` (Multi-turn - 3 turns): Kiểm tra chuỗi hội thoại hỏi lại khi thiếu text và kích hoạt tool mới `summarize` khi người dùng cung cấp dữ liệu.
5. `M08G_confirm_before_send` (Multi-turn - 3 turns): Kiểm tra rào chắn xác nhận, chỉ gọi tool `send` khi người dùng đã đồng ý rõ ràng ở lượt cuối.

### 3.4. Hợp nhất mã nguồn và chạy thực nghiệm (CP4)
- Thực hiện `git merge origin/huydn8816`, giải quyết xung đột tại 3 tệp dùng chung (`tools/__init__.py`, `test_tools_todo.py`, `eval_group.json`).
- Chạy kiểm thử hợp đồng và đơn vị: toàn bộ **83 passed, 0 failed**.
- Chạy thực nghiệm đánh giá mô hình:
  ```powershell
  uv run python run_eval.py --provider openrouter --version dev --suite group --eval-cases data/eval_group.json
  ```
  Sinh ra tệp bằng chứng thực nghiệm [dev_B_group_openrouter_20261110T190823717151.json](../../starter_v0/runs/dev_B_group_openrouter_20261110T190823717151.json).

---

## 4. Bằng chứng

- **Nhánh và Commit trên Git**:
  - Nhánh: `doananhhung` (đã push lên `origin/doananhhung`).
  - Commit tính năng cá nhân: `7f15ee4` (`feat(CP3,CP4): implement summarize tool, unit tests, and 5 eval group cases`).
  - Commit hợp nhất: `621dcd0` (`merge: integrate origin/huydn8816 (translate tool & evals) with summarize tool & evals`).
- **Tệp mã nguồn và kiểm thử liên quan**:
  - Mã nguồn tool: [tool.py](../../starter_v0/tools/summarize/tool.py), [TOOL.md](../../starter_v0/tools/summarize/TOOL.md)
  - Khai báo & Đăng ký: [tools.yaml](../../starter_v0/artifacts/tools.yaml), [tools/\_\_init\_\_.py](../../starter_v0/tools/__init__.py)
  - Unit tests: [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py) (3 tests đạt PASSED)
  - Dữ liệu eval nhóm: [eval_group.json](../../starter_v0/data/eval_group.json) (15 cases hợp nhất)
  - Tệp log thực nghiệm: [dev_B_group_openrouter_20261110T190823717151.json](../../starter_v0/runs/dev_B_group_openrouter_20261110T190823717151.json)
- **Công cụ AI đã sử dụng & Phương pháp tự kiểm tra**:
  - Sử dụng trợ lý AI để hỗ trợ thiết kế thuật toán tách câu regex lookbehind, đề xuất các ca kiểm thử biên (edge cases) và cấu trúc schema JSON tương thích với harness.
  - Tự kiểm chứng bằng thực thi lệnh trực tiếp trên terminal:
    - Chạy `uv run pytest tests/test_tool_contract.py` (65/65 passed).
    - Chạy `uv run pytest tests/test_tools_todo.py -k "summarize" -v` (3/3 passed).
    - Chạy `uv run pytest` (83 passed, 0 failed trên toàn bộ dự án).
    - Chạy `run_eval.py` xác thực tính tương thích của 15 cases nhóm với mô hình OpenRouter qua API thật.

---

## 5. Tự đánh giá

- **Mức độ hoàn thành**: Đạt 100% các tiêu chí kỹ thuật được giao thuộc Checkpoint 3 và Checkpoint 4.
- **Chất lượng mã nguồn**: Thuật toán chạy ổn định, an toàn (bắt trọn lỗi, không văng exception), bộ unit test chạy ngoại tuyến với tốc độ cao (< 0.2 giây).
- **Phối hợp nhóm**: Chủ động giải quyết xung đột khi hợp nhất mã nguồn, bảo đảm toàn bộ tính năng của bản thân và đồng đội đều hoạt động đồng thời mà không làm gián đoạn tiến độ chung.
