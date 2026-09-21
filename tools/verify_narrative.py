"""
tools/verify_narrative.py
Verifies a generated narrative against the rules in product-plan.v1.3.3.

Severity mapping (must/should) per spec:
  must:   char_count (outside 300-600 chars, 50-100 words), bracket_period, source_marker, language_ratio, emoji_count (when <4), senses (when <2), paragraph_break, first_use_mapping, line_break_density (outside 20-200 chars, 4-33 words, narrative lines only)
  should: char_count (outside 400-500 chars, 67-83 words), emoji_count (when 4-5), senses (when 1), emoji_count (when >10), line_break_density (outside 20-100 chars, 4-16 words)
  (inner_monologue rule removed in v1.1.2 per owner decision 2026-09-02)

Per spec:
- emoji: <4 = MUST fail, 4-5 = SHOULD fail, 6-10 = MUST pass, >10 = SHOULD fail (warn)
- senses: <2 = MUST fail, 1 = SHOULD fail, 2+ = MUST pass
- language_ratio: 90% threshold
- word windows follow the char bands divided by 6 (ADR-0008 precedent, lower bound up, upper bound down)

Output: JSON {"status": "pass|conditional|fail",
             "results": [{rule, severity, ok, value?, extra?}, ...],
             "must_failed": [...], "should_failed": [...]}
Exit code: 0=pass, 1=conditional, 2=fail
"""
import argparse
import json
import re
import sys
from pathlib import Path

DICT_DIR = Path(__file__).resolve().parent.parent / "dictionaries"

# Per-locale bracket pairs
BRACKET_PER_LOCALE = {
    "ja": ("『", "』"), "ko": ("『", "』"),
    "zh": ("《", "》"),
    "en": ("⟨", "⟩"),
    "ar": ("«", "»"), "es": ("«", "»"), "fr": ("«", "»"), "ru": ("«", "»"),
}

# Per-locale source marker format patterns removed with the all-locales
# existence check: every locale now parses markers against _MARKER_LOCALES.

# Per-locale inner monologue patterns removed in v1.1.2.
# Thought-verb-based inner_monologue rule was removed; verify no longer
# inspects thoughts. See docs/implementation-plan.v1.1.2.html (P-C).

# Emoji sequences (per ADR-0006): one visible emoji is one, counted as an
# RGI sequence. Base set keeps the spec ranges; the glue covers VS16,
# Fitzpatrick modifiers, ZWJ chains, Regional Indicator pairs, keycaps,
# and subdivision tag sequences. Stdlib re only, no optional dependency,
_RI = r"\U0001F1E6-\U0001F1FF"
_FITZ = r"\U0001F3FB-\U0001F3FF"
_EBASE = r"\U0001F300-\U0001FAFF\U00002600-\U000027BF"
_ELEM = r"[" + _EBASE + r"]\uFE0F?[" + _FITZ + r"]?"
EMOJI_PATTERN = re.compile(
    r"(?:[" + _RI + r"]{2}"
    r"|[0-9#*]\uFE0F?\u20E3"
    r"|\U0001F3F4[\U000E0020-\U000E007F]+\U000E007F"
    r"|" + _ELEM + r"(?:\u200D" + _ELEM + r")*)"
)

# Emotion categories (dictionaries carry these alongside the senses;
# only distinct words count — see check_emotion)
EMOTION_CATS = ("fear", "joy", "sadness", "anger", "surprise", "disgust")

# Senses categories
SENSE_CATS = ("sight", "sound", "smell", "taste", "touch")


# Story headings per locale (ADR-0004); legacy ## 物語 accepted everywhere.
STORY_HEADINGS = ("物語", "Story", "故事", "이야기", "قصة", "Historia", "Histoire", "История")
STORY_HEADING_PATTERN = re.compile(r"^##\s*(?:物語|Story|故事|이야기|قصة|Historia|Histoire|История)\b\s*$", re.MULTILINE)

# Output-shape guards (issue #8, ADR-0009): YAML frontmatter, story headings,
# title lines, and author attribution. Stdlib re only, no optional dependency.
FRONTMATTER_FENCE_RE = re.compile(
    r"\A[ \t]*---[ \t]*\r?\n.*?\r?\n[ \t]*---[ \t]*(?=\r?\n|$)", re.DOTALL
)
METADATA_KEY_RE = re.compile(
    r"^\s*(?:mode|thread_id|protagonist|author)\s*:", re.MULTILINE | re.IGNORECASE
)
TITLE_LINE_RE = re.compile(r"^#{3}(?!#)[ \t]*(.*?)[ \t]*$", re.MULTILINE)
VOICE_LINE_RE = re.compile(r"^\s*voice:.*$", re.MULTILINE)

LOCALE_DIR = Path(__file__).resolve().parent.parent / "locales"

_AUTHOR_NAMES_CACHE: list[str] | None = None


