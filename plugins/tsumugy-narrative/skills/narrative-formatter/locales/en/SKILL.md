---
name: tsumugy-narrative-en
description: Tsumugy Narrative delta for English. Adds English authors, brackets, citation, and word window to the canonical rules.
mode: episodic
thread_id: tsumugy-en
dictionary_path: dictionaries/en.json
---

# Tsumugy Narrative delta for en

Common rules live in the canonical skill at SKILL.md (repo root). This file holds only en differences. When the two disagree, the sections below win for en.

## Authors, en extras

Drawn from locales/en/authors.yaml alongside the common eight:

- Virginia Woolf, waves of inner time
- Ursula K. Le Guin, thought carried without ballast
- Kurt Vonnegut, plain absurd compassion
- Franz Kafka, precise bureaucratic dread

## Voice codebook

Common eight codes and English shelf labels live in the canonical skill. Locale extras:

- WO (Virginia Woolf): stream-of-consciousness style
- LG (Ursula K. Le Guin): speculative-thought style
- VO (Kurt Vonnegut): dark-comic style
- KA (Franz Kafka): bureaucratic-dread style

## Brackets and citation

Metaphor brackets are ⟨⟩ with no sentence ending punctuation inside. Story headings are ## Story and ## Notes. Source marker shape is `> Source: Ch. X P. Z / Para. N`.

## Count window

en counts words. MUST 50 to 100, SHOULD 67 to 83 per story.

## Verification

Run `tools/verify_narrative.py --locale en`. Verdicts read PASS, CONDITIONAL PASS, FAIL. Details in the canonical Verification section.

## Dictionary

Reference only: dictionaries/en.json. Do not edit at run time.

## Prohibited Metaphors

Full list lives in the canonical skill. No en addition.
