"""
tests/test_verify_must.py
Verifies that the must-severity rules correctly FAIL the given inputs.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from verify_narrative import verify


def test_empty_text_fails():
    r = verify("", "ja")
    assert r["status"] == "FAIL"
    assert "char_count" in r["must_failed"]


def test_bracket_period_fails():
    text = "テスト『括弧の中に句点。』が入っている長い物語を作る必要があります。" * 5
    r = verify(text, "ja")
    assert r["status"] == "FAIL"
    assert "bracket_period" in r["must_failed"]


def test_no_source_marker_fails():
    text = "冬の街角を🚶‍♀️🚶‍♀️🚶‍♀️🚶‍♀️🚶‍♀️歩いていた。音が聞こえ、光が滲み、匂いが漂い、涙が頬を伝い、胸が締め付けられる。私は立ち尽くしていた。音が聞こえ、光が滲み、匂いが漂い、涙が頬を伝い、胸が締め付けられる。私は立ち尽くしていた。" * 3
    r = verify(text, "ja")
    assert r["status"] == "FAIL"
    assert "source_marker" in r["must_failed"]


def test_inner_monologue_ignored():
    text = "🚶‍♀️🚶‍♀️🚶‍♀️🚶‍♀️🚶‍♀️🚶‍♀️冬の街角を猫が徘徊していた。影が長く伸び、通りには微かな光が滲んでいた。彼は心の中で思った、明日はきっとうまくいくと。光が滲み、音が聞こえ、匂いが漂い、涙が頬を伝う。胸が締め付けられる。世界は静かに揺れていた。温かいスープの味を思い出し、濡れた石の感触が靴底に伝わった。街灯の明かりが水たまりに揺れていた。\n> 出典：第1章 p.1 / 段落1"
    r = verify(text, "ja")
    # P-C: inner monologue is not a rule; verdict must not mention it
    assert all(x["rule"] != "inner_monologue" for x in r["results"])


def test_unsupported_locale_fails():
    r = verify("test", "xx")
    assert r["status"] == "FAIL"
    assert "unsupported_locale" in r["must_failed"]


def test_non_string_fails():
    r = verify(123, "ja")
    assert r["status"] == "FAIL"


if __name__ == "__main__":
    test_empty_text_fails()
    test_bracket_period_fails()
    test_no_source_marker_fails()
    test_inner_monologue_ignored()
    test_unsupported_locale_fails()
    test_non_string_fails()
    print("test_verify_must.py: all 6 tests passed")
