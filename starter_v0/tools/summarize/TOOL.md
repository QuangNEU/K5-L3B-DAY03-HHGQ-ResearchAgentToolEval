---
name: summarize
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [text, max_sentences, focus]
outputs: [tool, summary, key_points, sentence_count, original_length]
side_effect: false
---
# summarize

Trích xuất các câu ý chính từ một đoạn văn bản thô theo phương pháp extractive summarization.
Dùng khi người dùng yêu cầu tóm tắt hoặc rút gọn một bài viết, báo cáo hoặc đoạn văn bản dài mà không cần gọi API bên ngoài.
