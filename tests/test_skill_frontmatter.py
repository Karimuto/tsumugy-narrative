"""
tests/test_skill_frontmatter.py
TDD: canonical skill + diff-only locale deltas.
- Canonical: SKILL.md at repo root holds the common
  body (8 authors, 5 prohibited plus 2 boundary, verification, dictionary).
  Frontmatter keeps only name and description per skill format (issue #13);
  runtime values such as mode live in the body. No " or ' anywhere
  (v1.1.2 owner decision; only backticks and bare text).
- Locale deltas: locales/{lang}/SKILL.md hold only differences
  (4 extra authors, brackets, citation, count window). Frontmatter keeps the
  5 keys with mode episodic (out of scope for #13, left untouched).
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCALE_DIR = REPO_ROOT / "locales"
CANONICAL_SKILL = REPO_ROOT / "SKILL.md"
SKILL_LANGS = ["en", "ja", "zh", "ko", "ar", "es", "fr", "ru"]


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """Parse ---\n YAML \n--- body. Returns (frontmatter_dict, body_str)."""
    if not text.startswith("---"):
        raise ValueError("SKILL.md must start with --- frontmatter delimiter")
    end = text.find("\n---", 3)
    if end < 0:
        raise ValueError("SKILL.md frontmatter not closed (missing trailing ---)")
    fm_block = text[3:end].strip("\n")
    body = text[end + 4:].lstrip("\n")
    # Minimal YAML parser: key: value per line, value after the first ':' is stripped
    fm: dict = {}
    for line in fm_block.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line!r}")
        k, v = line.split(":", 1)
        fm[k.strip()] = v.strip()
    return fm, body


def _load_skill(lang: str) -> tuple[dict, str]:
    p = LOCALE_DIR / lang / "SKILL.md"
    if not p.exists():
        raise FileNotFoundError(f"missing SKILL.md for locale {lang}: {p}")
    return _split_frontmatter(p.read_text(encoding="utf-8"))


def _load_canonical() -> tuple[dict, str]:
    if not CANONICAL_SKILL.exists():
        raise FileNotFoundError(f"missing canonical skill: {CANONICAL_SKILL}")
    return _split_frontmatter(CANONICAL_SKILL.read_text(encoding="utf-8"))


def test_canonical_skill_exists():
    assert CANONICAL_SKILL.exists(), f"canonical skill missing: {CANONICAL_SKILL}"


def test_canonical_frontmatter_name():
    fm, _ = _load_canonical()
    assert fm.get("name") == "narrative-formatter", f"canonical name is {fm.get('name')!r}"
    assert fm.get("description"), "canonical description is empty"
    assert set(fm) == {"name", "description"}, f"canonical frontmatter must hold only name and description per skill format, got {sorted(fm)!r}"


def test_canonical_has_authors_section():
    _, body = _load_canonical()
    assert re.search(r"^##\s+Authors", body, re.MULTILINE), "canonical: missing '## Authors'"
    block = body.split("## Authors", 1)[1].split("##", 1)[0]
    n = sum(1 for line in block.splitlines() if re.match(r"^\s*-\s+", line))
    assert n >= 8, f"canonical: Authors has {n}, need >= 8 common authors"

_PROHIBITED_TERMS = (
    "量子は意志",
    "宇宙は意識",
    "教育は工場",
    "子どもは粘土",
    "子どもは白紙",
)
_BOUNDARY_TERMS = (
    "心は鏡",
    "老化は衰退",
)

def test_canonical_has_prohibited_metaphors_section():
    _, body = _load_canonical()
    assert re.search(r"^##\s+Prohibited Metaphors", body, re.MULTILINE), \
        "canonical: missing '## Prohibited Metaphors'"
    block = body.split("## Prohibited Metaphors", 1)[1].split("##", 1)[0]
    bullets = [line for line in block.splitlines() if re.match(r"^\s*-\s+", line)]
    assert len(bullets) == 5, f"canonical: Prohibited has {len(bullets)}, need exactly 5 items (issue #13)"
    for expected in _PROHIBITED_TERMS:
        assert any(expected in line for line in bullets), f"canonical: Prohibited missing {expected}"
        line = next(line for line in bullets if expected in line)
        assert len(line) > len(expected) + 5, f"canonical: Prohibited {expected} needs a reason"
    for removed in ("ウイルスは敵", "心はOS", "進化は彫刻", "死は敗北", "精神は幽霊", "自然は母", "意識は光", "心は磁石", "細胞は兵士", "免疫は狩人", "心はブラックボックス", "脳は政府", "自然は機械"):
        assert removed not in body, f"canonical: removed metaphor still present: {removed}"


def test_canonical_has_boundary_metaphors_section():
    _, body = _load_canonical()
    assert re.search(r"^##\s+Boundary Metaphors", body, re.MULTILINE), \
        "canonical: missing '## Boundary Metaphors'"
    block = body.split("## Boundary Metaphors", 1)[1].split("##", 1)[0]
    bullets = [line for line in block.splitlines() if re.match(r"^\s*-\s+", line)]
    assert len(bullets) == 2, f"canonical: Boundary has {len(bullets)}, need exactly 2 items (issue #13)"
    for expected in _BOUNDARY_TERMS:
        assert any(expected in line for line in bullets), f"canonical: Boundary missing {expected}"
        line = next(line for line in bullets if expected in line)
        assert len(line) > len(expected) + 5, f"canonical: Boundary {expected} needs a reason"
        assert "only when" in line.lower(), f"canonical: Boundary {expected} needs a use condition"


def test_canonical_default_is_fable():
    _, body = _load_canonical()
    assert re.search(r"Default is fable", body), "canonical: Modes default must read fable (issue #13)"
    assert "Default is episodic" not in body, "canonical: stale episodic default remains"


def test_canonical_must_should_bullets():
    _, body = _load_canonical()
    assert re.search(r"^##\s+Verification", body, re.MULTILINE), "canonical: missing Verification"
    must_block = body.split("Must rules", 1)[1].split("Should rules", 1)[0]
    must_bullets = [line for line in must_block.splitlines() if re.match(r"^\s*-\s+", line)]
    assert len(must_bullets) >= 10, f"canonical: Must rules has {len(must_bullets)} bullets, need >= 10"
    assert all(line.rstrip().endswith("(MUST)") for line in must_bullets), "canonical: every Must bullet must end with (MUST)"
    should_block = body.split("Should rules", 1)[1].split("##", 1)[0]
    should_bullets = [line for line in should_block.splitlines() if re.match(r"^\s*-\s+", line)]
    assert len(should_bullets) >= 3, f"canonical: Should rules has {len(should_bullets)} bullets, need >= 3"
    assert all(line.rstrip().endswith("(SHOULD)") for line in should_bullets), "canonical: every Should bullet must end with (SHOULD)"
    for token in ("300 to 600", "50 to 100", "0.9", "at least 4", "6 to 10", "400 to 500", "67 to 83", "20 to 200", "4 to 33", "20 to 100", "4 to 16"):
        assert token in body, f"canonical: numeric condition changed or missing: {token}"


def test_canonical_has_verification_section():
    _, body = _load_canonical()
    assert re.search(r"^##\s+Verification", body, re.MULTILINE), \
        "canonical: missing '## Verification' section"


_CANONICAL_METAPHOR_TERMS = _PROHIBITED_TERMS + _BOUNDARY_TERMS
_FIRST_USE_EXAMPLE = "一筋の矢🎯(イマチニブ)"
_BRACKET_CHARS = "『』《》⟨⟩«»"
_LOCALE_DATA_LINE = re.compile(r"^\s*-\s+(ja|en|zh|ko|ar|es|fr|ru)(\s|:|$)")


def _canonical_prose_without_data(body: str) -> str:
    """Strip enumerated locale-difference data, keep prose for language check."""
    kept: list[str] = []
    for line in body.splitlines():
        if _LOCALE_DATA_LINE.match(line):
            continue
        line = line.replace("## 物語", "HEADING")
        for term in _CANONICAL_METAPHOR_TERMS:
            line = line.replace(term, "TERM")
        line = line.replace(_FIRST_USE_EXAMPLE, "EXAMPLE")
        for ch in _BRACKET_CHARS:
            line = line.replace(ch, "")
        kept.append(line)
    return "\n".join(kept)


def test_canonical_english_only_prose():
    """Issue #17: canonical prose is English-only outside enumerated locale data."""
    _, body = _load_canonical()
    prose = _canonical_prose_without_data(body)
    bad = [
        line.strip()
        for line in prose.splitlines()
        if re.search(r"[^\x00-\x7F]", line)
    ]
    assert not bad, (
        "canonical: non-English prose outside enumerated data sections: "
        + "; ".join(repr(line) for line in bad[:5])
    )


