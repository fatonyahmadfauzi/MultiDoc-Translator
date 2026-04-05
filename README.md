# 🌍 MultiDoc Translator

[![VS Code](https://img.shields.io/badge/VS%20Code-1.85.0+-blue.svg)](https://code.visualstudio.com/)
[![Version](https://img.shields.io/github/v/release/fatonyahmadfauzi/MultiDoc-Translator?color=blue.svg)](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/releases)
[![License: MIT](https://img.shields.io/github/license/fatonyahmadfauzi/MultiDoc-Translator?color=green.svg)](LICENSE)
[![Build Status](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/actions/workflows/main.yml/badge.svg)](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/actions)
[![Repo Size](https://img.shields.io/github/repo-size/fatonyahmadfauzi/MultiDoc-Translator?color=yellow.svg)](https://github.com/fatonyahmadfauzi/MultiDoc-Translator)
[![Last Commit](https://img.shields.io/github/last-commit/fatonyahmadfauzi/MultiDoc-Translator?color=brightgreen.svg)](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/commits/main)
[![Installs](https://vsmarketplacebadges.dev/installs-short/fatonyahmadfauzi.multidoc-translator.svg)](https://marketplace.visualstudio.com/items?itemName=fatonyahmadfauzi.multidoc-translator)
[![Downloads](https://vsmarketplacebadges.dev/downloads-short/fatonyahmadfauzi.multidoc-translator.svg)](https://marketplace.visualstudio.com/items?itemName=fatonyahmadfauzi.multidoc-translator)
[![Rating](https://vsmarketplacebadges.dev/rating-short/fatonyahmadfauzi.multidoc-translator.svg)](https://marketplace.visualstudio.com/items?itemName=fatonyahmadfauzi.multidoc-translator)


> 🌐 Available in other languages: [中文](docs/lang/README-ZH.md) | [Español](docs/lang/README-ES.md)

---

A Visual Studio Code extension that automatically generates multilingual documentation files (`README.md` and `CHANGELOG.md`) using the **free Google Translate API** — no API key required.

---

## ✨ Features

- 🌍 Automatically translates `README.md` and `CHANGELOG.md` into **10+ languages** (Indonesian, French, German, Japanese, Mandarin, Spanish, Polish, Russian, Portuguese, Korean).
- ⚙️ **Automatic Changelog Management** — Detects `CHANGELOG.md`, adds a changelog section to `README.md` if missing, and translates it.
- 🔗 **Automatic GitHub URL Detection** — Retrieves your repository URL from `package.json` or `.git/config` to create accurate release links.
- 🔒 **Advanced Phrase Protection** — Protects code blocks, inline code, URLs, technical terms, brand names, and custom phrases (supports regex). You can add, remove, list, or reset protected phrases from the sidebar.
- 💬 Adds a language switcher block to each generated README (e.g., `- 🧠 Uses built-in Google Translate — no account or custom API key required.
- 🖱️ User-friendly sidebar interface to select languages, manage protection, and run translations.
- 📊 Displays detailed translation progress output.

---

## ✅ Supported VS Code Versions

- Minimum version: **1.85.0**
- Tested on **Windows**, **macOS**, and **Linux**.

---

## 🧩 Installation

### From Marketplace (Recommended)

1. Open **Visual Studio Code**.
2. Go to the **Extensions** view (`Ctrl+Shift+X`).
3. Search for `MultiDoc Translator`.
4. Click **Install**.

### From Source (For Development)

1. Clone this repository:
   ```bash
   git clone https://github.com/fatonyahmadfauzi/MultiDoc-Translator.git
   cd MultiDoc-Translator
   npm install
   ```
2. Open the folder in VS Code.
3. Press **F5** to launch the **Extension Development Host**.
4. In the new window, open your project containing `README.md` and (optionally) `CHANGELOG.md`.
5. Open the MultiDoc Translator sidebar → select languages → click **⚙️ Generate Multilingual READMEs**.

---

## ⌨️ Commands & Shortcuts

This extension provides several commands accessible via the Command Palette (`Ctrl+Shift+P`) or the sidebar interface.

| Command Name             | Command ID                                | Default Shortcut | Description                                                             |
| :----------------------- | :---------------------------------------- | :--------------- | :---------------------------------------------------------------------- |
| Run Translation          | `multi-doc-translator.run`                | `Ctrl+Alt+P`     | Generate multilingual README and CHANGELOG files for selected languages |
| Remove Selected Language | `multi-doc-translator.removeSelected`     | -                | Delete translation files for selected languages                         |
| Remove All Languages     | `multi-doc-translator.removeAll`          | -                | Delete all generated translation files                                  |
| Add Protected Phrase     | `multi-doc-translator.addProtect`         | -                | Add a phrase or regex pattern to the protection list                    |
| Remove Protected Phrase  | `multi-doc-translator.removeProtect`      | -                | Remove a phrase from the protection list                                |
| List Protected Phrases   | `multi-doc-translator.listProtect`        | -                | Display all currently protected phrases in Output                       |
| Reset Protection List    | `multi-doc-translator.initProtect`        | -                | Restore default protected phrases                                       |
| Enable Protection        | `multi-doc-translator.enableProtect`      | -                | Enable phrase protection system                                         |
| Disable Protection       | `multi-doc-translator.disableProtect`     | -                | Disable phrase protection system                                        |
| Check Protection Status  | `multi-doc-translator.statusProtect`      | -                | Display current protection status (Enabled/Disabled)                    |
| Show Progress Output     | `multi-doc-translator.showProgress`       | -                | Open the "Translation Progress" output panel                            |
| Auto Setup Changelog     | `multi-doc-translator.autoSetupChangelog` | -                | Add a changelog section to README.md if missing                         |
| Translate Only Changelog | `multi-doc-translator.translateChangelog` | -                | Translate only the `CHANGELOG.md` file                                  |
| Detect GitHub URL        | `multi-doc-translator.detectGitHubUrl`    | -                | Detect and display your GitHub repository URL                           |

---

## 🧠 Example

**Before:**

```markdown
# My Awesome Extension

A simple extension to help developers write better code.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

---

## License

MIT License © [Your Name](LICENSE)
```

**After (Example – Translated into French):**

```markdown
# My Awesome Extension

> 🌐 Disponible dans d'autres langues : [English](../../README.md) | [Bahasa Indonesia](README-ID.md) | ...

---

Une extension Visual Studio Code qui aide les développeurs à mieux écrire du code.

---

## 🧾 Changelog

Voir toutes les modifications notables pour chaque version dans le fichier [Changelog](CHANGELOG-FR.md).

> 📦 Vous pouvez aussi consulter les notes de publication directement sur la [page des Releases GitHub](https://github.com/your-repo/releases).

---

## 🧾 License

Licence MIT © [Your Name](../../LICENSE)
```

---

## 🧠 Sidebar Interface

The sidebar provides a centralized interface for:

- 📊 **Translation Progress** — View detailed translation logs.
- 📋 **Changelog Management** —
  - Auto-setup changelog section in `README.md`.
  - Translate only `CHANGELOG.md`.
  - Detect your GitHub repository URL.
- 🛡️ **Phrase Protection Settings** —
  - Enable/disable protection.
  - Add, remove, list, or reset protected phrases or regex.
- 🌐 **Language Selection** — Choose target languages for translation.
- 🚀 **Action Buttons** —
  - Generate Multilingual READMEs
  - Remove Selected
  - Remove All

---

## 💻 CLI Usage (Standalone Python Script)

You can also use the translator as a standalone Command Line Interface (CLI) application without opening VS Code!

**Requirements:**
```bash
pip install deep-translator tqdm colorama
```

**Usage:**
Run the script directly from your terminal. It comes with a beautiful interactive menu!

```bash
# Start the interactive UI menu
python path/to/multidoc_translator.py

# Or use command-line arguments directly:
python multidoc_translator.py --lang jp,zh
python multidoc_translator.py --translate-changelog all
python multidoc_translator.py --auto-setup-changelog
```

---

## 🛠️ Development

**Compile TypeScript:**

```bash
npm run compile
```

**Lint the code:**

```bash
npm run lint
```

**Run tests:**

```bash
npm test
```

---

## 🧑‍💻 Contributing

1. Fork this repository.
2. Run `npm install` to install dependencies.
3. Make your changes.
4. Compile TypeScript: `npm run compile`.
5. Test it in VS Code (`F5` → _Extension Development Host_).
6. Submit a Pull Request.

---

## 🐞 Bugs & Issues

Report any issues or suggestions on the [GitHub Issues Page](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/issues).

---

## 🧾 Changelog

See all notable changes for each version in the [CHANGELOG.md](CHANGELOG.md) file.  
📦 You can also view release notes directly on the [GitHub Releases page](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/releases).

---

## 🧾 License

MIT License © [fatonyahmadfauzi](LICENSE)
