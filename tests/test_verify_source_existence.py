"""
tests/test_verify_source_existence.py
Contract for the kind-tagged source index (issue #6, ADR-0008): a source
marker must name a real input position, not merely match the format.
Covers match / mismatch / missing_source / malformed across the three
kinds (paged, transcript, sectioned), plus the compat set (ASCII colon,
spacing) and the banned forms (brackets, chapter titles, page-less).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from verify_narrative import verify

PAGED = {"kind": "paged", "entries": [
    {"chapter": 2, "page": 10, "para": 1},
    {"label": "社会保障制度", "page": 7, "para": 1},
]}
TRANSCRIPT = {"kind": "transcript", "entries": [
    {"label": "薬理講義", "ref": "0:54"},
]}
SECTIONED = {"kind": "sectioned", "entries": [
    {"label": "寛大", "section": "1.1"},
    {"section": "2.3"},
]}

# Full-valid story (~270 chars, 6 lines): senses, emotion, 6 emojis,
# density in band. Only the marker line varies per test.
BODY_LINES = [
    "『庭の灯』🌸（灯）🌸🌸🌸🌸🌸夕立が路地を叩く夕方、光が水たまりに揺れていた。",
    "米屋の親父は大傘を広げ、音が雨に混ざって響いた。",
    "湯気の向こうで皆が笑い、今日も工房は腹いっぱいだと胸の奥が温かくなった。",
    "咳き込む職人を傘の下に入れ、冷えた背中をさすった。",
    "赤子を抱く母に湯気の匂いがふわりと立ちのぼった。",
    "温かい茶を飲ませ、胸に喜びが満ちていった。",
    "濡れた石畳の感触を確かめ、甘い飯の味が広がった。",
    "外では雀の声がして、誰かが小さく笑っていた。",
    "夜が更けて雨音だけが残り、明日への願いを胸に抱いた。",
    "囲炉裏の火が赤く燃え、煙の匂いが服に染み込んでいった。",
    "濡れた暖簾をくぐると、出汁の匂いと笑い声があふれていた。",
    "雨上がりの空に光が差し、皆の肩の力が抜けていった。",
    "軒下では猫が丸くなり、湯気の向こうで主人が静かに笑い、皆がそれを見て和んでいた。",
]


def _story(marker: str) -> str:
    return "## 物語\n### 夕立の約束\n" + "\n\n".join(BODY_LINES) + "\n" + marker


def _sm(text, locale="ja", sources=PAGED):
    rules = [r for r in verify(text, locale, sources)["results"] if r["rule"] == "source_marker"]
    assert len(rules) == 1
    return rules[0]


def test_paged_chapter_match_passes():
    r = verify(_story("> 出典：第2章 p.10 / 段落1"), "ja", PAGED)
    assert r["status"] == "PASS", r.get("must_failed")


def test_paged_label_match_passes():
    sm = _sm(_story("> 出典：社会保障制度 p.7 / 段落1"))
    assert sm["ok"] is True, sm


def test_hallucinated_chapter_fails():
    r = verify(_story("> 出典：第9章 p.99 / 段落1"), "ja", PAGED)
    assert r["status"] == "FAIL"
    assert "source_marker" in r["must_failed"]
    sm = _sm(_story("> 出典：第9章 p.99 / 段落1"))
    assert sm["ok"] is False
    assert sm["note"].startswith("source_mismatch"), sm


def test_missing_sources_fails():
    r = verify(_story("> 出典：第2章 p.10 / 段落1"), "ja")
    assert r["status"] == "FAIL"
    assert "source_marker" in r["must_failed"]
    sm = _sm(_story("> 出典：第2章 p.10 / 段落1"), sources=None)
    assert sm["note"].startswith("missing_source"), sm


def test_absent_marker_is_malformed():
    sm = _sm("\n".join(BODY_LINES))
    assert sm["ok"] is False
    assert sm["value"] == 0
    assert sm["note"].startswith("source_malformed"), sm


def test_bracket_form_is_banned():
    sm = _sm(_story("[出典：社会保障制度 p.7 / 段落1]"))
    assert sm["ok"] is False
    assert sm["note"].startswith("source_malformed"), sm


def test_chapter_title_in_marker_is_malformed():
    sm = _sm(_story("> 出典：第2章「細胞」 p.10 / 段落1"))
    assert sm["ok"] is False
    assert sm["note"].startswith("source_malformed"), sm


def test_pageless_marker_is_malformed():
    sm = _sm(_story("> 出典：第2章 / 段落1"))
    assert sm["ok"] is False
    assert sm["note"].startswith("source_malformed"), sm


def test_ascii_colon_and_spacing_are_compat():
    sm = _sm(_story("> 出典: 第2章 p.10 / 段落1"))
    assert sm["ok"] is True, sm
    sm = _sm(_story("> 出典：第2章  p.10  /  段落1"))
    assert sm["ok"] is True, sm


def test_multiple_markers_all_must_match():
    text = _story("> 出典：第2章 p.10 / 段落1\n> 出典：社会保障制度 p.7 / 段落1")
    sm = _sm(text)
    assert sm["value"] == 2
    assert sm["ok"] is True, sm


def test_multiple_markers_one_mismatch_fails():
    text = _story("> 出典：第2章 p.10 / 段落1\n> 出典：第7章 p.7 / 段落1")
    sm = _sm(text)
    assert sm["ok"] is False
    assert sm["note"].startswith("source_mismatch"), sm


def test_transcript_exact_ref_match():
    sm = _sm(_story("> 出典：薬理講義 0:54"), sources=TRANSCRIPT)
    assert sm["ok"] is True, sm
    sm = _sm(_story("> 出典：薬理講義 1:05"), sources=TRANSCRIPT)
    assert sm["ok"] is False
    assert sm["note"].startswith("source_mismatch"), sm


def test_sectioned_with_and_without_label():
    sm = _sm(_story("> 出典：寛大 1.1"), sources=SECTIONED)
    assert sm["ok"] is True, sm
    sm = _sm(_story("> 出典：2.3"), sources=SECTIONED)
    assert sm["ok"] is True, sm
    sm = _sm(_story("> 出典：吝嗇 1.1"), sources=SECTIONED)
    assert sm["ok"] is False
    assert sm["note"].startswith("source_mismatch"), sm


def test_invalid_kind_is_invalid_sources():
    r = verify(_story("> 出典：第2章 p.10 / 段落1"), "ja", {"kind": "book", "entries": []})
    assert r["status"] == "FAIL"
    assert "invalid_sources" in r["must_failed"]


def test_non_ja_existence_checked():
    en_sources = {"kind": "paged", "entries": [{"chapter": 1, "page": 1, "para": 1}]}
    text = "light " * 60 + "sound " * 60 + "\n> Source: Ch.1 P.1 / Para.1"
    sm = _sm(text, locale="en", sources=en_sources)
    assert sm["ok"] is True, sm
    sm = _sm(text, locale="en", sources=None)
    assert sm["ok"] is False
    assert sm["note"].startswith("missing_source"), sm
    sm = _sm(text.replace("Ch.1 P.1", "Ch.9 P.9"), locale="en", sources=en_sources)
    assert sm["ok"] is False
    assert sm["note"].startswith("source_mismatch"), sm


def test_zh_ko_paged_match():
    sm = _sm("光 " * 100 + "\n> 出处：第2章 P. 10 / 段落1", locale="zh",
             sources={"kind": "paged", "entries": [{"chapter": 2, "page": 10, "para": 1}]})
    assert sm["ok"] is True, sm
    sm = _sm("빛 " * 100 + "\n> 출처: 제2장 P. 10 / 문단1", locale="ko",
             sources={"kind": "paged", "entries": [{"chapter": 2, "page": 10, "para": 1}]})
    assert sm["ok"] is True, sm


def test_pageless_locales_match_without_page():
    ar_sources = {"kind": "paged", "entries": [{"chapter": 2, "para": 1}]}
    sm = _sm("اختبار " * 60 + "\n> المصدر: الفصل 2 / فقرة 1", locale="ar", sources=ar_sources)
    assert sm["ok"] is True, sm
    es_sources = {"kind": "paged", "entries": [{"chapter": 2, "para": 1}]}
    sm = _sm("prueba " * 60 + "\n> Fuente: Cap. 2 / Párr. 1", locale="es", sources=es_sources)
    assert sm["ok"] is True, sm
    fr_sources = {"kind": "paged", "entries": [{"chapter": 2, "para": 1}]}
    sm = _sm("test " * 60 + "\n> Source: Chap. 2 / Par. 1", locale="fr", sources=fr_sources)
    assert sm["ok"] is True, sm
    ru_sources = {"kind": "paged", "entries": [{"chapter": 2, "para": 1}]}
    sm = _sm("тест " * 60 + "\n> Источник: Гл. 2 / Абз. 1", locale="ru", sources=ru_sources)
    assert sm["ok"] is True, sm


def test_pageless_locales_mismatch_and_optional_page():
    ar_sources = {"kind": "paged", "entries": [{"chapter": 2, "para": 1}]}
    sm = _sm("اختبار " * 60 + "\n> المصدر: الفصل 9 / فقرة 1", locale="ar", sources=ar_sources)
    assert sm["ok"] is False
    assert sm["note"].startswith("source_mismatch"), sm
    with_page = {"kind": "paged", "entries": [{"chapter": 2, "page": 10, "para": 1}]}
    sm = _sm("اختبار " * 60 + "\n> المصدر: الفصل 2 P. 10 / فقرة 1", locale="ar", sources=with_page)
    assert sm["ok"] is True, sm


def test_bracket_banned_everywhere():
    sm = _sm("light " * 60 + "sound " * 60 + "\n[Source: Ch.1 P.1 / Para.1]",
             locale="en", sources=PAGED)
    assert sm["ok"] is False
    assert sm["note"].startswith("source_malformed"), sm


def test_other_locale_transcript_and_sectioned():
    sm = _sm("빛 " * 100 + "\n> 출처: 강의 0:54", locale="ko",
             sources={"kind": "transcript", "entries": [{"label": "강의", "ref": "0:54"}]})
    assert sm["ok"] is True, sm
    sm = _sm("light " * 60 + "sound " * 60 + "\n> Source: Book 1.2", locale="en",
             sources={"kind": "sectioned", "entries": [{"label": "Book", "section": "1.2"}]})
    assert sm["ok"] is True, sm


if __name__ == "__main__":
    test_paged_chapter_match_passes()
    test_paged_label_match_passes()
    test_hallucinated_chapter_fails()
    test_missing_sources_fails()
    test_absent_marker_is_malformed()
    test_bracket_form_is_banned()
    test_chapter_title_in_marker_is_malformed()
    test_pageless_marker_is_malformed()
    test_ascii_colon_and_spacing_are_compat()
    test_multiple_markers_all_must_match()
    test_multiple_markers_one_mismatch_fails()
    test_transcript_exact_ref_match()
    test_sectioned_with_and_without_label()
    test_invalid_kind_is_invalid_sources()
    test_non_ja_existence_checked()
    test_zh_ko_paged_match()
    test_pageless_locales_match_without_page()
    test_pageless_locales_mismatch_and_optional_page()
    test_bracket_banned_everywhere()
    test_other_locale_transcript_and_sectioned()
    print("test_verify_source_existence.py: all 21 tests passed")
