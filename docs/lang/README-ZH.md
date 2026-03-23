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


> 🌐 提供其他语言版本： [English](../../README.md) | [Polski](README-PL.md) | [日本語](README-JP.md) | [Deutsch](README-DE.md) | [Français](README-FR.md) | [Español](README-ES.md) | [Русский](README-RU.md) | [Português](README-PT.md) | [Bahasa Indonesia](README-ID.md) | [한국어](README-KR.md)

---

一个 Visual Studio Code 扩展，可使用 **免费的 Google Translate API** 自动生成多语言文档文件（`README.md` 和 `CHANGELOG.md`） - 无需 API 密钥。

---

## ✨ 特点

- 🌍 自动将 `README.md` 和 `CHANGELOG.md` 翻译成 **10 多种语言**（印度尼西亚语、法语、德语、日语、普通话、西班牙语、波兰语、俄语、葡萄牙语、韩语）。
- ⚙️ **自动变更日志管理** — 检测 `CHANGELOG.md`，将变更日志部分添加到 `README.md`（如果丢失），并进行翻译。
- 🔗 **自动 GitHub URL 检测** — 从 `package.json` 或 `.git/config` 检索存储库 URL 以创建准确的发布链接。
- 🔒 **高级短语保护** — 保护代码块、内联代码、URL、技术术语、品牌名称和自定义短语（支持正则表达式）。您可以从侧边栏添加、删除、列出或重置受保护的短语。
- 💬 为每个生成的 README 添加语言切换器块（例如 `> 🌐 其他语言版本：[Polski](docs/lang/README-PL.md) | [中文](docs/lang/README-ZH.md) | [日本语](docs/lang/README-JP.md) | [德语](docs/lang/README-DE.md) | [法语](docs/lang/README-FR.md) | [西班牙语](docs/lang/README-ES.md) | [Русский](docs/lang/README-RU.md) | [葡萄牙语](docs/lang/README-PT.md) | [印尼语](docs/lang/README-ID.md) | [한국어](docs/lang/README-KR.md)
- 🧠 使用内置 Google 翻译 — 无需帐户或自定义 API 密钥。
- 🖱️ 用户友好的侧边栏界面，用于选择语言、管理保护和运行翻译。
- 📊 显示详细的翻译进度输出。

---

## ✅ 支持的 VS Code 版本

- 最低版本：**1.85.0**
- 在 **Windows**、**macOS** 和 **Linux** 上进行测试。

---

## 🧩 安装

### 来自市场（推荐）

1. 打开 **Visual Studio Code**。
2. 转到 **扩展** 视图 (`Ctrl+Shift+X`)。
3. 搜索 `MultiDoc Translator`。
4. 单击“**安装**”。

### 来自源头（用于开发）

1. 克隆此存储库：
   ```bash
   git clone https://github.com/fatonyahmadfauzi/MultiDoc-Translator.git
   cd MultiDoc-Translator
   npm install
   ```
2. 在 VS Code 中打开该文件夹。
3. 按 **F5** 启动 **扩展开发主机**。
4. 在新窗口中，打开包含 `README.md` 和（可选）`CHANGELOG.md` 的项目。
5. 打开 MultiDoc Translator 侧边栏 → 选择语言 → 单击 **⚙️ 生成多语言自述文件**。

---

## ⌨️ 命令和快捷键

此扩展提供了多个可通过命令面板 (`Ctrl+Shift+P`) 或侧边栏界面访问的命令。

|命令名称 |命令ID |默认快捷方式 |描述 |
| :----------------------- | :---------------------------------------- | :--------------- | :---------------------------------------------------------------------- |
|运行翻译 | `multi-doc-translator.run` | `Ctrl+Alt+P` |为选定的语言生成多语言 README 和 CHANGELOG 文件 |
|删除所选语言 | `multi-doc-translator.removeSelected` | - |删除选定语言的翻译文件 |
|删除所有语言 | `multi-doc-translator.removeAll` | - |删除所有生成的翻译文件 |
|添加受保护的短语 | `multi-doc-translator.addProtect` | - |将短语或正则表达式模式添加到保护列表 |
|删除受保护的短语 | `multi-doc-translator.removeProtect` | - |从保护列表中删除短语 |
|列出受保护的短语 | `multi-doc-translator.listProtect` | - |在输出 | 显示所有当前受保护的短语
|重置保护列表 | `multi-doc-translator.initProtect` | - |恢复默认受保护短语 |
|启用保护 | `multi-doc-translator.enableProtect` | - |启用短语保护系统 |
|禁用保护 | `multi-doc-translator.disableProtect` | - |禁用短语保护系统 |
|检查保护状态 | `multi-doc-translator.statusProtect` | - |显示当前保护状态（启用/禁用）|
|显示进度输出 | `multi-doc-translator.showProgress` | - |打开“翻译进度”输出面板 |
|自动设置变更日志 | `multi-doc-translator.autoSetupChangelog` | - |如果缺少，请在 README.md 中添加变更日志部分 |
|仅翻译 更新日志 | `multi-doc-translator.translateChangelog` | - |仅翻译 `CHANGELOG.md` 文件 |
|检测 GitHub URL | `multi-doc-translator.detectGitHubUrl` | - |检测并显示您的 GitHub 存储库 URL |

---

## 🧠 示例

**前：**

```markdown
# My Awesome Extension

