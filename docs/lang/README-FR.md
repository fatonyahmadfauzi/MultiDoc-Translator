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


> 🌐 Disponible dans d'autres langues : [English](../../README.md) | [Polski](README-PL.md) | [中文](README-ZH.md) | [日本語](README-JP.md) | [Deutsch](README-DE.md) | [Español](README-ES.md) | [Русский](README-RU.md) | [Português](README-PT.md) | [Bahasa Indonesia](README-ID.md) | [한국어](README-KR.md)

---

Une extension Visual Studio Code qui génère automatiquement des fichiers de documentation multilingues (`README.md` et `CHANGELOG.md`) à l'aide de l'**API gratuite Google Translate** — aucune clé API requise.

---

## ✨ Caractéristiques

- 🌍 Traduit automatiquement `README.md` et `CHANGELOG.md` en **plus de 10 langues** (indonésien, français, allemand, japonais, mandarin, espagnol, polonais, russe, portugais, coréen).
- ⚙️ **Gestion automatique du journal des modifications** — Détecte `CHANGELOG.md`, ajoute une section du journal des modifications à `README.md` s'il est manquant et la traduit.
- 🔗 **Détection automatique d'URL GitHub** — Récupère l'URL de votre référentiel à partir de `package.json` ou `.git/config` pour créer des liens de version précis.
- 🔒 **Protection avancée des expressions** — Protège les blocs de code, le code en ligne, les URL, les termes techniques, les noms de marque et les expressions personnalisées (prend en charge les expressions régulières). Vous pouvez ajouter, supprimer, répertorier ou réinitialiser des phrases protégées à partir de la barre latérale.
- 💬 Ajoute un bloc de changement de langue à chaque README généré (par exemple, `- 🧠 Utilise Google Translate intégré — aucun compte ni clé API personnalisée requis.
- 🖱️ Interface de barre latérale conviviale pour sélectionner les langues, gérer la protection et exécuter des traductions.
- 📊 Affiche la sortie détaillée de la progression de la traduction.

---

## ✅ Versions de code VS prises en charge

- Version minimale : **1.85.0**
- Testé sur **Windows**, **macOS** et **Linux**.

---

## 🧩Installation

### Depuis Marketplace (recommandé)

1. Ouvrez **Visual Studio Code**.
2. Accédez à la vue **Extensions** (`Ctrl+Shift+X`).
3. Recherchez `MultiDoc Translator`.
4. Cliquez sur **Installer**.

### Depuis la source (pour le développement)

1. Clonez ce référentiel :
   ```bash
   git clone https://github.com/fatonyahmadfauzi/MultiDoc-Translator.git
   cd MultiDoc-Translator
   npm install
   ```
2. Ouvrez le dossier dans VS Code.
3. Appuyez sur **F5** pour lancer **Extension Development Host**.
4. Dans la nouvelle fenêtre, ouvrez votre projet contenant `README.md` et (éventuellement) `CHANGELOG.md`.
5. Ouvrez la barre latérale MultiDoc Translator → sélectionnez les langues → cliquez sur **⚙️ Générer des README multilingues**.

---

## ⌨️ Commandes et raccourcis

Cette extension fournit plusieurs commandes accessibles via la palette de commandes (`Ctrl+Shift+P`) ou l'interface de la barre latérale.

| Nom de la commande | ID de commande | Raccourci par défaut | Descriptif |
| :----------------------- | :---------------------------------------- | :--------------- | :---------------------------------------------------------------------- |
| Traduction Run | `multi-doc-translator.run` | `Ctrl+Alt+P` | Générez des fichiers README et CHANGELOG multilingues pour les langues sélectionnées |
| Supprimer la langue sélectionnée | `multi-doc-translator.removeSelected` | - | Supprimer les fichiers de traduction pour les langues sélectionnées |
| Supprimer toutes les langues | `multi-doc-translator.removeAll` | - | Supprimer tous les fichiers de traduction générés |
| Ajouter une phrase protégée | `multi-doc-translator.addProtect` | - | Ajouter une expression ou un modèle d'expression régulière à la liste de protection |
| Supprimer la phrase protégée | `multi-doc-translator.removeProtect` | - | Supprimer une phrase de la liste de protection |
| Liste des phrases protégées | `multi-doc-translator.listProtect` | - | Afficher toutes les phrases actuellement protégées dans Sortie |
| Réinitialiser la liste de protection | `multi-doc-translator.initProtect` | - | Restaurer les phrases protégées par défaut |
| Activer la protection | `multi-doc-translator.enableProtect` | - | Activer le système de protection des phrases |
| Désactiver la protection | `multi-doc-translator.disableProtect` | - | Désactiver le système de protection des phrases |
| Vérifier l'état de la protection | `multi-doc-translator.statusProtect` | - | Afficher l'état actuel de la protection (Activé/Désactivé) |
| Afficher la sortie de progression | `multi-doc-translator.showProgress` | - | Ouvrez le panneau de sortie « Progression de la traduction » |
| Journal des modifications de la configuration automatique | `multi-doc-translator.autoSetupChangelog` | - | Ajoutez une section du journal des modifications à README.md si elle est manquante |
| Traduire uniquement le journal des modifications | `multi-doc-translator.translateChangelog` | - | Traduisez uniquement le fichier `CHANGELOG.md` |
| Détecter l'URL GitHub | `multi-doc-translator.detectGitHubUrl` | - | Détectez et affichez l'URL de votre référentiel GitHub |

---

## 🧠 Exemple

**Avant:**

```markdown
# My Awesome Extension

A simple extension to help developers write better code.

---

## Changelog

See [Journal des modifications](CHANGELOG-FR.md).

---

## License

MIT License © [Your Name](../../LICENSE)
```

**Après (Exemple – Traduit en français) :**

```markdown
# My Awesome Extension

---

Une extension Visual Studio Code qui aide les développeurs à mieux écrire du code.

---

## 🧾 Journal des modifications

Voir toutes les modifications notables pour chaque version dans le fichier [Changelog](CHANGELOG-FR.md).

> 📦 Vous pouvez aussi consulter les notes de publication directement sur la [page des Releases GitHub](https://github.com/your-repo/releases).

---

## 🧾 License

Licence MIT © [Your Name](../../LICENSE)
```

---

## 🧠 Interface de la barre latérale

La barre latérale fournit une interface centralisée pour :

- 📊 **Progression de la traduction** — Consultez les journaux de traduction détaillés.
- 📋 **Gestion du journal des modifications** —
- Section du journal des modifications de configuration automatique dans `README.md`.
- Traduisez uniquement `CHANGELOG.md`.
- Détectez l'URL de votre référentiel GitHub.
- 🛡️ **Paramètres de protection des phrases** —
- Activer/désactiver la protection.
- Ajoutez, supprimez, répertoriez ou réinitialisez les phrases protégées ou les expressions régulières.
- 🌐 **Sélection de la langue** — Choisissez les langues cibles pour la traduction.
- 🚀 **Boutons d'action** —
- Générer des README multilingues
- Supprimer la sélection
- Supprimer tout

---

## 🛠️ Développement

**Compilez TypeScript : **

```bash
npm run compile
```

**Lint le code : **

```bash
npm run lint
```

**Exécuter des tests : **

```bash
npm test
```

---

## 🧑‍💻 Contribuer

1. Forkez ce référentiel.
2. Exécutez `npm install` pour installer les dépendances.
3. Effectuez vos modifications.
4. Compilez TypeScript : `npm run compile`.
5. Testez-le dans VS Code (`F5` → _Extension Development Host_).
6. Soumettez une demande de tirage.

---

## 🐞 Bogues et problèmes

Signalez tout problème ou suggestion sur la [Page des problèmes GitHub](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/issues).

---

## 🧾 Journal des modifications

Consultez tous les changements notables pour chaque version dans le fichier [Journal des modifications](CHANGELOG-FR.md).
📦 Vous pouvez également consulter les notes de version directement sur la [page GitHub Releases](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/releases).

---

## 🧾 Licence

MIT License © [fatonyahmadfauzi](../../LICENSE)
