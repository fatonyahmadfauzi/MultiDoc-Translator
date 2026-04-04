# Änderungsprotokoll

# Change Log

All notable changes to the "auto-translate-readmes" extension will be documented in this file.

Check [Keep a Changelog](http://keepachangelog.com/) for recommendations on how to structure this file.

## [Unreleased]


---

## [1.1.0] – 2025-10-18

### ✨ Hinzugefügt

- **Intelligente Absatzgruppierungs-Engine**
Intelligente Absatzgruppierung hinzugefügt, um mehrzeilige Absätze als zusammenhängende Blöcke zu übersetzen und gleichzeitig das ursprüngliche Markdown-Layout beizubehalten.
→ Erstellt genauere, kontextbezogene Übersetzungen, ohne die Zeilenausrichtung zu ändern.

- **Diff-Vorschaumodus (experimentell)**
Benutzer können jetzt Übersetzungsunterschiede in der Vorschau anzeigen, bevor sie die Ausgabe mit speichern
`auto-translate-readmes.previewDiff`-Befehl im VS-Code-Ausgabebereich.

- **README-Zeichensatz automatisch erkennen**
Erkennt und behält die Kodierung der Quelldatei (`UTF-8`, `UTF-16` oder `UTF-8-BOM`) automatisch bei, um plattformübergreifende Konsistenz zu gewährleisten.

---

### 🔧 Geändert

- **Inline-Markdown-Tokenizer v3**
Aktualisierter Tokenizer zum Schutz komplexer Markdown-Kombinationen:

- `**bold + _italic_ mix**`
- `[Click _here_](url)`
- Inline-HTML-Elemente wie `<span>` oder `<img>`

- **Konsistenz des Codeblocks**
Codeblöcke bleiben jetzt perfekt mit der ursprünglichen Einrückung und dem ursprünglichen Abstand erhalten (kein Beschneiden oder zusätzliche Zeilenumbrüche).

- **Verbesserte Formatierung des Sprachumschalters**
Der mehrsprachige Umschalter passt jetzt automatisch die Zeichensetzung und den Abstandsstil für jede Zielsprache an (e.g., japanische Doppelpunkte in voller Breite, französische Leerzeichen vor Doppelpunkten).

- **Stabilere Google API-Integration**
Beinhaltet jetzt einen automatischen Fallback auf einen sekundären Endpunkt, wenn `translate.googleapis.com` Ratengrenzen oder Netzwerkfehler erreicht.

---

### 🐞 Behoben

- **Kühne Handhabung (Edge Case)**
Es wurden Fälle behoben, in denen `**Before:**` oder `**After (Absolute):**` in `* *Before:**` aufgeteilt wurden.

- **Geschütztes Leerzeichen in Listen**
Es wurden Probleme verhindert, bei denen Bindestriche `-` in Listenelementen in einigen Sprachen (e.g., Französisch oder Russisch) direkt mit Text zusammengeführt wurden.

- **Nachgestellte Zeilenumbrüche beibehalten**
Die Übersetzungsausgabe behält jetzt die gleiche Anzahl an Leerzeilen wie die Quelldatei – keine werden gekürzt.

- **Emoji-Stabilität**
Kodierungsprobleme behoben, bei denen Emojis oder Sonderzeichen während der Übersetzung weggelassen wurden.

- **Plattformübergreifende EOL-Konsistenz**
Stellt konsistente Zeilenendezeichen (`\r\n` für Windows, `\n` für Unix) entsprechend der Quelldatei sicher.

---

### 🚀 Entwicklerhinweise

– Die Übersetzungslogik ist jetzt unter `translateBlock()` mit asynchroner Stapelverarbeitung modularisiert, um die Übersetzung um etwa 30 % zu beschleunigen.
- Jede generierte README-Datei enthält einen Metadatenkommentar:
`<!-- Auto-Translated v1.1.0 -->`
um Build-Versionen automatisch zu verfolgen.
- Bereit für die stabile Version **VS Code Marketplace v1.1**.

---

## [1.0.9] - 2025-10-17

### Geändert

- **Verfeinerte Übersetzungs-Engine (endgültige Überarbeitung)**
Der Übersetzungsprozess wurde perfektioniert, um die _exakte_ Struktur, den Abstand und die Anzahl der Zeilenumbrüche des ursprünglichen `README.md` beizubehalten.
- Einführung einer Zeilenumbruch-erhaltenden Logik (`split(/(\n)/)`), die ein identisches Layout in allen übersetzten Dateien gewährleistet.
- Verbesserte Markdown-Erkennung, um die Übersetzung von Listen, Tabellen, Codeblöcken, Überschriften, Links und Bildern sicher zu überspringen.
– Formatierungsnormalisierung (e.g., Zeilenumbruch, Regex-Abstand) entfernt, um eine 1:1-Zeilenzuordnung mit der Quelldatei beizubehalten.
– Verbesserte Handhabung für Zeilen mit gemischtem Inhalt (Text mit Inline-Code, Emojis oder Listenmarkierungen).
– Es wird sichergestellt, dass die Ausgabe mit konsistenter UTF-8-Kodierung und beibehaltenem EOL-Format (Windows `\r\n` oder Unix `\n`) geschrieben wird.

### Behoben

- **Exakte Markdown-Treue** – Die übersetzten Dateien stimmen nun optisch und strukturell genau mit der Quelle `README.md` überein.
- **Wiederherstellung der Einrückung** – Es wurden Probleme behoben, bei denen Unterlisten- oder verschachtelte Listenelemente nach der Übersetzung ihre Einrückung verloren.
- **Beibehaltung leerer Zeilen** – Das Verschwinden leerer Zeilen zwischen Absätzen und Listen wurde behoben.
- **Fett- und Inline-Codebehandlung** – Fälle behoben, in denen `**bold**` und `inline code` am Zeilenanfang falsch formatiert waren.
- **Integrität von Tabellenzeilen** – Beschädigte Trennlinien in komplexen Markdown-Tabellen in nicht-lateinischen Sprachen (e.g., Chinesisch, Koreanisch) wurden behoben.

---

## [1.0.8] - 2025-10-17

### Geändert

- **Abgeschlossene Übersetzungslogik**: Verbesserte Präzision für den Abstand zwischen Listenelementen und die Formatierungsintegrität.
- Verbesserte Markdown-Erhaltung und verfeinerte Handhabung des Übersetzungskontexts.

### Behoben

- Einrückungen und Zeilenumbrüche zwischen den Absätzen in Unterlisten wurden beibehalten.
- Die Formatierung von fett gedrucktem Text und Tabellen während der Übersetzung wurde korrigiert.

---

## [1.0.7] - 2025-10-17

### Hinzugefügt

- **Benutzer-Feedback**: Die Schaltfläche „Generieren“ zeigt jetzt ein sich drehendes Symbol und ist während der Übersetzung deaktiviert.
Der Vorgang löst außerdem eine Infomeldung aus und öffnet automatisch das Ausgabefeld.

### Geändert

- **Implementierte Bündelung**: Verwendet jetzt **esbuild**, um den gesamten Code in einer Datei zu bündeln.
- **Verbesserte Übersetzungslogik**: Umgeschrieben, um Zeile für Zeile zu übersetzen und gleichzeitig alle Markdown-Strukturen zu schützen.

### Behoben

- Veröffentlichungsfehler aufgrund fehlender Abhängigkeiten.
– Formatierungsfehler, einschließlich fehlender Leerzeichen, fehlerhafter Listenmarkierungen und verlorener Emojis.
- Doppelter Sprachumschalter-Header.
- Fehlende Typabhängigkeiten für den Build-Erfolg hinzugefügt.

---

## [1.0.6]

_(Interner Entwicklungs-Build, ersetzt durch 1.0.7.)_

---

## [1.0.5] - 2025-10-17

### Geändert

– Für eine bessere Zuverlässigkeit wurde die instabile `googletrans`-Bibliothek durch `deep-translator` ersetzt.

### Behoben

– Markdown-Beschädigung bei Fettdruck, Inline-Code und Tabellen behoben.
- Das Zusammenführen von Listenmarkierungen wurde behoben (`-Text` → `- Text`).
– `node-fetch` in Abhängigkeiten verschoben, um Laufzeitfehler zu verhindern.

---

## [1.0.4] - 2025-10-15

### Hinzugefügt

– Fügt automatisch einen mehrsprachigen Switcher-Block zu `README.md` hinzu, falls dieser fehlt.

### Behoben

- Fehlerhafte Markdown-Tabellentrennzeichen während der Übersetzung behoben.

---

## [1.0.3] - 2025-10-14

### Geändert

- Optimierte Verpackung für kleinere Größe und schnellere Installation.

---

## [1.0.2] - 2025-10-14

### Hinzugefügt

- Erste öffentliche Veröffentlichung.
