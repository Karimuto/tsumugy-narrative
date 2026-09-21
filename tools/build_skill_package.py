#!/usr/bin/env python3
"""
tools/build_skill_package.py

Assembles the distributable skill package from the repo sources so every
install route (Claude app upload, Claude Code marketplace, manual copy)
ships the same bytes:

  dist/narrative-formatter.skill
      ZIP whose root is the skill folder (Claude upload requirement):
      narrative-formatter/SKILL.md (+ skill.md mirror), locales/,
      dictionaries/, tools/*.py
  plugins/tsumugy-narrative/skills/narrative-formatter/
      Same tree, for the .claude-plugin/marketplace.json entry.

Deterministic output: sorted entries, fixed timestamps, so the freshness
test can byte-compare the committed artifacts against a rebuild.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR_NAME = "narrative-formatter"

# (source in repo, destination inside the skill folder)
SOURCES: list[tuple[Path, Path]] = [
    (REPO_ROOT / "SKILL.md", Path(SKILL_DIR_NAME) / "SKILL.md"),
]

# Whole directories copied as-is.
COPY_DIRS = ("locales", "dictionaries")

# Runtime tools the skill invokes; dev-only helpers stay out.
COPY_TOOLS = ("verify_narrative.py", "pick_authors.py", "serial_store.py")

ZIP_EPOCH = (2026, 1, 1, 0, 0, 0)

DIST_ZIP = REPO_ROOT / "dist" / "narrative-formatter.skill"
PLUGIN_SKILL_DIR = (
    REPO_ROOT / "plugins" / "tsumugy-narrative" / "skills" / SKILL_DIR_NAME
)


def collect() -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for src, dest in SOURCES:
        files[dest.as_posix()] = src.read_bytes()
    # NOTE: SKILL.md only, no lowercase skill.md mirror. Claude's uploader
    # rejects zips whose paths collide case-insensitively
    # ("Zip file contains duplicate paths").
    for dirname in COPY_DIRS:
        for src in sorted((REPO_ROOT / dirname).rglob("*")):
            if src.is_file():
                dest = Path(SKILL_DIR_NAME) / dirname / src.relative_to(
                    REPO_ROOT / dirname
                )
                files[dest.as_posix()] = src.read_bytes()
    for tool in COPY_TOOLS:
        src = REPO_ROOT / "tools" / tool
        files[(Path(SKILL_DIR_NAME) / "tools" / tool).as_posix()] = (
            src.read_bytes()
        )
    folded = [n.lower() for n in files]
    assert len(set(folded)) == len(files), "case-insensitive path collision"
    return files


def write_zip(files: dict[str, bytes], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, date_time=ZIP_EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, files[name])


def write_plugin_dir(files: dict[str, bytes], root: Path) -> None:
    prefix = SKILL_DIR_NAME + "/"
    for name, data in files.items():
        assert name.startswith(prefix), name
        dest = root / name[len(prefix):]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    # Prune stale files from earlier builds.
    wanted = {name[len(prefix):] for name in files}
    for existing in sorted(root.rglob("*")):
        if existing.is_file() and existing.relative_to(root).as_posix() not in wanted:
            existing.unlink()
def dist_files() -> dict[str, bytes]:
    """Dist ZIP layout: locale deltas renamed so the archive holds exactly
    one SKILL.md (Claude upload requirement). The plugin dir keeps the repo
    layout, where nested SKILL.md files are valid agent skills."""
    out: dict[str, bytes] = {}
    for name, data in collect().items():
        segs = name.split("/")
        if (
            len(segs) == 4
            and segs[0] == SKILL_DIR_NAME
            and segs[1] == "locales"
            and segs[3] == "SKILL.md"
        ):
            name = "/".join(segs[:3] + ["locale.md"])
        out[name] = data
    basenames = [n.rsplit("/", 1)[-1].lower() for n in out]
    assert basenames.count("skill.md") == 1, "dist must hold exactly one SKILL.md"
    return out


def main() -> int:
    files = collect()
    # Every packaged SKILL.md must carry the harness-required frontmatter.
    head = files[f"{SKILL_DIR_NAME}/SKILL.md"].decode("utf-8").split("---")[1]
    assert "name:" in head and "description:" in head, "frontmatter missing"
    write_zip(dist_files(), DIST_ZIP)
    write_plugin_dir(files, PLUGIN_SKILL_DIR)
    print(f"wrote {DIST_ZIP} ({DIST_ZIP.stat().st_size} bytes)")
    print(f"synced {PLUGIN_SKILL_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