def _load_author_names() -> list[str]:
    """Union of real author names across all locales/*/authors.yaml."""
    global _AUTHOR_NAMES_CACHE
    if _AUTHOR_NAMES_CACHE is None:
        names: set[str] = set()
        for path in sorted(LOCALE_DIR.glob("*/authors.yaml")):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            names.update(
                m.group(1)
                for m in re.finditer(r"^\s*-\s*name:\s*(.+?)\s*$", text, re.MULTILINE)
            )
        _AUTHOR_NAMES_CACHE = sorted(names)
    return _AUTHOR_NAMES_CACHE


def extract_preamble(text: str) -> str:
    """Text before the first story heading; empty when headings are absent."""
    matches = list(STORY_HEADING_PATTERN.finditer(text))
    if not matches:
        return ""
    return text[: matches[0].start()]


def check_frontmatter_yaml(text: str) -> dict:
    """File-level: a leading --- fence or thread-metadata key lines fail."""
    fence = FRONTMATTER_FENCE_RE.search(text)
    key = METADATA_KEY_RE.search(text)
    if fence is None and key is None:
        return {"rule": "frontmatter_yaml", "severity": "must", "ok": True, "story": None}
    match = fence.group(0) if fence is not None else key.group(0)
    return {
        "rule": "frontmatter_yaml",
        "severity": "must",
        "ok": False,
        "story": None,
        "match": match.strip()[:80],
    }


def check_story_heading(text: str) -> dict:
    """File-level: at least one story heading must delimit the document."""
    n = len(STORY_HEADING_PATTERN.findall(text))
    return {
        "rule": "story_heading",
        "severity": "must",
        "value": n,
        "ok": n >= 1,
        "story": None,
    }


def check_title(body: str) -> dict:
    """Per-story: exactly one ### title line opening the block."""
    title_lines = [m.group(1) for m in TITLE_LINE_RE.finditer(body)]
    base: dict = {"rule": "title", "severity": "must"}
    if not title_lines:
        return {**base, "ok": False, "note": "title_missing: no ### title line"}
    if len(title_lines) > 1:
        return {**base, "ok": False, "note": "title_multiple: one title line per story"}
    if not title_lines[0].strip():
        return {**base, "ok": False, "note": "title_empty: title text is blank"}
    non_empty = [line for line in body.splitlines() if line.strip()]
    if not non_empty or TITLE_LINE_RE.match(non_empty[0]) is None:
        return {**base, "ok": False, "note": "title_misplaced: title must open the story"}
    return {**base, "ok": True, "match": title_lines[0].strip()[:60]}


def check_author_attribution(body: str) -> dict:
    """Per-story: no real author name in surface text (voice lines stripped)."""
    clean = VOICE_LINE_RE.sub("", body).casefold()
    for name in _load_author_names():
        if re.fullmatch(r"[A-Za-z][A-Za-z .'-]*", name):
            # \b fails beside CJK (kana/kanji are \w): guard Latin runs instead.
            if re.search(r"(?<![A-Za-z])" + re.escape(name) + r"(?![A-Za-z])", clean, re.IGNORECASE):
                return {
                    "rule": "author_attribution",
                    "severity": "must",
                    "ok": False,
                    "match": name,
                }
        elif name.casefold() in clean:
            return {
                "rule": "author_attribution",
                "severity": "must",
                "ok": False,
                "match": name,
            }
    return {"rule": "author_attribution", "severity": "must", "ok": True}

def split_stories(text: str) -> list[dict]:
    """Split a multi-story document into per-story blocks.

    Each block is `## 物語 ... (next ## ... or EOF)`. Returns a list of dicts
    with keys: heading (str), body (str), source_marker (str|None).
    """
    matches = list(STORY_HEADING_PATTERN.finditer(text))
    blocks: list[dict] = []
    if not matches:
        # No `## 物語` headings: treat the whole text as one block (legacy).
        sm = _find_source_marker(text)
        return [{"heading": None, "body": text, "source_marker": sm}]
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block_text = text[start:end]
        sm = _find_source_marker(block_text)
        blocks.append({
            "heading": "## \u7269\u8a9e",
            "body": block_text.strip("\n"),
            "source_marker": sm,
        })
    return blocks


def _find_source_marker(block_text: str) -> str | None:
    """Return the first `> 出典...` blockquote line in the block, or None."""
    for line in block_text.splitlines():
        s = line.lstrip()
        if s.startswith(">"):
            rest = s[1:].lstrip()
            # 出典 / Source / Fuente / Source / 出处 / 출처 / المصدر / Источник (ASCII + fullwidth colon)
            if re.match(r"^(\u51fa\u5904|\u51fa\u5178|Source|Fuente|Source|\u51fa\u5904|\ucd9c\ucc98|\u0627\u0644\u0645\u0635\u062f\u0631|\u0418\u0441\u0442\u043e\u0447\u043d\u0438\u043a|\u0418\u0441\u0442\u043e\u0447\u043d\u0438\u043a|\u0438\u0441\u0442\u043e\u0447\u043d\u0438\u043a)\s*[:：\u3000]", rest):
                return line
    return None


