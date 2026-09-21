---
name: tsumugy-narrative-ja
description: Tsumugy Narrative日本語差分。正本の共通規則に日本語の作家と括弧と出典と文字数を足す。
mode: episodic
thread_id: tsumugy-ja
dictionary_path: dictionaries/ja.json
---

# Tsumugy Narrative delta for ja

Common rules live in the canonical skill at SKILL.md (repo root). This file holds only ja differences. When the two disagree, the sections below win for ja.

## Authors, ja extras

Drawn from locales/ja/authors.yaml alongside the common eight:

- 川端康成, 雪と沈黙の美しさ
- 芥川龍之介, 一閃と残る疑い
- 吉本ばなな, 温かく発光する悲しみ
- 村上春樹, 日常の街に滑り込む夢

## Voice codebook

Voice line shape: `voice: XX (LABEL)` with the label below. The common eight codes match the canonical skill.

- DO (Fyodor Dostoevsky): 心理小説風
- LX (Lu Xun): 社会批評風
- HE (Ernest Hemingway): 簡潔文体風
- GM (Gabriel Garcia Marquez): 日常幻想風
- DA (Osamu Dazai): 私小説風
- KU (Milan Kundera): 随想小説風
- MA (Naguib Mahfouz): 群像劇風
- MO (Toni Morrison): 記憶文学風
- KA (川端康成): 抒情美文風
- AK (芥川龍之介): 短編綺譚風
- YO (吉本ばなな): 温情小説風
- MU (村上春樹): 都市幻想風

## Brackets and citation

Metaphor brackets are 『』 with no sentence ending punctuation inside. Story headings are ## 物語 and ## 解説. Source marker shape is `> 出典：第X章 p.Z / 段落N`, or `> 出典：お題 p.Z / 段落N` when the input has no chapter. Halfwidth colon and spacing differences pass, page is required, bracket forms fail, chapter titles inside markers fail. Pass the source index with --source-index; every marker must match an entry or the story fails.

## Count window

ja counts characters. MUST 300 to 600, SHOULD 400 to 500 per story.

## Verification

Run `tools/verify_narrative.py --locale ja --source-index index.json`. Verdicts read PASS, CONDITIONAL PASS, FAIL. Details in the canonical Verification section.

## Dictionary

Reference only: dictionaries/ja.json. Do not edit at run time.

## Prohibited Metaphors

Full list lives in the canonical skill. No ja addition.
