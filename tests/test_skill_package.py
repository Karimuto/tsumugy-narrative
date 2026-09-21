"""
tests/test_skill_package.py

Distribution freshness (issue #21 follow-up, parent #11): the committed
one-click artifacts must match what tools/build_skill_package.py assembles
from the repo sources, so the Claude upload and the marketplace entry can
never drift from SKILL.md.

Asserts artifact bytes, never prose or layout.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import build_skill_package as builder  # noqa: E402

SKILL = "narrative-formatter"


def test_committed_artifacts_match_rebuild():
    files = builder.collect()
    assert f"{SKILL}/SKILL.md" in files
    assert files[f"{SKILL}/SKILL.md"] == (REPO_ROOT / "SKILL.md").read_bytes()
    # No lowercase skill.md mirror: Claude's uploader rejects zips whose
    # entries collide case-insensitively ("duplicate paths").
    assert f"{SKILL}/skill.md" not in files

    dist = builder.dist_files()
    basenames = [n.rsplit("/", 1)[-1].lower() for n in dist]
    assert basenames.count("skill.md") == 1, "dist must hold exactly one SKILL.md"
    with zipfile.ZipFile(builder.DIST_ZIP) as zf:
        names = zf.namelist()
        assert names == sorted(names), "zip entries must be deterministic"
        assert names and all(n.startswith(f"{SKILL}/") for n in names), (
            "zip root must be the skill folder (Claude upload requirement)"
        )
        folded = [n.lower() for n in names]
        assert len(set(folded)) == len(names), "duplicate paths in zip"
        for name in names:
            assert zf.read(name) == dist[name], f"stale zip entry: {name}"

    plugin_files = {
        p.relative_to(builder.PLUGIN_SKILL_DIR).as_posix(): p.read_bytes()
        for p in builder.PLUGIN_SKILL_DIR.rglob("*")
        if p.is_file()
    }
    prefix = f"{SKILL}/"
    want = {n[len(prefix):]: data for n, data in files.items()}
    assert plugin_files == want, (
        "marketplace plugin dir out of sync; rerun builder"
    )
