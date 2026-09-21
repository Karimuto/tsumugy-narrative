"""
tests/test_verify_error_cases.py
Validates the 10 error-case fixtures from verify-error-cases.json.
Each case has a name, text, locale, expected_status, and expected must_failed list.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from verify_narrative import verify

FIXTURE = ROOT / "tests" / "fixtures" / "verify-error-cases.json"


def test_error_cases():
    cases = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert len(cases) == 10, f"expected 10 cases, got {len(cases)}"
    for case in cases:
        text = case["text"]
        locale = case["locale"]
        expected = case["expected_status"]
        r = verify(text, locale, case.get("sources"))
        assert r["status"] == expected, (
            f"[{case['name']}] expected {expected}, got {r['status']}"
        )
        # Check must_failed_any if present
        if "expected_must_failed_any" in case:
            assert any(mf in r["must_failed"] for mf in case["expected_must_failed_any"]), (
                f"[{case['name']}] expected one of {case['expected_must_failed_any']} in must_failed, got {r['must_failed']}"
            )
        # Check should_failed_any if present
        if "expected_should_failed_any" in case:
            assert any(sf in r["should_failed"] for sf in case["expected_should_failed_any"]), (
                f"[{case['name']}] expected one of {case['expected_should_failed_any']} in should_failed, got {r['should_failed']}"
            )


def test_error_cases_invalid_input():
    r = verify(123, "ja")
    assert r["status"] == "FAIL"
    assert "invalid_input" in r["must_failed"]


def test_error_cases_unsupported_locale():
    r = verify("test", "xx")
    assert r["status"] == "FAIL"
    assert "unsupported_locale" in r["must_failed"]


if __name__ == "__main__":
    test_error_cases()
    test_error_cases_invalid_input()
    test_error_cases_unsupported_locale()
    print("test_verify_error_cases.py: all 3 tests passed")
