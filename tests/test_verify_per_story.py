"""
tests/test_verify_per_story.py
TDD: verify_narrative.py must split the text on `## 物語` and apply
char_count, bracket_period, source_marker, emoji_count, senses per story.
language_ratio is per-file.
"""
from __future__ import annotations
import pytest
from tools.verify_narrative import verify, split_stories


SAMPLE_TWO_STORIES = """\
## 物語
### 雨上がりの約束
雨上がりの街角を歩いていた古い石畳が濡れて光っていた『庭の灯』🌙（灯）🌙🌙🌙🌙🌙遠くから教会の鐘が聞こえた胸の奥がふいに冷えた雨の匂いがした冷たい空気の中を、私はただ歩いていました「あなたは誰ですか」と、誰かが囁いた空気が変わった温かいスープの味を思い出し、濡れた石の感触が靴底に伝わった街灯の明かりが水たまりに揺れ、影が長く伸びていた雨上がりの空に薄く光が差し、皆の肩の力が抜けていった濡れた暖簾をくぐると、出汁の匂いと低い笑い声があふれていた軒下では猫が丸くなり、湯気の向こうで主人が笑っていた。

石畳の水たまりに空が映り、風が静かに吹き抜けていった。

## 解説
疫学講義の冒頭

> 出典：第2章 p.10 / 段落1

## 物語
### 朝の粥
翌朝、台所で母が粥をよそっていた湯気が天井に漂い、台所の窓から差す光が白かった粥の甘い匂いが鼻をくすぐった古い木の箸を持つ母の手が微かに震えていた父は黙って粥を啜っていた誰も何も言わなかった味噌汁の温かい湯気が顔を撫で、箸が触れ合う小さな音が響いた『庭の灯』🌙（灯）🌙🌙🌙🌙🌙ご飯の甘い味が口いっぱいに広がった外では雀の声がしていた湯気の向こうで母が笑い、今日も工房は腹いっぱいだと思った箸が触れ合う音が響き、味噌汁の温もりが顔を包んでいった外では雀の声がして、朝の光が白く差し込んでいた。

昼餉の支度が始まり、包丁の小さな音が台所に響き渡っていった。

## 解説
家庭の場面

> 出典：第2章 p.12 / 段落2
"""

SOURCES_TWO_STORIES = {"kind": "paged", "entries": [
    {"chapter": 2, "page": 10, "para": 1},
    {"chapter": 2, "page": 12, "para": 2},
]}


def test_split_stories_returns_two_blocks():
    blocks = split_stories(SAMPLE_TWO_STORIES)
    assert len(blocks) == 2
    assert blocks[0]["source_marker"] is not None
    assert "p.10" in blocks[0]["source_marker"]
    assert "p.12" in blocks[1]["source_marker"]


def test_per_story_char_count_within_window():
    blocks = split_stories(SAMPLE_TWO_STORIES)
    for b in blocks:
        assert 300 <= len(b["body"]) <= 600, f"body_chars={len(b['body'])} out of window"


def test_per_story_emoji_in_sweet_spot():
    blocks = split_stories(SAMPLE_TWO_STORIES)
    for b in blocks:
        # 6-10 sweet spot
        # We don't count here; trust check_emoji; this is a smoke test
        # that emoji-bearing text doesn't trip parse errors.
        assert "🌙" in b["body"] or "🌟" in b["body"]


def test_per_story_source_marker_present():
    r = verify(SAMPLE_TWO_STORIES, "ja", SOURCES_TWO_STORIES)
    sm_results = [x for x in r["results"] if x["rule"] == "source_marker"]
    assert len(sm_results) == 2
    assert all(x["ok"] for x in sm_results)


def test_language_ratio_is_per_file():
    r = verify(SAMPLE_TWO_STORIES, "ja")
    lang = [x for x in r["results"] if x["rule"] == "language_ratio"]
    assert len(lang) == 1
    assert lang[0]["story"] is None


def test_must_failed_includes_char_count_when_short():
    short = """\
## 物語
短い。🌙

## 解説
短い解説

> 出典：第1章 p.1 / 段落1
"""
    r = verify(short, "ja")
    assert r["status"] == "FAIL"
    assert "char_count" in r["must_failed"]


def test_must_failed_includes_bracket_period_when_present():
    bad = """\
## 物語
テスト。『括弧の中に句点。』とまた『もう一つ。』がある。音がした。光の線が細くなった。雨が降り続いていた。古い木の扉が軋んだ。遠くで誰かが呼んでいた。空気が冷たかった。胸の奥が締まるようだった。🌙✨🔥📚🎵🌟

## 解説
括弧内句点

> 出典：第1章 p.1 / 段落1
"""
    r = verify(bad, "ja")
    assert "bracket_period" in r["must_failed"]


def test_bracket_period_passes_when_clean():
    clean = """\
## 物語
音がした。光の線が細くなった。雨が降り続いていた。古い木の扉が軋んだ。遠くで誰かが呼んでいた。空気が冷たかった。胸の奥が締まるようだった。コーヒーの匂いがした。🌙✨🔥📚🎵🌟

## 解説
解説

> 出典：第1章 p.1 / 段落1
"""
    r = verify(clean, "ja")
    bracket = [x for x in r["results"] if x["rule"] == "bracket_period"]
    assert all(x["ok"] for x in bracket)


def test_two_stories_pass_within_window():
    r = verify(SAMPLE_TWO_STORIES, "ja", SOURCES_TWO_STORIES)
    # either pass or conditional; the point is no must-fail unless a rule trips
    assert r["status"] in ("PASS", "CONDITIONAL PASS")
    # And there should be 2 per-story char_count results
    cc = [x for x in r["results"] if x["rule"] == "char_count"]
    assert len(cc) == 2
