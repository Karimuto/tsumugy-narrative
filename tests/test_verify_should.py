"""
tests/test_verify_should.py
Verifies that should-severity rules trigger CONDITIONAL PASS (not FAIL).
"""
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from verify_narrative import verify

SOURCES_PAGED_1 = {"kind": "paged", "entries": [{"chapter": 1, "page": 1, "para": 1}]}


def test_no_emoji_must_fail():
    # 200+ chars, has source, inner voice, senses. No emoji.
    # Per spec: <4 emojis = MUST fail
    text = (
        "冬の朝を歩いていた。影が長く伸び、通りには微かな光が滲んでいた。"
        "光が滲み、音が聞こえ、匂いが漂い、涙が頬を伝い、胸が締め付けられる。"
        "私は立ち尽くしていた。音が聞こえ、光が滲み、匂いが漂い、涙が頬を伝い、"
        "胸が締め付けられる。私は立ち尽くしていた。音が聞こえ、光が滲み、匂いが漂い、"
        "涙が頬を伝い、胸が締め付けられる。私は静かに歩き続けた。音が聞こえ、匂いが漂い、"
        "光が滲み、涙が頬を伝い、胸が締め付けられる。私は静かに歩き続けた。\n"
        "> 出典: 第1章 p.1 / 段落1"
    )
    r = verify(text, "ja")
    assert r["status"] == "FAIL", f"expected fail, got {r['status']}"
    assert "emoji_count" in r["must_failed"]


def test_senses_must_pass():
    # Normal Japanese text naturally hits multiple senses -> MUST pass.
    # Since issue #4, full PASS also needs a distinct emotion word
    # (胸に喜びが満ちた below); without it the story is CONDITIONAL PASS.
    # Use 6 emojis (6-10 range = MUST pass for emoji_count)
    text = "\n\n".join([
        "## 物語\n### 冬の朝\n"
        "『庭の灯』🌸（灯）🌸🌸🌸🌸🌸ある朝、私は起きた。胸に喜びが満ちた。何かが足りない気がした。",
        "私は立ち止まって思った。世界のどこかで誰かが同じことを考えている。",
        "時間が止まったように感じた。私は再び歩き始めた。",
        "別の日、私はまた起きた。何かが足りない気がして、私は立ち止まった。",
        "また別の日、私はまた起きた。何かが足りない気がして、私は歩き続けた。",
        "また別の日、私はまた起きた。何かが足りない気がして、私は立ち止まって思った。",
        "世界は静かに回っている。私はまた歩き始めた。",
        "私は立ち止まって思った。世界のどこかで誰かが同じことを考えている。",
        "時間が止まったように感じた。私は再び歩き始めた。",
        "別の日、私はまた起きた。何かが足りない気がして、私は立ち止まった。",
        "また別の日、私はまた起きた。何かが足りない気がして、私は立ち止まった。",
        "また別の日、私はまた起きた。何かが足りない気がして、私は歩き続けた。",
        "また別の日、私はまた起きた。何かが足りない気がして、私は立ち止まって思った。",
    ]) + "\n> 出典: 第1章 p.1 / 段落1"
    r = verify(text, "ja", SOURCES_PAGED_1)
    # Normal text hits 2+ senses -> MUST pass
    assert r["status"] == "PASS", f"expected pass, got {r['status']}: {r.get('must_failed')} {r.get('should_failed')}"


def test_emoji_warn_conditional():
    # 11+ emojis -> SHOULD fail (warn) -> conditional
    text = (
        "## 物語\n### 冬の朝\n"
        "『庭の灯』🌟（灯）🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟冬の朝を歩いていた。影が長く伸びていた。\n\n"
        "通りには微かな光が滲み、音が聞こえ、匂いが漂っていた。\n\n"
        "涙が頬を伝う。胸が締め付けられる。私は立ち尽くしていた。\n\n"
        "音が聞こえ、光が滲み、匂いが漂い、涙が頬を伝う。\n\n"
        "胸が締め付けられる。私は立ち止まり、冬の風に吹かれた。\n\n"
        "涙が頬を伝う。私は静かに歩き続け、夜の到来を思った。\n\n"
        "雨音だけが残り、明日への願いを胸に抱いて歩いた。\n\n"
        "光が滲み、影が伸び、私は再び立ち止まって考えた。\n\n"
        "匂いが漂い、音が響き、涙が頬を伝い続けていた。\n\n"
        "胸が締め付けられる。それでも私は前に進み続けた。\n\n"
        "冬の朝の光が滲み、私は静かに歩き続けた。\n"
        "> 出典: 第1章 p.1 / 段落1"
    )
    r = verify(text, "ja", SOURCES_PAGED_1)
    emoji_result = next(x for x in r["results"] if x["rule"] == "emoji_count")
    assert emoji_result["warn"] is True
    assert r["status"] == "CONDITIONAL PASS"
    assert "emoji_count" in r["should_failed"]


