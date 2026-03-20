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

> 🌐 Доступно na innych językach: [English](../../README.md) | [Polski](README-PL.md) | [中文](README-ZH.md) | [日本語](README-JP.md) | [Deutsch](README-DE.md) | [Français](README-FR.md) | [Español](README-ES.md) | [Português](README-PT.md) | [Bahasa Indonesia](README-ID.md) | [한국어](README-KR.md)

---

Расширение Visual Studio Code, которое автоматически генерирует файлы многоязычной документации (`README.md` и `CHANGELOG.md`) с использованием **бесплатного API Google Translate** — ключ API не требуется.

---

## ✨ Особенности

- 🌍 Автоматически переводит `README.md` и `CHANGELOG.md` на **более 10 языков** (индонезийский, французский, немецкий, японский, китайский, испанский, польский, русский, португальский, корейский).
- ⚙️ **Автоматическое управление журналом изменений** — обнаруживает `CHANGELOG.md`, добавляет раздел журнала изменений в `README.md`, если он отсутствует, и переводит его.
- 🔗 **Автоматическое определение URL-адреса GitHub** — извлекает URL-адрес вашего репозитория из `package.json` или `.git/config` для создания точных ссылок на выпуск.
- 🔒 **Расширенная защита фраз** — защищает блоки кода, встроенный код, URL-адреса, технические термины, названия брендов и пользовательские фразы (поддерживает регулярные выражения). Вы можете добавлять, удалять, перечислять или сбрасывать защищенные фразы на боковой панели.
- 💬 Добавляет блок переключения языка в каждый созданный файл README (например, `> 🌐 Available in other languages: [English](../../README.md) | ...`).
- 🧠 Использует встроенный Google Translate — не требуется учетная запись или специальный ключ API.
- 🖱️ Удобный интерфейс боковой панели для выбора языков, управления защитой и запуска переводов.
- 📊 Отображает подробный вывод о ходе перевода.

---

## ✅ Поддерживаемые версии кода VS

- Минимальная версия : **1.85.0**
- Протестировано на **Windows**, **macOS** и **Linux**.

---

## 🧩 Установка

### Из торговой площадки (рекомендуется)

1. Откройте **Код Visual Studio**.
2. Перейдите в представление **Расширения** (`Ctrl+Shift+X`).
3. Найдите `MultiDoc Translator`.
4. Нажмите **Установить**.

### Из исходного кода (для разработки)

1. Клонируйте этот репозиторий:
   ```bash
   git clone https://github.com/fatonyahmadfauzi/MultiDoc-Translator.git
   cd MultiDoc-Translator
   npm install
   ```
2. Откройте папку в VS Code.
3. Нажмите **F5**, чтобы запустить **Хост разработки расширений**.
4. В новом окне откройте проект, содержащий `README.md` и (необязательно) `CHANGELOG.md`.
5. Откройте боковую панель MultiDoc Translator → выберите языки → нажмите **⚙️ Создать многоязычные файлы README**.

---

## ⌨️ Команды и сочетания клавиш

Это расширение предоставляет несколько команд, доступных через палитру команд (`Ctrl+Shift+P`) или интерфейс боковой панели.

