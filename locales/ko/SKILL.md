---
name: tsumugy-narrative-ko
description: Tsumugy Narrative delta for Korean. Adds Korean authors, brackets, citation, and character window to the canonical rules.
mode: episodic
thread_id: tsumugy-ko
dictionary_path: dictionaries/ko.json
---

# Tsumugy Narrative delta for ko

Common rules live in the canonical skill at SKILL.md (repo root). This file holds only ko differences. When the two disagree, the sections below win for ko.

## Authors, ko extras

Drawn from locales/ko/authors.yaml alongside the common eight:

- 한용운, devotion and resistance in silence
- 박경리, river of land and people
- 황순원, clear sorrow of short tales
- 김유정, comic warmth of village lives

## Voice codebook

Voice line shape: `voice: XX (LABEL)` with the label below. The common eight codes match the canonical skill.

- DO (Fyodor Dostoevsky): 심리소설풍
- LX (Lu Xun): 사회비판풍
- HE (Ernest Hemingway): 간결문체풍
- GM (Gabriel Garcia Marquez): 일상환상풍
- DA (Osamu Dazai): 사소설풍
- KU (Milan Kundera): 수상소설풍
- MA (Naguib Mahfouz): 군상극풍
- MO (Toni Morrison): 기억문학풍
- HY (한용운): 침묵저항풍
- PA (박경리): 대하소설풍
- HW (황순원): 서정단편풍
- KI (김유정): 해학마을풍

## Brackets and citation

Metaphor brackets are 『』 with no sentence ending punctuation inside. Story headings are ## 이야기 and ## 해설. Source marker shape is `> 출처: 제X장 P. Z / 문단N`.

## Count window

ko counts characters. MUST 300 to 600, SHOULD 400 to 500 per story.

## Verification

Run `tools/verify_narrative.py --locale ko`. Verdicts read PASS, CONDITIONAL PASS, FAIL. Details in the canonical Verification section.

## Dictionary

Reference only: dictionaries/ko.json. Do not edit at run time.

## Prohibited Metaphors

Full list lives in the canonical skill. No ko addition.
