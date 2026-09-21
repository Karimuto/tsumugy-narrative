"""
tests/test_dict_schema.py
Validates all locale dictionaries against dictionaries/schema.json.

CI gate: 100 <= category_size <= 200, no duplicates, all 11 categories present.
"""
import json
import os
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("[SKIP] jsonschema not installed, using manual validation")
    jsonschema = None

DICT_DIR = Path(__file__).resolve().parent.parent / "dictionaries"
SCHEMA_PATH = DICT_DIR / "schema.json"
REQUIRED_CATEGORIES = [
    "sight", "sound", "smell", "taste", "touch",
    "fear", "joy", "sadness", "anger", "surprise", "disgust"
]

# Phases 1 only deliver ja/en; the gate is for those two first
PHASE1_LOCALES = ["ja", "en"]


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def validate_manual(d: dict, locale: str) -> list:
    """Manual validation when jsonschema is unavailable."""
    errors = []
    for cat in REQUIRED_CATEGORIES:
        if cat not in d:
            errors.append(f"[{locale}] missing category: {cat}")
            continue
        items = d[cat]
        if not isinstance(items, list):
            errors.append(f"[{locale}] {cat} is not a list")
            continue
        n = len(items)
        if n < 100 or n > 200:
            errors.append(f"[{locale}] {cat} has {n} items (must be 100-200)")
        if len(set(items)) != n:
            dupes = [x for x in set(items) if items.count(x) > 1]
            errors.append(f"[{locale}] {cat} has duplicates: {dupes[:3]}")
        if not all(isinstance(x, str) for x in items):
            errors.append(f"[{locale}] {cat} contains non-string")
    return errors


def test_ja_en_phase1():
    """Phase 1 gate: ja and en dictionaries must satisfy schema."""
    all_errors = []
    for locale in PHASE1_LOCALES:
        path = DICT_DIR / f"{locale}.json"
        assert path.exists(), f"Missing {path}"
        d = load_json(path)
        if jsonschema is not None:
            schema = load_json(SCHEMA_PATH)
            try:
                jsonschema.validate(d, schema)
                print(f"[OK] {locale}.json: schema-valid")
            except jsonschema.ValidationError as e:
                all_errors.append(f"[{locale}] schema invalid: {e.message}")
        else:
            errs = validate_manual(d, locale)
            if errs:
                all_errors.extend(errs)
            else:
                print(f"[OK] {locale}.json: manual-valid (all 11 cats, 100-200, no dupes)")
    if all_errors:
        for e in all_errors:
            print(f"[FAIL] {e}")
    assert not all_errors, f"Dictionary validation failed: {len(all_errors)} errors"


def test_remaining_locales_can_be_added_later():
    """Phase 1e (later): remaining 6 locales are not yet required."""
    remaining = ["zh", "ko", "ar", "es", "fr", "ru"]
    for locale in remaining:
        path = DICT_DIR / f"{locale}.json"
        if path.exists():
            print(f"[INFO] {locale}.json already exists")
        else:
            print(f"[SKIP] {locale}.json not yet created (Phase 1e)")


def test_notice_file_exists():
    """wordfreq NOTICE must exist (license compliance)."""
    notice = DICT_DIR / "NOTICE"
    assert notice.exists(), f"Missing {notice}"
    content = notice.read_text(encoding="utf-8")
    assert "MIT" in content, "NOTICE must reference MIT license"
    assert "wordfreq" in content, "NOTICE must reference wordfreq"
    print("[OK] NOTICE file references wordfreq + MIT")


if __name__ == "__main__":
    print("=== Dictionary Schema Validation ===")
    test_ja_en_phase1()
    test_remaining_locales_can_be_added_later()
    test_notice_file_exists()
    print("=== All tests passed ===")
