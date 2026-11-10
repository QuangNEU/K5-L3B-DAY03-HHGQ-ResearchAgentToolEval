from __future__ import annotations

import re
from collections import Counter
from typing import Any


def summarize_text(
    text: str,
    max_sentences: int = 3,
    focus: str = "general",
) -> dict[str, Any]:
    """Extractive summarization tool that extracts key sentences from raw text."""
    try:
        # Validate arguments
        if not isinstance(max_sentences, int) or max_sentences <= 0:
            return {
                "tool": "summarize",
                "error": "ValueError",
                "message": "max_sentences must be greater than 0",
            }

        if text is None:
            text = ""

        raw_text = str(text)
        cleaned = raw_text.strip()
        if not cleaned:
            return {
                "tool": "summarize",
                "summary": "",
                "key_points": [],
                "sentence_count": 0,
                "original_length": 0,
            }

        # Split text into sentences by punctuation or newlines
        parts = re.split(r"(?<=[.!?\n])\s+", cleaned)
        sentences = [p.strip() for p in parts if p.strip()]

        if not sentences:
            return {
                "tool": "summarize",
                "summary": cleaned,
                "key_points": [cleaned],
                "sentence_count": 1,
                "original_length": len(raw_text),
            }

        if len(sentences) <= max_sentences:
            return {
                "tool": "summarize",
                "summary": " ".join(sentences),
                "key_points": sentences,
                "sentence_count": len(sentences),
                "original_length": len(raw_text),
            }

        # Calculate word frequencies for simple extractive scoring
        words = re.findall(r"\w+", cleaned.lower())
        word_freq = Counter(words)

        scored: list[tuple[float, int, str]] = []
        for index, sentence in enumerate(sentences):
            s_words = re.findall(r"\w+", sentence.lower())
            score = sum(word_freq.get(w, 0) for w in s_words) / max(len(s_words), 1)
            # Give slight boost to earlier sentences (lead bias in journalism/research)
            position_boost = 1.0 / (index + 1)
            # Give boost if focus keyword appears
            focus_boost = 2.0 if focus and focus.lower() in sentence.lower() and focus.lower() != "general" else 0.0
            total_score = score + position_boost + focus_boost
            scored.append((total_score, index, sentence))

        # Select top max_sentences and sort back by chronological position
        top_sentences = sorted(scored, key=lambda x: x[0], reverse=True)[:max_sentences]
        top_sentences.sort(key=lambda x: x[1])

        selected = [s[2] for s in top_sentences]
        return {
            "tool": "summarize",
            "summary": " ".join(selected),
            "key_points": selected,
            "sentence_count": len(selected),
            "original_length": len(raw_text),
        }
    except Exception as exc:
        return {
            "tool": "summarize",
            "error": type(exc).__name__,
            "message": str(exc),
        }