def _load_dict(locale: str) -> dict:
    path = DICT_DIR / f"{locale}.json"
    if not path.exists():
        return None  # Return None to indicate missing
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _count_emojis(text: str) -> int:
    """Count emojis as RGI sequences: one visible emoji is one."""
    return len(EMOJI_PATTERN.findall(text))


CHAR_MUST = {"char": (300, 600), "word": (50, 100)}
CHAR_SHOULD = {"char": (400, 500), "word": (67, 83)}


def _count_unit(locale: str) -> str:
    return "char" if locale in ("ja", "zh", "ko") else "word"


def check_char_count(text: str, locale: str) -> dict:
    unit = _count_unit(locale)
    if unit == "char":
        value = len(text)
    else:
        value = len(re.findall(r"\b\w+\b", text))
    mlo, mhi = CHAR_MUST[unit]
    slo, shi = CHAR_SHOULD[unit]
    base = {"rule": "char_count", "value": value,
            "must_window": [mlo, mhi], "should_window": [slo, shi]}
    if not mlo <= value <= mhi:
        return {**base, "severity": "must", "ok": False}
    if not slo <= value <= shi:
        return {**base, "severity": "should", "ok": False,
                "note": "outside target band: aim for 400-500 chars (67-83 words)"}
    return {**base, "severity": "must", "ok": True}


def check_bracket_period(text: str, locale: str) -> dict:
    open_b, close_b = BRACKET_PER_LOCALE.get(locale, ("『", "』"))
    # Escape for regex
    open_esc = re.escape(open_b)
    close_esc = re.escape(close_b)
    # Match: open_b ... period ... close_b (period can be 。 or .)
    # Use [^open_b close_b] to avoid matching across bracket boundaries
    boundary_esc = re.escape(open_b + close_b)
    pattern = re.compile(f"{open_esc}[^{boundary_esc}]*?[。\\.][^{boundary_esc}]*?{close_esc}")
    m = pattern.search(text)
    return {
        "rule": "bracket_period",
        "severity": "must",
        "ok": m is None,
        "match": m.group(0) if m else None,
    }


SOURCE_KINDS = ("paged", "transcript", "sectioned")

# Per-locale marker grammars. page_required follows the canonical shapes:
# ja/en/zh/ko name a page, ar/es/fr/ru do not (a present page still must match).
_MARKER_LOCALES = {
    "ja": {"prefix": "出典", "chapter": r"第(\d+)章", "page": r"p\.(\d+)",
           "para": r"段落(\d+)", "page_required": True, "banned": "「」『』"},
    "en": {"prefix": "Source", "chapter": r"[Cc]h\.?\s*(\d+)", "page": r"[Pp]\.\s*(\d+)",
           "para": r"[Pp]ara\.?\s*(\d+)", "page_required": True, "banned": "⟨⟩"},
    "zh": {"prefix": "出处", "chapter": r"第(\d+)章", "page": r"[Pp]\.\s*(\d+)",
           "para": r"段落(\d+)", "page_required": True, "banned": "《》"},
    "ko": {"prefix": "출처", "chapter": r"제(\d+)장", "page": r"[Pp]\.\s*(\d+)",
           "para": r"문단(\d+)", "page_required": True, "banned": "『』"},
    "ar": {"prefix": "المصدر", "chapter": r"الفصل\s*(\d+)", "page": r"[Pp]\.\s*(\d+)",
           "para": r"فقرة\s*(\d+)", "page_required": False, "banned": "«»"},
    "es": {"prefix": "Fuente", "chapter": r"[Cc]ap\.?\s*(\d+)", "page": r"[Pp]\.\s*(\d+)",
           "para": r"[Pp]árr\.?\s*(\d+)", "page_required": False, "banned": "«»"},
    "fr": {"prefix": "Source", "chapter": r"[Cc]hap\.?\s*(\d+)", "page": r"[Pp]\.\s*(\d+)",
           "para": r"[Pp]ar\.?\s*(\d+)", "page_required": False, "banned": "«»"},
    "ru": {"prefix": "Источник", "chapter": r"[Гг]л\.?\s*(\d+)", "page": r"[Сс]\.\s*(\d+)",
           "para": r"[Аа]бз\.?\s*(\d+)", "page_required": False, "banned": "«»"},
}

# Bracket marker forms are banned attempts in every locale.
_BRACKET_MARKER_RE = re.compile(r"\[出典[:：]|\[[Ss]ource:|\[出处[:：]|\[출처[:：]|\[المصدر[:：]|\[[Ии]сточник[:：]|\[[Ff]uente:")

_SECTION_RE = re.compile(r"\d+(?:\.\d+)*")


def _label_ok(label: str, banned: str) -> bool:
    """Labels must not smuggle titles or bracketed text."""
    return not re.search("[" + re.escape(banned + "[]［］") + "]", label)


