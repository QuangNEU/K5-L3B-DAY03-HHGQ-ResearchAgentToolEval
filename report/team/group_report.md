# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3:

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

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
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

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

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
