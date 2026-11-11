# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: HHGQ
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: nvidia/nemotron-3.5-lightning:free

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Research Agent: Hỗ trợ tự động hóa việc tìm kiếm thông tin, trích xuất dữ liệu từ các URL, phân tích và tổng hợp thành kết quả nghiên cứu (digest) thông qua bộ công cụ (tools) tích hợp sẵn.

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.
Lệnh chạy: Kích hoạt môi trường (venv) và chạy streamlit run app.py tại thư mục starter_v0.
Dependency đã thêm vào requirements.txt: streamlit>=1.30.0

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: https://k5-l3b-day03-hhgq-researchagenttooleval-asgdbfdxyepihpbjlicpev.streamlit.app/

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin hoặc cần xác nhận (`response_type`: text / yes_no / choice), tạm dừng chờ lượt trả lời tiếp theo | không |
| timeline | lấy các tweet gần đây của **một tài khoản** X/Twitter (`screenname` là handle không có `@`) qua RapidAPI Twitter API45 | không |
| social_search | tìm tweet theo **từ khoá / chủ đề**, sắp xếp `Latest` hoặc `Top`, qua RapidAPI Twitter API45 | không |
| lookup | tìm kiếm web qua Tavily, có `topic` (`general` / `news`) và `timeframe` (day / week / month / year) | không |
| fetch | đọc nội dung của **một URL cụ thể** qua Firecrawl | không |
| format | trình bày các item đã thu thập thành bản tin markdown (template brief / sections / bullets / thread / daily_ai_vn), không tự lấy dữ liệu | không |
| send | đăng văn bản lên kênh Telegram; chỉ gửi khi `confirmed=true` (cần user xác nhận trước) | không (bonus có sẵn) |
| policy | tra cứu tài liệu chính sách nội bộ trong `company_policy/*.md`, trả về đoạn liên quan kèm nguồn | không (bonus có sẵn) |
| papers | tìm bài báo khoa học trên arXiv (sắp xếp theo relevance / ngày cập nhật / ngày nộp) | không (bonus có sẵn) |
| paper_text | tải PDF bài arXiv và trích nội dung text (giới hạn số trang, số ký tự) | không (bonus có sẵn) |
| translate | dịch văn bản tiếng Anh sang một hoặc nhiều ngôn ngữ (vi, zh, ja, ko, fr, de, es, ru, th, lo, km, id) trong một lần gọi; không nói ngôn ngữ thì mặc định tiếng Việt | **có** |
| summarize | tóm tắt văn bản thô bằng cách trích các câu ý chính (extractive), chạy local, không cần API | **có** |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1. `Dịch sang tiếng Nhật và tiếng Hàn: Good morning, team.` → `translate` với `target_languages=["ja","ko"]` trong một lần gọi
2. `Dịch giúp mình: The new model outperforms GPT-4 on reasoning tasks.` → `translate`, tự dịch sang tiếng Việt
3. `Tóm tắt thành 2 câu: <dán đoạn văn bản>` → `summarize` với `max_sentences=2`
4. `Dịch bài này hộ mình` (không kèm nội dung) → agent gọi `clarify` để xin văn bản

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

**Tool mới nhóm viết.** Mỗi tool có `tools/<tên>/tool.py` và `TOOL.md`, đăng ký trong `tools/__init__.py` (`TOOL_FUNCTIONS`) và `artifacts/tools.yaml`.

- **`translate`** — `starter_v0/tools/translate/`
  - **Làm gì:** dịch văn bản tiếng Anh sang một hoặc nhiều ngôn ngữ qua MyMemory API. Không cần key; biến tuỳ chọn `MYMEMORY_EMAIL` tăng hạn mức free.
  - **Tham số:**
    - `text` (bắt buộc): nguyên văn, không chèn câu lệnh của user.
    - `target_languages`: enum 12 mã ISO 639-1, mặc định `["vi"]`.
    - `tone`: `neutral` / `formal` / `casual`.
  - **Khi nào agent gọi:** user yêu cầu rõ việc dịch một đoạn tiếng Anh đã có. Nhiều ngôn ngữ thì gom vào **một** lần gọi.
  - **Khi nào không gọi:**
    - Hỏi nghĩa một từ: trả lời thẳng.
    - Chưa có văn bản: gọi `clarify`.
    - Văn bản nằm ở URL: gọi `fetch` trước.
    - Muốn đăng bản dịch: qua `send` và xin xác nhận.
  - **Chịu lỗi:**
    - Tự chuẩn hoá tham số sai: chữ hoa, trùng lặp, `en`, mã lạ, chuỗi đơn.
    - Cắt văn bản thành đoạn ≤ 450 byte theo giới hạn của MyMemory.
    - Lỗi ở một ngôn ngữ không làm hỏng các ngôn ngữ khác.
    - Phát hiện hết hạn mức qua `responseStatus`, vì MyMemory vẫn trả HTTP 200.