def _validate_sources(sources: dict) -> tuple:
    """Return (kind, entries) or raise ValueError for a malformed index."""
    if not isinstance(sources, dict):
        raise ValueError("sources must be an object with {kind, entries}")
    kind = sources.get("kind")
    if kind not in SOURCE_KINDS:
        raise ValueError(f"unknown source kind: {kind!r}; expected one of {sorted(SOURCE_KINDS)}")
    entries = sources.get("entries")
    if not isinstance(entries, list) or not all(isinstance(e, dict) for e in entries):
        raise ValueError("sources.entries must be a list of objects")
    return kind, entries


def _marker_attempts(body: str) -> list:
    """All source-marker attempt lines in a story body as (line, is_bracket)."""
    attempts = []
    for line in body.splitlines():
        s = line.lstrip()
        if s.startswith(">"):
            rest = s[1:].lstrip()
            if re.match(r"^(出典|[Ss]ource|[Ff]uente|出处|출처|المصدر|[Ии]сточник)\s*[:：　]", rest):
                attempts.append((line, False))
        if _BRACKET_MARKER_RE.search(line):
            attempts.append((line, True))
    return attempts


def _parse_paged(body: str, cfg: dict) -> tuple:
    """Parse the text after the locale prefix. Returns (parsed, None) or (None, reason)."""
    left, sep, right = body.rpartition("/")
    if not sep:
        return None, f"paged shape needs chapter/label plus paragraph: {body}"
    para_m = re.fullmatch(cfg["para"], right.strip())
    if not para_m:
        return None, f"bad paragraph part: {right.strip()}"
    rest = left.strip()
    chapter = None
    ch_m = re.match("^(?:" + cfg["chapter"] + r")\s*(.*)$", rest)
    if ch_m:
        chapter = int(ch_m.group(1))
        tail = ch_m.group(2).strip()
    else:
        tail = rest
    page = None
    page_m = re.search(cfg["page"] + r"\s*$", tail)
    if page_m:
        page = int(page_m.group(1))
        label = tail[:page_m.start()].strip() or None
    else:
        label = tail or None
    if chapter is None and label is None:
        return None, "paged marker needs chapter or label"
    if page is None and cfg["page_required"]:
        return None, f"page required: {body}"
    if label and not _label_ok(label, cfg["banned"]):
        return None, f"brackets not allowed in label: {label}"
    return {"chapter": chapter, "label": label, "page": page,
            "para": int(para_m.group(1))}, None


def _parse_marker(line: str, locale: str, kind: str) -> tuple:
    """Parse one blockquote marker line. Returns (parsed, None) or (None, reason)."""
    cfg = _MARKER_LOCALES[locale]
    m = re.match(r"^>\s*" + re.escape(cfg["prefix"]) + r"[:：]\s*(.+?)\s*$",
                 line.lstrip(), flags=re.IGNORECASE)
    if not m:
        return None, "not a source marker line"
    body = m.group(1)
    if kind == "paged":
        return _parse_paged(body, cfg)
    if kind == "transcript":
        if re.search(r"\s", body) is None:
            return None, "transcript marker needs label and ref"
        label, ref = body.rsplit(None, 1)
        return {"label": label, "ref": ref}, None
    if kind == "sectioned":
        parts = body.rsplit(None, 1)
        label, sec = (None, parts[0]) if len(parts) == 1 else parts
        if not _SECTION_RE.fullmatch(sec):
            return None, f"section must be dotted digits: {sec}"
        if label is not None and not label.strip():
            label = None
        return {"label": label, "section": sec}, None
    return None, f"unknown kind: {kind}"


def _num_eq(a, b) -> bool:
    try:
        return int(a) == int(b)
    except (TypeError, ValueError):
        return a == b


def _entry_matches(parsed: dict, kind: str, entry: dict) -> bool:
    """Every field the marker asserts must be backed by the index entry."""
    if kind == "paged":
        if parsed["chapter"] is not None and not _num_eq(entry.get("chapter"), parsed["chapter"]):
            return False
        if parsed["label"] is not None and entry.get("label") != parsed["label"]:
            return False
        if parsed["page"] is not None and not _num_eq(entry.get("page"), parsed["page"]):
            return False
        return _num_eq(entry.get("para"), parsed["para"])
    if kind == "transcript":
        return entry.get("label") == parsed["label"] and entry.get("ref") == parsed["ref"]
    if kind == "sectioned":
        if entry.get("section") != parsed["section"]:
            return False
        if parsed["label"] is not None and entry.get("label") != parsed["label"]:
            return False
        return True
    return False


