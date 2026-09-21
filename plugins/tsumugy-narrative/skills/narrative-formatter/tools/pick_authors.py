#!/usr/bin/env python3
"""Deterministic pick-2 draw over the author voices (issue #15).

Draws two distinct voices from the twelve (common eight plus the locale
delta four), or from the common eight with --common-only. A fixed --seed
reproduces the same pair; without it the seed comes from the OS entropy
pool and is echoed to stderr. Output lines keep the story output shape
``voice: XX (shelf label)`` and never carry real author names.

Usage:
  py tools/pick_authors.py --locale ja --seed 7

Episodic: redraw per story, write with the better-fitting voice.
Serial: draw once for the first episode, keep that voice for the whole
thread, and record the real-name choice in the ledger via
tools/serial_store.py --append --thread-id ID --episode-md EP
--ledger-update JSON (internal record, never shown in output).
The verifier never checks randomness (ADR-0005); the code tables below
must match SKILL.md plus locales/*/SKILL.md (tests enforce this).
"""
from __future__ import annotations

import argparse
import random
import secrets
import sys

COMMON = (
    ("DO", "psychological-novel style"),
    ("LX", "social-critique style"),
    ("HE", "spare-prose style"),
    ("GM", "marvellous-everyday style"),
    ("DA", "fragile-confession style"),
    ("KU", "playful-thought style"),
    ("MA", "crowded-street style"),
    ("MO", "embodied-memory style"),
)

EXTRAS = {
    "ja": (
        ("KA", "抒情美文風"),
        ("AK", "短編綺譚風"),
        ("YO", "温情小説風"),
        ("MU", "都市幻想風"),
    ),
    "en": (
        ("WO", "stream-of-consciousness style"),
        ("LG", "speculative-thought style"),
        ("VO", "dark-comic style"),
        ("KA", "bureaucratic-dread style"),
    ),
    "zh": (
        ("LS", "京味街头风"),
        ("MY", "幻觉乡土风"),
        ("YH", "苦难忍耐风"),
        ("BJ", "家族激流风"),
    ),
    "ko": (
        ("HY", "침묵저항풍"),
        ("PA", "대하소설풍"),
        ("HW", "서정단편풍"),
        ("KI", "해학마을풍"),
    ),
    "ar": (
        ("TH", "بصيرة التراث"),
        ("GH", "شهادة الشتات"),
        ("MD", "وطن في الشعر"),
        ("GI", "نبي الحب والعمل"),
    ),
    "es": (
        ("BO", "laberinto infinito"),
        ("AL", "espíritus domésticos"),
        ("JM", "frases de la duda"),
        ("CO", "juego metafísico"),
    ),
    "fr": (
        ("CA", "révolte absurde"),
        ("SE", "regard d’enfant"),
        ("DU", "voix du désir"),
        ("MD", "mémoire manquante"),
    ),
    "ru": (
        ("TO", "нравственная панорама"),
        ("CH", "тихий подтекст"),
        ("BU", "чертовщина в быту"),
        ("PA", "проза в стихах"),
    ),
}

COMMON_LABEL = {
    "ja": ("心理小説風", "社会批評風", "簡潔文体風", "日常幻想風",
           "私小説風", "随想小説風", "群像劇風", "記憶文学風"),
    "zh": ("心理小说风", "社会批判风", "简练文体风", "日常幻实风",
           "私小说风", "随笔小说风", "群像街区风", "记忆文学风"),
    "ko": ("심리소설풍", "사회비판풍", "간결문체풍", "일상환상풍",
           "사소설풍", "수상소설풍", "군상극풍", "기억문학풍"),
    "ar": ("رواية نفسية", "نقد اجتماعي", "نثر مقتضب", "عجائبي يومي",
           "اعتراف هش", "رواية-مقالة", "تعدد أصوات الشارع", "رواية الذاكرة"),
    "es": ("novela psicológica", "crítica social", "prosa escueta",
           "maravilla cotidiana", "confesión frágil", "novela-ensayo",
           "polifonía callejera", "novela de la memoria"),
    "fr": ("roman psychologique", "critique sociale", "prose dépouillée",
           "merveilleux quotidien", "confession fragile", "roman-essai",
           "polyphonie des rues", "roman de la mémoire"),
    "ru": ("психологический роман", "социальная критика", "скупая проза",
           "чудесное в обыденном", "хрупкая исповедь", "роман-эссе",
           "многоголосие улиц", "роман памяти"),
}

LOCALES = sorted(EXTRAS)


def _ensure_utf8_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def build_pool(locale: str = "en") -> list[dict]:
    """Voice pool for a locale: 12 entries, or the common 8 for "common"."""
    if locale == "common":
        return [{"code": c, "label": lab} for c, lab in COMMON]
    if locale not in EXTRAS:
        raise KeyError(f"unknown locale: {locale} (expected one of {LOCALES})")
    labels = COMMON_LABEL.get(locale, tuple(lab for _, lab in COMMON))
    pool = [{"code": c, "label": lab} for (c, _), lab in zip(COMMON, labels)]
    pool += [{"code": c, "label": lab} for c, lab in EXTRAS[locale]]
    return pool


def _coerce_seed(seed) -> int | str:
    if seed is None:
        return secrets.randbits(63)
    try:
        return int(seed)
    except (TypeError, ValueError):
        return str(seed)


def draw(locale: str = "en", seed=None) -> list[dict]:
    """Two distinct pool voices; same seed gives the same pair."""
    pool = build_pool(locale)
    return random.Random(_coerce_seed(seed)).sample(pool, 2)


def format_line(pick: dict) -> str:
    return f"voice: {pick['code']} ({pick['label']})"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="pick_authors",
        description="Draw two author voices without bias: seed-fixed and reproducible.",
        epilog="Example: py tools/pick_authors.py --locale ja --seed 7. "
        "Episodic: redraw per story. Serial: draw once for the first "
        "episode, keep it for the whole thread, record the choice in the "
        "ledger (serial_store --ledger-update). The verifier never checks "
        "randomness.",
    )
    p.add_argument("--locale", default="en", help=f"one of {LOCALES} (default en)")
    p.add_argument("--common-only", action="store_true",
                   help="draw from the common eight instead of the locale twelve")
    p.add_argument("--seed", default=None, help="reproducible draw key (default: OS entropy)")
    args = p.parse_args(argv)

    locale = "common" if args.common_only else args.locale
    try:
        build_pool(locale)
    except KeyError as e:
        print(e, file=sys.stderr)
        return 2
    seed = _coerce_seed(args.seed)
    if args.seed is None:
        print(f"seed: {seed}", file=sys.stderr)
    for pick in draw(locale, seed=seed):
        print(format_line(pick))
    return 0


if __name__ == "__main__":
    _ensure_utf8_stdout()
    raise SystemExit(main())
