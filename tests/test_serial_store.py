"""
tests/test_serial_store.py
TDD: tools/serial_store.py interface
- Layout: $TSUMUGY_SERIAL_ROOT/{thread_id}/ep{N}.md, ledger.md, meta.json
- CLI: --read / --append / --init / --list
- Atomic writes (no corruption on concurrent append)
- Round-trip persistence across invocations
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "tools" / "serial_store.py"


@pytest.fixture
def serial_root(tmp_path, monkeypatch):
    root = tmp_path / "serial"
    root.mkdir()
    monkeypatch.setenv("TSUMUGY_SERIAL_ROOT", str(root))
    return root


def _run(*args, env_extra=None):
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        env=env, capture_output=True, text=True, encoding="utf-8",
    )
    return r


def test_serial_init_creates_directory(serial_root):
    r = _run("--init", "--thread-id", "th01")
    assert r.returncode == 0, r.stderr
    assert (serial_root / "th01" / "meta.json").exists()


def test_serial_init_meta_json_shape(serial_root):
    _run("--init", "--thread-id", "th01")
    meta = json.loads((serial_root / "th01" / "meta.json").read_text(encoding="utf-8"))
    for key in ("thread_id", "created_at", "last_episode", "mode"):
        assert key in meta, f"meta.json missing {key!r}"


def test_serial_append_then_read(serial_root, tmp_path):
    _run("--init", "--thread-id", "th01")
    ep = tmp_path / "ep1.md"
    ep.write_text("First episode body. 光。音。 🌅\n", encoding="utf-8")
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps({"characters": ["aoi"], "facts": ["fact1"]}), encoding="utf-8")
    r = _run(
        "--append", "--thread-id", "th01",
        "--episode-md", str(ep), "--ledger-update", str(ledger),
    )
    assert r.returncode == 0, r.stderr

    # Read back
    r = _run("--read", "--thread-id", "th01")
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert "episodes" in out
    assert "ledger" in out
    assert len(out["episodes"]) == 1
    assert out["episodes"][0]["body"].startswith("First episode body")
    assert out["ledger"]["characters"] == ["aoi"]


def test_serial_append_increments_episode_number(serial_root, tmp_path):
    _run("--init", "--thread-id", "th01")
    work = tmp_path / "increments"
    work.mkdir()
    for i in range(1, 4):
        ep = work / f"ep{i}.md"
        ep.write_text(f"episode {i} body\n", encoding="utf-8")
        led = work / f"l{i}.json"
        led.write_text(json.dumps({"c": i}), encoding="utf-8")
        r = _run(
            "--append", "--thread-id", "th01",
            "--episode-md", str(ep), "--ledger-update", str(led),
        )
        assert r.returncode == 0, r.stderr
    # Files on disk
    for i in range(1, 4):
        assert (serial_root / "th01" / f"ep{i}.md").exists()
    # meta last_episode = 3
    meta = json.loads((serial_root / "th01" / "meta.json").read_text(encoding="utf-8"))
    assert meta["last_episode"] == 3


def test_serial_read_before_init_fails(serial_root):
    r = _run("--read", "--thread-id", "nope")
    assert r.returncode != 0
    assert "not found" in r.stderr.lower() or "not initialised" in r.stderr.lower()


def test_serial_ledger_persists_across_appends(serial_root, tmp_path):
    _run("--init", "--thread-id", "th01")
    # ep1
    ep1 = tmp_path / "ep1.md"
    ep1.write_text("ep1\n", encoding="utf-8")
    led1 = tmp_path / "l1.json"
    led1.write_text(json.dumps({"characters": ["x"]}), encoding="utf-8")
    _run("--append", "--thread-id", "th01", "--episode-md", str(ep1), "--ledger-update", str(led1))
    # ep2: ledger should be MERGED with prior
    ep2 = tmp_path / "ep2.md"
    ep2.write_text("ep2\n", encoding="utf-8")
    led2 = tmp_path / "l2.json"
    led2.write_text(json.dumps({"facts": ["f1"]}), encoding="utf-8")
    _run("--append", "--thread-id", "th01", "--episode-md", str(ep2), "--ledger-update", str(led2))

    ledger = (serial_root / "th01" / "ledger.md").read_text(encoding="utf-8")
    assert "x" in ledger
    assert "f1" in ledger


def test_serial_atomic_write_no_corruption(serial_root, tmp_path):
    """Concurrent appends must not produce a torn file."""
    import threading
    _run("--init", "--thread-id", "th01")
    errors = []

    def append_one(i):
        ep = tmp_path / f"ep_concurrent_{i}.md"
        ep.write_text(f"CONCURRENT_EP_{i}\n", encoding="utf-8")
        led = tmp_path / f"l_concurrent_{i}.json"
        led.write_text(json.dumps({"c": i}), encoding="utf-8")
        r = _run("--append", "--thread-id", "th01", "--episode-md", str(ep), "--ledger-update", str(led))
        if r.returncode != 0:
            errors.append(r.stderr)

    threads = [threading.Thread(target=append_one, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert errors == [], f"concurrent append errors: {errors}"
    # All 5 episodes present
    r = _run("--read", "--thread-id", "th01")
    out = json.loads(r.stdout)
    assert len(out["episodes"]) == 5
    bodies = "".join(ep["body"] for ep in out["episodes"])
    for i in range(5):
        assert f"CONCURRENT_EP_{i}" in bodies, f"missing episode {i}"


def test_serial_list_threads(serial_root):
    _run("--init", "--thread-id", "aaa")
    _run("--init", "--thread-id", "bbb")
    r = _run("--list")
    assert r.returncode == 0
    threads = json.loads(r.stdout)
    assert "aaa" in threads
    assert "bbb" in threads