def check_source_marker(body: str, locale: str, sources: dict | None) -> dict:
    """Per-story source existence check. Returned dict lacks the story key."""
    attempts = _marker_attempts(body)
    first_quote = next((line for line, bracket in attempts if not bracket), None)
    base = {"rule": "source_marker", "severity": "must", "value": len(attempts), "match": first_quote}
    if not attempts:
        return {**base, "ok": False, "note": "source_malformed: no source marker"}
    if sources is None:
        return {**base, "ok": False, "note": "missing_source: no source index supplied"}
    kind, entries = _validate_sources(sources)
    for line, is_bracket in attempts:
        if is_bracket:
            return {**base, "ok": False, "note": f"source_malformed: bracket form banned: {line.strip()}"}
        parsed, err = _parse_marker(line, locale, kind)
        if err:
            return {**base, "ok": False, "note": f"source_malformed: {err}"}
        if not any(_entry_matches(parsed, kind, e) for e in entries):
            return {**base, "ok": False, "note": f"source_mismatch: no index entry for {line.strip()}"}
    return {**base, "ok": True, "note": "ok"}


def check_emoji(text: str, locale: str) -> dict:
    n = _count_emojis(text)
    # Per spec: <4 = MUST fail, 4-5 = SHOULD fail, 6-10 = MUST pass, >10 = SHOULD fail (warn)
    if n < 4:
        severity = "must"
        ok = False
        warn = False
    elif n < 6:
        severity = "should"
        ok = False
        warn = False
    elif n <= 10:
        severity = "must"
        ok = True
        warn = False
    else:
        severity = "should"
        ok = False
        warn = True
    return {
        "rule": "emoji_count",
        "severity": severity,
        "value": n,
        "ok": ok,
        "warn": warn,
    }


def check_senses(text: str, locale: str) -> dict:
    d = _load_dict(locale)
    if d is None:
        # Dictionary missing - this is a MUST failure per spec
        return {
            "rule": "senses",
            "severity": "must",
            "ok": False,
            "note": f"dictionary missing for locale: {locale}",
        }
    hits = []
    for cat in SENSE_CATS:
        for word in d.get(cat, []):
            if not word:
                continue
            # CJK: allow 1-char atoms, use substring match
            if locale in ("ja", "zh", "ko"):
                pattern = re.escape(word)
            else:
                # Latin/Cyrillic/Arabic: word boundary
                pattern = r"\b" + re.escape(word) + r"\b"
            if re.search(pattern, text):
                hits.append(cat)
                break
    n = len(hits)
    # Per spec: 0 = MUST fail, 1 = SHOULD fail, 2+ = MUST pass
    if n >= 2:
        severity = "must"
        ok = True
    elif n == 1:
        severity = "should"
        ok = False
    else:
        severity = "must"
        ok = False
    return {
        "rule": "senses",
        "severity": severity,
        "hits": hits,
        "ok": ok,
    }


def check_emotion(text: str, locale: str) -> dict:
    d = _load_dict(locale)
    if d is None:
        # Dictionary missing - this is a MUST failure per spec
        return {
            "rule": "emotion",
            "severity": "must",
            "ok": False,
            "note": f"dictionary missing for locale: {locale}",
        }
    # Words shared with any sense category don't count: they fire on
    # sensory description, not on human feeling (e.g. 光 listed under
    # both sight and joy). Only distinct emotion signal satisfies this.
    sense_words = set()
    for cat in SENSE_CATS:
        sense_words.update(w for w in d.get(cat, []) if w)
    hits = []
    for cat in EMOTION_CATS:
        for word in d.get(cat, []):
            if not word or word in sense_words:
                continue
            if locale in ("ja", "zh", "ko"):
                pattern = re.escape(word)
            else:
                pattern = r"\b" + re.escape(word) + r"\b"
            if re.search(pattern, text):
                hits.append(cat)
                break
    if hits:
        severity = "must"
        ok = True
    else:
        severity = "should"
        ok = False
    return {
        "rule": "emotion",
        "severity": severity,
        "hits": hits,
        "ok": ok,
    }


def check_language_ratio(text: str, locale: str) -> dict:
    # Exclude citation line(s): blockquote source markers AND bracketed [Source: ...]
    # which contain Latin/digits like "p.1" and "第1章"
    body = re.sub(r"^>.*$", "", text, flags=re.MULTILINE)
    body = re.sub(r"\[[Ss]ource:[^\]]*\]", "", body)
    body = re.sub(r"\[出典[:：][^\]]*\]", "", body)
    body = re.sub(r"\[出处[:：][^\]]*\]", "", body)
    body = re.sub(r"\[출처[:：][^\]]*\]", "", body)
    body = re.sub(r"\[المصدر[:：][^\]]*\]", "", body)
    body = re.sub(r"\[[Ff]uente:[^\]]*\]", "", body)
    body = re.sub(r"\[[Ии]сточник:[^\]]*\]", "", body)
    # CJK: ideographs + hiragana + katakana + hangul + CJK punctuation/symbols
    cjk = len(re.findall(r"[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u31a0-\u31bf\u31f0-\u31ff\u3200-\u32ff\u3300-\u33ff\u4e00-\u9fff\uff00-\uffef\uac00-\ud7af]", body))
    arabic = len(re.findall(r"[\u0600-\u06ff]", body))
    cyrillic = len(re.findall(r"[\u0400-\u04ff]", body))
    latin = len(re.findall(r"[A-Za-z]", body))
    # Count visible "script" characters only: drop whitespace, drop emoji (any
    # code point >= U+1F000 or in emoji ranges), drop common punctuation.
    # Emoji are decorative and would otherwise lower the ratio for the wrong
    # reason.
    visible_body = "".join(
        c for c in body
        if not c.isspace()
        and ord(c) < 0x1F000
        and not (0x2600 <= ord(c) <= 0x27BF)  # misc symbols + dingbats
    )
    total = max(1, len(visible_body))
    if locale in ("ja", "zh", "ko"):
        ratio = cjk / total
    elif locale == "ar":
        ratio = arabic / total
    elif locale == "ru":
        ratio = cyrillic / total
    else:
        ratio = latin / total
    return {
        "rule": "language_ratio",
        "severity": "must",
        "value": round(ratio, 3),
        "ok": ratio >= 0.9,
        "story": None,
    }

