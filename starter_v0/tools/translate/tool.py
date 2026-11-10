"""translate — dịch văn bản tiếng Anh sang một hoặc nhiều ngôn ngữ qua MyMemory.

MyMemory không cần API key. Quota free ~5k ký tự/ngày (tính theo IP);
đặt MYMEMORY_EMAIL trong .env để tăng lên ~50k ký tự/ngày (tính theo email).
Docs: https://mymemory.translated.net/doc/spec.php
"""
from __future__ import annotations

import os
import re
from typing import Any

import requests

from tools._shared import TIMEOUT, err

TOOL_NAME = "translate"
SOURCE_LANG = "en"
DEFAULT_TARGETS = ["vi"]
SUPPORTED = ["vi", "zh", "ja", "ko", "fr", "de", "es", "ru", "th", "lo", "km", "id"]
MAX_CHARS = 5000  # giới hạn mỗi lần gọi để không đốt hết quota free

MYMEMORY_URL = "https://api.mymemory.translated.net/get"
MYMEMORY_MAX_BYTES = 450  # MyMemory giới hạn ~500 byte/q, chừa biên an toàn
MYMEMORY_CODES = {"zh": "zh-CN"}  # MyMemory dùng mã vùng cho tiếng Trung giản thể


def normalize_targets(target_languages: Any) -> list[str]:
    """Chuẩn hoá danh sách ngôn ngữ đích: lowercase, bỏ trùng, bỏ 'en' và mã không hỗ trợ.

    Rỗng / None → mặc định tiếng Việt.
    """
    if isinstance(target_languages, str):
        target_languages = [target_languages]
    result: list[str] = []
    for code in target_languages or []:
        code = str(code).strip().lower()
        if code in SUPPORTED and code not in result:
            result.append(code)
    return result or list(DEFAULT_TARGETS)


def split_chunks(text: str, max_bytes: int = MYMEMORY_MAX_BYTES) -> list[str]:
    """Cắt văn bản theo câu sao cho mỗi đoạn ≤ max_bytes (UTF-8)."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        # Câu quá dài: cắt cứng theo từ.
        while len(sentence.encode("utf-8")) > max_bytes:
            cut = sentence[:max_bytes]
            cut = cut.rsplit(" ", 1)[0] if " " in cut else cut
            chunks.append(cut)
            sentence = sentence[len(cut):].lstrip()
        candidate = f"{current} {sentence}".strip()
        if len(candidate.encode("utf-8")) <= max_bytes:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = sentence
    if current:
        chunks.append(current)
    return chunks


def _translate_one(text: str, target: str) -> str:
    email = os.getenv("MYMEMORY_EMAIL")
    pieces: list[str] = []
    for chunk in split_chunks(text):
        params = {"q": chunk, "langpair": f"{SOURCE_LANG}|{MYMEMORY_CODES.get(target, target)}"}
        if email:
            params["de"] = email
        response = requests.get(MYMEMORY_URL, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        # MyMemory trả HTTP 200 kể cả khi hết quota → phải đọc responseStatus.
        status = int(data.get("responseStatus") or 200)
        if status != 200:
            raise RuntimeError(f"MyMemory error {status}: {data.get('responseDetails')}")
        pieces.append(data["responseData"]["translatedText"])
    return " ".join(pieces)


def translate_text(text: str = "", target_languages: list[str] | None = None, tone: str = "neutral") -> dict[str, Any]:
    try:
        text = (text or "").strip()
        if not text:
            raise ValueError("Empty text: nothing to translate")
        truncated = len(text) > MAX_CHARS
        text = text[:MAX_CHARS]
        targets = normalize_targets(target_languages)

        translations: dict[str, str] = {}
        errors: dict[str, str] = {}
        for code in targets:  # lỗi một ngôn ngữ không làm hỏng các ngôn ngữ còn lại
            try:
                translations[code] = _translate_one(text, code)
            except Exception as exc:
                errors[code] = f"{type(exc).__name__}: {exc}"
        if not translations:
            raise RuntimeError(f"All translations failed: {errors}")

        result: dict[str, Any] = {
            "tool": TOOL_NAME,
            "backend": "mymemory",
            "source_language": SOURCE_LANG,
            "target_languages": targets,
            "tone": tone,
            "tone_applied": False,  # MyMemory không hỗ trợ điều chỉnh văn phong
            "truncated": truncated,
            "translations": translations,
        }
        if errors:
            result["errors"] = errors
        return result
    except Exception as exc:
        return err(TOOL_NAME, exc)