- **`summarize`** — `starter_v0/tools/summarize/`
  - **Làm gì:** tóm tắt extractive, chạy local, không cần API. Câu được chấm điểm theo tần suất từ, cộng thêm điểm cho câu đứng đầu và câu chứa từ khoá `focus`. Kết quả giữ đúng thứ tự câu gốc.
  - **Tham số:** `text` (bắt buộc), `max_sentences` (mặc định 3), `focus` (mặc định `general`).
  - **Khi nào agent gọi:** user yêu cầu tóm tắt một văn bản đã có, do user dán vào hoặc lấy từ lượt trước.
  - **Chịu lỗi:** text rỗng trả kết quả rỗng; `max_sentences ≤ 0` trả dict lỗi.
- Hai tool kết hợp được với tool có sẵn thành chuỗi `fetch` → `summarize` → `translate`, để đọc bài tiếng Anh rồi tóm tắt và dịch.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi chưa tối ưu trước khi sửa |  | 0.55 | runs/v0_B_base_openrouter_20261110T181628834511.json |
| v1 | system_prompt.md | system_prompt hien tai dang khien model tu quyet dinh va ao tuong | 0.55 | 0.65 | runs/v1_B_base_openrouter_20261110T192535963510.json |
| v2 | system_prompt.md + tools.yaml | Description của tool "lookup" chưa đầy đủ + system prompt thiếu chỉ dẫn lấy dữ lieu trong trường hợp multiturn | 0.65 | 0.8 | runs/v2_B_base_openrouter_20261110T224459387016.json |
| v3 | system_prompt.md + tools.yaml | Làm rõ định dạng timeline.screenname sẽ giúp model truyền đúng tên tài khoản X. Thêm ví dụ về việc giữ số lượng đã sửa khi lượt cuối chỉ nhắc lại đối tượng sẽ giúp model dùng đúng số lượng. | 0.8 | 0.8 | runs/v3_B_base_openrouter_20261111T020747209566.json |
| v4 | tools.yaml | Giải thích rõ hai kiểu tìm kiếm news và general sẽ giúp model chọn đúng topic theo nhu cầu tra cứu. | 0.8 | 0.9 | runs/v4_B_base_openrouter_20261111T023343260878.json |
| v5 | tools.yaml |  Làm rõ description của tool social_search cũng như các tools còn lại để tránh hallucination trong các lần chạy tiếp. | 0.9 | 0.95 | runs/v5_B_base_openrouter_20261111T031733401977.json |


### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R10_missing_handle (v0) | Missing info | `timeline(screenname="sama", limit=5)` | Thiếu handle nhưng đoán `sama`; thiếu `clarify`. | v1 bỏ chỉ dẫn đoán thông tin quan trọng; v1 pass với `clarify(response_type="text")`. |
| R11_missing_url (v0) | Missing info | `social_search(query="trending article", search_type="Latest", limit=1)` | Thiếu URL, đối tượng mơ hồ nhưng tự đưa ra bài viết; thiếu `clarify`. | v1 bỏ chỉ dẫn đoán URL và yêu cầu hỏi khi đối tượng vẫn mơ hồ; v1 pass với `clarify` hỏi link hoặc nội dung. |
| R12_confirm_before_send (v0) | Missing tool; extra tool | `format(template="brief", ...)` | Thiếu `clarify` xác nhận trước khi gửi. | v1 yêu cầu xác nhận trước khi gửi; v1 vẫn fail, gọi `send` để hỏi nội dung thay vì `clarify`. |
| R03_web_news_routing (v1) | Wrong arg value | `lookup(query="AI news today", topic="news", timeframe="day")` | Expected `query="AI"`. | v2 làm rõ `lookup.query`; v2 pass. |
| R13_parallel_web_and_tweets (v1) | Wrong arg value; missing tool | `lookup(query="AI news today", topic="news", timeframe="day")` | Query sai và thiếu `social_search`. | v2 làm rõ `lookup.query`; v2 pass |
| M02_carryover_timeframe (v1) | Wrong arg value | `lookup(query="robotics news today", topic="news", timeframe="day")` | Expected `query="robotics"`. | v2 làm rõ query và cách giữ, cập nhật thông tin qua các lượt; v2 pass. |
| M03_correction_handle (v1) | Wrong arg value | `timeline(screenname="AndrejKarpathy", limit=3)` | Expected `screenname="karpathy"`. | v2 thêm quy tắc ưu tiên giá trị mới nhất; v2 vẫn fail với `screenname="Andrej Karpathy"`. |
| M05_correction_limit (v1) | Wrong arg value | `timeline(screenname="elonmusk", limit=10)` | Expected `limit=3`. | v2 yêu cầu ưu tiên giá trị mới nhất; v2 vẫn fail với `limit=10`. |
| M03_correction_handle (v2) | Wrong arg value | `timeline(screenname="Andrej Karpathy", limit=3)` | Tên hiển thị thay vì handle `karpathy`. | v3 làm rõ `timeline.screenname` ưu tiên dùng handle; v3 pass |
| M05_correction_limit (v2) | Wrong arg value | `timeline(screenname="elonmusk", limit=10)` | Expected `limit=3`. | v3 thêm ví dụ cho trường hợp xử lý multiturn vào system prompt; v3 vẫn fail. v4,v5 pass. |
| R03_web_news_routing (v3) | Wrong arg value | `lookup(query="AI", timeframe="day")` | Thiếu `topic="news"`. | v4 làm rõ cách chọn `lookup.topic`; v4 pass. |
| M03_correction_handle (v4) | Missing tool; extra tool | `social_search(query="Andrej Karpathy Twitter", limit=3)` | Model hiểu sai description của 2 tool `timeline` và `social_search`. | v5 làm rõ `timeline` lấy bài đăng của người dùng cụ thể,  `social_search` dùng khi tra cứu thông tin theo từ khóa, làm rõ luôn các description của các tools còn lại để tránh haluciation; v5 pass. |

Nguồn: [version log](../../starter_v0/artifacts/version_log.csv), [run v0](../../starter_v0/runs/v0_B_base_openrouter_20261110T181628834511.json), [v1](../../starter_v0/runs/v1_B_base_openrouter_20261110T192535963510.json), [v2](../../starter_v0/runs/v2_B_base_openrouter_20261110T224459387016.json), [v3](../../starter_v0/runs/v3_B_base_openrouter_20261111T020747209566.json), [v4](../../starter_v0/runs/v4_B_base_openrouter_20261111T023343260878.json), [v5](../../starter_v0/runs/v5_B_base_openrouter_20261111T031733401977.json). Thay đổi đối chiếu theo commit `a376c0b`, `d0d4bee`, `ab8e5e5`, `07dcd61`, `37c9ed9`.

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_translate_default_vi | Dịch không nói ngôn ngữ → dịch luôn, mặc định tiếng Việt, không hỏi lại | `translate(text=nguyên văn)` | PASS |
| G02_translate_multi_language_one_call | Nhiều ngôn ngữ → một lần gọi, đổi tên sang mã ISO | `translate(target_languages=[ja, ko])` | PASS |
| G03_papers_latest_sort_and_limit | "3 paper mới nộp gần đây nhất" → đúng tool và tham số | `papers(max_results=3, sort_by=submittedDate)` | PASS |
| G04_word_meaning_no_tool | Hỏi nghĩa một từ → trả lời thẳng | không gọi tool | PASS |
| G05_parallel_translate_and_papers | Hai yêu cầu độc lập → gọi song song hai tool | `translate([ko])` + `papers(max_results=3)` | PASS |
| G06_missing_text_clarify | Yêu cầu tóm tắt nhưng không có văn bản → hỏi lại | `clarify(response_type=text)` | FAIL |
| G07_arxiv_search_sort | Paper arXiv "xếp theo ngày nộp" | `papers(query="LLM reasoning", sort_by=submittedDate)` | PASS |
| M01G_clarify_then_translate | Lượt 1 có ngôn ngữ, lượt 2 có văn bản → ghép lại | `translate(text, [fr])` | PASS |
| M02G_correction_target_language | User sửa ngôn ngữ đích ja → zh | `translate(text, [zh])` | PASS |
| M03G_add_target_language | Cộng dồn ngôn ngữ vi + th vào một lần gọi | `translate(text, [vi, th])` | FAIL |
| M04G_translate_then_send_needs_confirm | Dịch xong muốn đăng → xin xác nhận trước | `clarify(response_type=yes_no)` | FAIL |
| M05G_parallel_timeline_and_web_news | Hiểu "ông ấy" là Karpathy, gọi song song hai tool | `timeline(karpathy, 3)` + `lookup(news, week)` | FAIL |
| M06G_read_then_summarize | Đã có nội dung bài ở lượt trước → tóm tắt thành 2 câu | `summarize(max_sentences=2)` | PASS |
| M07G_clarify_then_summarize | Lượt đầu thiếu văn bản, lượt sau bổ sung → tóm tắt | `summarize` | PASS |
| M08G_confirm_before_send | User đã đồng ý ở lượt trước → được gửi | `send(confirmed=true)` | PASS |