def test_canonical_no_quotes_anywhere():
    """v1.1.2 owner decision: no " or ' in SKILL.md files; only backticks and bare text."""
    text = CANONICAL_SKILL.read_text(encoding="utf-8")
    assert '"' not in text, "canonical: ASCII double quote found"
    assert "'" not in text, "canonical: ASCII single quote found"


@pytest.mark.parametrize("lang", SKILL_LANGS)
def test_skill_file_exists(lang):
    p = LOCALE_DIR / lang / "SKILL.md"
    assert p.exists(), f"SKILL.md missing for {lang}: {p}"


@pytest.mark.parametrize("lang", SKILL_LANGS)
def test_skill_frontmatter_required_keys(lang):
    fm, _ = _load_skill(lang)
    for key in ("name", "description", "mode", "thread_id", "dictionary_path"):
        assert key in fm, f"{lang}: frontmatter missing required key {key!r}"
        assert fm[key], f"{lang}: frontmatter key {key!r} is empty"


@pytest.mark.parametrize("lang", SKILL_LANGS)
def test_skill_mode_is_episodic(lang):
    fm, _ = _load_skill(lang)
    assert fm["mode"] == "episodic", f"{lang}: mode is {fm['mode']!r}, must be episodic"


@pytest.mark.parametrize("lang", SKILL_LANGS)
def test_skill_no_quotes_anywhere(lang):
    """v1.1.2 owner decision: no " or ' in SKILL.md files; only backticks and bare text."""
    p = LOCALE_DIR / lang / "SKILL.md"
    text = p.read_text(encoding="utf-8")
    assert '"' not in text, f"{lang}: ASCII double quote found"
    assert "'" not in text, f"{lang}: ASCII single quote found"