A simple extension to help developers write better code.

---

## Changelog

See [变更日志](CHANGELOG-ZH.md).

---

## License

MIT License © [Your Name](../../LICENSE)
```

**之后（示例 - 翻译成法语）：**

```markdown
# My Awesome Extension

> 🌐 Disponible dans d'autres langues : [English](../../README.md) | [Bahasa Indonesia](README-ID.md) | ...

---

Une extension Visual Studio Code qui aide les développeurs à mieux écrire du code.

---

## 🧾 变更日志

Voir toutes les modifications notables pour chaque version dans le fichier [Changelog](CHANGELOG-FR.md).

> 📦 Vous pouvez aussi consulter les notes de publication directement sur la [page des Releases GitHub](https://github.com/your-repo/releases).

---

## 🧾 License

Licence MIT © [Your Name](../../LICENSE)
```

---

## 🧠 侧边栏界面

侧边栏提供了一个集中界面，用于：

- 📊 **翻译进​​度** — 查看详细的翻译日志。
- 📋 **变更日志管理** —
- `README.md` 中的自动设置变更日志部分。
- 仅翻译 `CHANGELOG.md`。
- 检测您的 GitHub 存储库 URL。
- 🛡️ **短语保护设置** —
- 启用/禁用保护。
- 添加、删除、列出或重置受保护的短语或正则表达式。
- 🌐 **语言选择** — 选择翻译的目标语言。
- 🚀 **操作按钮** —
- 生成多语言自述文件
- 删除选定的
- 全部删除

---

## 🛠️ 发展

**编译TypeScript：**

```bash
npm run compile
```

**Lint 代码：**

```bash
npm run lint
```

**运行测试：**

```bash
npm test
```

---

## 🧑‍💻 贡献

1. 分叉此存储库。
2. 运行 `npm install` 安装依赖项。
3. 做出改变。
4. 编译TypeScript：`npm run compile`。
5. 在 VS Code 中测试（`F5` → _扩展开发主机_）。
6. 提交拉取请求。

---

## 🐞 错误和问题

在 [GitHub 问题页面](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/issues). 上报告任何问题或建议

---

## 🧾 变更日志

在 [变更日志](CHANGELOG-ZH.md) 文件中查看每个版本的所有显着更改。
📦 您还可以直接在[GitHub Releases page](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/releases).

---

## 🧾 许可证

MIT License © [fatonyahmadfauzi](../../LICENSE)
