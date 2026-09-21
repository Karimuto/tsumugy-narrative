"""
tests/test_verify_emoji_sequences.py
TDD: emoji are counted as RGI sequences (ADR-0006), one visible emoji is one.
Seam: check_emoji() via verify(), the same public boundary as the other
verify tests. Expected values come from UTS #51 RGI sequence definitions,
not from the implementation.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from verify_narrative import check_emoji

def test_subdivision_flag_counts_as_one_emoji():
    # WAVING WHITE FLAG + tag letters g b e n g + CANCEL TAG is one sequence.
    england = "\U0001F3F4\U000E0067\U000E0062\U000E0065\U000E006E\U000E0067\U000E007F"
    assert check_emoji(england, "ja")["value"] == 1


def test_flag_pair_counts_as_one_emoji():
    # Regional Indicator pair U+1F1E6 U+1F1F5 is one RGI flag sequence.
    assert check_emoji("\U0001F1E6\U0001F1F5", "ja")["value"] == 1


def test_six_flags_hit_sweet_spot():
    r = check_emoji("\U0001F1E6\U0001F1F5" * 6, "ja")
    assert r["value"] == 6
    assert r["ok"] is True


def test_keycap_sequence_counts_as_one_emoji():
    # DIGIT ONE + VS16 + COMBINING ENCLOSING KEYCAP is one RGI sequence.
    assert check_emoji("1\uFE0F\u20E3", "ja")["value"] == 1


def test_skin_tone_modifier_counts_as_one_emoji():
    # THUMBS UP + EMOJI MODIFIER FITZPATRICK TYPE-4 is one RGI sequence.
    assert check_emoji("\U0001F44D\U0001F3FD", "ja")["value"] == 1


def test_zwj_family_counts_as_one_emoji():
    # MAN + ZWJ + WOMAN + ZWJ + GIRL + ZWJ + BOY is one RGI ZWJ sequence.
    family = "\U0001F468\u200D\U0001F469\u200D\U0001F467\u200D\U0001F466"
    assert check_emoji(family, "ja")["value"] == 1


def test_zwj_profession_counts_as_one_emoji():
    # WOMAN + ZWJ + ROCKET is one RGI ZWJ sequence.
    assert check_emoji("\U0001F469\u200D\U0001F680", "ja")["value"] == 1


def test_six_zwj_families_hit_sweet_spot():
    family = "\U0001F468\u200D\U0001F469\u200D\U0001F467\u200D\U0001F466"
    r = check_emoji(family * 6, "ja")
    assert r["value"] == 6
    assert r["ok"] is True


if __name__ == "__main__":
    test_subdivision_flag_counts_as_one_emoji()
    test_flag_pair_counts_as_one_emoji()
    test_six_flags_hit_sweet_spot()
    test_keycap_sequence_counts_as_one_emoji()
    test_skin_tone_modifier_counts_as_one_emoji()
    test_zwj_family_counts_as_one_emoji()
    test_zwj_profession_counts_as_one_emoji()
    test_six_zwj_families_hit_sweet_spot()
    print("test_verify_emoji_sequences.py: all 8 tests passed")
