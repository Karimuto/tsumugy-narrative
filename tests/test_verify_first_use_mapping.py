"""
tests/test_verify_first_use_mapping.py
First-use mapping rule (grill 2026-09-05, ADR-0011): the first occurrence
of every locale-bracket metaphor in the narrative region must read
METAPHOR + anchor emoji + (textbook term), full or half width parens.
Later occurrences need the anchor emoji only. Every anchor emoji must be
introduced by a 3-point set at or before its position: bare anchors with
no introduction, and anchors used before their introduction, MUST fail.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from verify_narrative import verify

MARKER = "> 出典：第1章 p.1 / 段落1"

SOURCES_PAGED_1 = {"kind": "paged", "entries": [{"chapter": 1, "page": 1, "para": 1}]}

MAPPED_LINES = [
    "『一筋の矢』🎯（イマチニブ）が空を切り裂き、光が差して音が響き渡り、皆が駆け寄ってきた。",
    "湯気の匂いが立ちのぼる中『祝い花』🌸（安堵）がほころび、矢🎯は的に吸い込まれ主人が頷いた。",
    "湯気の匂いが立ちのぼる中、矢🎯は的の真ん中に吸い込まれ、主人が静かに頷いた🌸",
    "指先ですくって舐めた蜜の甘い味が口いっぱいに広がり、冷えた体に温もりが戻ってきた🌸",
    "老婆の冷たい手に触れたその瞬間に震えが止まり、胸の奥に喜びが満ちていった🌸",
    "濡れた石畳の上で皆の影が一つに重なり合い、誰かが小さく笑い出した🌸",
    "雨上がりの空に薄く光が差し込み、皆の肩の力が抜けて帰り支度を始めた🌸",
    "軒下では猫が丸くなり、湯気の向こうで主人が静かに笑い、夜が更けていった🌸",
    "外では雀の声がして、誰かが小さく笑い、夜が更けていった。",
    "井戸の水面に光が揺れ、朝の訪れを告げる音が静かに広がった。",
    "夜が更けて雨音だけが残り、明日への願いを胸に抱いて歩き続けた。",
]


def _doc(body: str) -> str:
    return "## 物語\n### 矢の朝\n" + body + "\n" + MARKER


def _mapping(results):
    return next(x for x in results if x["rule"] == "first_use_mapping")


def test_mapped_first_use_passes():
    r = verify(_doc("\n\n".join(MAPPED_LINES)), "ja", SOURCES_PAGED_1)
    m = _mapping(r["results"])
    assert m["ok"] is True, f"3-point first use should pass: {m}"
    assert r["status"] == "PASS", f"expected PASS, got {r['status']}: {r.get('must_failed')} {r.get('should_failed')}"


def test_unmapped_bracket_must_fails():
    body = "\n\n".join(
        [MAPPED_LINES[0].replace("『一筋の矢』🎯（イマチニブ）", "『一筋の矢』が空を切ったと皆が言い")] + MAPPED_LINES[1:]
    )
    r = verify(_doc(body), "ja", SOURCES_PAGED_1)
    m = _mapping(r["results"])
    assert m["ok"] is False, f"bare bracket should fail: {m}"
    assert m["severity"] == "must"
    assert r["status"] == "FAIL"
    assert "first_use_mapping" in r["must_failed"]


def test_emoji_without_term_must_fails():
    body = "\n\n".join(
        [MAPPED_LINES[0].replace("🎯（イマチニブ）", "🎯")] + MAPPED_LINES[1:]
    )
    r = verify(_doc(body), "ja", SOURCES_PAGED_1)
    m = _mapping(r["results"])
    assert m["ok"] is False, f"emoji without term should fail: {m}"
    assert "first_use_mapping" in r["must_failed"]


def test_ascii_parens_pass():
    body = "\n\n".join(
        [MAPPED_LINES[0].replace("🎯（イマチニブ）", "🎯(イマチニブ)")] + MAPPED_LINES[1:]
    )
    r = verify(_doc(body), "ja", SOURCES_PAGED_1)
    m = _mapping(r["results"])
    assert m["ok"] is True, f"half width parens should pass: {m}"


def test_second_metaphor_needs_own_mapping():
    extra = "『緑の染料壺』が棚に並び、ぶるぶると震えて色を吸い込んでいた。光が差し音が響き、皆が見守る中で主人が頷き、夜が更けて朝が近づいていた。"
    body = "\n\n".join(MAPPED_LINES + [extra])
    r = verify(_doc(body), "ja", SOURCES_PAGED_1)
    m = _mapping(r["results"])
    assert m["ok"] is False, f"second unmapped metaphor should fail: {m}"
    assert "緑の染料壺" in m.get("misses", [])


def test_bare_anchors_without_mapping_must_fail():
    body = "\n\n".join([line.replace("『一筋の矢』🎯（イマチニブ）", "一筋の矢🎯（イマチニブ）") for line in MAPPED_LINES])
    r = verify(_doc(body), "ja", SOURCES_PAGED_1)
    m = _mapping(r["results"])
    assert m["ok"] is False, f"bare anchors with no introduction should fail: {m}"
    assert "🎯" in m.get("unmapped", []), f"unintroduced anchor should be named: {m}"
    assert r["status"] == "FAIL"
    assert "first_use_mapping" in r["must_failed"]


def test_anchor_used_before_introduction_must_fail():
    early = "鍵🔑を握りしめ、夜の薬局の片隅に立ち尽くしていた。冷たい風が頬を撫で、遠くで鐘の音が響き渡っていた。"
    late = "やがて主人が差し出した『鍵』🔑（真鍮の鍵）が淡い光を放ち、皆が息を呑んで見つめていた。"
    body = "\n\n".join([early, late] + MAPPED_LINES[2:])
    r = verify(_doc(body), "ja", SOURCES_PAGED_1)
    m = _mapping(r["results"])
    assert m["ok"] is False, f"use before introduction should fail: {m}"
    assert "🔑" in m.get("unmapped", []), f"early anchor should be named: {m}"
    assert "first_use_mapping" in r["must_failed"]


def test_carryover_anchor_reuse_passes():
    ep1 = "『灯』🏮（希望）が闇夜に燃え、皆がその温もりに集まってきた。光が差して音が響き、主人が静かに頷いた。"
    ep2 = "次の夜も灯🏮は燃え続け、旅人たちが影を落としながら温まっていた。風が優しく吹き、皆が見守っていた。"
    doc = "## 物語\n### 一\n" + ep1 + "\n" + MARKER + "\n## 物語\n### 二\n" + ep2 + "\n" + MARKER
    r = verify(doc, "ja", SOURCES_PAGED_1)
    maps = [x for x in r["results"] if x["rule"] == "first_use_mapping"]
    assert len(maps) == 2, f"expected per-story results: {maps}"
    assert all(x["ok"] for x in maps), f"serial reuse of introduced anchor should pass: {maps}"


if __name__ == "__main__":
    test_mapped_first_use_passes()
    test_unmapped_bracket_must_fails()
    test_emoji_without_term_must_fails()
    test_ascii_parens_pass()
    test_second_metaphor_needs_own_mapping()
    test_bare_anchors_without_mapping_must_fail()
    test_anchor_used_before_introduction_must_fail()
    test_carryover_anchor_reuse_passes()
    print("test_verify_first_use_mapping.py: all 8 tests passed")
