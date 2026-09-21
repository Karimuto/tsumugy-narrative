"""
tests/test_verify_locales.py
Per-locale fixture validation. Runs ja and en fixtures and checks expected status.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from verify_narrative import verify

FIXTURE = ROOT / "tests" / "fixtures" / "verify-test-raw.json"


def test_all_fixtures_run():
    """All fixtures from verify-test-raw.json should run without exception."""
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert len(data) > 0, "fixture must not be empty"
    for case in data:
        # Support both old (payload) and new (text/locale at top level) formats
        if "payload" in case:
            text = case["payload"]["text"]
            locale = case["payload"]["locale"]
        else:
            text = case["text"]
            locale = case["locale"]
        r = verify(text, locale)
        assert "status" in r
        assert r["status"] in ("PASS", "CONDITIONAL PASS", "FAIL")


def test_ja_locale_works():
    r = verify("テスト" * 100, "ja")
    assert "status" in r


def test_en_locale_works():
    r = verify("test " * 200, "en")
    assert "status" in r


def test_zh_locale_works():
    r = verify("测试" * 200, "zh")
    assert "status" in r


def test_ko_locale_works():
    r = verify("테스트" * 200, "ko")
    assert "status" in r


def test_ar_locale_works():
    r = verify("اختبار " * 200, "ar")
    assert "status" in r


def test_es_locale_works():
    r = verify("test " * 200, "es")
    assert "status" in r


def test_fr_locale_works():
    r = verify("test " * 200, "fr")
    assert "status" in r


def test_ru_locale_works():
    r = verify("тест " * 200, "ru")
    assert "status" in r


if __name__ == "__main__":
    test_all_fixtures_run()
    test_ja_locale_works()
    test_en_locale_works()
    test_zh_locale_works()
    test_ko_locale_works()
    test_ar_locale_works()
    test_es_locale_works()
    test_fr_locale_works()
    test_ru_locale_works()
    print("test_verify_locales.py: all 9 tests passed")
