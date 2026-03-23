# 🌍 MultiDoc Translator

[![VS Code](https://img.shields.io/badge/VS%20Code-1.85.0+-blue.svg)](https://code.visualstudio.com/)
[![Version](https://img.shields.io/github/v/release/fatonyahmadfauzi/MultiDoc-Translator?color=blue.svg)](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/releases)
[![License: MIT](https://img.shields.io/github/license/fatonyahmadfauzi/MultiDoc-Translator?color=green.svg)](../../LICENSE)
[![Build Status](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/actions/workflows/main.yml/badge.svg)](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/actions)
[![Repo Size](https://img.shields.io/github/repo-size/fatonyahmadfauzi/MultiDoc-Translator?color=yellow.svg)](https://github.com/fatonyahmadfauzi/MultiDoc-Translator)
[![Last Commit](https://img.shields.io/github/last-commit/fatonyahmadfauzi/MultiDoc-Translator?color=brightgreen.svg)](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/commits/main)
[![Installs](https://vsmarketplacebadges.dev/installs-short/fatonyahmadfauzi.multidoc-translator.svg)](https://marketplace.visualstudio.com/items?itemName=fatonyahmadfauzi.multidoc-translator)
[![Downloads](https://vsmarketplacebadges.dev/downloads-short/fatonyahmadfauzi.multidoc-translator.svg)](https://marketplace.visualstudio.com/items?itemName=fatonyahmadfauzi.multidoc-translator)
[![Rating](https://vsmarketplacebadges.dev/rating-short/fatonyahmadfauzi.multidoc-translator.svg)](https://marketplace.visualstudio.com/items?itemName=fatonyahmadfauzi.multidoc-translator)


> 🌐 他の言語でも利用可能: [English](../../README.md) | [Polski](README-PL.md) | [中文](README-ZH.md) | [Deutsch](README-DE.md) | [Français](README-FR.md) | [Español](README-ES.md) | [Русский](README-RU.md) | [Português](README-PT.md) | [Bahasa Indonesia](README-ID.md) | [한국어](README-KR.md)

---

**無料の Google Translate API** を使用して多言語ドキュメント ファイル (`README.md` および `CHANGELOG.md`) を自動的に生成する Visual Studio Code 拡張機能。API キーは必要ありません。

---

## ✨ 特徴

- 🌍 `README.md` と `CHANGELOG.md` を **10 以上の言語** (インドネシア語、フランス語、ドイツ語、日本語、北京語、スペイン語、ポーランド語、ロシア語、ポルトガル語、韓国語) に自動的に翻訳します。
- ⚙️ **自動変更ログ管理** — `CHANGELOG.md` を検出し、変更ログ セクションが見つからない場合は `README.md` に追加し、それを翻訳します。
- 🔗 **GitHub URL の自動検出** — `package.json` または `.git/config` からリポジトリ URL を取得して、正確なリリース リンクを作成します。
- 🔒 **高度なフレーズ保護** — コード ブロック、インライン コード、URL、技術用語、ブランド名、カスタム フレーズを保護します (正規表現をサポート)。サイドバーから保護されたフレーズを追加、削除、リスト、またはリセットできます。
- 💬 生成された各 README に言語スイッチャー ブロックを追加します (例: `> 🌐 他の言語で利用可能: [Polski](docs/lang/README-PL.md) | [中文](docs/lang/README-ZH.md) | [日本語](docs/lang/README-JP.md) | [ドイツ語](docs/lang/README-DE.md) | [フランス語](docs/lang/README-FR.md) | [スペイン語](docs/lang/README-ES.md) | [Русский](docs/lang/README-RU.md) | [ポルトガル語](docs/lang/README-PT.md) | [インドネシア語](docs/lang/README-ID.md) | [한국어](docs/lang/README-KR.md)
- 🧠 組み込みの Google 翻訳を使用します。アカウントやカスタム API キーは必要ありません。
- 🖱️ 言語の選択、保護の管理、翻訳の実行を行うためのユーザーフレンドリーなサイドバーインターフェイス。
- 📊 詳細な翻訳進行状況の出力を表示します。

---

## ✅ サポートされている VS コードのバージョン

- 最小バージョン : **1.85.0**
- **Windows**、**macOS**、および **Linux** でテスト済み。

---

## 🧩 インストール

### マーケットプレイスから (推奨)

1. **Visual Studio Code** を開きます。
2. **拡張機能** ビュー (`Ctrl+Shift+X`) に移動します。
3. `MultiDoc Translator` を検索します。
4. [**インストール**] をクリックします。

### ソースから (開発用)

1. このリポジトリのクローンを作成します。
   ```bash
   git clone https://github.com/fatonyahmadfauzi/MultiDoc-Translator.git
   cd MultiDoc-Translator
   npm install
   ```
2. VS Code でフォルダーを開きます。
3. **F5** を押して **Extension Development Host** を起動します。
4. 新しいウィンドウで、`README.md` と (オプションで) `CHANGELOG.md` を含むプロジェクトを開きます。
5. MultiDoc Translator サイドバーを開き、言語を選択し、**⚙️多言語 README の生成** をクリックします。

---

## ⌨️ コマンドとショートカット

この拡張機能は、コマンド パレット (`Ctrl+Shift+P`) またはサイドバー インターフェイスからアクセスできるいくつかのコマンドを提供します。

|コマンド名 |コマンドID |デフォルトのショートカット |説明 |
| :----------------------- | :---------------------------------------- | :--------------- | :---------------------------------------------------------------------- |
|翻訳を実行 | `multi-doc-translator.run` | `Ctrl+Alt+P` |選択した言語の多言語 README および CHANGELOG ファイルを生成 |
|選択した言語を削除 | `multi-doc-translator.removeSelected` | - |選択した言語の翻訳ファイルを削除する |
|すべての言語を削除 | `multi-doc-translator.removeAll` | - |生成されたすべての翻訳ファイルを削除します。
|保護されたフレーズを追加 | `multi-doc-translator.addProtect` | - |フレーズまたは正規表現パターンを保護リストに追加します。
|保護されたフレーズを削除 | `multi-doc-translator.removeProtect` | - |保護リストからフレーズを削除する |
|保護されたフレーズをリストする | `multi-doc-translator.listProtect` | - |現在保護されているすべてのフレーズを出力 | に表示します。
|リセット保護リスト | `multi-doc-translator.initProtect` | - |デフォルトの保護されたフレーズを復元する |
|保護を有効にする | `multi-doc-translator.enableProtect` | - |フレーズ保護システムを有効にする |
|保護を無効にする | `multi-doc-translator.disableProtect` | - |フレーズ保護システムを無効にする |
|保護ステータスを確認する | `multi-doc-translator.statusProtect` | - |現在の保護ステータスを表示 (有効/無効) |
|進行状況の出力を表示 | `multi-doc-translator.showProgress` | - | 「翻訳の進行状況」出力パネルを開きます |
|自動セットアップ変更ログ | `multi-doc-translator.autoSetupChangelog` | - |不足している場合は、README.md に変更ログセクションを追加します。
|変更履歴のみを翻訳 | `multi-doc-translator.translateChangelog` | - | `CHANGELOG.md` ファイルのみを翻訳する |
| GitHub URL を検出 | `multi-doc-translator.detectGitHubUrl` | - | GitHub リポジトリ URL を検出して表示する |

---

## 🧠 例

**前に：**

```markdown
# My Awesome Extension

A simple extension to help developers write better code.

---

## Changelog

See [変更履歴](CHANGELOG-JP.md).

---

## License

MIT License © [Your Name](../../LICENSE)
```

**後 (例 - フランス語に翻訳):**

```markdown
# My Awesome Extension

> 🌐 Disponible dans d'autres langues : [English](../../README.md) | [Bahasa Indonesia](README-ID.md) | ...

---

Une extension Visual Studio Code qui aide les développeurs à mieux écrire du code.

---

## 🧾 変更履歴

Voir toutes les modifications notables pour chaque version dans le fichier [Changelog](CHANGELOG-FR.md).

> 📦 Vous pouvez aussi consulter les notes de publication directement sur la [page des Releases GitHub](https://github.com/your-repo/releases).

---

## 🧾 License

Licence MIT © [Your Name](../../LICENSE)
```

---

## 🧠 サイドバーインターフェイス

サイドバーは、次の集中インターフェイスを提供します。

- 📊 **翻訳の進行状況** — 詳細な翻訳ログを表示します。
- 📋 **変更ログ管理** —
- `README.md` の自動セットアップ変更ログ セクション。
- `CHANGELOG.md` のみを翻訳します。
- GitHub リポジトリ URL を検出します。
- 🛡️ **フレーズ保護設定** —
- 保護を有効/無効にします。
- 保護されたフレーズまたは正規表現を追加、削除、リスト、またはリセットします。
- 🌐 **言語の選択** — 翻訳の対象言語を選択します。
- 🚀 **アクションボタン** —
- 多言語の README を生成する
- 選択したものを削除
- すべて削除

---

## 🛠️ 開発

**TypeScript をコンパイルします : **

```bash
npm run compile
```

**Lint コード : **

```bash
npm run lint
```

**テストの実行:**

```bash
npm test
```

---

## 🧑‍💻 貢献しています

1. このリポジトリをフォークします。
2. `npm install` を実行して依存関係をインストールします。
3. 変更を加えます。
4. TypeScript: `npm run compile` をコンパイルします。
5. VS Code でテストします (`F5` → _Extension Development Host_)。
6. プルリクエストを送信します。

---

## 🐞 バグと問題

問題や提案があれば [GitHub 問題ページ](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/issues). で報告してください。

---

## 🧾 変更履歴

[変更履歴](CHANGELOG-JP.md) ファイル内の各バージョンの注目すべき変更点をすべて参照してください。
📦 [GitHub リリース ページ](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/releases). でリリース ノートを直接表示することもできます。

---

## 🧾 ライセンス

MIT License © [ファトニャフマドファウジ](../../LICENSE)
