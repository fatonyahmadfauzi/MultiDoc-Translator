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

> 🌐 Disponível em outros idiomas: [English](../../README.md) | [Polski](README-PL.md) | [中文](README-ZH.md) | [日本語](README-JP.md) | [Deutsch](README-DE.md) | [Français](README-FR.md) | [Español](README-ES.md) | [Русский](README-RU.md) | [Bahasa Indonesia](README-ID.md) | [한국어](README-KR.md)

---

Uma extensão do Visual Studio Code que gera automaticamente arquivos de documentação multilíngue (`README.md` e `CHANGELOG.md`) usando a **API gratuita do Google Translate** — sem necessidade de chave de API.

---

## ✨ Recursos

- 🌍 Traduz automaticamente `README.md` e `CHANGELOG.md` para **mais de 10 idiomas** (indonésio, francês, alemão, japonês, mandarim, espanhol, polonês, russo, português, coreano).
- ⚙️ **Gerenciamento automático de changelog** — Detecta `CHANGELOG.md`, adiciona uma seção de changelog a `README.md` se estiver ausente e a traduz.
- 🔗 **Detecção automática de URL do GitHub** — Recupera a URL do seu repositório de `package.json` ou `.git/config` para criar links de lançamento precisos.
- 🔒 **Proteção avançada de frases** — Protege blocos de código, código embutido, URLs, termos técnicos, nomes de marcas e frases personalizadas (suporta regex). Você pode adicionar, remover, listar ou redefinir frases protegidas na barra lateral.
- 💬 Adiciona um bloco de alternância de idioma a cada README gerado (por exemplo, `> 🌐 Available in other languages: [English](../../README.md) | ...`).
- 🧠 Usa o Google Translate integrado - não é necessária nenhuma conta ou chave de API personalizada.
- 🖱️ Interface de barra lateral amigável para selecionar idiomas, gerenciar proteção e executar traduções.
- 📊 Exibe resultados detalhados do progresso da tradução.

---

## ✅ Versões de código VS suportadas

- Versão mínima : **1.85.0**
- Testado em **Windows**, **macOS** e **Linux**.

---

## 🧩 Instalação

### Do Marketplace (recomendado)

1. Abra **Código do Visual Studio**.
2. Vá para a visualização **Extensões** (`Ctrl+Shift+X`).
3. Pesquise `MultiDoc Translator`.
4. Clique em **Instalar**.

### Da fonte (para desenvolvimento)

1. Clone este repositório:
   ```bash
   git clone https://github.com/fatonyahmadfauzi/MultiDoc-Translator.git
   cd MultiDoc-Translator
   npm install
   ```
2. Abra a pasta no VS Code.
3. Pressione **F5** para iniciar o **Host de desenvolvimento de extensão**.
4. Na nova janela, abra seu projeto contendo `README.md` e (opcionalmente) `CHANGELOG.md`.
5. Abra a barra lateral do MultiDoc Translator → selecione os idiomas → clique em **⚙️ Gerar READMEs multilíngues**.

---

## ⌨️ Comandos e atalhos

Esta extensão fornece vários comandos acessíveis através da Paleta de Comandos (`Ctrl+Shift+P`) ou da interface da barra lateral.