# Line-break density bands (ADR-0011 supersedes ADR-0008): narrative lines only.
# CJK locales count chars, others count words. Measured over narrative
# lines only: the region between the ### title line and the ##解説
# heading, excluding headings, source markers, voice lines, and empty
# lines. MUST fails outside 20-200 chars (4-33 words); SHOULD warns
# outside 20-100 chars (4-16 words) with the literary override.
DENSITY_MUST = {"char": (20, 200), "word": (4, 33)}
DENSITY_SHOULD = {"char": (20, 100), "word": (4, 16)}

LINE_BREAK_OVERRIDE_NOTE = (
    "文学的効果が認知負荷を上回ると判断したら修正不要"
    " — CONDITIONAL PASSのまま納品可"
)


def _content_lines(text: str) -> list[str]:
    """Non-empty narrative lines: _narrative_lines minus markers."""
    return [
        line for line in _narrative_lines(text)
        if line.strip() and not line.lstrip().startswith(">")
    ]


def check_line_break_density(text: str, locale: str) -> dict:
    lines = _content_lines(text)
    if not lines:
        return {
            "rule": "line_break_density",
            "severity": "should",
            "value": 0,
            "ok": True,
            "note": "no content lines",
        }
    unit_kind = "char" if locale in ("ja", "zh", "ko") else "word"
    if unit_kind == "char":
        total = sum(len(line) for line in lines)
        unit = "chars"
    else:
        total = sum(len(re.findall(r"\b\w+\b", line)) for line in lines)
        unit = "words"
    mlo, mhi = DENSITY_MUST[unit_kind]
    slo, shi = DENSITY_SHOULD[unit_kind]
    density = total / len(lines)
    base = {"rule": "line_break_density", "value": round(density, 1),
            "unit": unit, "must_window": [mlo, mhi], "should_window": [slo, shi]}
    if not mlo <= density <= mhi:
        return {
            **base,
            "severity": "must",
            "ok": False,
        }
    if not slo <= density <= shi:
        return {
            **base,
            "severity": "should",
            "ok": False,
            "note": LINE_BREAK_OVERRIDE_NOTE,
        }
    return {
        "rule": "line_break_density",
        "severity": "should",
        "value": round(density, 1),
        "unit": unit,
        "ok": True,
    }

def _narrative_lines(block_body: str) -> list[str]:
    """Lines of the story narrative region of one split block.

    The region starts after an opening ### title line (or at the first
    content line when untitled) and ends before the first ## section
    heading (usually ##解説). Headings, source markers, and voice lines
    never count as narrative lines.
    """
    lines = block_body.splitlines()
    start = 0
    for i, line in enumerate(lines):
        if TITLE_LINE_RE.match(line):
            start = i + 1
            break
        s = line.strip()
        if s and not s.startswith("##"):
            start = i
            break
    region = []
    for line in lines[start:]:
        if line.lstrip().startswith("##"):
            break
        region.append(line)
    return region


def check_paragraph_break(text: str, locale: str) -> dict:
    """Story-body paragraphs must be divided by a blank line (ADR-0010).

    Any run of two or more consecutive non-empty narrative lines is a
    joined-paragraph MUST failure. A single-paragraph body passes
    vacuously; overlong single lines remain the density rule territory.
    """
    base = {"rule": "paragraph_break", "severity": "must"}
    run = 0
    worst = 0
    for line in _narrative_lines(text):
        s = line.strip()
        if not s or s.startswith(">") or VOICE_LINE_RE.match(line):
            run = 0
            continue
        run += 1
        worst = max(worst, run)
    if worst >= 2:
        return {**base, "ok": False, "value": worst,
                "note": "joined_paragraphs: separate story-body paragraphs with a blank line"}
    return {**base, "ok": True, "value": worst}

