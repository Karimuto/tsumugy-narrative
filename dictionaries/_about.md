# Tsumugy Dictionaries

This directory holds the per-locale sense + emotion word lists used by
`tools/verify_narrative.py` to score generated narratives.

## Files

- `schema.json` — JSON Schema (draft-07) gating 11 categories,
  100–200 items each, no duplicates.
- `ja.json`, `en.json` — Phase 1 locales (must be present).
- `zh.json`, `ko.json`, `ar.json`, `es.json`, `fr.json`, `ru.json` —
  Phase 1e locales (added in later phases; tests skip them until present).
- `NOTICE` — license attribution for `wordfreq` (MIT).

## 11 Categories (required)

- Five senses: `sight`, `sound`, `smell`, `taste`, `touch`
- Six emotions: `fear`, `joy`, `sadness`, `anger`, `surprise`, `disgust`

## Per-JSON `_about` key

Each locale file embeds a top-level `_about` object (currently
non-validating — schema does not enforce it, but editors keep it
documented):

```json
{
  "_about": {
    "version": "1.1.2",
    "locale": "ja",
    "display_name": "日本語",
    "source": "wordfreq (ja) + curated",
    "license": "MIT (see ../NOTICE)",
    "schema": "schema.json",
    "regenerated_by": "human curation + wordfreq seed",
    "notes": "Per spec, 100-200 items per category, uniqueItems."
  },
  "sight": [...],
  ...
}
```

The verifier (`tools/verify_narrative.py`) ignores `_about` when looking
up categories; it only reads the 11 known category names.

## Edit policy

- Categories are atomic strings, no multi-word phrases.
- Avoid names that double as proper nouns (people, places, brands).
- Keep cross-category uniqueness loose (e.g. "光" may appear in
  `sight` and `joy`; that's fine, schemas are per-category unique only).
- Do not delete categories to bypass the schema — fix the word list.
