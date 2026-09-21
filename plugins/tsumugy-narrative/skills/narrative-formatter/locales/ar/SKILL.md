---
name: tsumugy-narrative-ar
description: Tsumugy Narrative delta for Arabic. Adds Arabic authors, brackets, citation, and word window to the canonical rules.
mode: episodic
thread_id: tsumugy-ar
dictionary_path: dictionaries/ar.json
---

# Tsumugy Narrative delta for ar

Common rules live in the canonical skill at SKILL.md (repo root). This file holds only ar differences. When the two disagree, the sections below win for ar.

## Authors, ar extras

Drawn from locales/ar/authors.yaml alongside the common eight:

- طه حسين, blind insight into heritage
- غسان كنفاني, witness of displacement
- محمود درويش, homeland carried in verse
- جبران خليل جبران, prophet of love and work

## Voice codebook

Voice line shape: `voice: XX (LABEL)` with the label below. The common eight codes match the canonical skill.

- DO (Fyodor Dostoevsky): رواية نفسية
- LX (Lu Xun): نقد اجتماعي
- HE (Ernest Hemingway): نثر مقتضب
- GM (Gabriel Garcia Marquez): عجائبي يومي
- DA (Osamu Dazai): اعتراف هش
- KU (Milan Kundera): رواية-مقالة
- MA (Naguib Mahfouz): تعدد أصوات الشارع
- MO (Toni Morrison): رواية الذاكرة
- TH (طه حسين): بصيرة التراث
- GH (غسان كنفاني): شهادة الشتات
- MD (محمود درويش): وطن في الشعر
- GI (جبران خليل جبران): نبي الحب والعمل

## Brackets and citation

Metaphor brackets are «» with no sentence ending punctuation inside. Story headings are ## قصة and ## شرح. Source marker shape is `> المصدر: الفصل X / فقرة N`.

## Count window

ar counts words. MUST 50 to 100, SHOULD 67 to 83 per story.

## Verification

Run `tools/verify_narrative.py --locale ar`. Verdicts read PASS, CONDITIONAL PASS, FAIL. Details in the canonical Verification section.

## Dictionary

Reference only: dictionaries/ar.json. Do not edit at run time.

## Prohibited Metaphors

Full list lives in the canonical skill. No ar addition.
