---
name: tsumugy-narrative-es
description: Tsumugy Narrative delta for Spanish. Adds Spanish authors, brackets, citation, and word window to the canonical rules.
mode: episodic
thread_id: tsumugy-es
dictionary_path: dictionaries/es.json
---

# Tsumugy Narrative delta for es

Common rules live in the canonical skill at SKILL.md (repo root). This file holds only es differences. When the two disagree, the sections below win for es.

## Authors, es extras

Drawn from locales/es/authors.yaml alongside the common eight:

- Jorge Luis Borges, precise libraries of infinity
- Isabel Allende, spirits inside the household
- Javier Marías, slow sentences of doubt
- Julio Cortázar, play as metaphysics

## Voice codebook

Voice line shape: `voice: XX (LABEL)` with the label below. The common eight codes match the canonical skill.

- DO (Fyodor Dostoevsky): novela psicológica
- LX (Lu Xun): crítica social
- HE (Ernest Hemingway): prosa escueta
- GM (Gabriel Garcia Marquez): maravilla cotidiana
- DA (Osamu Dazai): confesión frágil
- KU (Milan Kundera): novela-ensayo
- MA (Naguib Mahfouz): polifonía callejera
- MO (Toni Morrison): novela de la memoria
- BO (Jorge Luis Borges): laberinto infinito
- AL (Isabel Allende): espíritus domésticos
- JM (Javier Marías): frases de la duda
- CO (Julio Cortázar): juego metafísico

## Brackets and citation

Metaphor brackets are «» with no sentence ending punctuation inside. Story headings are ## Historia and ## Explicación. Source marker shape is `> Fuente: Cap. X / Párr. N`.

## Count window

es counts words. MUST 50 to 100, SHOULD 67 to 83 per story.

## Verification

Run `tools/verify_narrative.py --locale es`. Verdicts read PASS, CONDITIONAL PASS, FAIL. Details in the canonical Verification section.

## Dictionary

Reference only: dictionaries/es.json. Do not edit at run time.

## Prohibited Metaphors

Full list lives in the canonical skill. No es addition.