def check_first_use_mapping(text: str, locale: str, introduced: dict | None = None) -> dict:
    """First-use metaphor mapping must be a 3-point set (grill 2026-09-05).

    The first occurrence of every locale-bracket metaphor in the narrative
    region must read METAPHOR + anchor emoji + (textbook term), with full
    or half width parens allowed. Later occurrences need the anchor emoji
    only. Every anchor emoji in the region must be introduced by a 3-point
    set at or before its position: bare anchors with no introduction, and
    anchors used before their introduction, are a MUST failure naming the
    anchors. Missing 3-point sets are a MUST failure naming the metaphors.

    `introduced` is an optional dict carried across stories in file order
    (serial threads reuse anchors without re-mapping): it is updated in
    place with this story's introductions. Known limitation: cross-story
    reuse in episodic mode also passes, as the verifier has no mode signal.
    """
    base = {"rule": "first_use_mapping", "severity": "must"}
    open_b, close_b = BRACKET_PER_LOCALE.get(locale, ("『", "』"))
    region = "\n".join(
        line for line in _narrative_lines(text)
        if line.strip() and not line.lstrip().startswith(">")
        and not VOICE_LINE_RE.match(line)
    )
    if not region.strip():
        return {**base, "ok": True, "value": 0, "note": "no narrative lines"}
    if introduced is None:
        introduced = {}
    bpat = re.compile(re.escape(open_b) + "(.*?)" + re.escape(close_b))
    valid = []
    misses = []
    seen = set()
    for m in bpat.finditer(region):
        content = m.group(1).strip()
        if not content or content in seen:
            continue
        seen.add(content)
        rest = region[m.end():].lstrip()
        em = EMOJI_PATTERN.match(rest)
        if em is None:
            misses.append(content)
            continue
        rest2 = rest[em.end():].lstrip()
        if re.match(r"[（(][^）)\n]+[）)]", rest2) is None:
            misses.append(content)
            continue
        anchor = em.group(0)
        gap = len(region[m.end():]) - len(rest)
        a_start = m.end() + gap
        valid.append((anchor, a_start, a_start + len(anchor), content))
    spans = [(s, e) for _, s, e, _ in valid]
    events = [(s, 0, "intro", a, c) for a, s, e, c in valid]
    for em in EMOJI_PATTERN.finditer(region):
        s, e = em.span()
        if any(a <= s and e <= b for a, b in spans):
            continue
        events.append((s, 1, "use", em.group(0), ""))
    events.sort(key=lambda t: (t[0], t[1]))
    unmapped = []
    for _, _, kind, val, content in events:
        if kind == "intro":
            introduced[val] = content
        elif val not in introduced and val not in unmapped:
            unmapped.append(val)
    if misses or unmapped:
        return {**base, "ok": False, "value": len(seen),
                "misses": misses[:8], "unmapped": unmapped[:8],
                "note": "first use must read METAPHOR emoji (term); bare anchors must be introduced"}
    return {**base, "ok": True, "value": len(seen)}


