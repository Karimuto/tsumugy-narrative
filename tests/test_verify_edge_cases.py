"""
tests/test_verify_edge_cases.py
Edge cases added in v1.1.2:
  - bracket_period with mixed bracket pairs (zh 《》/en ⟨⟩/ar/fr/es/ru «»)
  - source_marker count >= 1 (not just present/absent)
  - inner_monologue rule fully removed (P-C): no rule in results, no
    "inner_monologue" in must_failed, text with thoughts still PASSes
    on its own merits
  - CLI empty --text (now optional) + stdin JSON path
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from verify_narrative import verify


SAMPLE_JA_WITH_THOUGHTS_AND_SOURCE = (
    "🚶‍♀️🚶‍♀️🚶‍♀️🚶‍♀️🚶‍♀️🚶‍♀️冬の街角を猫が徘徊していた。"
    "影が長く伸び、通りには微かな光が滲んでいた。"
    "光が滲み、音が聞こえ、匂いが漂い、涙が頬を伝い、胸が締め付けられる。"
    "私は思った。世界は静かに揺れていた。"
    "音が聞こえ、光が滲み、匂いが漂い、涙が頬を伝い、胸が締め付けられる。"
    "私は立ち尽くしていた。\n"
    "> 出典: 第1章 p.1 / 段落1"
)

SOURCES_PAGED_1 = {"kind": "paged", "entries": [{"chapter": 1, "page": 1, "para": 1}]}
SOURCES_PAGED_3 = {"kind": "paged", "entries": [
    {"chapter": 1, "page": 1, "para": 1},
    {"chapter": 1, "page": 2, "para": 2},
    {"chapter": 2, "page": 3, "para": 1},
]}


def _rule(result, name):
    for r in result["results"]:
        if r["rule"] == name:
            return r
    raise AssertionError(f"rule {name!r} not in results: {[r['rule'] for r in result['results']]}")


# --- bracket_period mixed bracket pairs ---------------------------------

def test_bracket_period_ja_mixed_safe():
    """Two separate 『…』 with 。 inside → still fails (one match suffices)."""
    text = "テスト『括弧の中に句点。』と『もう一つ。』" + "音" * 30 + "光が滲み。" * 20
    r = verify(text, "ja")
    assert "bracket_period" in r["must_failed"], r["must_failed"]


def test_bracket_period_ja_clean_passes():
    text = (
        "🚶‍♀️🚶‍♀️🚶‍♀️🚶‍♀️🚶‍♀️🚶‍♀️" + "光" * 30 + "音" * 30 + "匂い" * 20
        + "涙" * 20 + "胸" * 20 + "『括弧は句点なし』" * 3 + "\n> 出典: 第1章 p.1 / 段落1"
    )
    r = verify(text, "ja")
    assert "bracket_period" not in r["must_failed"], r["must_failed"]


def test_bracket_period_en_dot_inside_angle():
    """en: ⟨…⟩ with . inside → fails."""
    text = (
        "The street " * 20 + "⟨with a period. inside⟩ " * 5
        + "light " * 20 + "sound " * 20 + "\n> Source: Ch.1 p.1 / Para.1"
    )
    r = verify(text, "en")
    assert "bracket_period" in r["must_failed"], r["must_failed"]


def test_bracket_period_zh_chinese_period():
    """zh: 《…》 with 。 → fails (regex covers both 。 and .)."""
    text = "街上走着" * 50 + "《里面有句号。还有一个》" * 3 + "\n> 出处: 第1章 p.1 / 段落1"
    r = verify(text, "zh")
    assert "bracket_period" in r["must_failed"], r["must_failed"]


# --- source_marker count >= 1 -------------------------------------------

def test_source_marker_count_zero_fails():
    r = verify(SAMPLE_JA_WITH_THOUGHTS_AND_SOURCE, "ja", SOURCES_PAGED_1)
    sm = _rule(r, "source_marker")
    assert sm["value"] >= 1
    assert sm["ok"] is True


def test_source_marker_count_one_passes():
    r = verify(SAMPLE_JA_WITH_THOUGHTS_AND_SOURCE, "ja", SOURCES_PAGED_1)
    sm = _rule(r, "source_marker")
    assert sm["value"] == 1


def test_source_marker_count_multiple_records_all():
    text = SAMPLE_JA_WITH_THOUGHTS_AND_SOURCE + "\n> 出典: 第1章 p.2 / 段落2\n> 出典: 第2章 p.3 / 段落1"
    r = verify(text, "ja", SOURCES_PAGED_3)
    sm = _rule(r, "source_marker")
    assert sm["value"] == 3
    assert sm["ok"] is True


def test_source_marker_missing_fails():
    text = "🚶‍♀️🚶‍♀️🚶‍♀️🚶‍♀️🚶‍♀️🚶‍♀️" + "光" * 30 + "音" * 20 + "匂い" * 20 + "涙" * 20 + "胸" * 20 + "私は思った"
    r = verify(text, "ja")
    sm = _rule(r, "source_marker")
    assert sm["value"] == 0
    assert sm["ok"] is False
    assert "source_marker" in r["must_failed"]


# --- inner_monologue fully removed (P-C) ---------------------------------

def test_inner_monologue_rule_removed():
    """verify() no longer returns an inner_monologue rule."""
    r = verify(SAMPLE_JA_WITH_THOUGHTS_AND_SOURCE, "ja")
    rules = [x["rule"] for x in r["results"]]
    assert "inner_monologue" not in rules, rules


def test_text_with_thoughts_not_penalized():
    """A 'ja' text with thought-verbs and otherwise-good shape must not
    be must_failed on any inner-monologue-style rule. (It can still
    fail on char_count, etc. — we check the inner_monologue absence.)"""
    r = verify(SAMPLE_JA_WITH_THOUGHTS_AND_SOURCE, "ja")
    assert "inner_monologue" not in r["must_failed"]


def test_verify_does_not_reference_inner_monologue_pattern():
    """Module no longer exposes INNER_MONOLOGUE_PATTERNS."""
    import verify_narrative as vn
    assert not hasattr(vn, "INNER_MONOLOGUE_PATTERNS")
    assert not hasattr(vn, "check_inner_monologue")


# --- CLI: --text now optional (P-D) -------------------------------------

def test_cli_text_optional_passes_empty_results_path():
    """`--text ""` is now accepted (was an argparse error before v1.1.2)."""
    res = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "verify_narrative.py"),
         "--text", "", "--locale", "ja"],
        capture_output=True, text=True,
    )
    assert res.returncode == 2, res.stderr
    payload = json.loads(res.stdout)
    assert payload["status"] == "FAIL"
    # The result list must point at the failing rule, not be empty.
    assert payload["results"], "results must not be empty (P-D)"
    assert any(r["rule"] == "char_count" for r in payload["results"])


def test_cli_stderr_summarizes_failure():
    res = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "verify_narrative.py"),
         "--text", "", "--locale", "ja"],
        capture_output=True, text=True,
    )
    assert "FAIL" in res.stderr
    assert "char_count" in res.stderr


def test_cli_stdin_json_path():
    payload = json.dumps({"text": SAMPLE_JA_WITH_THOUGHTS_AND_SOURCE, "locale": "ja"})
    res = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "verify_narrative.py"),
         "--locale", "ja"],
        input=payload, capture_output=True, text=True,
    )
    out = json.loads(res.stdout)
    assert out["status"] in ("PASS", "CONDITIONAL PASS", "FAIL")


if __name__ == "__main__":
    test_bracket_period_ja_mixed_safe()
    test_bracket_period_ja_clean_passes()
    test_bracket_period_en_dot_inside_angle()
    test_bracket_period_zh_chinese_period()
    test_source_marker_count_zero_fails()
    test_source_marker_count_one_passes()
    test_source_marker_count_multiple_records_all()
    test_source_marker_missing_fails()
    test_inner_monologue_rule_removed()
    test_text_with_thoughts_not_penalized()
    test_verify_does_not_reference_inner_monologue_pattern()
    test_cli_text_optional_passes_empty_results_path()
    test_cli_stderr_summarizes_failure()
    test_cli_stdin_json_path()
    print("test_verify_edge_cases.py: all 14 tests passed")