Kết quả từ `starter_v0/runs/v0_B_base_openrouter_20261110T185844884854.json`: 11/15 pass, `case_accuracy` 0.7333, `tool_routing_accuracy` 0.8667, `argument_accuracy` 0.7333, `multiturn_accuracy` 0.625, `provider_error_cases` 0.

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Dịch giúp mình: The new model outperforms GPT-4 on reasoning tasks. | `translate(text=…, target_languages=["vi"])` | `v0+peb1c8179815b+ta62f73730eab` | Đúng: "Mô hình mới vượt trội hơn GPT-4 trong các nhiệm vụ suy luận." |
| 2 | Dịch sang tiếng Nhật và tiếng Hàn: Good morning, team. | `translate(target_languages=["ja","ko"])`, một lần gọi | như trên | Đúng: trả đủ bản tiếng Nhật và tiếng Hàn |
| 3 | Dịch bài này hộ mình | `clarify(response_type="text")` | như trên | Đúng: hỏi lại xin nội dung hoặc URL, không dịch bừa |
| 4 | Tóm tắt rồi dịch sang tiếng Việt: https://openai.com/research/ | `fetch(url=…)` | như trên | Một phần: chỉ gọi `fetch`, model tự tóm tắt và dịch trong câu trả lời, không gọi `summarize` hay `translate` |
| 5 | Tweet mới nhất của Sam Altman, dịch sang tiếng Việt | `timeline(sama, 1)` | như trên | Một phần: lấy đúng tweet nhưng tự dịch, không gọi `translate` |

Nguồn: `starter_v0/transcripts/v0_openrouter_20261110T182949813877.transcript.json` (model `nvidia/nemotron-3.5-super-vl:free`). Lượt 4 và 5 cho thấy prompt v0 ("Always finish the request in a single step") làm agent bỏ qua bước thứ hai của chuỗi tool.

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) | `tools/translate/`, `tools/summarize/`; khai báo trong `artifacts/tools.yaml`, đăng ký trong `tools/__init__.py` | `translate` gọi API thật dịch đúng sang vi/ja/ko/zh; `summarize` chạy local. Cả hai pass `tests/test_tool_contract.py` (có hàm, tham số khớp chữ ký, có `TOOL.md`) | `translate` không có side effect và chỉ dịch, muốn đăng phải qua `send` + xác nhận. Giới hạn 5.000 ký tự/lần để giữ hạn mức free. Mọi lỗi trả dict lỗi, không raise |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) | `starter_v0/tests/test_tools_todo.py`: 8 test `translate` + 3 test `summarize`. `pytest`: 83 passed, 0 failed (14 skipped là stub của tool có sẵn) | Test chạy offline: HTTP giả lập bằng `fake_http`, `conftest.py` chặn mạng thật |
| UI (lệnh chạy + link dùng thử) | https://dozens-commission-cologne-ricky.trycloudflare.com  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

