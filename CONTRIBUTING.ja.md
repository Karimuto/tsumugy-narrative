# Tsumugy-Narrative へのコントリビュート

他の言語で読む: [English](CONTRIBUTING.md) · [中文](CONTRIBUTING.zh.md)。正本は英語版であり、翻訳との差異がある場合は英語版が優先されます。

コントリビュートありがとうございます。レビューを速くするため、変更は小さく一つに絞ってください。

## ライセンス

コントリビュートにより、あなたの寄稿は MIT ライセンスの下で提供されることに同意したものとみなされます（inbound = outbound）。

## 使用言語

Issue と Pull Request は日本語または英語で記述できます。

## 貢献の手順

1. リポジトリをフォークし、`master` からトピックごとにブランチを作成します。
2. 変更を行います。一つのトピックに絞り、無関係な編集を混ぜないでください。
3. `SKILL.md`・`locales/`・`dictionaries/`・`tools/verify_narrative.py`・`tools/pick_authors.py`・`tools/serial_store.py` に触れたら配布物を再ビルドします: `py -X utf8 tools/build_skill_package.py`。`dist/narrative-formatter.skill` と `plugins/tsumugy-narrative/skills/narrative-formatter/` が更新されます。どちらもコミットされる生成物で、手編集はしません。
4. テストスイートを実行します: `py -X utf8 -m pytest tests/ -q`。
5. 日本語または英語で Pull Request を開きます。何を・なぜ変更したかを記述してください。

## Pull Request のチェックリスト

- [ ] `py -X utf8 -m pytest tests/ -q` が通る（対象外の場合は理由を説明）。
- [ ] 変更は一つのトピックに絞られており、無関係な編集を含まない。
- [ ] 自分の寄稿が MIT ライセンスの下で提供されることに同意する（inbound = outbound）。

## Issue の報告

Issue は日本語または英語で開いてください。実行内容、期待した結果、実際の結果を、再現手順や例とともに記載してください。
