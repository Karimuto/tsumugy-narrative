---
name: narrative-formatter
description: Transform dense textbook passages into memorable stories with metaphors and source markers. Use when the user wants to memorize with stories.
---

# Narrative Formatter

Turn textbook passages into stories that stick in memory. Each story keeps a visible link to the exact passage it came from, so readers can always trace back.

## Story unit

One story fills one story block. A block holds four parts in order:

1. Literary title line, third level heading. Give it a novel chapter feel, not a dry label.
2. Story body, 300 to 600 characters for ja zh ko with 400 to 500 as the target band, 50 to 100 words for other locales with 67 to 83 as the target band. Write scenes with people doing and feeling things, not diagrams. Favor one striking slice over full coverage.
3. Explanation, one or two sentences: state the mechanism or structure the story depicts, then map the key metaphors back to the textbook concepts.
4. Source marker, blockquote line pointing at chapter, page, paragraph.

Story headings differ per locale. Legacy ## 物語 is accepted in every locale:

- ja: ## 物語 / ## 解説, marker is > 出典：第X章 p.Z / 段落N
- en: ## Story / ## Notes, marker is > Source: Ch. X P. Z / Para. N
- zh: ## 故事 / ## 讲解, marker is > 出处：第X章 P. Z / 段落N
- ko: ## 이야기 / ## 해설, marker is > 출처: 제X장 P. Z / 문단N
- ar: ## قصة / ## شرح, marker is > المصدر: الفصل X / فقرة N
- es: ## Historia / ## Explicación, marker is > Fuente: Cap. X / Párr. N
- fr: ## Histoire / ## Explication, marker is > Source: Chap. X / Par. N
- ru: ## История / ## Пояснение, marker is > Источник: Гл. X / Абз. N

Repeat the block once per passage. Never write meta words inside the story body such as story, summary, visualAid. Never print author names in the output.

## Modes

Output shape stays the same in all modes. Only the way stories get made differs. Internal keys are episodic, serial, fable. Default is fable. A plain language request beats runtime frontmatter, runtime frontmatter beats the default. The top frontmatter holds only name and description, runtime values such as mode live in this section. Write in the language of the input text unless the request names another locale.

### Episodic

Stay faithful to the text. Give each passage its own world, cast, and metaphor. Each story stands alone, so readers may start anywhere.

Flow: read passage, pull out the core concept, build a standalone metaphor world, write the story, spell out the mapping in the explanation.

### Serial

Keep one protagonist and one world across episodes, like chapters of a novel. Start each new story where the last one ended.

Flow: read the stored tail plus ledger, fold the new passage concept into the same world, continue the story, note growth or change in the explanation.
Output follows the story unit exactly: title, body with bracket metaphors and one emoji per character and object, explanation, source marker. Never emit YAML frontmatter, thread metadata, or author names in the output; thread state lives only in serial_store files.

Memory: this mode alone keeps state. Pass thread_id in frontmatter. Read state with tools/serial_store.py --read --thread-id ID. Save with tools/serial_store.py --append --thread-id ID --episode-md PATH --ledger-update JSON. Episodes live under ~/.tsumugy/serial/ID as epN.md plus ledger.md plus meta.json.

### Fable

Favor impression over fidelity. Drift from the source and bend details when it makes the story hit harder, tolerating some inaccuracy for memorability. Episodic chases clarity and stays faithful, fable chases force and stays memorable. That tradeoff is the point.

Flow: pull out the essence, build a loose story world, let the story carry 80 percent of the weight, close the story body with one line that reads as the moral of the story, then re-read that closing line and confirm it lands as the lesson before delivering. Keep the explanation to one light line without the moral.

## Authors

Default voice blends eight authors. Do not imitate one author per story by default. For each story, draw two authors at random from the twelve below, then write with the one that fits the topic better. Draw the two with tools/pick_authors.py --locale <locale> [--seed N] (episodic: redraw per story; serial: draw once for the first episode and keep it for the whole thread); the verifier never checks randomness. In serial mode, keep the first episode author for the whole thread and note the real-name choice in the ledger (internal record, never shown in output).

Common eight, all locales (voice code in brackets):

- Fyodor Dostoevsky [DO], inner turmoil and moral pressure
- Lu Xun [LX], sharp gaze at society through small lives
- Ernest Hemingway [HE], plain surface with weight below
- Gabriel Garcia Marquez [GM], wonder treated as everyday fact
- Osamu Dazai [DA], fragile first person honesty
- Milan Kundera [KU], playful thought inside the scene
- Naguib Mahfouz [MA], crowded street polyphony
- Toni Morrison [MO], memory carried in body and place

Four more per locale live in the locale delta file, same one line each with their own voice codes.

Voice line: after the source marker of each story, add one small line `voice: XX (shelf label)` where XX is the chosen author code and the shelf label comes from the codebook below (or the locale delta override). The shelf label is a generic genre hint, never a real author name. This line is the persistent per-story author record, for episodic stories too. Never print real author names in the output.

Common codebook (English shelf labels; locale deltas override all twelve in their own language):

- DO: psychological-novel style
- LX: social-critique style
- HE: spare-prose style
- GM: marvellous-everyday style
- DA: fragile-confession style
- KU: playful-thought style
- MA: crowded-street style
- MO: embodied-memory style

## Metaphors

Mark every hard concept with a metaphor right after the concept, wrapped in the locale brackets below. Inside the brackets, never place sentence ending punctuation. Enough metaphors means a high school reader can follow without stopping.

- ja ko: 『』
- zh: 《》
- en: ⟨⟩
- ar es fr ru: «»

