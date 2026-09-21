"""
tests/test_locale_yaml.py
TDD: locales/{lang}/authors.yaml invariants.
- File exists for every supported locale
- Parses as YAML (minimal: key: value + list under authors:)
- Has at least 12 authors total (8 main + 4 locale-specific)
- Every author has: name, era, one_liner, ng_examples (list, may be empty)
- The ng_examples aggregate across all 12 authors covers the pinned 11-item
  NG set (#16: the 80-row triage doc is gone; SKILL.md "Prohibited Metaphors"
  carries 5, authors.yaml carries all 11)
- Each author name is unique within the locale
"""
from __future__ import annotations

from pathlib import Path
import re
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCALE_DIR = REPO_ROOT / "locales"
SKILL_PATH = REPO_ROOT / "SKILL.md"
SKILL_LANGS = ["en", "ja", "zh", "ko", "ar", "es", "fr", "ru"]

# NG inventory after #16 (docs/ng-metaphor-candidates.md deleted):
# SKILL.md "Prohibited Metaphors" carries 5; the remaining 6 live only in
# authors.yaml ng_examples. EXPECTED_NG pins the union (11).
EXPECTED_NG_COUNT = 11
EXPECTED_AUTHORS_MIN = 12


def _load_yaml_minimal(path: Path) -> dict:
    """Minimal YAML parser sufficient for authors.yaml schema.

    Schema:
    locale: en
    authors:
      - name: <str>
        era: <str>
        one_liner: <str>
        ng_examples: [<str>, ...]
    """
    text = path.read_text(encoding="utf-8")
    out: dict = {"locale": None, "authors": []}
    cur_author: dict | None = None
    in_authors = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not in_authors:
            if line.startswith("locale:"):
                out["locale"] = line.split(":", 1)[1].strip()
            elif line.startswith("authors:"):
                in_authors = True
            continue
        # in authors
        if line.startswith("  - "):
            if cur_author is not None:
                out["authors"].append(cur_author)
            head = line[4:]
            cur_author = {"ng_examples": []}
            if ":" in head:
                k, v = head.split(":", 1)
                cur_author[k.strip()] = v.strip()
        elif line.startswith("    "):
            assert cur_author is not None, f"unexpected indented line {line!r}"
            cont = line.strip()
            if cont.startswith("- "):
                cur_author["ng_examples"].append(cont[2:].strip())
            elif ":" in cont:
                k, v = cont.split(":", 1)
                key = k.strip()
                val = v.strip()
                if key == "ng_examples":
                    if val == "":
                        # ng_examples: <newline>  - item form; array exists.
                        pass
                    elif val.startswith("[") and val.endswith("]"):
                        # Inline form: ng_examples: [a, b]
                        inner = val[1:-1].strip()
                        if inner:
                            cur_author["ng_examples"] = [x.strip().strip("'\"") for x in inner.split(",")]
                        # else: empty inline list, keep []
                else:
                    cur_author[key] = val
    if cur_author is not None:
        out["authors"].append(cur_author)
    return out


def _skill_prohibited_metaphors() -> set[str]:
    """Parse the SKILL.md "Prohibited Metaphors" bullets.

    Shape: "- <metaphor>: <reason>" under the "## Prohibited Metaphors"
    heading. Only exact "XはY" bullets count; prose lines are ignored.
    """
    text = SKILL_PATH.read_text(encoding="utf-8")
    in_section = False
    found: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("## "):
            in_section = line == "## Prohibited Metaphors"
            continue
        if not in_section or not line.startswith("- "):
            continue
        head = line[2:].split(":", 1)[0].strip()
        if re.fullmatch(r".+は.+", head):
            found.add(head)
    return found


def _all_ng_examples() -> set[str]:
    """Union of every ng_examples entry across all locales."""
    actual: set[str] = set()
    for lang in SKILL_LANGS:
        data = _load_yaml_minimal(LOCALE_DIR / lang / "authors.yaml")
        for a in data["authors"]:
            for ex in a["ng_examples"]:
                actual.add(ex.strip())
    return actual


