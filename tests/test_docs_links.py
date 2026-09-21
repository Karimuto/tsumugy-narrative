"""
tests/test_docs_links.py
Documentation link integrity (issues #20-#22, parent #11; #16 prunes the
install doc and submission packs): every markdown link and image target in
the eight-README set resolves to a real file. The not-yet-translated
allowlist is empty since #22 landed all translations; any new dead target
fails.

No live network: external references are shape-checked as well-formed https
URLs only. Reachability at publish time is a human gate, not this test.

Full set: eight READMEs (EN canonical + seven renders of the frozen Japanese
source). docs/install.ja.md and docs/submit/*.ja.md were removed in #16
(install matrix lives in the READMEs; submit packs are local-only history),
so they are intentionally absent from LINK_DOCS.
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent

DOCS = [REPO_ROOT / name for name in [
    "README.md",
    "README.ja.md",
    "README.zh.md",
    "README.ko.md",
    "README.ar.md",
    "README.es.md",
    "README.fr.md",
    "README.ru.md",
]]

# Every doc carrying links must resolve them; switcher-block shape stays
# README-only.
LINK_DOCS = DOCS

# Final sibling names carried by all eight switcher blocks (#20 format freeze).
FROZEN_SIBLINGS = [
    "README.md",
    "README.ja.md",
    "README.zh.md",
    "README.ko.md",
    "README.ar.md",
    "README.es.md",
    "README.fr.md",
    "README.ru.md",
]

# All translations landed in #22, so nothing may miss. Any dead internal target
# fails; any entry re-added here must be referenced and actually missing.
EXPECTED_MISSING: set[str] = set()

_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
_BARE_URL_RE = re.compile(r"https?://[^\s)\"'<>\]]+")


def _strip_fences(text: str) -> str:
    """Drop fenced code blocks so sample story text never parses as links."""
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def _link_targets(text: str) -> list[str]:
    targets: list[str] = []
    for m in _LINK_RE.finditer(_strip_fences(text)):
        raw = m.group(1).strip()
        if not raw:
            continue
        target = raw.split()[0].strip("<>")
        if target:
            targets.append(target)
    return targets


def _bare_urls(text: str) -> list[str]:
    return [m.group(0).rstrip(".,;:!?") for m in _BARE_URL_RE.finditer(text)]


def _check_external(url: str, where: str) -> None:
    parts = urlparse(url)
    assert parts.scheme == "https", f"{where}: external ref must be https: {url!r}"
    assert parts.netloc and " " not in url, f"{where}: malformed URL: {url!r}"


def _anchors(text: str) -> set[str]:
    """GitHub heading anchors for `#fragment` targets (#21 adds such links)."""
    found: set[str] = set()
    for m in re.finditer(r"^#{1,6}\s+(.*?)\s*$", text, re.MULTILINE):
        title = re.sub(r"<[^>]+>", "", m.group(1)).replace("`", "")
        slug = re.sub(r"[^\w\s\-]", "", title.lower(), flags=re.UNICODE)
        found.add(slug.strip().replace(" ", "-"))
    return found


def _read(doc: Path) -> str:
    return doc.read_text(encoding="utf-8-sig")


def test_readme_docs_exist():
    for doc in LINK_DOCS:
        assert doc.is_file(), f"doc in the existing set is missing: {doc}"


def test_switcher_blocks_carry_final_sibling_names():
    """Every README links all seven siblings (the file itself is the eighth)."""
    for doc in DOCS:
        targets = {t.split("#")[0] for t in _link_targets(_read(doc))}
        want = {s for s in FROZEN_SIBLINGS if s != doc.name}
        assert want <= targets, f"{doc.name}: switcher missing siblings: {sorted(want - targets)}"


def test_internal_link_targets_resolve():
    dead: list[str] = []
    for doc in LINK_DOCS:
        text = _read(doc)
        for target in _link_targets(text):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                _check_external(target, doc.name)
                continue
            path_part, _, frag = target.partition("#")
            if not path_part:
                assert frag in _anchors(text), f"{doc.name}: dead anchor: {target!r}"
                continue
            if not (doc.parent / path_part).is_file() and path_part not in EXPECTED_MISSING:
                dead.append(f"{doc.name} -> {target}")
                continue
            if frag and (doc.parent / path_part).is_file():
                dest = (doc.parent / path_part).read_text(encoding="utf-8-sig")
                assert frag in _anchors(dest), f"{doc.name}: dead anchor: {target!r}"
    assert not dead, f"dead internal links (only {sorted(EXPECTED_MISSING)} may miss): {dead}"


def test_missing_allowlist_matches_reality():
    for name in EXPECTED_MISSING:
        assert not (REPO_ROOT / name).exists(), (
            f"{name} now exists; drop it from EXPECTED_MISSING (translation landed)"
        )
    referenced = set()
    for doc in DOCS:
        referenced.update(t.split("#")[0] for t in _link_targets(_read(doc)))
    assert EXPECTED_MISSING <= referenced, (
        f"allowlist drift, unreferenced: {sorted(EXPECTED_MISSING - referenced)}"
    )


def test_external_references_are_well_formed_https():
    for doc in LINK_DOCS:
        for url in _bare_urls(_read(doc)):
            _check_external(url, doc.name)