Give each character and object exactly one emoji, used every time it appears. Pick the emoji to match the bracketed metaphor, never the parenthesized textbook term. On first use, map metaphor to textbook term in the shape metaphor emoji (term), for example 一筋の矢🎯(イマチニブ). Aim the cast at absurd, funny, eerie, or ironic for strong memory hooks.

## Emoji Anchors

Each anchor stays tied to the bracketed metaphor it stands for. Prefer concrete things over abstract marks, so the picture recalls the meaning on its own. Abstract ideas take concrete object emoji, never abstract symbols. Reuse is covered under Metaphors: one anchor per character and object, every appearance.

## Prohibited Metaphors

Never use these mappings, each with its reason:

- 量子は意志: treats science like religion, turning physics into mysticism
- 宇宙は意識: same as above, dressing cosmology as religion
- 教育は工場: risks turning politically extreme
- 子どもは粘土: risks hurting specific people by denying agency
- 子どもは白紙: same as above, ignoring heredity and environment

## Boundary Metaphors

Use only with a condition that keeps them honest, each with its reason and use condition:

- 心は鏡: hard to grasp as a metaphor, obscures active construction. Use only when the story explicitly shows the mind actively building alongside reflecting.
- 老化は衰退: risks hurting specific people with negative framing. Use only when the story also shows diversity and non-decline aspects of aging.

## Verification

Run tools/verify_narrative.py --locale LOCALE with --text or --input after drafting, always with --source-index pointing at the kind-tagged source index JSON, or with sources inside --input. Verdicts read PASS, CONDITIONAL PASS, FAIL. Exit codes are 0, 1, 2 in the same order. Any MUST failure gives FAIL. With no MUST failure, 3 or more SHOULD warnings give FAIL, 1 or 2 give CONDITIONAL PASS, none gives PASS. Rules run per story, except language ratio, frontmatter presence, and story heading presence which run per file. must_failed names the failing rules, should_failed names warnings. Fix what must_failed or should_failed names on FAIL, then run again. Deliver output only on PASS or CONDITIONAL PASS.

Source markers name real input positions, never plausible ones. Every marker must match an entry in the source index or the story fails. Three kinds: paged for page numbered material with chapter or label plus page and paragraph, transcript for transcribed material with label plus ref matched exactly, sectioned for section numbered documents with dotted section plus optional label. Every locale checks existence against the index with its own grammar. Page is required in ja en zh ko and optional in ar es fr ru, where a present page still must match. Bracket forms never count as markers.

Must rules, one bullet per check:

- Length hard window: char count in the hard window of 300 to 600 characters for ja zh ko or 50 to 100 words for other locales (MUST)
- Metaphor brackets: no sentence ending punctuation inside metaphor brackets (MUST)
- Source marker: source marker matching the source index per story (MUST)
- Language ratio: language ratio at least 0.9 (MUST)
- Emoji count: emoji count at least 4 with 6 to 10 sweet and above 10 warned counted as visible sequences where one shown emoji is one (MUST)
- Senses: senses from at least 2 of sight sound smell taste touch using the locale dictionary (MUST)
- Line density hard window: line-break density average inside 20 to 200 chars per line for ja zh ko or 4 to 33 words per line for other locales counted over narrative lines between the title line and the explanation heading excluding headings and the source marker and empty lines (MUST)
- First-use mapping: first-use metaphor mapping as a 3-point set of bracketed metaphor plus anchor emoji plus textbook term in full or half width parens with reuse by anchor emoji only (MUST)
- Paragraph break: story-body paragraphs divided by a blank line with no two consecutive non-empty lines between the title line and the explanation heading (MUST)
- Output shape: no YAML frontmatter block or thread metadata key line anywhere in the output (MUST)
- Title line: one literary title line per story opening its story block (MUST)
- Author attribution: no real author names anywhere except inside voice lines which carry no verification (MUST)

Should rules, one bullet per check:

- Emotion: emotion signal from the emotion lists in the locale dictionary, counting only words that appear there and never words shared with the senses lists. A story with no such word warns and counts toward the SHOULD tally, so give every story at least one moment of human feeling (SHOULD)
- Length target band: char count outside the target band of 400 to 500 characters for ja zh ko or 67 to 83 words for other locales warns (SHOULD)
- Density target band: line-break density outside 20 to 100 chars per line for ja zh ko or 4 to 16 words per line for other locales warns (SHOULD)
- Literary override: when literary effect outweighs cognitive load, leave the passage as is to maximize learning effect (SHOULD)

## Dictionary

Read only. Senses and emotion words come from dictionaries/LOCALE.json at run time. Default dictionary is dictionaries/en.json, locale deltas point at their own file. Never paste word lists here. Background notes live in dictionaries/_about.md.

## Chain of thought

1. Pull out the core concepts, terms, relations, mechanisms from the source.
2. Turn them into a concrete scene with feeling actors, not a chart.
3. Wrap hard concepts in locale bracket metaphors, no ending punctuation inside.
4. Fix one Emoji anchor per character and object, map metaphor emoji (term) on first use.
5. Take the assigned author voice for tone and pace.
6. Draft the story plus explanation plus source marker, then verify, then fix failures.
7. Check the Emoji anchors against four checks: count in the 6 to 10 window, concrete object for each anchor, direct tie to the bracketed metaphor, same anchor reused for the same character and object. Rewrite on any miss before finalizing.
8. For fable stories only, re-read the closing line and confirm it reads as the moral of the story. Rewrite on any miss before finalizing.