- **Số test:** 11 test cho tool mới (8 `translate`, 3 `summarize`).
- **Lỗi unit test bắt được mà eval không bắt được:** khi hết hạn mức, MyMemory vẫn trả **HTTP 200** và chỉ ghi lỗi trong body (`responseStatus: 429`).
  - Nếu code chỉ kiểm tra HTTP status, tool sẽ trả câu cảnh báo "MYMEMORY WARNING…" như thể đó là bản dịch.
  - Eval không phát hiện được, vì eval chỉ chấm tool nào được gọi và tham số gì, không chấm kết quả tool trả về.
  - `test_translate_mymemory_quota_exceeded_returns_error_dict` kiểm tra đúng trường hợp này.
- **Lỗi thứ hai cùng loại:** model truyền `target_languages=["JA","ja","en","xx"]`. `test_translate_normalizes_bad_target_languages_from_model` xác nhận tool chuẩn hoá thành `["ja"]` thay vì gửi request lỗi.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

- **Chọn backend cho `translate`:**
  - Azure, Google và DeepL đều cần nhập thẻ hoặc thiếu ngôn ngữ (DeepL không có Lào, Khmer). Nhóm chọn MyMemory vì không cần key.
  - Đổi lại, MyMemory giới hạn khoảng 500 byte mỗi request, nên code cắt văn bản thành đoạn ≤ 450 byte.
  - MyMemory không hỗ trợ văn phong, nên tham số `tone` được nhận nhưng không áp dụng (output ghi `tone_applied: false`).
- **Model free bị 429:** `google/gemma-4-31b-it:free` và `gemma-4-26b-a4b-it:free` liên tục trả 429 do nhà cung cấp quá tải. Nhóm chuyển sang `nvidia/nemotron-3.5-super-vl:free` khi chat thử, và dùng `openai/gpt-4o-mini` cho run eval.
- **Viết eval case cho đúng cách chấm:** `run_eval.py` chỉ chấm lần gọi model đầu tiên, so khớp tham số chính xác, và tính fail khi gọi thừa tool.
  - Vì vậy case dùng nhiều tool phải kiểm tra **gọi song song**, không kiểm tra chuỗi tuần tự.
  - Mỗi case chỉ kiểm tra tham số cần thiết. Ví dụ G01 không kiểm tra `target_languages`, vì bỏ trống là hợp lệ.
- **Merge hai nhánh:** hai thành viên cùng sửa `tools.yaml`, `tools/__init__.py`, `tests/test_tools_todo.py` và `data/eval_group.json`, gây conflict.
  - Cách gộp: giữ khai báo, đăng ký và test của cả hai tool; gộp danh sách case.
  - Kiểm tra sau khi gộp: `pytest` vẫn 0 failed (commit `621dcd0`).

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- **Fix nào thuộc `system_prompt.md`?**
  - M04G (tự gửi Telegram) đến từ câu "just go ahead and do it".
  - Transcript lượt 4–5 (bỏ qua bước `summarize`/`translate`) đến từ câu "Always finish the request in a single step".
  - Cả hai là lỗi hành vi chung, không riêng tool nào, nên sửa ở prompt.
- **Fix nào thuộc `tools.yaml`?**
  - G06: thiếu `response_type` của `clarify`.
  - M05G: thiếu `topic=news` của `lookup`.
  - M03G: gọi `translate` lặp lại.
  - Đây là lỗi quy ước tham số và cách dùng từng tool, nên sửa ở description và tham số.
- **Failure nào cần review thủ công thay vì chấm tự động?**
  - Transcript lượt 4–5: agent không gọi `translate` nhưng vẫn trả bản dịch tiếng Việt hợp lý. Eval sẽ tính là sai tool, nhưng phải đọc mới biết chất lượng bản dịch có chấp nhận được không.
  - M03G: lần gọi đầu đã đúng, chỉ thừa lần gọi thứ hai.
  - Chất lượng bản dịch của `translate` và độ hợp lý của câu `summarize` chọn ra không được eval chấm.
- **Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?**
  - Giả thuyết: description của `summarize` ("Dùng khi người dùng yêu cầu tóm tắt…") có thể **giành route** của các case base R04 ("Tóm tắt bài này: <URL>", đúng là `fetch`) và R11 ("Tóm tắt bài viết này", đúng là `clarify`).
  - Cách thử: thêm vào `summarize` dòng "KHÔNG DÙNG KHI: chỉ có URL → `fetch` trước; chưa có văn bản → `clarify`", rồi chạy lại base eval so sánh hai case này.

## 8. Tài liệu tham khảo

-
