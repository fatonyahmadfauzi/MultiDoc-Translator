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


> 🌐 Dostępne w innych językach: [English](../../README.md) | [中文](README-ZH.md) | [日本語](README-JP.md) | [Deutsch](README-DE.md) | [Français](README-FR.md) | [Español](README-ES.md) | [Русский](README-RU.md) | [Português](README-PT.md) | [Bahasa Indonesia](README-ID.md) | [한국어](README-KR.md)

---

Rozszerzenie Visual Studio Code, które automatycznie generuje wielojęzyczne pliki dokumentacji (`README.md` i `CHANGELOG.md`) przy użyciu **bezpłatnego interfejsu API Tłumacza Google** — klucz API nie jest wymagany.

---

## ✨ Funkcje

- 🌍 Automatycznie tłumaczy `README.md` i `CHANGELOG.md` na **10+ języków** (indonezyjski, francuski, niemiecki, japoński, mandaryński, hiszpański, polski, rosyjski, portugalski, koreański).
- ⚙️ **Automatyczne zarządzanie dziennikiem zmian** — wykrywa `CHANGELOG.md`, dodaje sekcję dziennika zmian do `README.md`, jeśli jej brakuje, i tłumaczy ją.
- 🔗 **Automatyczne wykrywanie adresu URL GitHub** — pobiera adres URL repozytorium z `package.json` lub `.git/config` w celu utworzenia dokładnych linków do wersji.
- 🔒 **Zaawansowana ochrona fraz** — Chroni bloki kodu, kod wbudowany, adresy URL, terminy techniczne, nazwy marek i niestandardowe frazy (obsługuje regex). Możesz dodawać, usuwać, wyświetlać listę lub resetować chronione frazy na pasku bocznym.
- 💬 Dodaje blok zmiany języka do każdego wygenerowanego pliku README (np. `- 🧠 Korzysta z wbudowanego Tłumacza Google — nie jest wymagane żadne konto ani niestandardowy klucz API.
- 🖱️ Przyjazny dla użytkownika interfejs paska bocznego do wybierania języków, zarządzania ochroną i uruchamiania tłumaczeń.
- 📊 Wyświetla szczegółowe wyniki postępu tłumaczenia.

---

## ✅ Obsługiwane wersje kodu VS

- Minimalna wersja : **1.85.0**
- Testowano na **Windows**, **macOS** i **Linux**.

---

## 🧩 Instalacja

### Z Marketplace (zalecane)

1. Otwórz **Kod Visual Studio**.
2. Przejdź do widoku **Rozszerzenia** (`Ctrl+Shift+X`).
3. Wyszukaj `MultiDoc Translator`.
4. Kliknij **Zainstaluj**.

### Ze źródła (dla rozwoju)

1. Sklonuj to repozytorium:
   ```bash
   git clone https://github.com/fatonyahmadfauzi/MultiDoc-Translator.git
   cd MultiDoc-Translator
   npm install
   ```
2. Otwórz folder w VS Code.
3. Naciśnij **F5**, aby uruchomić **Host rozwoju rozszerzeń**.
4. W nowym oknie otwórz swój projekt zawierający `README.md` i (opcjonalnie) `CHANGELOG.md`.
5. Otwórz pasek boczny MultiDoc Translator → wybierz języki → kliknij **⚙️ Generuj wielojęzyczne pliki README**.

---

## ⌨️ Polecenia i skróty

To rozszerzenie udostępnia kilka poleceń dostępnych za pośrednictwem palety poleceń (`Ctrl+Shift+P`) lub interfejsu paska bocznego.

| Nazwa polecenia | Identyfikator polecenia | Domyślny skrót | Opis |
| :----------------------- | :---------------------------------------- | :--------------- | :---------------------------------------------------------------------- |
| Uruchom tłumaczenie | `multi-doc-translator.run` | `Ctrl+Alt+P` | Generuj wielojęzyczne pliki README i CHANGELOG dla wybranych języków |
| Usuń wybrany język | `multi-doc-translator.removeSelected` | - | Usuń pliki tłumaczeń dla wybranych języków |
| Usuń wszystkie języki | `multi-doc-translator.removeAll` | - | Usuń wszystkie wygenerowane pliki tłumaczeń |
| Dodaj frazę chronioną | `multi-doc-translator.addProtect` | - | Dodaj frazę lub wzór wyrażenia regularnego do listy ochrony |
| Usuń frazę chronioną | `multi-doc-translator.removeProtect` | - | Usuń frazę z listy ochrony |
| Lista chronionych fraz | `multi-doc-translator.listProtect` | - | Wyświetl wszystkie aktualnie chronione frazy w Wyjściu |
| Resetuj listę zabezpieczeń | `multi-doc-translator.initProtect` | - | Przywróć domyślne chronione frazy |
| Włącz ochronę | `multi-doc-translator.enableProtect` | - | Włącz system ochrony fraz |
| Wyłącz ochronę | `multi-doc-translator.disableProtect` | - | Wyłącz system ochrony fraz |
| Sprawdź stan ochrony | `multi-doc-translator.statusProtect` | - | Wyświetl aktualny stan ochrony (włączony/wyłączony) |
| Pokaż wynik postępu | `multi-doc-translator.showProgress` | - | Otwórz panel wyjściowy „Postęp tłumaczenia” |
| Lista zmian automatycznej konfiguracji | `multi-doc-translator.autoSetupChangelog` | - | Dodaj sekcję dziennika zmian do pliku README.md, jeśli brakuje |
| Tylko tłumaczenie Dziennik zmian | `multi-doc-translator.translateChangelog` | - | Przetłumacz tylko plik `CHANGELOG.md` |
| Wykryj adres URL GitHub | `multi-doc-translator.detectGitHubUrl` | - | Wykryj i wyświetl adres URL repozytorium GitHub |

---

## 🧠 Przykład

**Zanim:**

```markdown
# My Awesome Extension

A simple extension to help developers write better code.

---

## Changelog

See [Dziennik zmian](CHANGELOG-PL.md).

---

## License

MIT License © [Your Name](../../LICENSE)
```

**Po (przykład – przetłumaczony na język francuski):**

```markdown
# My Awesome Extension

> 🌐 Disponible dans d'autres langues : [English](../../README.md) | [Bahasa Indonesia](README-ID.md) | ...

---

Une extension Visual Studio Code qui aide les développeurs à mieux écrire du code.

---

## 🧾 Dziennik zmian

Voir toutes les modifications notables pour chaque version dans le fichier [Changelog](CHANGELOG-FR.md).

> 📦 Vous pouvez aussi consulter les notes de publication directement sur la [page des Releases GitHub](https://github.com/your-repo/releases).

---

## 🧾 License

Licence MIT © [Your Name](../../LICENSE)
```

---

## 🧠 Interfejs paska bocznego

Pasek boczny zapewnia scentralizowany interfejs dla:

- 📊 **Postęp tłumaczenia** — Wyświetl szczegółowe dzienniki tłumaczeń.
- 📋 **Zarządzanie dziennikiem zmian** —
- Sekcja dziennika zmian automatycznej konfiguracji w `README.md`.
- Tłumacz tylko `CHANGELOG.md`.
- Wykryj adres URL repozytorium GitHub.
- 🛡️ **Ustawienia ochrony fraz** —
- Włącz/wyłącz ochronę.
- Dodawaj, usuwaj, wyświetlaj lub resetuj chronione frazy lub wyrażenia regularne.
- 🌐 **Wybór języka** — Wybierz języki docelowe tłumaczenia.
- 🚀 **Przyciski akcji** —
- Generuj wielojęzyczne pliki README
- Usuń wybrane
- Usuń wszystko

---

## 🛠️Rozwój

**Skompiluj TypeScript : **

```bash
npm run compile
```

**Lint kod : **

```bash
npm run lint
```

**Przeprowadź testy : **

```bash
npm test
```

---

## 🧑‍💻 Współtworzenie

1. Zrób fork tego repozytorium.
2. Uruchom `npm install`, aby zainstalować zależności.
3. Wprowadź zmiany.
4. Skompiluj TypeScript: `npm run compile`.
5. Przetestuj go w kodzie VS (`F5` → _Host rozwoju rozszerzenia_).
6. Prześlij żądanie ściągnięcia.

---

## 🐞 Błędy i problemy

Zgłaszaj wszelkie problemy lub sugestie na [stronie problemów GitHub](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/issues).

---

## 🧾 Dziennik zmian

Zobacz wszystkie istotne zmiany dla każdej wersji w pliku [Dziennik zmian](CHANGELOG-PL.md).
📦 Możesz także wyświetlić informacje o wersji bezpośrednio na [stronie z wydaniami w GitHub](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/releases).

---

## 🧾 Licencja

MIT License © [fatonyahmadfauzi](../../LICENSE)