def verify(text: str, locale: str, sources: dict | None = None) -> dict:
    """Verify text. sources is a kind-tagged index {kind, entries} or None.

    sources=None fails the per-story source_marker rule with missing_source:
    existence against the input material is required, format alone never passes.
    """
    if not isinstance(text, str):
        return {
            "status": "FAIL",
            "must_failed": ["invalid_input"],
            "results": [{
                "rule": "invalid_input",
                "severity": "must",
                "ok": False,
                "note": f"expected str, got {type(text).__name__}",
            }],
        }
    if locale not in BRACKET_PER_LOCALE:
        return {
            "status": "FAIL",
            "must_failed": ["unsupported_locale"],
            "results": [{
                "rule": "unsupported_locale",
                "severity": "must",
                "ok": False,
                "note": f"unsupported locale: {locale!r}; supported: {sorted(BRACKET_PER_LOCALE)}",
            }],
        }

    if sources is not None:
        try:
            _validate_sources(sources)
        except ValueError as e:
            return {
                "status": "FAIL",
                "must_failed": ["invalid_sources"],
                "results": [{
                    "rule": "invalid_sources",
                    "severity": "must",
                    "ok": False,
                    "note": str(e),
                }],
            }

    blocks = split_stories(text)
    preamble = extract_preamble(text)
    main_text = VOICE_LINE_RE.sub("", text[len(preamble):] if preamble else text)
    results = []
    # File-level rules: language ratio, frontmatter, story headings.
    results.append(check_language_ratio(main_text, locale))
    results.append(check_frontmatter_yaml(text))
    results.append(check_story_heading(text))
    # All other rules are per-story, over clean bodies: voice lines carry
    # no verification (ADR-0009) and never reach any check.
    # Anchor introductions accumulate in file order so serial episodes may
    # reuse earlier anchors without re-mapping (see check_first_use_mapping).
    mapping_introduced: dict = {}
    for idx, block in enumerate(blocks, start=1):
        body = VOICE_LINE_RE.sub("", block["body"])
        results.append({
            "rule": "story_index",
            "severity": "info",
            "story": idx,
            "ok": True,
            "body_chars": len(body),
            "has_source_marker": block["source_marker"] is not None,
        })
        # Tag every per-story rule with its story index so downstream
        # aggregation can keep rule-level visibility while still pinning the
        # failure to a specific story.
        for r in (
            check_char_count(body, locale),
            check_bracket_period(body, locale),
            check_emoji(body, locale),
            check_senses(body, locale),
            check_emotion(body, locale),
            check_line_break_density(body, locale),
            check_paragraph_break(body, locale),
            check_first_use_mapping(body, locale, mapping_introduced),
            check_title(body),
            check_author_attribution(body),
        ):
            r["story"] = idx
            results.append(r)
        # source_marker: existence against the kind-tagged source index,
        # parsed with the per-locale grammar in every locale.
        sm = check_source_marker(body, locale, sources)
        sm["story"] = idx
        results.append(sm)

    # Aggregate per-rule must-failed names (without story suffix) so the
    # public must_failed list is human-readable; detailed per-story info
    # remains in `results` with story#N tags.
    detailed_must_failed = [
        f"{r['rule']}#story{r['story']}" for r in results
        if r.get("severity") == "must" and not r.get("ok")
        and r.get("rule") not in ("invalid_input", "unsupported_locale", "invalid_sources", "story_index", "language_ratio", "frontmatter_yaml", "story_heading")
        and "story" in r
    ]
    file_level_order = ("language_ratio", "frontmatter_yaml", "story_heading")
    file_level_failed = [
        name for name in file_level_order
        if any(rr["rule"] == name and not rr.get("ok") for rr in results)
    ]
    aggregate_must_failed = file_level_failed + sorted({
        name.split("#", 1)[0] for name in detailed_must_failed
    })

    if any(r["rule"] in ("invalid_input", "unsupported_locale", "invalid_sources") for r in results):
        must_failed = [r["rule"] for r in results if r["rule"] in ("invalid_input", "unsupported_locale", "invalid_sources") and not r["ok"]]
    else:
        must_failed = aggregate_must_failed
    should_failed = sorted({
        r["rule"] for r in results
        if r.get("severity") == "should" and not r.get("ok")
    })
    if must_failed:
        status = "FAIL"
    elif len(should_failed) >= 3:
        status = "FAIL"
    elif should_failed:
        status = "CONDITIONAL PASS"
    else:
        status = "PASS"
    return {
        "status": status,
        "results": results,
        "must_failed": must_failed,
        "should_failed": should_failed,
    }


def main():
    p = argparse.ArgumentParser(
        description="Verify a Tsumugy narrative against the rules in product-plan v1.3.3."
    )
    p.add_argument("--text", nargs="?", default=None,
                   help="narrative text to verify (omit to read from stdin or --input)")
    p.add_argument("--locale", required=True,
                   help="locale code: ja/en/zh/ko/ar/es/fr/ru")
    p.add_argument("--input", help="JSON file with {text, locale, sources}")
    p.add_argument("--source-index", help="JSON file with the kind-tagged source index {kind, entries}")
    p.add_argument("--quiet", action="store_true",
                   help="suppress stderr diagnostic summary")
    args = p.parse_args()
    try:
        sources = None
        if args.source_index:
            with open(args.source_index, encoding="utf-8") as f:
                sources = json.load(f)
        if args.input:
            with open(args.input, encoding="utf-8") as f:
                payload = json.load(f)
            text = payload.get("text", "")
            locale = payload.get("locale", args.locale)
            if sources is None:
                sources = payload.get("sources")
        elif args.text is not None:
            text = args.text
            locale = args.locale
        else:
            stdin_data = sys.stdin.read()
            if stdin_data.strip():
                payload = json.loads(stdin_data)
                text = payload.get("text", "")
                locale = payload.get("locale", args.locale)
                if sources is None:
                    sources = payload.get("sources")
            else:
                p.error("no text provided: use --text, --input, or pipe JSON to stdin")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        result = {
            "status": "FAIL",
            "must_failed": ["invalid_input"],
            "results": [{
                "rule": "invalid_input",
                "severity": "must",
                "ok": False,
                "note": str(e),
            }],
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(2)

    result = verify(text, locale, sources)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if not args.quiet:
        status = result["status"]
        if status == "FAIL":
            bits = []
            if result["must_failed"]:
                bits.append(f"must_failed: {', '.join(result['must_failed'])}")
            if result["should_failed"]:
                bits.append(f"should_failed: {', '.join(result['should_failed'])}")
            where = "; ".join(bits) or "(no rules failed)"
            sys.stderr.write(f"[verify] FAIL — {where}\n")
        elif status == "CONDITIONAL PASS":
            where = ", ".join(result["should_failed"]) or "(no rules failed)"
            sys.stderr.write(f"[verify] CONDITIONAL PASS — should_failed: {where}\n")
        else:
            sys.stderr.write("[verify] PASS\n")

    if result["status"] == "PASS":
        sys.exit(0)
    if result["status"] == "CONDITIONAL PASS":
        sys.exit(1)
    sys.exit(2)


if __name__ == "__main__":
    main()