# The full NG inventory: 5 prohibited metaphors enforced in SKILL.md plus 6
# that live only in authors.yaml ng_examples. Pinned by name so a silent
# edit to either source fails loudly instead of shrinking coverage.
EXPECTED_NG = frozenset({
    "量子は意志",
    "宇宙は意識",
    "教育は工場",
    "子どもは粘土",
    "子どもは白紙",
    "心は鏡",
    "ウイルスは敵",
    "心はOS",
    "進化は彫刻",
    "死は敗北",
    "精神は幽霊",
})


@pytest.mark.parametrize("lang", SKILL_LANGS)
def test_authors_yaml_exists(lang):
    p = LOCALE_DIR / lang / "authors.yaml"
    assert p.exists(), f"authors.yaml missing for {lang}: {p}"


@pytest.mark.parametrize("lang", SKILL_LANGS)
def test_authors_yaml_locale_matches(lang):
    p = LOCALE_DIR / lang / "authors.yaml"
    data = _load_yaml_minimal(p)
    assert data["locale"] == lang, f"{lang}: locale field is {data['locale']!r}"


@pytest.mark.parametrize("lang", SKILL_LANGS)
def test_authors_yaml_has_minimum_authors(lang):
    p = LOCALE_DIR / lang / "authors.yaml"
    data = _load_yaml_minimal(p)
    assert len(data["authors"]) >= EXPECTED_AUTHORS_MIN, \
        f"{lang}: {len(data['authors'])} authors, need >= {EXPECTED_AUTHORS_MIN}"


@pytest.mark.parametrize("lang", SKILL_LANGS)
def test_authors_have_required_fields(lang):
    p = LOCALE_DIR / lang / "authors.yaml"
    data = _load_yaml_minimal(p)
    for i, a in enumerate(data["authors"]):
        for k in ("name", "era", "one_liner"):
            assert k in a and a[k], f"{lang}: author #{i} missing {k}"
        assert "ng_examples" in a, f"{lang}: author #{i} missing ng_examples"
        assert isinstance(a["ng_examples"], list), f"{lang}: author #{i} ng_examples must be list"


@pytest.mark.parametrize("lang", SKILL_LANGS)
def test_authors_names_unique(lang):
    p = LOCALE_DIR / lang / "authors.yaml"
    data = _load_yaml_minimal(p)
    names = [a["name"] for a in data["authors"]]
    assert len(names) == len(set(names)), f"{lang}: duplicate author names in {names}"


@pytest.mark.parametrize("lang", SKILL_LANGS)
def test_authors_cover_ng_list(lang):
    """Every NG metaphor must appear in at least one author's ng_examples."""
    p = LOCALE_DIR / lang / "authors.yaml"
    data = _load_yaml_minimal(p)
    assert len(EXPECTED_NG) == EXPECTED_NG_COUNT, \
        f"sanity: expected {EXPECTED_NG_COUNT} NG, got {sorted(EXPECTED_NG)}"
    # Build a flat set of all ng_examples from all authors (in this locale)
    actual = set()
    for a in data["authors"]:
        for ex in a["ng_examples"]:
            actual.add(ex.strip())
    missing = set(EXPECTED_NG) - actual
    assert not missing, f"{lang}: NG list missing from authors: {missing}"


def test_skill_prohibited_metaphors_match_authors():
    """SKILL.md prohibited bullets must all be covered by authors.yaml."""
    prohibited = _skill_prohibited_metaphors()
    assert set(prohibited) <= set(EXPECTED_NG), \
        f"SKILL.md lists metaphors outside the pinned NG set: {sorted(set(prohibited) - set(EXPECTED_NG))}"
    missing = prohibited - _all_ng_examples()
    assert not missing, f"SKILL.md prohibited metaphors missing from authors: {missing}"
