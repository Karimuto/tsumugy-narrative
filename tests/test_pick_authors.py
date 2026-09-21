"""Tests for tools/pick_authors.py (issue #15).

Deterministic pick-2 draw from the twelve author voices
(common eight + locale delta four). Stdlib only.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import pick_authors

LOCALES = ["ja", "en", "zh", "ko", "ar", "es", "fr", "ru"]


def _skill_codebook(locale):
    """Parse the voice codebook out of the SKILL files.

    Returns {code: label}. Root SKILL.md holds the common eight in
    `- XX: label` shape; each locale delta holds all twelve in
    `- XX (Name): label` shape, except en which lists only its four
    extras (common eight live in the canonical skill).
    """
    books = {}
    root = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for m in re.finditer(r"^-\s+([A-Z]{2}):\s+(.+)$", root, re.MULTILINE):
        books[m.group(1)] = m.group(2).strip()
    if locale == "common":
        return books
    text = (ROOT / "locales" / locale / "SKILL.md").read_text(encoding="utf-8")
    full = {}
    for m in re.finditer(r"^-\s+([A-Z]{2})\s+\(.+\):\s+(.+)$", text, re.MULTILINE):
        full[m.group(1)] = m.group(2).strip()
    if locale == "en":
        full = {**books, **full}
    assert len(full) == 12, f"{locale}: expected 12 codebook rows, got {len(full)}"
    return full


def _real_names():
    names = set()
    for path in sorted((ROOT / "locales").glob("*/authors.yaml")):
        for line in path.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s.startswith("name:"):
                names.add(s[len("name:"):].strip())
    for locale in LOCALES:
        text = (ROOT / "locales" / locale / "SKILL.md").read_text(encoding="utf-8")
        for m in re.finditer(r"^-\s+[A-Z]{2}\s+\((.+)\):\s+.+$", text, re.MULTILINE):
            names.add(m.group(1).strip())
    root = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for m in re.finditer(r"^-\s+(.+?)\s+\[[A-Z]{2}\],", root, re.MULTILINE):
        names.add(m.group(1).strip())
    return {n for n in names if n}


def test_same_seed_same_result():
    for locale in ["ja", "en", "common"]:
        a = pick_authors.draw(locale, seed=42)
        b = pick_authors.draw(locale, seed=42)
        assert a == b, f"{locale}: same seed must give same pair"


def test_draw_two_without_duplicates():
    for locale in LOCALES + ["common"]:
        for seed in range(20):
            picks = pick_authors.draw(locale, seed=seed)
            assert len(picks) == 2, f"{locale}/{seed}: must draw exactly two"
            assert picks[0]["code"] != picks[1]["code"], \
                f"{locale}/{seed}: picks must not repeat"


def test_pool_sizes():
    assert len(pick_authors.build_pool("common")) == 8
    for locale in LOCALES:
        assert len(pick_authors.build_pool(locale)) == 12, locale


def test_pool_matches_skill_codebooks():
    for locale in LOCALES + ["common"]:
        pool = {e["code"]: e["label"] for e in pick_authors.build_pool(locale)}
        assert pool == _skill_codebook(locale), f"{locale}: pool drifted from SKILL"


def test_draw_covers_pool():
    seen = set()
    for seed in range(200):
        for p in pick_authors.draw("ja", seed=seed):
            seen.add(p["code"])
    assert seen == set(_skill_codebook("ja")), f"unseen codes: {seen ^ set(_skill_codebook('ja'))}"


def test_output_has_no_real_names():
    names = _real_names()
    assert names, "expected a non-empty author-name set"
    for locale in LOCALES + ["common"]:
        for seed in (1, 7, 42):
            for p in pick_authors.draw(locale, seed=seed):
                line = pick_authors.format_line(p)
                for n in names:
                    assert n.casefold() not in line.casefold(), f"{locale}: leak: {n}"


def test_voice_line_shape():
    p = pick_authors.draw("ja", seed=7)[0]
    assert re.fullmatch(r"voice: [A-Z]{2} \(.+\)", pick_authors.format_line(p)), \
        pick_authors.format_line(p)


def test_unknown_locale_fails():
    try:
        pick_authors.build_pool("xx")
    except (KeyError, ValueError, SystemExit):
        return
    raise AssertionError("unknown locale must fail")


def test_help_documents_serial_vs_episodic():
    out = subprocess.run([sys.executable, str(ROOT / "tools" / "pick_authors.py"),
                          "--help"], capture_output=True, text=True).stdout.lower()
    for word in ("serial", "episodic", "ledger", "seed"):
        assert word in out, f"--help must explain {word}"


def test_verifier_has_no_randomness_check():
    src = (ROOT / "tools" / "verify_narrative.py").read_text(encoding="utf-8")
    assert "import random" not in src and "from random" not in src
    assert "randomness" not in src.casefold()


def test_cli_draws_two():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "pick_authors.py"),
         "--locale", "ja", "--seed", "7"],
        capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    assert len(lines) == 2, proc.stdout
    assert all(re.fullmatch(r"voice: [A-Z]{2} \(.+\)", ln.strip()) for ln in lines), \
        proc.stdout
