"""
tests/test_verify_line_breaks.py
Line-break density rule (ADR-0008, issue #7): per-story average chars/line
(ja/zh/ko) or words/line (other locales) over content lines, excluding the
source-marker line and empty lines. SHOULD band 20-100 chars (4-16 words),
MUST cap above 300 chars (50 words), no MUST lower bound.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from verify_narrative import verify

MARKER = "> 出典：第1章 p.1 / 段落1"

SOURCES_PAGED_1 = {"kind": "paged", "entries": [{"chapter": 1, "page": 1, "para": 1}]}

def _doc(body: str) -> str:
    return "## 物語\n### 長屋の朝\n" + body + "\n" + MARKER


# ~44 chars/line over 10 lines: mirrors the accepted 夕立 example.
MID_BAND_BODY = "\n\n".join([
    "『庭の灯』🌸（灯）🌸🌸🌸🌸🌸夕立が長屋の路地を叩く夕方、光が水たまりに揺れていた。",
    "米屋の親父は赤い大傘をぐっと広げ、音が雨に混ざって響いた。",
    "咳き込む職人の肩を傘の下に入れ、冷えた背中をさすって温めた。",
    "赤子を抱く母の頭上にも骨を伸ばし、湯気の匂いがふわりと立った。",
    "白髪の老婆の冷たい手を両手で包み、握り飯をそっと届けた。",
    "死んだ大工の遺族には白い飯をよそい、温かい茶を飲ませた。",
    "職を失った若者に笑って声をかけ、胸に喜びが満ちていった。",
    "米俵は余る家から足りぬ家へ運べばいいのさと親父は笑った。",
    "町の医者が職人の傷を洗い、赤い夕日が屋根を照らしていた。",
    "濡れた石畳の上で皆の影が一つに重なり、誰かが小さく笑った。",
    "軒下では猫が丸くなり、湯気の向こうで主人が静かに笑っていた。",
    "濡れた暖簾をくぐると、出汁の匂いと低い笑い声があふれていた。",
    "雨上がりの空に薄く光が差し、皆の肩の力が抜けていった。",
])

# ~35 chars/line over 12 lines: mirrors the accepted 井戸端 example.
SHORT_LINE_BODY = "\n\n".join([
    "長屋の井戸端で老婆が転んで皆が駆け寄った。",
    "悲鳴より先に、財布を数える指が震えていた。",
    "隣の職人は咳をこらえ、朝の光が差し込んだ。",
    "妊婦は腹を抱えて立ち尽くし、遠くの音を聞いた。",
    "大工は仕事が途切れ、空の弁当箱をただ眺めた。",
    "そこへ八百屋の主人が大傘を広げ、匂いが立った。",
    "米俵から白い飯が茶碗によそわれ、湯気がのぼった。",
    "赤い夕日が屋根を照らし、子どもらが笑い声を上げた。",
    "老婆の冷たい手が茶碗に触れたとき、震えが止まった。",
    "主人は明日は我が身だよと笑いかけて座った。",
    "妊婦は湯呑みの温もりにそっと目を細めていた。",
    "胸に喜びが満ちて、『庭の灯』🌸（灯）🌸🌸🌸🌸🌸灯りが一つずつともった。",
    "井戸の水面に光が揺れ、朝の訪れを告げる音が静かに広がった。",
    "隣の子が笑い、湯飲みの温もりが冷えた手にじんわり伝わった。",
    "赤い夕日が沈み、帰り道に小さな灯りが一つまた一つともった。",
])
# ~215 chars/line over 2 lines: mirrors the accepted ハル example.
# Dense but deliverable -> CONDITIONAL PASS via SHOULD, never MUST.
DENSE_BODY = "\n\n".join([
    "『庭の灯』🌸（灯）🌸🌸ハルは緑の工房の朝番を任されている。天井に張られた緑の天幕が、昇りたての太陽の日差しを一身に受け止める。光が天幕に触れた途端、温かい痺れが床から壁へと駆け抜け、隅の影まで緑が濃くなった。工房じゅうが一斉に目を覚ましたようだ。",
    "ハルは桶から水を汲み、天幕の下へそっと注ぐ。天幕は光の力で水を割り、軽い泡がぷかりと浮かんで天窓から空へ逃げていく。その小さな音を耳に残しながら、残された欠片と大気の粉を釜で煮詰める。釜は低い唸りを上げ、煮汁はだんだんとろみを帯びてくる。指先ですくって舐めると、ほのかに甘い蜜の味がして、湯気の匂いが立ちのぼった。外には青い匂いが立ち、胸に喜びが満ちて、今日も工房は腹いっぱいだ🌸🌸🌸と胸の奥が温かくなった。",
])

# 400 chars on a single content line: the wall the MUST cap exists for.
WALL_BODY = (
    "🌸🌸🌸🌸🌸🌸冬の朝を歩いていた。影が長く伸び、通りには微かな光が滲んでいた。"
    "光が滲み、音が聞こえ、匂いが漂い、涙が頬を伝い、胸が締め付けられる。"
    "私は立ち尽くしていた。音が聞こえ、光が滲み、匂いが漂い、涙が頬を伝い、"
    "胸が締め付けられる。私は立ち尽くしていた。音が聞こえ、光が滲み、匂いが漂い、"
    "涙が頬を伝い、胸が締め付けられる。私は静かに歩き続けた。音が聞こえ、匂いが漂い、"
    "光が滲み、涙が頬を伝い、胸が締め付けられる。胸に喜びが満ちた。私は静かに歩き続けた。"
    "冬の風が頬を撫で、遠くで鐘の音が響き、空が白み始めていた。今日も一日が始まる。凍てつく道端の水たまりには薄氷が張り、吐く息が白く立ちのぼって朝日の中で静かにほどけていった。私は両手をこすり合わせ、今日という日の温もりを探しながら一歩ずつ前に進んでいった。"
)


def _density(results):
    return next(x for x in results if x["rule"] == "line_break_density")


def test_mid_band_passes():
    r = verify(_doc(MID_BAND_BODY), "ja", SOURCES_PAGED_1)
    d = _density(r["results"])
    assert d["ok"] is True, f"mid-band density should pass: {d}"
    assert r["status"] == "PASS", f"expected pass, got {r['status']}: {r.get('must_failed')} {r.get('should_failed')}"


def test_short_lines_pass():
    r = verify(_doc(SHORT_LINE_BODY), "ja", SOURCES_PAGED_1)
    d = _density(r["results"])
    assert d["ok"] is True, f"short-line density should pass: {d}"
    assert r["status"] == "PASS", f"expected pass, got {r['status']}: {r.get('must_failed')} {r.get('should_failed')}"


def test_dense_body_warns_but_passes_conditionally():
    r = verify(_doc(DENSE_BODY), "ja", SOURCES_PAGED_1)
    d = _density(r["results"])
    assert d["severity"] == "should", f"dense body must be SHOULD, not MUST: {d}"
    assert d["ok"] is False
    assert "文学的効果" in d.get("note", ""), f"SHOULD note must carry the literary override: {d}"
    assert "line_break_density" in r["should_failed"]
    assert r["must_failed"] == [], f"dense body must not fail MUST: {r['must_failed']}"
    assert r["status"] == "CONDITIONAL PASS"


def test_wall_of_text_fails_must():
    r = verify(WALL_BODY + "\n" + MARKER, "ja")
    d = _density(r["results"])
    assert d["severity"] == "must", f"wall body must be MUST: {d}"
    assert d["ok"] is False
    assert "line_break_density" in r["must_failed"]
    assert r["status"] == "FAIL"


def test_marker_and_blank_lines_excluded():
    padded = "\n\n" + _doc(MID_BAND_BODY).replace("\n", "\n\n") + "\n"
    r_plain = verify(_doc(MID_BAND_BODY), "ja", SOURCES_PAGED_1)
    r_padded = verify(padded, "ja", SOURCES_PAGED_1)
    assert _density(r_padded["results"])["value"] == _density(r_plain["results"])["value"]
    assert r_padded["status"] == "PASS"


def test_english_counts_words_not_chars():
    # 6 long words/line: ~200 chars/line would MUST-fail on char units,
    # but passes on the specified word units (SHOULD band 4-16 words/line).
    word = "supercalifragilisticexpialidocious"
    lines = [" ".join([word] * 6) for _ in range(28)]
    lines[0] = "🌟🌟🌟🌟🌟🌟 light sound " + lines[0]
    lines[-1] = lines[-1] + " joy"
    text = "\n".join(lines) + "\n> Source: Ch. 1 P. 1 / Para. 1"
    r = verify(text, "en")
    d = _density(r["results"])
    assert d["ok"] is True, f"word-unit density should pass: {d}"
    assert "line_break_density" not in r["must_failed"]


if __name__ == "__main__":
    test_mid_band_passes()
    test_short_lines_pass()
    test_dense_body_warns_but_passes_conditionally()
    test_wall_of_text_fails_must()
    test_marker_and_blank_lines_excluded()
    test_english_counts_words_not_chars()
    print("test_verify_line_breaks.py: all 6 tests passed")
