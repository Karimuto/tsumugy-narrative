---
name: tsumugy-narrative-fr
description: Tsumugy Narrative delta for French. Adds French authors, brackets, citation, and word window to the canonical rules.
mode: episodic
thread_id: tsumugy-fr
dictionary_path: dictionaries/fr.json
---

# Tsumugy Narrative delta for fr

Common rules live in the canonical skill at SKILL.md (repo root). This file holds only fr differences. When the two disagree, the sections below win for fr.

## Authors, fr extras

Drawn from locales/fr/authors.yaml alongside the common eight:

- Albert Camus, sunlit revolt of the absurd
- Antoine de Saint-Exupéry, flight seen with child eyes
- Marguerite Duras, spare voice of desire
- Patrick Modiano, streets of missing memory

## Voice codebook

Voice line shape: `voice: XX (LABEL)` with the label below. The common eight codes match the canonical skill.

- DO (Fyodor Dostoevsky): roman psychologique
- LX (Lu Xun): critique sociale
- HE (Ernest Hemingway): prose dépouillée
- GM (Gabriel Garcia Marquez): merveilleux quotidien
- DA (Osamu Dazai): confession fragile
- KU (Milan Kundera): roman-essai
- MA (Naguib Mahfouz): polyphonie des rues
- MO (Toni Morrison): roman de la mémoire
- CA (Albert Camus): révolte absurde
- SE (Antoine de Saint-Exupéry): regard d’enfant
- DU (Marguerite Duras): voix du désir
- MD (Patrick Modiano): mémoire manquante

## Brackets and citation

Metaphor brackets are «» with no sentence ending punctuation inside. Story headings are ## Histoire and ## Explication. Source marker shape is `> Source: Chap. X / Par. N`.

## Count window

fr counts words. MUST 50 to 100, SHOULD 67 to 83 per story.

## Verification

Run `tools/verify_narrative.py --locale fr`. Verdicts read PASS, CONDITIONAL PASS, FAIL. Details in the canonical Verification section.

## Dictionary

Reference only: dictionaries/fr.json. Do not edit at run time.

## Prohibited Metaphors

Full list lives in the canonical skill. No fr addition.
