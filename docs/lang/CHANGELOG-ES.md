# Registro de cambios

# Change Log

All notable changes to the "auto-translate-readmes" extension will be documented in this file.

Check [Keep a Changelog](http://keepachangelog.com/) for recommendations on how to structure this file.

## [Unreleased]


---

## [1.1.0] – 2025-10-18

### ✨ Añadido

- ** Motor inteligente de agrupación de párrafos **
Se ha añadido una agrupación inteligente de párrafos para traducir los párrafos de varias líneas como bloques cohesivos mientras se conserva el diseño original de Markdown.
→ Produce traducciones más precisas y conscientes del contexto sin cambiar la alineación de las líneas.

- ** Modo de vista previa de diff (experimental)**
Los usuarios ahora pueden obtener una vista previa de los diffs de traducción antes de guardar la salida utilizando
`auto-translate-readmes.previewDiff` comando en el panel de salida de código VS.

- **Detectar automáticamente el conjunto de caracteres README **
Detecta y conserva automáticamente la codificación de archivos de origen (`UTF-8`, `UTF-16` o `UTF-8-BOM`) para garantizar la coherencia entre plataformas.

---

Cambiado

- **Inline Markdown Tokenizer v3**
Tokenizador actualizado para proteger combinaciones complejas de Markdown:

P0
P0
- Elementos HTML en línea como `<span>` o `<img>`

- ** Consistencia del bloque de código **
Los bloques de código ahora se conservan perfectamente con la muesca y el espaciado originales (sin recortes ni nuevas líneas adicionales).

- ** Formato mejorado del selector de idiomas **
El conmutador multilingüe ahora ajusta automáticamente la puntuación y el estilo de espaciado para cada idioma de destino (e.g., dos puntos japoneses de ancho completo, espacios franceses antes de los dos puntos).

- ** Integración más estable con Google API **
Ahora incluye el repliegue automático a un punto final secundario cuando `translate.googleapis.com` alcanza los límites de velocidad o los errores de red.

---

### 🐞 Corregido

- ** Manipulación en negrita (Edge Case)**
Se corrigieron los casos en los que __p0 __ o __ p1__ se dividían en `* *Before:**`.

- **Espacio no rompedor en las listas**
Se evitaron problemas en los que los guiones `-` de los elementos de la lista se fusionaban directamente con el texto en algunos idiomas (e.g., francés o ruso).

- **Preservar las nuevas líneas de seguimiento **
La salida de traducción ahora conserva el mismo número de líneas en blanco que el archivo de origen; ninguna está recortada.

- ** Estabilidad Emoji **
Se han corregido problemas de codificación en los que se eliminaban emojis o caracteres especiales durante la traducción.

- ** Consistencia de EOL multiplataforma **
Garantiza la coherencia de los caracteres de fin de línea (__p0 __ para Windows, __ p1__ para Unix) según el archivo de origen.

---

Notas del desarrollador

- La lógica de traducción ahora está modularizada en `translateBlock()` con procesamiento por lotes asíncrono para una traducción ~30% más rápida.
- Cada README generado incluye un comentario de metadatos:
P0
para realizar un seguimiento de las versiones de compilación automáticamente.
- Listo para **VS Code Marketplace v1.1 lanzamiento estable **.

---

## [1.0.9] - 2025-10-17

con 

- ** Motor de traducción refinado (revisión final)**
Perfeccioné el proceso de traducción para preservar la estructura_exacta_, el espaciado y el recuento de nuevas líneas del `README.md` original.
- Presentamos la lógica de preservación de nuevas líneas (`split(/(\n)/)`) que garantiza un diseño idéntico en todos los archivos traducidos.
- Reconocimiento mejorado de Markdown para omitir de forma segura la traducción de listas, tablas, bloques de código, encabezados, enlaces e imágenes.
- Se ha eliminado la normalización de formato (e.g., recorte de nuevas líneas, expresiones regulares de espaciado) para mantener la asignación de líneas 1:1 con el archivo de origen.
- Manejo mejorado para líneas de contenido mixto (texto con código en línea, emojis o marcadores de lista).
- Se garantiza que la salida se escriba utilizando una codificación UTF-8 coherente y un formato EOL conservado (Windows `\r\n` o Unix `\n`).

Fijo

- **Exact Markdown Fidelity** – Los archivos traducidos ahora coinciden visual y estructuralmente con la fuente `README.md` exactamente.
- ** Restauración de sangría ** – Se corrigieron los problemas en los que los elementos de la sub-lista o de la lista anidada perdían su sangría después de la traducción.
- ** Conservación de líneas vacías ** – Se corrigieron las líneas en blanco que desaparecían entre los párrafos y las listas.
- ** Manejo de código en negrita y en línea ** – Casos corregidos en los que `**bold**` y __ p1__ al inicio de la línea tenían un formato incorrecto.
- ** Integridad de línea de tabla ** – Se corrigieron líneas separadoras dañadas en tablas Markdown complejas en idiomas no latinos (e.g., chino, coreano).

---

## [1.0.8] - 2025-10-17

con 

- ** Lógica de traducción finalizada **: precisión mejorada para el espaciado de elementos de lista y la integridad del formato.
- Conservación mejorada de Markdown y manejo refinado del contexto de traducción.

Fijo

- Se ha conservado la sangría de la sublista y las nuevas líneas entre párrafos.
- Formato fijo de texto en negrita y tablas durante la traducción.

---

## [1.0.7] - 2025-10-17

 Añadido

- ** Comentarios del usuario **: El botón "Generar" ahora muestra un icono giratorio y está desactivado durante la traducción.
El proceso también activa un mensaje de información y abre el panel de salida automáticamente.

Cambiado

- ** Combinación implementada **: ahora utiliza * *esbuild** para agrupar todo el código en un solo archivo.
- ** Lógica de traducción mejorada **: reescrita para traducir línea por línea mientras se protegen todas las estructuras de Markdown.

Fijo

- Error de publicación debido a dependencias faltantes.
- Errores de formato, incluidos espacios faltantes, marcadores de lista rotos y emojis perdidos.
- Duplicar el encabezado del conmutador de idioma.
- Se han añadido dependencias de tipo faltantes para el éxito de la compilación.

---

## [1.0.6]

_(Construcción de desarrollo interno, reemplazada por 1.0.7.)_

---

## [1.0.5] - 2025-10-17

con 

- Se ha sustituido la biblioteca inestable __p0 __ por `deep-translator` para mayor fiabilidad.

Fijo

- Corrupción de Markdown corregida que involucra negrita, código en línea y tablas.
- Fusión de marcadores de lista fijos (__p0 → __ `- Text`).
- Se ha movido `node-fetch` a las dependencias para evitar fallos en el tiempo de ejecución.

---

## [1.0.4] - 2025-10-15

añadido

- Añade automáticamente un bloque de conmutación multilingüe a `README.md` si falta.

Fijo

- Se han corregido los separadores de tablas Markdown rotos durante la traducción.

---

## [1.0.3] - 2025-10-14

Cambiado

- Embalaje optimizado para un tamaño más pequeño y una instalación más rápida.

---

## [1.0.2] - 2025-10-14

 Añadido

Publicación inicial
