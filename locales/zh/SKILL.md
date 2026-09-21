---
name: tsumugy-narrative-zh
description: Tsumugy Narrative delta for Chinese. Adds Chinese authors, brackets, citation, and character window to the canonical rules.
mode: episodic
thread_id: tsumugy-zh
dictionary_path: dictionaries/zh.json
---

# Tsumugy Narrative delta for zh

Common rules live in the canonical skill at SKILL.md (repo root). This file holds only zh differences. When the two disagree, the sections below win for zh.

## Authors, zh extras

Drawn from locales/zh/authors.yaml alongside the common eight:

- 老舍, Beijing street compassion
- 莫言, hallucinated harvest land
- 余華, plain endurance through suffering
- 巴金, family torrent and dawn

## Voice codebook

Voice line shape: `voice: XX (LABEL)` with the label below. The common eight codes match the canonical skill.

- DO (Fyodor Dostoevsky): 心理小说风
- LX (Lu Xun): 社会批判风
- HE (Ernest Hemingway): 简练文体风
- GM (Gabriel Garcia Marquez): 日常幻实风
- DA (Osamu Dazai): 私小说风
- KU (Milan Kundera): 随笔小说风
- MA (Naguib Mahfouz): 群像街区风
- MO (Toni Morrison): 记忆文学风
- LS (老舍): 京味街头风
- MY (莫言): 幻觉乡土风
- YH (余華): 苦难忍耐风
- BJ (巴金): 家族激流风

## Brackets and citation

Metaphor brackets are 《》 with no sentence ending punctuation inside. Story headings are ## 故事 and ## 讲解. Source marker shape is `> 出处：第X章 P. Z / 段落N`.

## Count window

zh counts characters. MUST 300 to 600, SHOULD 400 to 500 per story.

## Verification

Run `tools/verify_narrative.py --locale zh`. Verdicts read PASS, CONDITIONAL PASS, FAIL. Details in the canonical Verification section.

## Dictionary

Reference only: dictionaries/zh.json. Do not edit at run time.

## Prohibited Metaphors

Full list lives in the canonical skill. No zh addition.
