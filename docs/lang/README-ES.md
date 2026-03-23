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


> 🌐 Disponible en otros idiomas: [English](../../README.md) | [Polski](README-PL.md) | [中文](README-ZH.md) | [日本語](README-JP.md) | [Deutsch](README-DE.md) | [Français](README-FR.md) | [Русский](README-RU.md) | [Português](README-PT.md) | [Bahasa Indonesia](README-ID.md) | [한국어](README-KR.md)

---

Una extensión de Visual Studio Code que genera automáticamente archivos de documentación multilingüe (`README.md` y `CHANGELOG.md`) utilizando la **API gratuita de Google Translate**; no se requiere clave API.

---

## ✨ Características

- 🌍 Traduce automáticamente `README.md` y `CHANGELOG.md` a **más de 10 idiomas** (indonesio, francés, alemán, japonés, mandarín, español, polaco, ruso, portugués, coreano).
- ⚙️ **Gestión automática del registro de cambios**: detecta `CHANGELOG.md`, agrega una sección de registro de cambios a `README.md` si falta y la traduce.
- 🔗 **Detección automática de URL de GitHub**: recupera la URL de su repositorio de `package.json` o `.git/config` para crear enlaces de lanzamiento precisos.
- 🔒 **Protección avanzada de frases**: protege bloques de código, código en línea, URL, términos técnicos, nombres de marcas y frases personalizadas (admite expresiones regulares). Puede agregar, eliminar, enumerar o restablecer frases protegidas desde la barra lateral.
- 💬 Agrega un bloque de cambio de idioma a cada archivo README generado (por ejemplo, `- 🧠 Utiliza el Traductor de Google integrado: no se requiere cuenta ni clave API personalizada.
- 🖱️ Interfaz de barra lateral fácil de usar para seleccionar idiomas, administrar la protección y ejecutar traducciones.
- 📊 Muestra resultados detallados del progreso de la traducción.

---

## ✅ Versiones de código VS compatibles

- Versión mínima : **1.85.0**
- Probado en **Windows**, **macOS** y **Linux**.

---

## 🧩 Instalación

### Desde Marketplace (recomendado)

1. Abra **Código de Visual Studio**.
2. Vaya a la vista **Extensiones** (`Ctrl+Shift+X`).
3. Busque `MultiDoc Translator`.
4. Haga clic en **Instalar**.

### De la fuente (para desarrollo)

1. Clona este repositorio:
   ```bash
   git clone https://github.com/fatonyahmadfauzi/MultiDoc-Translator.git
   cd MultiDoc-Translator
   npm install
   ```
2. Abra la carpeta en VS Code.
3. Presione **F5** para iniciar el **Host de desarrollo de extensiones**.
4. En la nueva ventana, abra su proyecto que contiene `README.md` y (opcionalmente) `CHANGELOG.md`.
5. Abra la barra lateral de MultiDoc Translator → seleccione idiomas → haga clic en **⚙️ Generar archivos README multilingües**.

---

## ⌨️ Comandos y atajos

Esta extensión proporciona varios comandos accesibles a través de la paleta de comandos (`Ctrl+Shift+P`) o la interfaz de la barra lateral.

| Nombre del comando | ID de comando | Acceso directo predeterminado | Descripción |
| :----------------------- | :---------------------------------------- | :--------------- | :---------------------------------------------------------------------- |
| ejecutar traducción | `multi-doc-translator.run` | `Ctrl+Alt+P` | Genere archivos README y CHANGELOG multilingües para idiomas seleccionados |
| Eliminar idioma seleccionado | `multi-doc-translator.removeSelected` | - | Eliminar archivos de traducción para idiomas seleccionados |
| Eliminar todos los idiomas | `multi-doc-translator.removeAll` | - | Eliminar todos los archivos de traducción generados |
| Agregar frase protegida | `multi-doc-translator.addProtect` | - | Agregar una frase o patrón de expresiones regulares a la lista de protección |
| Eliminar frase protegida | `multi-doc-translator.removeProtect` | - | Eliminar una frase de la lista de protección |
| Listar frases protegidas | `multi-doc-translator.listProtect` | - | Muestra todas las frases actualmente protegidas en Salida |
| Restablecer lista de protección | `multi-doc-translator.initProtect` | - | Restaurar frases protegidas predeterminadas |
| Habilitar protección | `multi-doc-translator.enableProtect` | - | Habilitar sistema de protección de frases |
| Desactivar protección | `multi-doc-translator.disableProtect` | - | Desactivar el sistema de protección de frases |
| Verificar estado de protección | `multi-doc-translator.statusProtect` | - | Mostrar el estado de protección actual (Habilitado/Deshabilitado) |
| Mostrar resultado de progreso | `multi-doc-translator.showProgress` | - | Abra el panel de salida "Progreso de la traducción" |
| Registro de cambios de configuración automática | `multi-doc-translator.autoSetupChangelog` | - | Agregue una sección de registro de cambios a README.md si falta |
| Traducir sólo registro de cambios | `multi-doc-translator.translateChangelog` | - | Traducir sólo el archivo `CHANGELOG.md` |
| Detectar URL de GitHub | `multi-doc-translator.detectGitHubUrl` | - | Detecta y muestra la URL de tu repositorio de GitHub |

---

## 🧠 Ejemplo

**Antes:**

```markdown
# My Awesome Extension

A simple extension to help developers write better code.

---

## Changelog

See [Registro de cambios](CHANGELOG-ES.md).

---

## License

MIT License © [Your Name](../../LICENSE)
```

**Después (Ejemplo – Traducido al francés):**

```markdown
# My Awesome Extension

> 🌐 Disponible dans d'autres langues : [English](../../README.md) | [Bahasa Indonesia](README-ID.md) | ...

---

Une extension Visual Studio Code qui aide les développeurs à mieux écrire du code.

---

## 🧾 Registro de cambios

Voir toutes les modifications notables pour chaque version dans le fichier [Changelog](CHANGELOG-FR.md).

> 📦 Vous pouvez aussi consulter les notes de publication directement sur la [page des Releases GitHub](https://github.com/your-repo/releases).

---

## 🧾 License

Licence MIT © [Your Name](../../LICENSE)
```

---

## 🧠 Interfaz de la barra lateral

La barra lateral proporciona una interfaz centralizada para:

- 📊 **Progreso de la traducción**: vea registros de traducción detallados.
- 📋 **Gestión del registro de cambios** —
- Sección de registro de cambios de configuración automática en `README.md`.
- Traducir sólo `CHANGELOG.md`.
- Detecta la URL de tu repositorio de GitHub.
- 🛡️ **Configuración de protección de frases** —
- Activar/desactivar la protección.
- Agregar, eliminar, enumerar o restablecer frases protegidas o expresiones regulares.
- 🌐 **Selección de idioma**: elija los idiomas de destino para la traducción.
- 🚀 **Botones de acción** —
- Generar archivos README multilingües
- Eliminar seleccionado
- Eliminar todo

---

## 🛠️ Desarrollo

**Compilar TypeScript : **

```bash
npm run compile
```

**Lint el código : **

```bash
npm run lint
```

**Ejecutar pruebas : **

```bash
npm test
```

---

## 🧑‍💻 Contribuyendo

1. Bifurque este repositorio.
2. Ejecute `npm install` para instalar dependencias.
3. Realice sus cambios.
4. Compile TypeScript: `npm run compile`.
5. Pruébelo en VS Code (`F5` → _Extension Development Host_).
6. Envíe una solicitud de extracción.

---

## 🐞 Errores y problemas

Informe cualquier problema o sugerencia en la [Página de problemas de GitHub](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/issues).

---

## 🧾 Registro de cambios

Vea todos los cambios notables para cada versión en el archivo [Registro de cambios](CHANGELOG-ES.md).
📦 También puede ver las notas de la versión directamente en la [Página de versiones de GitHub](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/releases).

---

## 🧾 Licencia

MIT License © [fatonyahmadfauzi](../../LICENSE)
