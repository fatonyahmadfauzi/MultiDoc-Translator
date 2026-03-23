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


> 🌐 In anderen Sprachen verfügbar: [English](../../README.md) | [Polski](README-PL.md) | [中文](README-ZH.md) | [日本語](README-JP.md) | [Français](README-FR.md) | [Español](README-ES.md) | [Русский](README-RU.md) | [Português](README-PT.md) | [Bahasa Indonesia](README-ID.md) | [한국어](README-KR.md)

---

Eine Visual Studio Code-Erweiterung, die mithilfe der **kostenlosen Google Translate-API** automatisch mehrsprachige Dokumentationsdateien (`README.md` und `CHANGELOG.md`) generiert – kein API-Schlüssel erforderlich.

---

## ✨ Funktionen

- 🌍 Übersetzt `README.md` und `CHANGELOG.md` automatisch in **10+ Sprachen** (Indonesisch, Französisch, Deutsch, Japanisch, Mandarin, Spanisch, Polnisch, Russisch, Portugiesisch, Koreanisch).
- ⚙️ **Automatische Änderungsprotokollverwaltung** – Erkennt `CHANGELOG.md`, fügt einen Änderungsprotokollabschnitt zu `README.md` hinzu, falls dieser fehlt, und übersetzt ihn.
- 🔗 **Automatische GitHub-URL-Erkennung** – Ruft Ihre Repository-URL von `package.json` oder `.git/config` ab, um genaue Release-Links zu erstellen.
- 🔒 **Erweiterter Phrasenschutz** – Schützt Codeblöcke, Inline-Code, URLs, technische Begriffe, Markennamen und benutzerdefinierte Phrasen (unterstützt Regex). Sie können geschützte Phrasen in der Seitenleiste hinzufügen, entfernen, auflisten oder zurücksetzen.
- 💬 Fügt jeder generierten README-Datei einen Sprachumschalterblock hinzu (z. B. `- 🧠 Verwendet das integrierte Google Translate – kein Konto oder benutzerdefinierter API-Schlüssel erforderlich.
- 🖱️ Benutzerfreundliche Seitenleistenoberfläche zum Auswählen von Sprachen, Verwalten des Schutzes und Ausführen von Übersetzungen.
- 📊 Zeigt eine detaillierte Ausgabe des Übersetzungsfortschritts an.

---

## ✅ Unterstützte VS-Codeversionen

- Mindestversion : **1.85.0**
- Getestet auf **Windows**, **macOS** und **Linux**.

---

## 🧩 Installation

### Vom Marktplatz (empfohlen)

1. Öffnen Sie **Visual Studio Code**.
2. Gehen Sie zur Ansicht **Erweiterungen** (`Ctrl+Shift+X`).
3. Suchen Sie nach `MultiDoc Translator`.
4. Klicken Sie auf **Installieren**.

### Aus der Quelle (für die Entwicklung)

1. Klonen Sie dieses Repository:
   ```bash
   git clone https://github.com/fatonyahmadfauzi/MultiDoc-Translator.git
   cd MultiDoc-Translator
   npm install
   ```
2. Öffnen Sie den Ordner in VS Code.
3. Drücken Sie **F5**, um den **Extension Development Host** zu starten.
4. Öffnen Sie im neuen Fenster Ihr Projekt, das `README.md` und (optional) `CHANGELOG.md` enthält.
5. Öffnen Sie die Seitenleiste des MultiDoc Translator → wählen Sie Sprachen aus → klicken Sie auf **⚙️ Mehrsprachige READMEs generieren**.

---

## ⌨️ Befehle und Verknüpfungen

Diese Erweiterung stellt mehrere Befehle bereit, auf die über die Befehlspalette (`Ctrl+Shift+P`) oder die Seitenleistenoberfläche zugegriffen werden kann.

| Befehlsname | Befehls-ID | Standardverknüpfung | Beschreibung |
| :----------------------- | :---------------------------------------- | :--------------- | :---------------------------------------------------------------------- |
| Übersetzung ausführen | `multi-doc-translator.run` | `Ctrl+Alt+P` | Generieren Sie mehrsprachige README- und CHANGELOG-Dateien für ausgewählte Sprachen |
| Ausgewählte Sprache entfernen | `multi-doc-translator.removeSelected` | - | Übersetzungsdateien für ausgewählte Sprachen löschen |
| Alle Sprachen entfernen | `multi-doc-translator.removeAll` | - | Alle generierten Übersetzungsdateien löschen |
| Geschützte Phrase hinzufügen | `multi-doc-translator.addProtect` | - | Fügen Sie der Schutzliste eine Phrase oder ein Regex-Muster hinzu |
| Geschützte Phrase entfernen | `multi-doc-translator.removeProtect` | - | Eine Phrase aus der Schutzliste entfernen |
| Geschützte Phrasen auflisten | `multi-doc-translator.listProtect` | - | Alle aktuell geschützten Phrasen in Ausgabe | anzeigen
| Schutzliste zurücksetzen | `multi-doc-translator.initProtect` | - | Standardmäßig geschützte Phrasen wiederherstellen |
| Schutz aktivieren | `multi-doc-translator.enableProtect` | - | Phrasenschutzsystem aktivieren |
| Schutz deaktivieren | `multi-doc-translator.disableProtect` | - | Phrasenschutzsystem deaktivieren |
| Schutzstatus prüfen | `multi-doc-translator.statusProtect` | - | Aktuellen Schutzstatus anzeigen (Aktiviert/Deaktiviert) |
| Fortschrittsausgabe anzeigen | `multi-doc-translator.showProgress` | - | Öffnen Sie den Ausgabebereich „Übersetzungsfortschritt“ |
| Auto-Setup-Änderungsprotokoll | `multi-doc-translator.autoSetupChangelog` | - | Fügen Sie einen Abschnitt zum Änderungsprotokoll zu README.md hinzu, falls dieser fehlt |
| Nur Changelog übersetzen | `multi-doc-translator.translateChangelog` | - | Übersetzen Sie nur die `CHANGELOG.md`-Datei |
| GitHub-URL erkennen | `multi-doc-translator.detectGitHubUrl` | - | Ermitteln Sie die URL Ihres GitHub-Repositorys und zeigen Sie sie an |

---

## 🧠 Beispiel

**Vor:**

```markdown
# My Awesome Extension

A simple extension to help developers write better code.

---

## Changelog

See [Änderungsprotokoll](CHANGELOG-DE.md).

---

## License

MIT License © [Your Name](../../LICENSE)
```

**Nachher (Beispiel – ins Französische übersetzt):**

```markdown
# My Awesome Extension

> 🌐 Disponible dans d'autres langues : [English](../../README.md) | [Bahasa Indonesia](README-ID.md) | ...

---

Une extension Visual Studio Code qui aide les développeurs à mieux écrire du code.

---

## 🧾 Änderungsprotokoll

Voir toutes les modifications notables pour chaque version dans le fichier [Changelog](CHANGELOG-FR.md).

> 📦 Vous pouvez aussi consulter les notes de publication directement sur la [page des Releases GitHub](https://github.com/your-repo/releases).

---

## 🧾 License

Licence MIT © [Your Name](../../LICENSE)
```

---

## 🧠 Seitenleistenoberfläche

Die Seitenleiste bietet eine zentrale Schnittstelle für:

- 📊 **Übersetzungsfortschritt** – Detaillierte Übersetzungsprotokolle anzeigen.
- 📋 **Changelog-Management** —
- Abschnitt zum automatischen Setup des Änderungsprotokolls in `README.md`.
- Übersetzen Sie nur `CHANGELOG.md`.
- Ermitteln Sie die URL Ihres GitHub-Repositorys.
- 🛡️ **Phrasenschutzeinstellungen** —
- Schutz aktivieren/deaktivieren.
- Geschützte Phrasen oder Regex hinzufügen, entfernen, auflisten oder zurücksetzen.
- 🌐 **Sprachauswahl** – Zielsprachen für die Übersetzung auswählen.
- 🚀 **Aktionsschaltflächen** —
- Generieren Sie mehrsprachige READMEs
- Ausgewählte entfernen
- Alle entfernen

---

## 🛠️ Entwicklung

**Kompilieren TypeScript : **

```bash
npm run compile
```

**Lint der Code : **

```bash
npm run lint
```

**Tests durchführen : **

```bash
npm test
```

---

## 🧑‍💻 Mitwirken

1. Forken Sie dieses Repository.
2. Führen Sie `npm install` aus, um Abhängigkeiten zu installieren.
3. Nehmen Sie Ihre Änderungen vor.
4. Kompilieren Sie TypeScript: `npm run compile`.
5. Testen Sie es in VS Code (`F5` → _Extension Development Host_).
6. Senden Sie eine Pull-Anfrage.

---

## 🐞 Fehler und Probleme

Melden Sie alle Probleme oder Vorschläge auf der [GitHub-Problemseite](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/issues).

---

## 🧾 Änderungsprotokoll

Alle wichtigen Änderungen für jede Version finden Sie in der Datei [Änderungsprotokoll](CHANGELOG-DE.md).
📦 Sie können Versionshinweise auch direkt auf der [GitHub-Versionsseite](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/releases). anzeigen.

---

## 🧾 Lizenz

MIT License © [fatonyahmadfauzi](../../LICENSE)
