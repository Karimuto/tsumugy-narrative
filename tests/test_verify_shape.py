"""
tests/test_verify_shape.py
Shape must-rules (issue #8, ADR-0009): frontmatter_yaml and story_heading
run per file; title and author_attribution run per story over clean bodies
(preamble separated out, voice lines excluded from every check).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from verify_narrative import (
    check_frontmatter_yaml,
    check_title,
    extract_preamble,
    split_stories,
    verify,
)

SOURCES_PAGED_1 = {"kind": "paged", "entries": [{"chapter": 1, "page": 1, "para": 1}]}

JA_BODY = "\n\n".join([
    "『庭の灯』🌸（灯）🌸🌸🌸🌸🌸夕立が路地を叩く夕方、光が水たまりに揺れていた。",
    "夜が更けて雨音だけが残り、明日への願いを胸に抱いた。",
    "囲炉裏の火が赤く燃え、煙の匂いが服に染み込んだ。",
    "遠くの寺から鐘の音が響き、雪が静かに降り始めた。",
    "祖母の温かい手に触れ、涙がこぼれそうになった。",
    "釜の湯気が天井にのぼり、米の甘い香りが広がった。",
    "犬が遠くで吠え、風が戸を叩く音がした。",
    "米屋の親父は大傘を広げ、音が雨に混ざって響いた。",
    "湯気の匂いがふわりと立ち、冷えた背中をさすって温めた。",
    "赤子を抱く母に茶を飲ませ、胸に喜びが満ちていった。",
    "濡れた石畳の感触を確かめ、甘い飯の味が広がった。",
    "外では雀の声がして、誰かが小さく笑った。",
    "軒下では猫が丸くなり、湯気の向こうで主人が笑っていた。",
    "濡れた暖簾をくぐると、出汁の匂いと笑い声があふれていた。",
    "雨上がりの空に光が差し、皆の肩の力が抜けていった。",
])

JA_MARKER = "> 出典：第1章 p.1 / 段落1"


def _doc(body=JA_BODY, heading="## 物語", title="### 夕立の約束",
         marker=JA_MARKER, preamble=""):
    return preamble + heading + "\n" + title + "\n" + body + "\n" + marker + "\n"


def _shape_failed(r):
    return [n for n in ("frontmatter_yaml", "story_heading", "title",
                        "author_attribution") if n in r["must_failed"]]


def test_clean_doc_passes_shape_and_status():
    r = verify(_doc(), "ja", SOURCES_PAGED_1)
    assert _shape_failed(r) == [], f"shape must pass: {r['must_failed']}"
    assert r["status"] == "PASS", f"{r['status']}: {r['must_failed']} {r['should_failed']}"


def test_frontmatter_fence_fails():
    fence = "---\nmode: serial\nthread_id: review3-serial\nauthor: Fyodor Dostoevsky\n---\n"
    r = verify(_doc(preamble=fence), "ja", SOURCES_PAGED_1)
    assert r["status"] == "FAIL"
    assert "frontmatter_yaml" in r["must_failed"]


def test_metadata_key_without_fence_fails():
    r = verify(_doc(preamble="thread_id: review3-serial\n"), "ja", SOURCES_PAGED_1)
    assert "frontmatter_yaml" in r["must_failed"]


def test_whitespace_preamble_passes():
    r = verify(_doc(preamble="\n\n"), "ja", SOURCES_PAGED_1)
    assert "frontmatter_yaml" not in r["must_failed"]
    assert r["status"] == "PASS", f"{r['status']}: {r['must_failed']}"


def test_check_frontmatter_direct():
    assert check_frontmatter_yaml("## 物語\n本文\n")["ok"] is True
    assert check_frontmatter_yaml("---\nmode: serial\n---\n## 物語\n")["ok"] is False
    assert check_frontmatter_yaml("## 物語\nprotagonist: 田中\n")["ok"] is False


def test_no_heading_fails():
    r = verify(JA_BODY + "\n" + JA_MARKER + "\n", "ja", SOURCES_PAGED_1)
    assert "story_heading" in r["must_failed"]


def test_extract_preamble():
    assert extract_preamble("## 物語\n本文\n") == ""
    assert extract_preamble("\n\n## 物語\n本文\n") == "\n\n"
    text = "---\nmode: serial\n---\n## 物語\n本文\n"
    assert extract_preamble(text) == "---\nmode: serial\n---\n"
    blocks = split_stories(text)
    assert len(blocks) == 1
    assert "---" not in blocks[0]["body"]


def test_title_missing_fails():
    r = verify("## 物語\n" + JA_BODY + "\n" + JA_MARKER + "\n", "ja", SOURCES_PAGED_1)
    assert "title" in r["must_failed"]


def test_title_empty_fails():
    r = verify("## 物語\n###   \n" + JA_BODY + "\n" + JA_MARKER + "\n",
               "ja", SOURCES_PAGED_1)
    assert "title" in r["must_failed"]


def test_title_misplaced_fails():
    doc = "## 物語\n" + JA_BODY + "\n### 夕立の約束\n" + JA_MARKER + "\n"
    r = verify(doc, "ja", SOURCES_PAGED_1)
    assert "title" in r["must_failed"]


def test_check_title_direct():
    assert check_title("### 夜汽車の約束\n本文\n")["ok"] is True
    assert check_title("本文のみ\n")["ok"] is False
    assert check_title("###   \n本文\n")["ok"] is False
    assert check_title("前置き\n### 題\n")["ok"] is False
    assert check_title("### 一つ目\n### 二つ目\n")["ok"] is False


def test_author_latin_leak_fails():
    body = JA_BODY + "彼の声はFyodor Dostoevskyの独白のようだった。"
    r = verify(_doc(body=body), "ja", SOURCES_PAGED_1)
    assert "author_attribution" in r["must_failed"]


def test_author_cjk_leak_fails():
    body = JA_BODY + "川端康成の雪国の一節を思い出した。"
    r = verify(_doc(body=body), "ja", SOURCES_PAGED_1)
    assert "author_attribution" in r["must_failed"]


def test_voice_line_excluded():
    doc = _doc() + "voice: DO (psychological-novel style)\n"
    r = verify(doc, "ja", SOURCES_PAGED_1)
    assert "author_attribution" not in r["must_failed"]
    assert r["status"] == "PASS", f"voice lines must affect no check: {r['must_failed']} {r['should_failed']}"


def test_voice_line_real_name_not_checked():
    # Q6 decision: voice lines carry no verification, even when malformed.
    doc = _doc() + "voice: DO (Fyodor Dostoevsky)\n"
    r = verify(doc, "ja", SOURCES_PAGED_1)
    assert "author_attribution" not in r["must_failed"]


def test_en_shape_rules():
    body = "The baker opened his shop at dawn. Light fell on the wet stones."
    marker = "> Source: Ch. 1 P. 1 / Para. 1"
    ok = "## Story\n### The Promise of Rain\n" + body + "\n" + marker + "\n"
    r = verify(ok, "en")
    assert _shape_failed(r) == [], f"en shape must pass: {r['must_failed']}"
    leaked = ("## Story\n### The Promise of Rain\n" + body
              + " Virginia Woolf would have loved it.\n" + marker + "\n")
    r = verify(leaked, "en")
    assert "author_attribution" in r["must_failed"]

def test_3_serial_regression():
    # End to end proof on the reported artifact: the leading YAML block
    # must fail shape rules, not slide through on emoji alone. The author
    # name lives in the preamble, so the frontmatter rule owns the failure;
    # body leaks are covered by the unit tests above.
    # Fixture migrated from samples/manual in #16 (samples/ is untracked).
    text = (ROOT / "tests" / "fixtures"
            / "serial-frontmatter-regression.md").read_text(encoding="utf-8")
    r = verify(text, "ja")
    assert r["status"] == "FAIL"
    assert "frontmatter_yaml" in r["must_failed"]


if __name__ == "__main__":
    test_clean_doc_passes_shape_and_status()
    test_frontmatter_fence_fails()
    test_metadata_key_without_fence_fails()
    test_whitespace_preamble_passes()
    test_check_frontmatter_direct()
    test_no_heading_fails()
    test_extract_preamble()
    test_title_missing_fails()
    test_title_empty_fails()
    test_title_misplaced_fails()
    test_check_title_direct()
    test_author_latin_leak_fails()
    test_author_cjk_leak_fails()
    test_voice_line_excluded()
    test_voice_line_real_name_not_checked()
    test_en_shape_rules()
    test_3_serial_regression()
    print("test_verify_shape.py: all 17 tests passed")
