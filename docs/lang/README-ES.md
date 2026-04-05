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


> 🌐 Disponible en otros idiomas: [English](../../README.md) | [中文](README-ZH.md)

---

Una extensión de Visual Studio Code que genera automáticamente archivos de documentación multilingües (`README.md` y `CHANGELOG.md`) mediante el ** Traductor gratuito de Google API**, sin necesidad de la clave API.

---

## ✨ Características

- Traduce 🌍 automáticamente `README.md` y `CHANGELOG.md` a ** más de 10idiomas** (alemán, indonesio, francés, japonés, mandarín, español, polaco, ruso, portugués y coreano).
- ⚙️ ** Gestión automática del registro de cambios **: detecta `CHANGELOG.md`, añade una sección de registro de cambios a `README.md` si falta y la traduce.
- 🔗 ** Detección automática de GitHub URL ** — Recupera la URL de tu repositorio de `package.json` o `.git/config` para crear enlaces de publicación precisos.
- 🔒 ** Protección avanzada de frases **: protege bloques de código, código en línea, URL, términos técnicos, nombres de marcas y frases personalizadas (admite expresiones regulares). Puedes añadir, eliminar, enumerar o restablecer frases protegidas desde la barra lateral.
- 💬 Añade un bloque de cambio de idioma a cada archivo README generado (e.g., `- 🧠 Utiliza el Traductor de Google integrado: no se requiere una cuenta ni una clave API personalizada.
- 🖱️ Interfaz de barra lateral fácil de usar para seleccionar idiomas, gestionar la protección y ejecutar traducciones.
- 📊 Muestra el resultado detallado del progreso de la traducción.

---

## ✅ Versiones de código VS compatibles

- Versión mínima : **1.85.0**
- Probado en **Windows**, **macOS** y **Linux**.

---

INSTALACIÓN

### Desde Marketplace (recomendado)

1. Abra **Visual Studio Code**.
2. Ve a la vista **Extensiones * * (`Ctrl+Shift+X`).
3. Busca `MultiDoc Translator`.
4. Haga clic en **Instalar**.

### De la fuente (para desarrollo)

1. Clone este repositorio:
   ```bash
   git clone https://github.com/fatonyahmadfauzi/MultiDoc-Translator.git
   cd MultiDoc-Translator
   npm install
   ```
2. Abra la carpeta en VS Code.
3. Pulsa **F5** para iniciar el ** Anfitrión de desarrollo de extensiones **.
4. En la nueva ventana, abre el proyecto que contiene `README.md` y (opcionalmente) `CHANGELOG.md`.
5. Abra la barra lateral del Traductor MultiDoc, → seleccione idiomas, → haga clic en **⚙️ Generar READMEs multilingües **.

---

##️ Comandos y accesos directos

Esta extensión proporciona varios comandos accesibles a través de la paleta de comandos (`Ctrl+Shift+P`) o la interfaz de la barra lateral.

| Nombre del comando | ID del comando | Acceso directo predeterminado | Descripción                                                             |
| :----------------------- | :---------------------------------------- | :--------------- | :---------------------------------------------------------------------- |
| Ejecutar traducción          | `multi-doc-translator.run`                | `Ctrl+Alt+P`     | Generar archivos README y CHANGELOG multilingües para los idiomas seleccionados |
| Eliminar idioma seleccionado | `multi-doc-translator.removeSelected`     | -                | Eliminar archivos de traducción para los idiomas seleccionados |
| Eliminar todos los idiomas     | `multi-doc-translator.removeAll`          | -                | Eliminar todos los archivos de traducción generados |
| Añadir frase protegida | `multi-doc-translator.addProtect`         | -                | Añadir una frase o patrón de expresiones regulares a la lista de protección |
| Eliminar frase protegida | `multi-doc-translator.removeProtect`      | -                | Eliminar una frase de la lista de protección |
| Lista de frases protegidas | `multi-doc-translator.listProtect`        | -                | Mostrar todas las frases protegidas actualmente en la salida                       |
| Restablecer lista de protección | `multi-doc-translator.initProtect`        | -                | Restaurar frases protegidas predeterminadas |
| Activar protección        | `multi-doc-translator.enableProtect`      | -                | Activar sistema de protección de frases |
| Desactivar protección       | `multi-doc-translator.disableProtect`     | -                | Desactivar sistema de protección de frases |
| Comprobar el estado de protección | `multi-doc-translator.statusProtect`      | -                | Mostrar el estado de protección actual (Activado/Desactivado)                    |
| Mostrar resultado del progreso | `multi-doc-translator.showProgress`       | -                | Abrir el panel de salida "Progreso de la traducción" |
| Registro de cambios de configuración automática | `multi-doc-translator.autoSetupChangelog` | -                | Añade una sección de registro de cambios a README.md si falta                         |
| Traducir solo el registro de cambios | `multi-doc-translator.translateChangelog` | -                | Traducir solo el archivo `CHANGELOG.md` |
| Detecta GitHub URL        | `multi-doc-translator.detectGitHubUrl`    | -                | Detecta y muestra la URL de tu repositorio GitHub |

---

Ejemplo

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

## Interfaz de 🧠 la barra lateral

La barra lateral proporciona una interfaz centralizada para:

- 📊 ** Progreso de la traducción ** — Ver registros de traducción detallados.
- 📋 ** Gestión de registros de cambios ** —
- Sección de registro de cambios de configuración automática en `README.md`.
- Traduce solo `CHANGELOG.md`.
- Detecta la URL de tu repositorio GitHub.
- 🛡️ ** Configuración de protección de frases ** —
- Activar/desactivar la protección.
- Añade, elimina, enumera o restablece frases protegidas o expresiones regulares.
- 🌐 ** Selección de idioma ** — Elige los idiomas de destino para la traducción.
Botones de acciones
- Generar READMEs multilingües
Eliminar fila seleccionada(s) 
Borrar todo

---

## 💻 CLI Uso (Autónomo Python Guión)

¡También puede usar el traductor como una aplicación independiente de interfaz de línea de comandos (CLI) sin abrir VS Code!

Requerimientos
```bash
pip install deep-translator tqdm colorama
```

Uso
Ejecuta el script directamente desde tu terminal. ¡Viene con un bonito menú interactivo!

```bash
# Start the interactive UI menu
python path/to/multidoc_translator.py

# Or use command-line arguments directly:
python multidoc_translator.py --lang jp,zh
python multidoc_translator.py --translate-changelog all
python multidoc_translator.py --auto-setup-changelog
```

---

## 🛠️ Desarrollo

**Compilar TypeScript : **

```bash
npm run compile
```

** Indique el código : **

```bash
npm run lint
```

Realización de pruebas

```bash
npm test
```

---

## 🧑‍💻 Contribuyendo

1. Bifurque este repositorio.
2. Ejecuta `npm install` para instalar dependencias.
A continuación, haga los cambios. 
4. Compile TypeScript: `npm run compile`.
5. Pruébalo en el código VS (`F5`→_Extension Development Host_).
6. Envía una solicitud de extracción.

---

## 🐞 Errores y problemas

Notificá cualquier problema o sugerencia en el [GitHub Issues Page](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/issues).

---

## 🧾 Registro de cambios

Consulta todos los cambios notables para cada versión en el archivo [Registro de cambios](CHANGELOG-ES.md).
📦 También puedes ver las notas de la versión directamente en el [GitHub Releases page](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/releases).

---

## 🧾 Licencia

MIT License © [fatonyahmadfauzi](../../LICENSE)
