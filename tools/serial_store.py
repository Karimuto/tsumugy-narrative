"""
tools/serial_store.py
CLI for the serial-mode memory layer of tsumugy-narrative.

Layout: $TSUMUGY_SERIAL_ROOT/{thread_id}/ep{N}.md, ledger.md, meta.json

Commands:
  --init    --thread-id ID
  --append  --thread-id ID --episode-md PATH --ledger-update PATH
  --read    --thread-id ID
  --list

All writes are atomic (tempfile + os.replace) and ledger updates are merged
shallowly (new keys override, prior keys preserved).
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import tempfile
from pathlib import Path


def _root() -> Path:
    return Path(os.environ.get("TSUMUGY_SERIAL_ROOT", str(Path.home() / ".tsumugy" / "serial")))


def _thread_dir(thread_id: str) -> Path:
    return _root() / thread_id


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Try a few times: on Windows os.replace can hit a transient
    # WinError 5 if another process is mid-rename on the same path.
    last: Exception | None = None
    for _ in range(8):
        fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            try:
                os.replace(tmp, path)
                return
            except PermissionError as e:
                last = e
                # brief backoff
                import time as _t
                _t.sleep(0.02)
        except Exception:
            if os.path.exists(tmp):
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
            raise
    # Exhausted retries
    if os.path.exists(tmp):
        try:
            os.unlink(tmp)
        except OSError:
            pass
    raise RuntimeError(f"atomic_write failed after retries: {path} ({last})")


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _ensure_utf8_stdout() -> None:
    """Reconfigure stdout to UTF-8 so emoji / CJK survive Windows cp1252/cp932."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass


def _read_meta(d: Path) -> dict:
    return json.loads((d / "meta.json").read_text(encoding="utf-8"))


def _write_meta(d: Path, meta: dict) -> None:
    _atomic_write(d / "meta.json", json.dumps(meta, ensure_ascii=False, indent=2) + "\n")


def _lock_path(d: Path) -> Path:
    return d / ".append.lock"


class _FileLock:
    """Cooperative exclusive lock. Cross-platform (fcntl on POSIX,
    msvcrt on Windows). Released in __exit__."""
    def __init__(self, path: Path, timeout: float = 5.0, poll: float = 0.05):
        self.path = path
        self.timeout = timeout
        self.poll = poll
        self._fh = None

    def __enter__(self):
        import time as _t
        path = self.path
        path.parent.mkdir(parents=True, exist_ok=True)
        deadline = _t.time() + self.timeout
        while True:
            try:
                # Open in binary append mode; this is atomic on Windows when
                # using os.open with O_CREAT|O_EXCL, but we use a simpler
                # "open then check exclusive" pattern.
                fh = open(path, "a+b")
                break
            except OSError:
                if _t.time() > deadline:
                    raise
                _t.sleep(self.poll)
        # Acquire exclusive lock (no-op on POSIX without fcntl, but Windows
        # msvcrt.locking provides the actual exclusion)
        self._fh = fh
        try:
            import msvcrt  # type: ignore
            # Lock 1 byte at offset 0
            while True:
                try:
                    fh.seek(0)
                    msvcrt.locking(fh.fileno(), msvcrt.LK_LOCK, 1)
                    break
                except OSError:
                    if _t.time() > deadline:
                        raise
                    _t.sleep(self.poll)
        except ImportError:
            # POSIX fallback: fcntl flock
            try:
                import fcntl  # type: ignore
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            except ImportError:
                pass
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._fh is not None:
            try:
                self._fh.flush()
            except OSError:
                pass
            try:
                import msvcrt  # type: ignore
                try:
                    self._fh.seek(0)
                    msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass
            except ImportError:
                pass
            try:
                self._fh.close()
            except OSError:
                pass
            self._fh = None


def _read_ledger(d: Path) -> dict:
    p = d / "ledger.md"
    if not p.exists():
        return {}
    text = p.read_text(encoding="utf-8").strip()
    if not text:
        return {}
    # ledger.md is a fenced JSON block
    if text.startswith("```"):
        body = text.split("```", 2)[1]
        if body.startswith("json"):
            body = body[4:]
        body = body.strip()
        return json.loads(body)
    return json.loads(text)


