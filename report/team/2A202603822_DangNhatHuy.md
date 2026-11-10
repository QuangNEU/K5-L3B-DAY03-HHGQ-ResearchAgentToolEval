# Báo cáo cá nhân — DangNhatHuy-2A202603822

## 1. Thông tin thành viên

- Họ tên: Đặng Nhật Huy
- MSSV: 2A202603822
- Email: 26ai.huydn@vinuni.edu.vn

## 2. Phần việc phụ trách

- **CP3 — Tool mới `translate`:** thiết kế khai báo, viết code, tài liệu và unit test cho tool dịch văn bản tiếng Anh sang một hoặc nhiều ngôn ngữ.
- **CP4 — Eval nhóm:** viết 10 eval case trong `data/eval_group.json` (5 single turn + 5 multi turn).

## 3. Đóng góp cụ thể

### 3.1. Tool `translate`

**Mục tiêu:** cho agent dịch nội dung tiếng Anh đã thu thập được (bài `fetch`, tweet, abstract paper, hoặc đoạn user dán vào) sang ngôn ngữ khác. Nếu user không nói dịch sang tiếng nào thì mặc định dịch sang tiếng Việt.

**Khai báo cho model** — `starter_v0/artifacts/tools.yaml`

Description viết theo yêu cầu CP2: làm gì, khi nào dùng, khi nào không dùng.

- *Dùng khi:* user yêu cầu rõ việc dịch một đoạn tiếng Anh đã có sẵn. Nếu user muốn nhiều ngôn ngữ thì gom vào **một** lần gọi.
- *Không dùng khi:*
  - Nguồn không phải tiếng Anh.
  - User chỉ hỏi nghĩa một từ: trả lời thẳng.
  - Chưa có văn bản để dịch: gọi `clarify`.
  - Văn bản nằm ở một URL: gọi `fetch` trước.
  - Muốn đăng bản dịch: phải qua `send` và xin xác nhận.

| Tham số | Kiểu | Quy ước |
|---|---|---|
| `text` (required) | string | Nguyên văn tiếng Anh, không chèn câu lệnh của user |
| `target_languages` | array, enum 12 mã ISO 639-1 | `vi, zh, ja, ko, fr, de, es, ru, th, lo, km, id`. Có bảng đổi tên sang mã (ví dụ "Nhật" → `ja`). Bỏ trống thì dùng `["vi"]` |
| `tone` | enum `neutral / formal / casual` | Văn phong theo từ khoá của user |

Dùng `enum` cho mã ngôn ngữ để model không tự bịa mã, và để eval so khớp tham số chính xác.

**Code** — `starter_v0/tools/translate/tool.py`

- Backend là **MyMemory API** (`https://api.mymemory.translated.net/get`). Không cần API key. Biến tuỳ chọn `MYMEMORY_EMAIL` tăng hạn mức free từ khoảng 5k lên khoảng 50k ký tự/ngày.
- `normalize_targets()` xử lý tham số model truyền sai: chuyển chữ thường, bỏ trùng, bỏ `en` và mã không hỗ trợ, nhận cả chuỗi đơn. Danh sách rỗng thì dùng `["vi"]`.
- `split_chunks()` cắt văn bản theo câu thành đoạn ≤ 450 byte, vì MyMemory giới hạn khoảng 500 byte mỗi request.
- Mỗi ngôn ngữ được dịch riêng. Một ngôn ngữ lỗi thì ghi vào `errors`, các ngôn ngữ khác vẫn trả kết quả.
- MyMemory trả HTTP 200 kể cả khi hết hạn mức, nên code đọc `responseStatus` trong body để phát hiện lỗi.
- Giới hạn 5.000 ký tự mỗi lần gọi, có cờ `truncated`.
- Mọi lỗi trả về dict lỗi chuẩn qua `err()`, không raise exception.

**Đăng ký và tài liệu**

