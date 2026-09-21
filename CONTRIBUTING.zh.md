# 为 Tsumugy-Narrative 做贡献

其他语言版本: [English](CONTRIBUTING.md) · [日本語](CONTRIBUTING.ja.md)。以英文版为正本；如译文与英文版不一致，以英文版为准。

感谢您的贡献。请保持每次变更小而聚焦，以便快速评审。

## 许可证

参与贡献即表示您同意您的贡献将在 MIT 许可证下提供（inbound = outbound）。

## 使用语言

Issue 和 Pull Request 可以使用日语或英语撰写。

## 贡献步骤

1. Fork 本仓库，并从 `master` 为单个主题创建分支。
2. 进行修改。每次只聚焦一个主题，不要混入无关的编辑。
3. 若改动了 `SKILL.md`、`locales/`、`dictionaries/` 或 `tools/verify_narrative.py`、`tools/pick_authors.py`、`tools/serial_store.py`，请重建发布包：`py -X utf8 tools/build_skill_package.py`。这会更新 `dist/narrative-formatter.skill` 与 `plugins/tsumugy-narrative/skills/narrative-formatter/`，两者均为已提交的构建产物，请勿手工编辑。
4. 运行测试套件: `py -X utf8 -m pytest tests/ -q`。
5. 用日语或英语提交 Pull Request，说明改了什么以及为什么改。

## Pull Request 检查清单

- [ ] `py -X utf8 -m pytest tests/ -q` 已通过（如不适用请说明原因）。
- [ ] 本次变更只聚焦一个主题，不包含无关的编辑。
- [ ] 我同意我的贡献将在 MIT 许可证下提供（inbound = outbound）。

## 报告 Issue

请用日语或英语提交 Issue，写明您的操作、预期结果和实际结果，并附上可复现问题的步骤或示例。