| Имя команды | Идентификатор команды | Ярлык по умолчанию | Описание |
| :----------------------- | :---------------------------------------- | :--------------- | :---------------------------------------------------------------------- |
| Запустить перевод | `multi-doc-translator.run` | `Ctrl+Alt+P` | Создание многоязычных файлов README и CHANGELOG для выбранных языков |
| Удалить выбранный язык | `multi-doc-translator.removeSelected` | - | Удалить файлы перевода для выбранных языков |
| Удалить все языки | `multi-doc-translator.removeAll` | - | Удалить все созданные файлы перевода |
| Добавить защищенную фразу | `multi-doc-translator.addProtect` | - | Добавьте фразу или шаблон регулярного выражения в список защиты |
| Удалить защищенную фразу | `multi-doc-translator.removeProtect` | - | Удалить фразу из списка защиты |
| Список защищенных фраз | `multi-doc-translator.listProtect` | - | Отобразить все защищенные в данный момент фразы в разделе «Вывод |
| Сбросить список защиты | `multi-doc-translator.initProtect` | - | Восстановить защищенные фразы по умолчанию |
| Включить защиту | `multi-doc-translator.enableProtect` | - | Включить систему защиты фраз |
| Отключить защиту | `multi-doc-translator.disableProtect` | - | Отключить систему защиты фраз |
| Проверить статус защиты | `multi-doc-translator.statusProtect` | - | Отображение текущего состояния защиты (Включено/Выключено) |
| Показать результаты выполнения | `multi-doc-translator.showProgress` | - | Откройте панель вывода «Ход перевода» |
| Журнал изменений автоматической настройки | `multi-doc-translator.autoSetupChangelog` | - | Добавьте раздел журнала изменений в README.md, если он отсутствует |
| Перевести только журнал изменений | `multi-doc-translator.translateChangelog` | - | Перевести только файл `CHANGELOG.md` |
| Обнаружение URL-адреса GitHub | `multi-doc-translator.detectGitHubUrl` | - | Обнаружение и отображение URL-адреса вашего репозитория GitHub |

---

## 🧠 Пример

**До:**

```markdown
# My Awesome Extension

A simple extension to help developers write better code.

---

## Changelog

See [Журнал изменений](CHANGELOG-RU.md).

---

## License

MIT License © [Your Name](../../LICENSE)
```

**После (пример – перевод на французский):**

```markdown
# My Awesome Extension

> 🌐 Disponible dans d'autres langues : [English](../../README.md) | [Bahasa Indonesia](README-ID.md) | ...

---

Une extension Visual Studio Code qui aide les développeurs à mieux écrire du code.

---

## 🧾 Журнал изменений

Voir toutes les modifications notables pour chaque version dans le fichier [Changelog](CHANGELOG-FR.md).

> 📦 Vous pouvez aussi consulter les notes de publication directement sur la [page des Releases GitHub](https://github.com/your-repo/releases).

---

## 🧾 License

Licence MIT © [Your Name](../../LICENSE)
```

---

## 🧠 Интерфейс боковой панели

Боковая панель предоставляет централизованный интерфейс для:

- 📊 **Прогресс перевода** — просмотр подробных журналов перевода.
- 📋 **Управление журналом изменений** —
— Раздел журнала изменений автоматической настройки в `README.md`.
- Переводите только `CHANGELOG.md`.
- Определите URL-адрес вашего репозитория GitHub.
- 🛡️ **Настройки фразовой защиты** —
- Включить/отключить защиту.
- Добавляйте, удаляйте, перечисляйте или сбрасывайте защищенные фразы или регулярные выражения.
- 🌐 **Выбор языка** — выберите целевые языки для перевода.
- 🚀 **Кнопки действий** —
- Создание многоязычных файлов README.
- Удалить выбранное
- Удалить все

---

## 🛠️ Развитие

**Скомпилируйте TypeScript : **

```bash
npm run compile
```

**Lint код : **

```bash
npm run lint
```

**Выполнить тесты : **

```bash
npm test
```

---

## 🧑‍💻 Вносим вклад

1. Форкните этот репозиторий.
2. Запустите `npm install` для установки зависимостей.
3. Внесите изменения.
4. Скомпилируйте TypeScript: `npm run compile`.
5. Протестируйте его в VS Code (`F5` → _Extension Development Host_).
6. Отправьте запрос на включение.

---

## 🐞 Ошибки и проблемы

Сообщайте о любых проблемах или предложениях на [Странице проблем GitHub](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/issues).

---

## 🧾 Список изменений

Все заметные изменения для каждой версии смотрите в файле [Журнал изменений](CHANGELOG-RU.md).
📦 Вы также можете просмотреть примечания к выпуску непосредственно на [странице релизов GitHub](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/releases).

---

## 🧾 Лицензия

MIT License © [фатоньяхмадфаузи](../../LICENSE)
