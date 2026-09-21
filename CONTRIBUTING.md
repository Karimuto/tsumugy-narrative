# Contributing to Tsumugy-Narrative

Read this in: [日本語](CONTRIBUTING.ja.md) · [中文](CONTRIBUTING.zh.md). English is the canonical version; if translations differ, this file takes precedence.

Thank you for contributing. Keep changes small and focused so review stays fast.

## License

By contributing, you agree that your contributions will be licensed under the MIT License (inbound = outbound).

## Languages

Issues and pull requests may be written in Japanese or English.

## How to contribute

1. Fork the repository and create a branch from `master` for one topic.
2. Make your change. Keep it limited to one topic; do not mix unrelated edits.
3. If you touched `SKILL.md`, `locales/`, `dictionaries/`, or `tools/verify_narrative.py`, `tools/pick_authors.py`, `tools/serial_store.py`, rebuild the distributables: `py -X utf8 tools/build_skill_package.py`. This refreshes `dist/narrative-formatter.skill` and `plugins/tsumugy-narrative/skills/narrative-formatter/`; both are committed build output, never hand-edited.
4. Run the test suite: `py -X utf8 -m pytest tests/ -q`.
5. Open a pull request in Japanese or English. Describe what changed and why.

## Pull-request checklist

- [ ] `py -X utf8 -m pytest tests/ -q` passes (or explain why it does not apply).
- [ ] The change is limited to one topic with no unrelated edits.
- [ ] I agree that my contribution is licensed under the MIT License (inbound = outbound).

## Reporting issues

Open an issue in Japanese or English. Include what you did, what you expected, and what happened instead, with steps or examples that reproduce the problem.