def _write_ledger(d: Path, ledger: dict) -> None:
    body = json.dumps(ledger, ensure_ascii=False, indent=2)
    _atomic_write(d / "ledger.md", "```json\n" + body + "\n```\n")


def cmd_init(args) -> int:
    d = _thread_dir(args.thread_id)
    if d.exists() and (d / "meta.json").exists():
        print(f"thread {args.thread_id} already initialised at {d}", file=sys.stderr)
        return 0
    d.mkdir(parents=True, exist_ok=True)
    meta = {
        "thread_id": args.thread_id,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "last_episode": 0,
        "mode": "serial",
    }
    _write_meta(d, meta)
    _atomic_write(d / "ledger.md", "```json\n{}\n```\n")
    print(f"initialised {d}")
    return 0


def _next_ep_num(d: Path) -> int:
    meta = _read_meta(d)
    return int(meta.get("last_episode", 0)) + 1


def cmd_append(args) -> int:
    d = _thread_dir(args.thread_id)
    if not (d / "meta.json").exists():
        print(f"thread not found: {args.thread_id} (run --init first)", file=sys.stderr)
        return 2
    with _FileLock(_lock_path(d)):
        n = _next_ep_num(d)
        ep_path_src = Path(args.episode_md)
        body = ep_path_src.read_text(encoding="utf-8")
        _atomic_write(d / f"ep{n}.md", body)
        # Ledger update
        cur = _read_ledger(d)
        new = json.loads(Path(args.ledger_update).read_text(encoding="utf-8"))
        if not isinstance(new, dict):
            print("--ledger-update must be a JSON object", file=sys.stderr)
            return 2
        # Shallow merge; lists are replaced wholesale
        cur.update(new)
        _write_ledger(d, cur)
        # Meta bump
        meta = _read_meta(d)
        meta["last_episode"] = n
        meta["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _write_meta(d, meta)
    print(f"appended ep{n} to {args.thread_id}")
    return 0


def cmd_read(args) -> int:
    d = _thread_dir(args.thread_id)
    if not (d / "meta.json").exists():
        print(f"thread not initialised: {args.thread_id}", file=sys.stderr)
        return 2
    meta = _read_meta(d)
    episodes = []
    for i in range(1, int(meta.get("last_episode", 0)) + 1):
        p = d / f"ep{i}.md"
        if p.exists():
            episodes.append({"episode": i, "body": p.read_text(encoding="utf-8")})
    ledger = _read_ledger(d)
    out = {"meta": meta, "episodes": episodes, "ledger": ledger}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_list(args) -> int:
    r = _root()
    if not r.exists():
        print("[]")
        return 0
    threads = []
    for child in sorted(r.iterdir()):
        if (child / "meta.json").exists():
            threads.append(child.name)
    print(json.dumps(threads, ensure_ascii=False))
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="serial_store")
    sub = p.add_mutually_exclusive_group(required=True)
    sub.add_argument("--init", action="store_true")
    sub.add_argument("--append", action="store_true")
    sub.add_argument("--read", action="store_true")
    sub.add_argument("--list", action="store_true")
    p.add_argument("--thread-id", dest="thread_id")
    p.add_argument("--episode-md", dest="episode_md")
    p.add_argument("--ledger-update", dest="ledger_update")
    args = p.parse_args(argv)

    if args.init:
        if not args.thread_id:
            print("--init requires --thread-id", file=sys.stderr)
            return 2
        return cmd_init(args)
    if args.append:
        if not (args.thread_id and args.episode_md and args.ledger_update):
            print("--append requires --thread-id, --episode-md, --ledger-update", file=sys.stderr)
            return 2
        return cmd_append(args)
    if args.read:
        if not args.thread_id:
            print("--read requires --thread-id", file=sys.stderr)
            return 2
        return cmd_read(args)
    if args.list:
        return cmd_list(args)
    return 1


if __name__ == "__main__":
    _ensure_utf8_stdout()
    raise SystemExit(main())
