# Tsumugy-Narrative

Textbook passages transformed into memorable stories that preserve traceability to their sources.

## Language

**Episodic**:
Independent one-shot story per passage, no memory carried between stories.
_Avoid_: braided, one-shot (ambiguous), standalone

**Serial**:
Continuing story in one world with one protagonist across episodes, memory carried forward.
_Avoid_: continuous, series

**Fable**:
Impression-first free story that may drift from the source text to maximise memorability.
_Avoid_: aesopian, moral tale,寓話 (as internal key)

**Story**:
One verifiable narrative unit: a story body plus its explanation plus its source marker.
_Avoid_: visualAid (legacy), episode (serial-only), block, sample

**Source marker**:
The citation line tying a story to its textbook origin (chapter, page, paragraph).
Every marker must match an entry in the source index.
_Avoid_: citation,出典マーカー (as code term), Source tag

**Source index**:
The kind-tagged list of real source positions markers are checked against: paged, transcript, sectioned.
_Avoid_: source list, reference file

**Prohibited metaphor**:
A metaphor mapping banned in all modes for inaccuracy or harm.
_Avoid_: NG (loose), banned list

**Boundary metaphor**:
A metaphor allowed only with conditions, separated from prohibited ones.
_Avoid_: conditional NG, gray list

**Emoji anchor**:
The single emoji fixed to one character or object, reused on every appearance.
_Avoid_: emoji mapping, 絵文字対応

**First-use mapping**:
The 3-point set on a metaphor first appearance: bracketed metaphor plus anchor emoji plus textbook term in parens, reused by anchor emoji only.
_Avoid_: term gloss, 用語注

**Thread**:
One serial continuity: ordered episodes plus their accumulated ledger.
_Avoid_: thread_id (the identifier, not the thing), session, chain

**Ledger**:
Accumulated character and world state for a thread, updated per episode.
_Avoid_: memory, history, Character/World Ledger (as separate things)

**Verification status**:
Per-story verdict. PASS, CONDITIONAL PASS, or FAIL.
_Avoid_: pass/fail lowercase (code-internal only), must OK / should OK, retry/escalate

**Author voice**:
The style borrowed at generation time, picked per story by the pick-2 draw.
_Avoid_: author name (the person, not the voice), attribution

**Author attribution**:
A real author name shown in the output, claiming or implying authorship.
_Avoid_: voice code, shelf label, record

**Author record**:
The internal note of which author voice was chosen (serial ledger, voice line code).
_Avoid_: attribution, source marker

**Voice code**:
The two-letter code identifying the chosen author voice, decodable only with the SKILL codebooks.
_Avoid_: author name, shelf label

**Shelf label**:
The generic genre hint shown beside the voice code, identifying no real person.
_Avoid_: author name, attribution

**Line-break density**:
Average characters per line for ja zh ko, average words per line for other locales, over story-body content lines excluding the source marker and empty lines.
_Avoid_: 改行頻度, 改行数

**Title line**:
One literary title per story, written as the third-level heading that opens each story block.
_Avoid_: 見出し (the story delimiter), heading

**Frontmatter**:
Leading YAML block carrying thread metadata, never part of the deliverable output.
_Avoid_: header, メタデータ