def test_emoji_4to5_should_fail():
    # 4-5 emojis -> SHOULD fail (conditional)
    text = (
        "## 物語\n### 冬の朝\n"
        "『庭の灯』🌸（灯）🌸🌸🌸ある朝、私は起きた。何かが足りない気がした。\n\n"
        "私は立ち止まって思った。世界のどこかで誰かが考えている。\n\n"
        "時間が止まったように感じた。私は再び歩き始めた。\n\n"
        "別の日、私はまた起きた。何かが足りない気がした。\n\n"
        "光が滲み、音が聞こえ、匂いが漂い、涙が頬を伝った。\n\n"
        "胸が締め付けられる。私は立ち止まり、冬の風を受けた。\n\n"
        "涙が頬を伝う。私は静かに歩き続け、夜を思った。\n\n"
        "雨音だけが残り、明日への願いを胸に抱いて歩いた。\n\n"
        "光が滲み、影が伸び、私は再び立ち止まって考えた。\n\n"
        "匂いが漂い、音が響き、明日への願いが胸に残った。\n\n"
        "それでも私は前に進み続け、冬の朝を歩き続けた。\n\n"
        "夜が更けて雨音だけが残り、私は歩き続けた。\n"
        "> 出典: 第1章 p.1 / 段落1"
    )
    r = verify(text, "ja", SOURCES_PAGED_1)
    emoji_result = next(x for x in r["results"] if x["rule"] == "emoji_count")
    assert emoji_result["value"] == 4
    assert emoji_result["severity"] == "should"
    assert not emoji_result["ok"]
    assert r["status"] == "CONDITIONAL PASS"

def _base_pass_text():
    return "\n\n".join([
        "## 物語\n### 冬の朝\n"
        "『庭の灯』🌸（灯）🌸🌸🌸🌸🌸🌸ある朝、私は起きた。胸に喜びが満ちた。何かが足りない気がした。",
        "私は立ち止まって思った。世界のどこかで誰かが同じことを考えている。",
        "時間が止まったように感じた。私は再び歩き始めた。",
        "別の日、私はまた起きた。何かが足りない気がして、私は立ち止まった。",
        "また別の日、私はまた起きた。何かが足りない気がして、私は歩き続けた。",
        "また別の日、私はまた起きた。何かが足りない気がして、私は立ち止まって思った。",
        "世界は静かに回っている。私はまた歩き始めた。",
        "私は立ち止まって思った。世界のどこかで誰かが同じことを考えている。",
        "時間が止まったように感じた。私は再び歩き始めた。",
        "別の日、私はまた起きた。何かが足りない気がして、私は立ち止まった。",
        "また別の日、私はまた起きた。何かが足りない気がして、私は立ち止まった。",
        "また別の日、私はまた起きた。何かが足りない気がして、私は歩き続けた。",
        "また別の日、私はまた起きた。何かが足りない気がして、私は立ち止まって思った。",
    ]) + "\n> 出典: 第1章 p.1 / 段落1"


def test_two_should_stays_conditional():
    # MUST 0 + SHOULD 2 (emotion missing, emoji 4) -> CONDITIONAL PASS.
    text = _base_pass_text().replace("胸に喜びが満ちた。", "胸が締め付けられた。")
    text = text.replace("🌸🌸🌸🌸🌸🌸", "🌸🌸🌸🌸", 1)
    r = verify(text, "ja", SOURCES_PAGED_1)
    assert r["must_failed"] == []
    assert sorted(r["should_failed"]) == ["emoji_count", "emotion"]
    assert r["status"] == "CONDITIONAL PASS"


def test_three_should_fails():
    # MUST 0 + SHOULD 3 (emotion, emoji, char_count target band) -> FAIL.
    text = _base_pass_text().replace("胸に喜びが満ちた。", "胸が締め付けられた。")
    text = text.replace("🌸🌸🌸🌸🌸🌸", "🌸🌸🌸🌸", 1)
    filler = "\n\n私は再び歩き始めた。私は再び歩き始めた。私は再び歩き始めた。私は再び歩き始めた。"
    text = text.replace("\n> 出典", filler + "\n> 出典")
    r = verify(text, "ja", SOURCES_PAGED_1)
    assert r["must_failed"] == []
    assert sorted(r["should_failed"]) == ["char_count", "emoji_count", "emotion"]
    assert r["status"] == "FAIL"
    assert len(r["should_failed"]) >= 3

if __name__ == "__main__":
    test_no_emoji_must_fail()
    test_senses_must_pass()
    test_emoji_warn_conditional()
    test_emoji_4to5_should_fail()
    test_two_should_stays_conditional()
    test_three_should_fails()
    print("test_verify_should.py: all 6 tests passed")