@pytest.mark.parametrize("lang", SKILL_LANGS)
def test_skill_has_authors_section(lang):
    """Locale delta carries its 4 extra authors; the common 8 live in canonical."""
    _, body = _load_skill(lang)
    assert re.search(r"^##\s+Authors", body, re.MULTILINE), \
        f"{lang}: missing '## Authors' section"
    authors_block = body.split("## Authors", 1)[1].split("##", 1)[0]
    n_authors = sum(1 for line in authors_block.splitlines() if re.match(r"^\s*-\s+", line))
    assert n_authors >= 4, f"{lang}: Authors section has {n_authors} authors, need >= 4 locale extras"


@pytest.mark.parametrize("lang", SKILL_LANGS)
def test_skill_has_prohibited_metaphors_section(lang):
    """Locale delta points at canonical; the full NG list lives in canonical."""
    _, body = _load_skill(lang)
    assert re.search(r"^##\s+Prohibited Metaphors", body, re.MULTILINE), \
        f"{lang}: missing '## Prohibited Metaphors' section"


@pytest.mark.parametrize("lang", SKILL_LANGS)
def test_skill_has_verification_section(lang):
    _, body = _load_skill(lang)
    assert re.search(r"^##\s+Verification", body, re.MULTILINE), \
        f"{lang}: missing '## Verification' section"


@pytest.mark.parametrize("lang", SKILL_LANGS)
def test_skill_has_dictionary_reference(lang):
    _, body = _load_skill(lang)
    assert re.search(r"^##\s+Dictionary", body, re.MULTILINE), \
        f"{lang}: missing '## Dictionary' section"
    dict_block = body.split("## Dictionary", 1)[1].split("##", 1)[0]
    assert f"dictionaries/{lang}.json" in dict_block, \
        f"{lang}: Dictionary section must reference dictionaries/{lang}.json"


@pytest.mark.parametrize("lang", SKILL_LANGS)
def test_skill_dictionary_path_is_bare(lang):
    """The dictionary path token must appear as bare text (no surrounding quotes)."""
    _, body = _load_skill(lang)
    assert f"dictionaries/{lang}.json" in body


if __name__ == "__main__":
    test_canonical_skill_exists()
    test_canonical_frontmatter_name()
    test_canonical_has_authors_section()
    test_canonical_has_prohibited_metaphors_section()
    test_canonical_has_verification_section()
    test_canonical_no_quotes_anywhere()
    print("test_skill_frontmatter.py: canonical checks passed")
