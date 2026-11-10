"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    pytest.skip(TODO)


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    pytest.skip(TODO)


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    pytest.skip(TODO)


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    pytest.skip(TODO)


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    pytest.skip(TODO)


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    pytest.skip(TODO)


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    pytest.skip(TODO)


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    pytest.skip(TODO)


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    pytest.skip(TODO)


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    pytest.skip(TODO)


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    pytest.skip(TODO)


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    pytest.skip(TODO)


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    pytest.skip(TODO)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    pytest.skip(TODO)


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

# ---------------- translate (team tool) ----------------

translate_tool = TOOL_FUNCTIONS["translate"]


@pytest.fixture
def no_translate_keys(monkeypatch) -> None:
    # conftest.clean_env does not know our new env vars, so clear them here.
    monkeypatch.delenv("MYMEMORY_EMAIL", raising=False)


def mymemory_ok(text: str) -> FakeResponse:
    return FakeResponse({"responseData": {"translatedText": text}, "responseStatus": 200})


def test_translate_without_target_defaults_to_vietnamese(no_translate_keys, fake_http) -> None:
    calls = fake_http(mymemory_ok("Xin chào thế giới"))

    result = translate_tool(text="Hello world")

    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.mymemory.translated.net/get"
    assert calls[0]["params"] == {"q": "Hello world", "langpair": "en|vi"}
    assert result["backend"] == "mymemory"
    assert result["target_languages"] == ["vi"]
    assert result["translations"] == {"vi": "Xin chào thế giới"}


def test_translate_multiple_languages_one_request_each(monkeypatch, no_translate_keys, fake_http) -> None:
    monkeypatch.setenv("MYMEMORY_EMAIL", "team@example.com")
    calls = fake_http(mymemory_ok("ok"))

    result = translate_tool(text="Hello", target_languages=["vi", "zh"])

    assert [c["params"]["langpair"] for c in calls] == ["en|vi", "en|zh-CN"]  # zh mapped to zh-CN
    assert all(c["params"]["de"] == "team@example.com" for c in calls)
    assert set(result["translations"]) == {"vi", "zh"}  # keys stay ISO codes


def test_translate_normalizes_bad_target_languages_from_model(no_translate_keys, fake_http) -> None:
    calls = fake_http(mymemory_ok("ok"))

    # Model sends duplicates, wrong case, the source language and an unknown code.
    result = translate_tool(text="Hi", target_languages=["JA", "ja", "en", "xx"])

    assert result["target_languages"] == ["ja"]
    assert [c["params"]["langpair"] for c in calls] == ["en|ja"]


def test_translate_string_target_is_accepted(no_translate_keys, fake_http) -> None:
    fake_http(mymemory_ok("ok"))
    result = translate_tool(text="Hi", target_languages="ko")
    assert result["target_languages"] == ["ko"]


def test_translate_empty_text_returns_error_without_request(no_translate_keys, fake_http) -> None:
    calls = fake_http(mymemory_ok("unused"))

    result = translate_tool(text="   ", target_languages=["vi"])

    assert result["error"] == "ValueError"
    assert calls == []


def test_translate_long_text_is_split_into_chunks(no_translate_keys, fake_http) -> None:
    calls = fake_http(mymemory_ok("x"))
    sentence = "This is a fairly long English sentence used for chunking. "
    text = sentence * 20  # ~1,200 bytes > 450-byte MyMemory limit

    result = translate_tool(text=text)

    assert len(calls) >= 3
    assert all(len(c["params"]["q"].encode("utf-8")) <= 450 for c in calls)
    assert "error" not in result


def test_translate_http_error_returns_error_dict(no_translate_keys, fake_http) -> None:
    fake_http(FakeResponse(status_code=503))

    result = translate_tool(text="Hello", target_languages=["vi"])

    assert result["tool"] == "translate"
    assert result["error"] == "RuntimeError"  # every language failed
    assert "HTTPError" in result["message"]  # per-language cause is kept


def test_translate_mymemory_quota_exceeded_returns_error_dict(no_translate_keys, fake_http) -> None:
    # MyMemory answers HTTP 200 but puts the real status in the body.
    fake_http(FakeResponse({"responseData": {"translatedText": ""}, "responseStatus": 429,
                            "responseDetails": "MYMEMORY WARNING: YOU USED ALL AVAILABLE FREE TRANSLATIONS"}))

    result = translate_tool(text="Hello", target_languages=["vi", "ja"])

    assert result["error"] == "RuntimeError"
    assert "429" in result["message"]
