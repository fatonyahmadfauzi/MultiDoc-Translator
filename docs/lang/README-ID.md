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

> 🌐 Tersedia dalam bahasa lain: [English](../../README.md) | [Polski](README-PL.md) | [中文](README-ZH.md) | [日本語](README-JP.md) | [Deutsch](README-DE.md) | [Français](README-FR.md) | [Español](README-ES.md) | [Русский](README-RU.md) | [Português](README-PT.md) | [한국어](README-KR.md)

---

Ekstensi Visual Studio Code yang secara otomatis menghasilkan file dokumentasi multibahasa (`README.md` dan `CHANGELOG.md`) menggunakan **Google Translate API gratis** — tidak diperlukan kunci API.

---

## ✨ Fitur

- 🌍 Otomatis menerjemahkan `README.md` dan `CHANGELOG.md` ke dalam **10+ bahasa** (Indonesia, Prancis, Jerman, Jepang, Mandarin, Spanyol, Polandia, Rusia, Portugis, Korea).
- ⚙️ **Manajemen Changelog Otomatis** — Mendeteksi `CHANGELOG.md`, menambahkan bagian changelog ke `README.md` jika hilang, dan menerjemahkannya.
- 🔗 **Deteksi URL GitHub Otomatis** — Mengambil URL repositori Anda dari `package.json` atau `.git/config` untuk membuat tautan rilis yang akurat.
- 🔒 **Perlindungan Frasa Tingkat Lanjut** — Melindungi blok kode, kode sebaris, URL, istilah teknis, nama merek, dan frasa khusus (mendukung regex). Anda dapat menambah, menghapus, membuat daftar, atau mengatur ulang frasa yang dilindungi dari sidebar.
- 💬 Menambahkan blok pengalih bahasa ke setiap README yang dihasilkan (mis., `> 🌐 Available in other languages: [English](../../README.md) | ...`).
- 🧠 Menggunakan Google Terjemahan bawaan — tidak memerlukan akun atau kunci API khusus.
- 🖱️ Antarmuka sidebar yang mudah digunakan untuk memilih bahasa, mengelola perlindungan, dan menjalankan terjemahan.
- 📊 Menampilkan keluaran kemajuan terjemahan secara detail.

---

## ✅ Versi VS Code yang Didukung

- Versi minimum : **1.85.0**
- Diuji pada **Windows**, **macOS**, dan **Linux**.

---

## 🧩 Instalasi

### Dari Marketplace (Disarankan)

1. Buka **Kode Visual Studio**.
2. Buka tampilan **Ekstensi** (`Ctrl+Shift+X`).
3. Cari `MultiDoc Translator`.
4. Klik **Instal**.

### Dari Sumber (Untuk Pengembangan)

1. Kloning repositori ini:
   ```bash
   git clone https://github.com/fatonyahmadfauzi/MultiDoc-Translator.git
   cd MultiDoc-Translator
   npm install
   ```
2. Buka folder di VS Code.
3. Tekan **F5** untuk meluncurkan **Extension Development Host**.
4. Di jendela baru, buka proyek Anda yang berisi `README.md` dan (opsional) `CHANGELOG.md`.
5. Buka sidebar MultiDoc Translator → pilih bahasa → klik **⚙️ Hasilkan README Multibahasa**.

---

## ⌨️ Perintah & Pintasan

Ekstensi ini menyediakan beberapa perintah yang dapat diakses melalui Command Palette (`Ctrl+Shift+P`) atau antarmuka sidebar.

