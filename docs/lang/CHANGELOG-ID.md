# log perubahan

# Change Log

All notable changes to the "auto-translate-readmes" extension will be documented in this file.

Check [Keep a Changelog](http://keepachangelog.com/) for recommendations on how to structure this file.

## [Unreleased]


---

## [1.1.0] – 2025-10-18

### ✨ Ditambahkan

- **Mesin Pengelompokan Paragraf Cerdas**
Menambahkan pengelompokan paragraf cerdas untuk menerjemahkan paragraf multi-baris sebagai blok kohesif sambil mempertahankan tata letak Markdown asli.
→ Menghasilkan terjemahan yang lebih akurat dan sadar konteks tanpa mengubah perataan garis.

- **Mode Pratinjau Berbeda (Eksperimental)**
Pengguna sekarang dapat melihat pratinjau perbedaan terjemahan sebelum menyimpan keluaran menggunakan
Perintah `auto-translate-readmes.previewDiff` di Panel Output VS Code.

- **Deteksi Otomatis README Charset**
Secara otomatis mendeteksi dan mempertahankan pengkodean file sumber (`UTF-8`, `UTF-16`, atau `UTF-8-BOM`) untuk konsistensi lintas platform.

---

### 🔧 Berubah

- **Tokenizer Penurunan Harga Sebaris v3**
Tokenizer yang diperbarui untuk melindungi kombinasi penurunan harga yang kompleks:

- `**bold + _italic_ mix**`
- `[Click _here_](url)`
- Elemen HTML sebaris seperti `<span>` atau `<img>`

- **Konsistensi Blok Kode**
Blok kode kini dipertahankan secara sempurna dengan lekukan dan spasi asli (tanpa pemangkasan atau baris baru tambahan).

- **Peningkatan Pemformatan Pengalih Bahasa**
Pengalih multibahasa sekarang secara otomatis menyesuaikan tanda baca dan gaya spasi untuk setiap bahasa target (e.g., titik dua lebar penuh Jepang, spasi Prancis sebelum titik dua).

- **Integrasi Google API yang Lebih Stabil**
Kini menyertakan fallback otomatis ke titik akhir sekunder ketika `translate.googleapis.com` mencapai batas kecepatan atau kesalahan jaringan.

---

### 🐞 Diperbaiki

- **Penanganan Tebal (Edge Case)**
Memperbaiki kasus ketika `**Before:**` atau `**After (Absolute):**` dipecah menjadi `* *Before:**`.

- **Ruang Tak Terputus dalam Daftar**
Mencegah masalah ketika tanda hubung `-` dalam item daftar digabungkan langsung dengan teks dalam beberapa bahasa (e.g., Prancis, atau Rusia).

- **Pertahankan Baris Baru yang Tertinggal**
Output terjemahan sekarang mempertahankan jumlah baris kosong yang sama dengan file sumber — tidak ada yang terpotong.

- **Stabilitas Emoji**
Memperbaiki masalah pengkodean ketika emoji atau karakter khusus dihilangkan selama penerjemahan.

- **Konsistensi EOL Lintas Platform**
Memastikan karakter akhir baris yang konsisten (`\r\n` untuk Windows, `\n` untuk Unix) sesuai dengan file sumber.

---

### 🚀 Catatan Pengembang

- Logika terjemahan kini dimodulasi dalam `translateBlock()` dengan batching asinkron untuk terjemahan ~30% lebih cepat.
- Setiap README yang dihasilkan menyertakan komentar metadata:
`<!-- Auto-Translated v1.1.0 -->`
untuk melacak versi build secara otomatis.
- Siap untuk **VS Code Marketplace v1.1 rilis stabil**.

---

## [1.0.9] - 2025-10-17

### Berubah

- **Mesin Terjemahan yang Disempurnakan (Revisi Akhir)**
Menyempurnakan proses penerjemahan untuk mempertahankan struktur _exact_, spasi, dan jumlah baris baru dari `README.md` asli.
- Memperkenalkan logika pelestarian baris baru (`split(/(\n)/)`) memastikan tata letak yang identik di semua file yang diterjemahkan.
- Peningkatan pengenalan penurunan harga untuk melewati terjemahan daftar, tabel, blok kode, judul, tautan, dan gambar dengan aman.
- Menghapus normalisasi pemformatan (e.g., pemangkasan baris baru, regex spasi) untuk mempertahankan pemetaan baris 1:1 dengan file sumber.
- Peningkatan penanganan untuk baris konten campuran (teks dengan kode sebaris, emoji, atau penanda daftar).
- Output yang dipastikan ditulis menggunakan pengkodean UTF-8 yang konsisten dan format EOL yang dipertahankan (Windows `\r\n` atau Unix `\n`).

### Tetap

- **Exact Markdown Fidelity** – File yang diterjemahkan sekarang secara visual dan struktural sama persis dengan sumber `README.md`.
- **Pemulihan Indentasi** – Memperbaiki masalah ketika sub-daftar atau item daftar bertumpuk kehilangan indentasinya setelah penerjemahan.
- **Pelestarian Baris Kosong** – Memperbaiki baris kosong yang hilang antara paragraf dan daftar.
- **Penanganan Kode Tebal & Sebaris** – Memperbaiki kasus ketika `**bold**` dan `inline code` pada baris awal salah format.
- **Integritas Garis Tabel** – Memperbaiki garis pemisah yang rusak dalam tabel Penurunan Harga yang kompleks dalam bahasa non-Latin (e.g., China, Korea).

---

## [1.0.8] - 2025-10-17

### Berubah

- **Logika Terjemahan yang Difinalisasi**: Peningkatan presisi untuk penspasian item daftar dan integritas pemformatan.
- Pelestarian Markdown yang ditingkatkan dan penanganan konteks terjemahan yang disempurnakan.

### Tetap

- Indentasi sub-daftar dan baris baru antar paragraf dipertahankan.
- Memperbaiki format teks dan tabel tebal selama penerjemahan.

---

## [1.0.7] - 2025-10-17

### Ditambahkan

- **Masukan Pengguna**: Tombol "Hasilkan" kini menampilkan ikon berputar dan dinonaktifkan selama penerjemahan.
Proses ini juga memicu pesan info dan membuka panel keluaran secara otomatis.

### Berubah

- **Penggabungan yang Diimplementasikan**: Sekarang menggunakan **esbuild** untuk menggabungkan semua kode ke dalam satu file.
- **Peningkatan Logika Penerjemahan**: Ditulis ulang untuk menerjemahkan baris demi baris sekaligus melindungi semua struktur penurunan harga.

### Tetap

- Bug penerbitan karena ketergantungan yang hilang.
- Kesalahan pemformatan termasuk spasi yang hilang, penanda daftar rusak, dan emoji hilang.
- Duplikat header pengalih bahasa.
- Menambahkan dependensi tipe yang hilang untuk kesuksesan build.

---

## [1.0.6]

_(Pembangunan pengembangan internal, digantikan oleh 1.0.7.)_

---

## [1.0.5] - 2025-10-17

### Berubah

- Mengganti perpustakaan `googletrans` yang tidak stabil dengan `deep-translator` untuk keandalan yang lebih baik.

### Tetap

- Memperbaiki kerusakan penurunan harga yang melibatkan kode tebal, sebaris, dan tabel.
- Memperbaiki penggabungan penanda daftar (`-Text` → `- Text`).
- Memindahkan `node-fetch` ke dependensi untuk mencegah kegagalan runtime.

---

## [1.0.4] - 2025-10-15

### Ditambahkan

- Secara otomatis menambahkan blok pengalih multibahasa ke `README.md` jika hilang.

### Tetap

- Memperbaiki pemisah tabel Markdown yang rusak selama penerjemahan.

---

## [1.0.3] - 2025-10-14

### Berubah

- Kemasan yang dioptimalkan untuk ukuran lebih kecil dan pemasangan lebih cepat.

---

## [1.0.2] - 2025-10-14

### Ditambahkan

- Rilis publik awal.
