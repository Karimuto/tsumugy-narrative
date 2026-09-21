"""
tests/test_verify_emotion.py
TDD for issue #4 (brief v2): the verifier must score emotion presence
per story. Distinct emotion-dictionary words (excluding words shared
with any sense category) pass; absence is a SHOULD failure
(CONDITIONAL PASS), never a MUST failure.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from verify_narrative import check_emotion, verify


def _story(body: str) -> str:
    return "## 物語\n### 小さな朝\n" + body + "\n> 出典: 第1章 p.1 / 段落1"

SOURCES_PAGED_1 = {"kind": "paged", "entries": [{"chapter": 1, "page": 1, "para": 1}]}


# Senses-rich but emotion-free: every content word verified against
# dictionaries/ja.json to carry no distinct emotion signal.
# One segment per line keeps line-break density in the PASS band so
# these tests pin emotion behavior only.
EMOTION_FREE_BODY = "\n\n".join([
    "『庭の灯』🌸（灯）🌸🌸🌸🌸🌸光が差し影が伸びた。色と形が線を描き、音と声が響き渡る。",
    "光が差し影が伸びた。色と形が線を描き、音と声が響き渡る。",
    "光が差し影が伸びた。色と形が線を描き、音と声が響き渡る。",
    "光が差し影が伸びた。色と形が線を描き、音と声が響き渡る。",
    "光が差し影が伸びた。色と形が線を描き、音と声が響き渡る。",
    "光が差し影が伸びた。色と形が線を描き、音と声が響き渡る。",
    "光が差し影が伸びた。色と形が線を描き、音と声が響き渡る。",
    "光が差し影が伸びた。色と形が線を描き、音と声が響き渡る。",
    "光が差し影が伸びた。色と形が線を描き、音と声が響き渡る。",
    "光が差し影が伸びた。色と形が線を描き、音と声が響き渡る。",
    "光が差し影が伸びた。色と形が線を描き、音と声が響き渡る。",
    "光が差し影が伸びた。色と形が線を描き、音と声が響き渡る。",
    "光が差し影が伸びた。色と形が線を描き、音と声が響き渡る。",
])


def test_emotion_present_passes():
    r = check_emotion("胸に喜びが満ちた。光が差した。", "ja")
    assert r["rule"] == "emotion"
    assert r["ok"] is True


def test_emotion_absent_should_fails():
    r = check_emotion(EMOTION_FREE_BODY, "ja")
    assert r["rule"] == "emotion"
    assert r["ok"] is False
    assert r["severity"] == "should"


def test_emotion_shared_words_do_not_count():
    # 光 and 影 live in both sense and emotion lists; alone they
    # must not satisfy the emotion rule.
    r = check_emotion("光が差し影が伸びた。", "ja")
    assert r["ok"] is False
    assert r["severity"] == "should"


def test_emotion_missing_dict_must_fails():
    r = check_emotion("喜びが満ちた。", "xx")
    assert r["severity"] == "must"
    assert r["ok"] is False


def test_emotion_absent_story_is_conditional():
    r = verify(_story(EMOTION_FREE_BODY), "ja", SOURCES_PAGED_1)
    assert r["status"] == "CONDITIONAL PASS", (
        f"expected conditional, got {r['status']}: {r.get('must_failed')} {r.get('should_failed')}"
    )
    assert r["should_failed"] == ["emotion"]
    assert r["must_failed"] == []


def test_emotion_present_story_passes():
    body = EMOTION_FREE_BODY + "胸に喜びが満ちた。"
    r = verify(_story(body), "ja", SOURCES_PAGED_1)
    assert r["status"] == "PASS", (
        f"expected pass, got {r['status']}: {r.get('must_failed')} {r.get('should_failed')}"
    )


if __name__ == "__main__":
    test_emotion_present_passes()
    test_emotion_absent_should_fails()
    test_emotion_shared_words_do_not_count()
    test_emotion_missing_dict_must_fails()
    test_emotion_absent_story_is_conditional()
    test_emotion_present_story_passes()
    print("test_verify_emotion.py: all 6 tests passed")