| Nama Perintah | ID Perintah | Pintasan Bawaan | Deskripsi |
| :----------------------- | :---------------------------------------- | :--------------- | :---------------------------------------------------------------------- |
| Jalankan Terjemahan | `multi-doc-translator.run` | `Ctrl+Alt+P` | Hasilkan file README dan CHANGELOG multibahasa untuk bahasa yang dipilih |
| Hapus Bahasa yang Dipilih | `multi-doc-translator.removeSelected` | - | Hapus file terjemahan untuk bahasa yang dipilih |
| Hapus Semua Bahasa | `multi-doc-translator.removeAll` | - | Hapus semua file terjemahan yang dihasilkan |
| Tambahkan Frase yang Dilindungi | `multi-doc-translator.addProtect` | - | Tambahkan frase atau pola regex ke daftar proteksi |
| Hapus Frase yang Dilindungi | `multi-doc-translator.removeProtect` | - | Hapus frasa dari daftar perlindungan |
| Daftar Frasa yang Dilindungi | `multi-doc-translator.listProtect` | - | Tampilkan semua frasa yang saat ini dilindungi di Output |
| Atur Ulang Daftar Perlindungan | `multi-doc-translator.initProtect` | - | Kembalikan frasa yang dilindungi default |
| Aktifkan Perlindungan | `multi-doc-translator.enableProtect` | - | Aktifkan sistem perlindungan frase |
| Nonaktifkan Perlindungan | `multi-doc-translator.disableProtect` | - | Nonaktifkan sistem perlindungan frase |
| Periksa Status Perlindungan | `multi-doc-translator.statusProtect` | - | Menampilkan status perlindungan saat ini (Diaktifkan/Dinonaktifkan) |
| Tampilkan Kemajuan Keluaran | `multi-doc-translator.showProgress` | - | Buka panel keluaran "Kemajuan Terjemahan" |
| Log Perubahan Pengaturan Otomatis | `multi-doc-translator.autoSetupChangelog` | - | Tambahkan bagian changelog ke README.md jika tidak ada |
| Terjemahkan Hanya Changelog | `multi-doc-translator.translateChangelog` | - | Terjemahkan hanya file `CHANGELOG.md` |
| Deteksi URL GitHub | `multi-doc-translator.detectGitHubUrl` | - | Deteksi dan tampilkan URL repositori GitHub Anda |

---

## 🧠 Contoh

**Sebelum:**

```markdown
# My Awesome Extension

A simple extension to help developers write better code.

---

## Changelog

See [log perubahan](CHANGELOG-ID.md).

---

## License

MIT License © [Your Name](../../LICENSE)
```

**Setelah (Contoh – Diterjemahkan ke dalam bahasa Prancis):**

```markdown
# My Awesome Extension

> 🌐 Disponible dans d'autres langues : [English](../../README.md) | [Bahasa Indonesia](README-ID.md) | ...

---

Une extension Visual Studio Code qui aide les développeurs à mieux écrire du code.

---

## 🧾 log perubahan

Voir toutes les modifications notables pour chaque version dans le fichier [Changelog](CHANGELOG-FR.md).

> 📦 Vous pouvez aussi consulter les notes de publication directement sur la [page des Releases GitHub](https://github.com/your-repo/releases).

---

## 🧾 License

Licence MIT © [Your Name](../../LICENSE)
```

---

## 🧠 Antarmuka Bilah Sisi

Sidebar menyediakan antarmuka terpusat untuk:

- 📊 **Kemajuan Terjemahan** — Melihat log terjemahan terperinci.
- 📋 **Manajemen Changelog** —
- Bagian changelog pengaturan otomatis di `README.md`.
- Terjemahkan hanya `CHANGELOG.md`.
- Deteksi URL repositori GitHub Anda.
- 🛡️ **Pengaturan Perlindungan Frasa** —
- Mengaktifkan/menonaktifkan perlindungan.
- Tambahkan, hapus, daftar, atau setel ulang frasa atau regex yang dilindungi.
- 🌐 **Pemilihan Bahasa** — Pilih bahasa target untuk terjemahan.
- 🚀 **Tombol Aksi** —
- Hasilkan README Multibahasa
- Hapus yang Dipilih
- Hapus semua

---

## 🛠️ Perkembangan

**Kompilasi TypeScript : **

```bash
npm run compile
```

**Lint kode : **

```bash
npm run lint
```

**Jalankan pengujian : **

```bash
npm test
```

---

## 🧑‍💻 Berkontribusi

1. Cabangkan repositori ini.
2. Jalankan `npm install` untuk menginstal dependensi.
3. Lakukan perubahan Anda.
4. Kompilasi TypeScript: `npm run compile`.
5. Uji di VS Code (`F5` → _Extension Development Host_).
6. Kirim Permintaan Tarik.

---

## 🐞 Bug & Masalah

Laporkan masalah atau saran apa pun di [Halaman Masalah GitHub](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/issues).

---

## 🧾 Catatan Perubahan

Lihat semua perubahan penting untuk setiap versi di file [log perubahan](CHANGELOG-ID.md).
📦 Anda juga dapat melihat catatan rilis langsung di [halaman Rilis GitHub](https://github.com/fatonyahmadfauzi/MultiDoc-Translator/releases).

---

## 🧾 Lisensi

MIT License © [fatonyahmadfauzi](../../LICENSE)