- `starter_v0/tools/__init__.py`: import `translate_text` và thêm `"translate": translate_text` vào `TOOL_FUNCTIONS`.
- `starter_v0/tools/translate/TOOL.md`: frontmatter theo contract trong `tools/README.md` (`provider: MyMemory`, `requires_env: []`, `side_effect: false`), kèm mô tả hành vi và output.
- `starter_v0/.env.example`: thêm dòng tuỳ chọn `# MYMEMORY_EMAIL=`.

**Unit test** — `starter_v0/tests/test_tools_todo.py`

8 test, đều chạy offline: HTTP được giả lập bằng fixture `fake_http`, không gọi mạng thật.

| Test | Hành vi kiểm tra |
|---|---|
| `test_translate_without_target_defaults_to_vietnamese` | Không truyền ngôn ngữ thì gửi `langpair=en\|vi` |
| `test_translate_multiple_languages_one_request_each` | Nhiều ngôn ngữ thì mỗi ngôn ngữ một request; `zh` đổi thành `zh-CN`; email được gửi qua tham số `de` |
| `test_translate_normalizes_bad_target_languages_from_model` | `["JA","ja","en","xx"]` được chuẩn hoá thành `["ja"]` |
| `test_translate_string_target_is_accepted` | Chuỗi `"ko"` được hiểu là `["ko"]` |
| `test_translate_empty_text_returns_error_without_request` | Text rỗng thì trả `ValueError`, không gọi API |
| `test_translate_long_text_is_split_into_chunks` | Văn bản khoảng 1.200 byte được cắt, mỗi đoạn ≤ 450 byte |
| `test_translate_http_error_returns_error_dict` | Lỗi HTTP 503 trả dict lỗi, giữ nguyên nhân `HTTPError` |
| `test_translate_mymemory_quota_exceeded_returns_error_dict` | HTTP 200 nhưng `responseStatus=429` vẫn được báo là lỗi |

### 3.2. Eval nhóm — `starter_v0/data/eval_group.json`

10 case, ID có hậu tố `G` để không trùng với bộ base. 7/10 case nhắm vào tool mới `translate`, vượt yêu cầu CP3 là "≥ 1 case route tới tool mới".

**Single turn**

| ID | Câu hỏi (rút gọn) | Expected | Loại lỗi |
|---|---|---|---|
| G01 | "Dịch giúp mình: The new model outperforms…" | `translate(text=nguyên văn)` | `wrong_tool` |
| G02 | "Dịch sang tiếng Nhật và tiếng Hàn: Good morning, team." | `translate(target_languages=[ja, ko])`, một lần gọi | `wrong_arg_value` |
| G03 | "Tìm 3 paper mới nộp gần đây nhất trên arXiv về LLM agents" | `papers(max_results=3, sort_by=submittedDate)` | `wrong_arg_value` |
| G04 | "Từ "outperform" nghĩa là gì?" | Không gọi tool | `unnecessary_tool` |
| G05 | "Dịch … sang tiếng Hàn, đồng thời tìm 3 paper về machine translation" | `translate(ko)` + `papers(3)` gọi song song | `wrong_tool` |

**Multi turn**

| ID | Hội thoại (rút gọn) | Expected | Loại lỗi |
|---|---|---|---|
| M01G | Dịch sang tiếng Pháp → gửi văn bản → "đúng nguyên văn" | `translate(text, [fr])` | `missing_info` |
| M02G | Dịch sang tiếng Nhật → "À nhầm, tiếng Trung" → "Vẫn câu đó" | `translate(text, [zh])` | `wrong_arg_value` |
| M03G | Dịch sang tiếng Việt → "Thêm tiếng Thái" → "cả hai một lần" | `translate(text, [vi, th])` | `wrong_arg_value` |
| M04G | Dịch sang tiếng Việt → "Đăng bản dịch lên Telegram luôn" | `clarify(response_type=yes_no)` | `wrong_boundary` |
| M05G | Tweet của Karpathy → "tin web về ông ấy tuần này" → "lấy cả hai cùng lúc" | `timeline(karpathy, 3)` + `lookup(news, week)` song song | `wrong_tool` |

**Nguyên tắc viết case** (dựa trên cách `run_eval.py` chấm điểm):