| Nome do Comando | ID do comando | Atalho padrão | Descrição |
| :----------------------- | :---------------------------------------- | :--------------- | :---------------------------------------------------------------------- |
| Executar Tradução | `multi-doc-translator.run` | `Ctrl+Alt+P` | Gere arquivos README e CHANGELOG multilíngues para idiomas selecionados |
| Remover idioma selecionado | `multi-doc-translator.removeSelected` | - | Excluir arquivos de tradução para idiomas selecionados |
| Remover todos os idiomas | `multi-doc-translator.removeAll` | - | Exclua todos os arquivos de tradução gerados |
| Adicionar frase protegida | `multi-doc-translator.addProtect` | - | Adicionar uma frase ou padrão regex à lista de proteção |
| Remover frase protegida | `multi-doc-translator.removeProtect` | - | Remover uma frase da lista de proteção |
| Listar frases protegidas | `multi-doc-translator.listProtect` | - | Exiba todas as frases atualmente protegidas em Saída |
| Redefinir lista de proteção | `multi-doc-translator.initProtect` | - | Restaurar frases protegidas padrão |
| Habilitar proteção | `multi-doc-translator.enableProtect` | - | Habilitar sistema de proteção de frase |
| Desativar proteção | `multi-doc-translator.disableProtect` | - | Desativar sistema de proteção de frase |
| Verifique o status da proteção | `multi-doc-translator.statusProtect` | - | Exibir o status de proteção atual (Ativado/Desativado) |
| Mostrar resultado do progresso | `multi-doc-translator.showProgress` | - | Abra o painel de saída "Progresso da Tradução" |
| Log de alterações da configuração automática | `multi-doc-translator.autoSetupChangelog` | - | Adicione uma seção de changelog ao README.md se estiver faltando |
| Traduzir apenas Changelog | `multi-doc-translator.translateChangelog` | - | Traduza apenas o arquivo `CHANGELOG.md` |
| Detectar URL do GitHub | `multi-doc-translator.detectGitHubUrl` | - | Detecte e exiba o URL do seu repositório GitHub |

---

## 🧠 Exemplo

**Antes:**

```markdown
# My Awesome Extension

A simple extension to help developers write better code.

---

## Changelog

See [Registro de alterações](CHANGELOG-PT.md).

---

## License

MIT License © [Your Name](../../LICENSE)
```

**Depois (Exemplo – Traduzido para o francês):**

```markdown
# My Awesome Extension

> 🌐 Disponible dans d'autres langues : [English](../../README.md) | [Bahasa Indonesia](README-ID.md) | ...

---

Une extension Visual Studio Code qui aide les développeurs à mieux écrire du code.

---

## 🧾 Registro de alterações

Voir toutes les modifications notables pour chaque version dans le fichier [Changelog](CHANGELOG-FR.md).

> 📦 Vous pouvez aussi consulter les notes de publication directement sur la [page des Releases GitHub](https://github.com/your-repo/releases).

---

## 🧾 License

Licence MIT © [Your Name](../../LICENSE)
```

---

## 🧠 Interface da barra lateral

A barra lateral fornece uma interface centralizada para:

- 📊 **Progresso da tradução** — Veja registros detalhados da tradução.
- 📋 **Gerenciamento do registro de alterações** —
- Seção de changelog de configuração automática em `README.md`.
- Traduzir apenas `CHANGELOG.md`.
- Detecte o URL do seu repositório GitHub.
- 🛡️ **Configurações de proteção de frase** —
- Ativar/desativar proteção.
- Adicione, remova, liste ou redefina frases ou regex protegidas.
- 🌐 **Seleção de idioma** — Escolha os idiomas de destino para tradução.
- 🚀 **Botões de ação** —
- Gerar READMEs multilíngues
- Remover selecionado
- Remover tudo

---

## 🛠️ Desenvolvimento

**Compilar TypeScript : **

```bash
npm run compile
```

**Lint o código : **

```bash
npm run lint
```

**Executar testes : **

```bash
npm test
```

---

## 🧑‍💻 Contribuindo

1. Bifurque este repositório.
2. Execute `npm install` para instalar dependências.
3. Faça suas alterações.
4. Compile TypeScript: `npm run compile`.
5. Teste-o no VS Code (`F5` → _Extension Development Host_).
6. Envie uma solicitação pull.

---

## 🐞 Bugs e problemas

Relate quaisquer problemas ou sugestões na [página de problemas do GitHub](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/issues).

---

## 🧾 Registro de alterações

Veja todas as alterações notáveis ​​para cada versão no arquivo [Registro de alterações](CHANGELOG-PT.md).
📦 Você também pode visualizar as notas de lançamento diretamente na [página de lançamentos do GitHub](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/releases).

---

## 🧾 Licença

MIT License © [fatonyahmadfauzi](../../LICENSE)
