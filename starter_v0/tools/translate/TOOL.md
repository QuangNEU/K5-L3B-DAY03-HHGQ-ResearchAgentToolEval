---
name: translate
track: core
kind: live_api
provider: MyMemory
requires_env: []
inputs: [text, target_languages, tone]
outputs: [translations, target_languages, backend, errors]
side_effect: false
---
# translate

Translates English text into one or more languages in a single call via the
MyMemory API (https://mymemory.translated.net). If `target_languages` is empty,
it defaults to Vietnamese (`["vi"]`).

## API key

None required. Optional `MYMEMORY_EMAIL` in `.env` raises the free quota from
~5k chars/day (per IP) to ~50k chars/day (per email).

## Behaviour

- `target_languages` is normalized: lowercased, de-duplicated, `en` and unsupported codes dropped.
  Supported: `vi, zh, ja, ko, fr, de, es, ru, th, lo, km, id`.
- One GET request per language per chunk; text is split into ≤450-byte sentence chunks
  (MyMemory's per-request limit is ~500 bytes).
- Text is capped at 5,000 chars per call (`truncated: true` in the output).
- One failing language is reported in `errors` without breaking the others.
- MyMemory returns HTTP 200 even when the quota is used up; the tool reads
  `responseStatus` from the body and reports it as an error.
- `tone` is accepted and echoed, but MyMemory cannot apply it (`tone_applied: false`).
- Errors (empty text, HTTP failure, quota exceeded) return the standard error dict, never raise.

## Output

```json
{
  "tool": "translate",
  "backend": "mymemory",
  "source_language": "en",
  "target_languages": ["vi", "ja"],
  "translations": {"vi": "...", "ja": "..."}
}
```