- Eval chỉ chấm lần gọi model đầu tiên. Vì vậy case dùng nhiều tool (G05, M05G) kiểm tra việc **gọi song song**, không kiểm tra chuỗi tuần tự.
- Tham số so khớp chính xác và gọi thừa tool bị tính fail, nên mỗi case chỉ kiểm tra tham số thật sự cần thiết.
  - Ví dụ G01 không kiểm tra `target_languages`: model bỏ trống tham số này là đúng theo khai báo.
  - M05G không kiểm tra `query` của `lookup`: viết "Karpathy" hay "Andrej Karpathy" đều hợp lý.
- Các case multi turn kiểm tra ba kỹ năng: ghép thông tin giữa các lượt, xử lý khi user sửa lại, và hiểu đại từ ("ông ấy").

## 4. Bằng chứng

- **File:**
  - `starter_v0/artifacts/tools.yaml` (khối `translate`)
  - `starter_v0/tools/translate/tool.py`
  - `starter_v0/tools/translate/TOOL.md`
  - `starter_v0/tools/__init__.py`
  - `starter_v0/tests/test_tools_todo.py`
  - `starter_v0/data/eval_group.json`
- **Commit:** `b6906e4` — "Thêm tool translate"
- **Kết quả kiểm tra:**
  - `pytest` (chạy trong `starter_v0/`): **75 passed, 0 failed**. 14 test còn skip là stub của tool có sẵn, được phép skip theo README.
  - `pytest tests/test_tool_contract.py` pass cho `translate`: có hàm thực thi, tham số khớp chữ ký hàm, có `TOOL.md` đúng tên.
  - Gọi API thật: `translate("The new model outperforms GPT-4 on reasoning tasks.")` trả về `"Mô hình mới vượt trội hơn GPT-4 trong các nhiệm vụ suy luận."`. Gọi với `target_languages=["ja","ko"]` trả đủ bản tiếng Nhật và tiếng Hàn.
  - 10 case được nạp và kiểm tra bằng chính `run_eval.load_cases()` và `validate_expected_tools()`: đúng `failure_type`, mọi tool expected đều được khai báo và có code.
- **AI và công cụ đã dùng:** Claude Code hỗ trợ đọc codebase, viết code tool, test, eval case và báo cáo này. Cách tự kiểm tra:
  - Đọc lại code và giải thích được từng phần.
  - Chạy `pytest` sau mỗi thay đổi.
  - Gọi API thật để xác nhận kết quả dịch.
  - Đối chiếu eval case với logic chấm trong `run_eval.py` (`case_messages`, `compare_subset`, `evaluate_phase_b`).
  - Khi đổi backend từ Azure + MyMemory sang chỉ MyMemory, một test lỗi HTTP bị fail. Đã kiểm tra lại: code chạy đúng thiết kế (gom lỗi từng ngôn ngữ thành `RuntimeError`), nên sửa test cho khớp thay vì sửa code.

## 5. Tự đánh giá

**Làm tốt**

- Tool `translate` đủ bốn phần theo yêu cầu CP3: code, `TOOL.md`, đăng ký trong `__init__.py` và `tools.yaml`, test. Số test (8) vượt mức tối thiểu 3.
- Tool chịu được tham số sai từ model và các lỗi của API, không làm agent crash.
- Eval case được viết dựa trên cách chấm thật của `run_eval.py`, nên tránh được fail oan.

**Hạn chế**

- MyMemory không hỗ trợ văn phong: tham số `tone` được nhận nhưng không áp dụng (`tone_applied: false`). Hạn mức free thấp, và mỗi ngôn ngữ cần một request riêng.
- Chưa chạy `run_eval.py --suite group` để có kết quả thật của 10 case.

**Việc tiếp theo**

- Chạy eval nhóm với `v0` và các version sau, ghi metric vào `version_log.csv`.
- Thêm quy tắc chọn tool cho `translate` vào `system_prompt.md`.
- Cân nhắc bỏ `tone` khỏi khai báo, hoặc thêm backend LLM để áp dụng được văn phong.
