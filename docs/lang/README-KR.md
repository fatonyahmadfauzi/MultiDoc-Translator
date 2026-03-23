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


> 🌐 다른 언어로도 사용 가능: [English](../../README.md) | [Polski](README-PL.md) | [中文](README-ZH.md) | [日本語](README-JP.md) | [Deutsch](README-DE.md) | [Français](README-FR.md) | [Español](README-ES.md) | [Русский](README-RU.md) | [Português](README-PT.md) | [Bahasa Indonesia](README-ID.md)

---

**무료 Google Translate API**를 사용하여 다국어 문서 파일(`README.md` 및 `CHANGELOG.md`)을 자동으로 생성하는 Visual Studio Code 확장입니다. API 키가 필요하지 않습니다.

---

## ✨ 특징

- 🌍 `README.md` 및 `CHANGELOG.md`을 **10개 이상의 언어**(인도네시아어, 프랑스어, 독일어, 일본어, 중국어, 스페인어, 폴란드어, 러시아어, 포르투갈어, 한국어)로 자동 번역합니다.
- ⚙️ **자동 변경 로그 관리** — `CHANGELOG.md`을 감지하고 누락된 경우 `README.md`에 변경 로그 섹션을 추가하고 번역합니다.
- 🔗 **자동 GitHub URL 감지** — `package.json` 또는 `.git/config`에서 저장소 URL을 검색하여 정확한 릴리스 링크를 생성합니다.
- 🔒 **고급 문구 보호** — 코드 블록, 인라인 코드, URL, 기술 용어, 브랜드 이름 및 사용자 정의 문구를 보호합니다(정규식 지원). 사이드바에서 보호된 문구를 추가, 제거, 나열 또는 재설정할 수 있습니다.
- 💬 생성된 각 README(예: `- 🧠 내장된 Google 번역을 사용합니다. 계정이나 맞춤 API 키가 필요하지 않습니다.
- 🖱️ 언어 선택, 보호 관리 및 번역 실행을 위한 사용자 친화적인 사이드바 인터페이스.
- 📊 자세한 번역 진행 상황 출력을 표시합니다.

---

## ✅ 지원되는 VS 코드 버전

- 최소 버전 : **1.85.0**
- **Windows**, **macOS** 및 **Linux**에서 테스트되었습니다.

---

## 🧩 설치

### 마켓플레이스에서(권장)

1. **Visual Studio Code**를 엽니다.
2. **확장** 보기(`Ctrl+Shift+X`)로 이동합니다.
3. `MultiDoc Translator`을(를) 검색하세요.
4. **설치**를 클릭합니다.

### 소스에서(개발용)

1. 이 저장소를 복제합니다.
   ```bash
   git clone https://github.com/fatonyahmadfauzi/MultiDoc-Translator.git
   cd MultiDoc-Translator
   npm install
   ```
2. VS Code에서 폴더를 엽니다.
3. **F5**를 눌러 **확장 개발 호스트**를 시작합니다.
4. 새 창에서 `README.md` 및 (선택적으로) `CHANGELOG.md`이 포함된 프로젝트를 엽니다.
5. MultiDoc 번역기 사이드바를 열고 → 언어를 선택하고 → **⚙️ 다국어 README 생성**을 클릭합니다.

---

## ⌨️ 명령 및 단축키

이 확장은 명령 팔레트(`Ctrl+Shift+P`) 또는 사이드바 인터페이스를 통해 액세스할 수 있는 여러 명령을 제공합니다.

| 명령 이름 | 명령 ID | 기본 바로가기 | 설명 |
| :----------------------- | :---------------------------------------- | :--------------- | :---------------------------------------------------------------------- |
| 번역 실행 | `multi-doc-translator.run` | `Ctrl+Alt+P` | 선택한 언어에 대한 다국어 README 및 CHANGELOG 파일 생성 |
| 선택한 언어 제거 | `multi-doc-translator.removeSelected` | - | 선택한 언어에 대한 번역 파일 삭제 |
| 모든 언어 제거 | `multi-doc-translator.removeAll` | - | 생성된 모든 번역 파일 삭제 |
| 보호된 문구 추가 | `multi-doc-translator.addProtect` | - | 보호 목록에 문구 또는 정규식 패턴 추가 |
| 보호된 문구 제거 | `multi-doc-translator.removeProtect` | - | 보호 목록에서 문구 제거 |
| 보호된 문구 나열 | `multi-doc-translator.listProtect` | - | 현재 보호된 모든 문구를 출력 |
| 보호 목록 재설정 | `multi-doc-translator.initProtect` | - | 기본 보호 문구 복원 |
| 보호 활성화 | `multi-doc-translator.enableProtect` | - | 문구 보호 시스템 활성화 |
| 보호 비활성화 | `multi-doc-translator.disableProtect` | - | 문구 보호 시스템 비활성화 |
| 보호 상태 확인 | `multi-doc-translator.statusProtect` | - | 현재 보호 상태 표시(활성화/비활성화) |
| 진행률 출력 표시 | `multi-doc-translator.showProgress` | - | "번역 진행률" 출력 패널 열기 |
| 자동 설정 변경 로그 | `multi-doc-translator.autoSetupChangelog` | - | 누락된 경우 README.md에 변경 로그 섹션을 추가하세요. |
| 변경 내역만 번역 | `multi-doc-translator.translateChangelog` | - | `CHANGELOG.md` 파일만 번역 |
| GitHub URL 감지 | `multi-doc-translator.detectGitHubUrl` | - | GitHub 저장소 URL 감지 및 표시 |

---

## 🧠 예

**전에:**

```markdown
# My Awesome Extension

A simple extension to help developers write better code.

---

## Changelog

See [변경 내역](CHANGELOG-KR.md).

---

## License

MIT License © [Your Name](../../LICENSE)
```

**이후(예 – 프랑스어로 번역됨):**

```markdown
# My Awesome Extension

> 🌐 Disponible dans d'autres langues : [English](../../README.md) | [Bahasa Indonesia](README-ID.md) | ...

---

Une extension Visual Studio Code qui aide les développeurs à mieux écrire du code.

---

## 🧾 변경 내역

Voir toutes les modifications notables pour chaque version dans le fichier [Changelog](CHANGELOG-FR.md).

> 📦 Vous pouvez aussi consulter les notes de publication directement sur la [page des Releases GitHub](https://github.com/your-repo/releases).

---

## 🧾 License

Licence MIT © [Your Name](../../LICENSE)
```

---

## 🧠 사이드바 인터페이스

사이드바는 다음을 위한 중앙 집중식 인터페이스를 제공합니다.

- 📊 **번역 진행** — 자세한 번역 로그를 봅니다.
- 📋 **변경 로그 관리** —
- `README.md`의 자동 설정 변경 로그 섹션.
- `CHANGELOG.md`만 번역하세요.
- GitHub 저장소 URL을 감지합니다.
- 🛡️ **문구 보호 설정** —
- 보호를 활성화/비활성화합니다.
- 보호된 문구 또는 정규식을 추가, 제거, 나열 또는 재설정합니다.
- 🌐 **언어 선택** — 번역할 대상 언어를 선택하세요.
- 🚀 **작업 버튼** —
- 다국어 README 생성
- 선택 항목 제거
- 모두 제거

---

## 🛠️ 개발

**컴파일 TypeScript : **

```bash
npm run compile
```

**Lint 코드 : **

```bash
npm run lint
```

**테스트 실행 : **

```bash
npm test
```

---

## 🧑‍💻 기여

1. 이 저장소를 포크하십시오.
2. `npm install`을 실행하여 종속성을 설치합니다.
3. 변경합니다.
4. TypeScript: `npm run compile`을 컴파일합니다.
5. VS Code(`F5` → _Extension Development Host_)에서 테스트합니다.
6. 풀 요청(Pull Request)을 제출하세요.

---

## 🐞 버그 및 문제

[GitHub 문제 페이지](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/issues).에서 문제나 제안 사항을 보고하세요.

---

## 🧾 변경 내역

[변경 내역](CHANGELOG-KR.md) 파일에서 각 버전의 주요 변경 사항을 모두 확인하세요.
📦 [GitHub 릴리스 페이지](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/releases).에서 직접 릴리스 노트를 볼 수도 있습니다.

---

## 🧾 라이센스

MIT License © [fatonyahmadfauzi](../../LICENSE)
