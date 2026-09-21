---
name: tsumugy-narrative-ru
description: Tsumugy Narrative delta for Russian. Adds Russian authors, brackets, citation, and word window to the canonical rules.
mode: episodic
thread_id: tsumugy-ru
dictionary_path: dictionaries/ru.json
---

# Tsumugy Narrative delta for ru

Common rules live in the canonical skill at SKILL.md (repo root). This file holds only ru differences. When the two disagree, the sections below win for ru.

## Authors, ru extras

Drawn from locales/ru/authors.yaml alongside the common eight:

- Leo Tolstoy, vast moral panoramas
- Anton Chekhov, quiet unspoken undercurrents
- Mikhail Bulgakov, devilry inside the everyday
- Boris Pasternak, verse pressed into prose

## Voice codebook

Voice line shape: `voice: XX (LABEL)` with the label below. The common eight codes match the canonical skill.

- DO (Fyodor Dostoevsky): психологический роман
- LX (Lu Xun): социальная критика
- HE (Ernest Hemingway): скупая проза
- GM (Gabriel Garcia Marquez): чудесное в обыденном
- DA (Osamu Dazai): хрупкая исповедь
- KU (Milan Kundera): роман-эссе
- MA (Naguib Mahfouz): многоголосие улиц
- MO (Toni Morrison): роман памяти
- TO (Leo Tolstoy): нравственная панорама
- CH (Anton Chekhov): тихий подтекст
- BU (Mikhail Bulgakov): чертовщина в быту
- PA (Boris Pasternak): проза в стихах

## Brackets and citation

Metaphor brackets are «» with no sentence ending punctuation inside. Story headings are ## История and ## Пояснение. Source marker shape is `> Источник: Гл. X / Абз. N`.

## Count window

ru counts words. MUST 50 to 100, SHOULD 67 to 83 per story.

## Verification

Run `tools/verify_narrative.py --locale ru`. Verdicts read PASS, CONDITIONAL PASS, FAIL. Details in the canonical Verification section.

## Dictionary

Reference only: dictionaries/ru.json. Do not edit at run time.

## Prohibited Metaphors

Full list lives in the canonical skill. No ru addition.
