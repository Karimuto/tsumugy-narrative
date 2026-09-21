"""
tests/test_verify_paragraph_break.py
Paragraph-break rule (ADR-0010): story-body paragraphs must be divided by
a blank line. Any run of two or more consecutive non-empty narrative lines
(between the ### title and ## 解説, headings/markers/voice excluded) is a
MUST failure. Single-paragraph bodies pass vacuously.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from verify_narrative import verify

MARKER = "> 出典：第1章 p.1 / 段落1"

SOURCES_PAGED_1 = {"kind": "paged", "entries": [{"chapter": 1, "page": 1, "para": 1}]}

STORY_LINES = [
    "光が水たまりに揺れ、赤い大傘の下で雨の音がしきりに響き渡り、濡れた路地に皆が駆け寄ってきたところだった『庭の灯』🌸（灯）、皆が頷いた、朝が近づいていた",
    "米屋の親父は咳き込む職人を傘の下に招き入れ、冷えた背中を両手でさすって温め、湯飲みをそっと渡した🌸、湯気が立ちのぼった",
    "湯気の匂いがふわりと立ちのぼり、赤子の母に白い飯をよそって喜ばれ、皆の顔に笑みが広がっていった🌸、雨音が響いていた",
    "指先ですくってそっと舐めるとほのかに甘い蜜の味が口いっぱいに広がり、冷えた体に温もりが戻ってきた🌸、光が揺れていた",
    "老婆の冷たい手が茶碗に触れたその瞬間に震えがすっと止まっていき、皆がほっとして顔を見合わせた🌸、皆が笑っていた",
    "胸に喜びが満ちあふれて、濡れた石畳の上で皆の影が一つに重なり、誰かが小さく笑い出した🌸、風が吹き抜けた",
    "雨上がりの空に薄く光が差し、皆の肩の力が抜けて帰り支度を始めた🌸、夜が更けていった",
]


def _doc(body: str) -> str:
    return "## 物語\n### 長屋の朝\n" + body + "\n" + MARKER


def _rule(results, name):
    return next(x for x in results if x["rule"] == name)


def test_blank_separated_passes():
    r = verify(_doc("\n\n".join(STORY_LINES)), "ja", SOURCES_PAGED_1)
    p = _rule(r["results"], "paragraph_break")
    assert p["ok"] is True, f"blank-separated body should pass: {p}"
    assert r["status"] == "PASS", f"expected PASS, got {r['status']}: {r.get('must_failed')} {r.get('should_failed')}"


def test_joined_paragraphs_must_fail():
    r = verify(_doc("\n".join(STORY_LINES)), "ja", SOURCES_PAGED_1)
    p = _rule(r["results"], "paragraph_break")
    assert p["ok"] is False, f"joined body should fail: {p}"
    assert p["severity"] == "must"
    assert r["status"] == "FAIL", f"expected FAIL, got {r['status']}"
    assert "paragraph_break" in r["must_failed"]


def test_single_paragraph_passes_vacuously():
    line = "光が水たまりに揺れ、赤い大傘の下で雨の音が響いた。湯気の匂いが立ち、指先の蜜が甘く、老婆の手の温もりに触れた。胸に喜びが満ちて皆の影が一つに重なった『庭の灯』🌸（灯）🌸🌸🌸🌸🌸。"
    r = verify(_doc(line), "ja", SOURCES_PAGED_1)
    p = _rule(r["results"], "paragraph_break")
    assert p["ok"] is True, f"single paragraph has nothing to separate: {p}"


    expl = "この物語は長屋の夕立を描いた。傘と飯のやり取りが対応する。"
    body = "\n\n".join(STORY_LINES[:3])
    doc = "## 物語\n### 長屋の朝\n" + body + "\n## 解説\n" + expl + "\n" + MARKER
    r = verify(doc, "ja", SOURCES_PAGED_1)
    p = _rule(r["results"], "paragraph_break")
    assert p["ok"] is True, f"explanation lines must not trigger: {p}"


def test_dialogue_shape_passes():
    lines = [
        "「傘に入りな」と親父が言い、雨の音が暗い路地いっぱいに高く響いた『庭の灯』🌸（灯）、光が揺れていた、湯気が立ちのぼった、朝が近づいていた、風が吹き抜けた",
        "職人は咳をこらえながら、湯気の匂いにそっと目を細めて座り込んだ🌸、皆が笑っていた、雨音が響いていた、皆が頷いた、夜が更けていった",
        "光が水たまりに揺れ、甘い茶をすすれば冷え切った温もりが戻った🌸、風が吹き抜けた、光が揺れていた、湯気が立ちのぼった、朝が近づいていた",
        "老婆の冷たい手にそっと触れると、胸の奥に喜びが満ちていった🌸、夜が更けていった、皆が笑っていた、雨音が響いていた、皆が頷いた",
        "皆の影が一つに重なり合い、濡れた石畳の上で誰かが小さく笑った🌸🌸、朝が近づいていた、風が吹き抜けた、光が揺れていた、湯気が立ちのぼった",
        "雨が上がれば路地に光が戻り、明日への願いを胸に抱いた🌸、皆が頷いた、夜が更けていった、皆が笑っていた、雨音が響いていた",
    ]
    r = verify(_doc("\n\n".join(lines)), "ja", SOURCES_PAGED_1)
    p = _rule(r["results"], "paragraph_break")
    assert p["ok"] is True, f"dialogue shape should pass: {p}"
    assert r["status"] == "PASS", f"expected PASS, got {r['status']}: {r.get('must_failed')} {r.get('should_failed')}"


def test_partial_join_reports_worst_run():
    body = STORY_LINES[0] + "\n" + STORY_LINES[1] + "\n\n" + STORY_LINES[2]
    r = verify(_doc(body), "ja", SOURCES_PAGED_1)
    p = _rule(r["results"], "paragraph_break")
    assert p["ok"] is False
    assert p["value"] == 2, f"worst run should be 2: {p}"
    assert "paragraph_break" in r["must_failed"]


if __name__ == "__main__":
    test_blank_separated_passes()
    test_joined_paragraphs_must_fail()
    test_single_paragraph_passes_vacuously()
    test_explanation_lines_are_out_of_scope()
    test_dialogue_shape_passes()
    test_partial_join_reports_worst_run()
    print("test_verify_paragraph_break.py: all 6 tests passed")
