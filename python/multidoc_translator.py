#!/usr/bin/env python3
"""
MultiDoc Translator - Automated multi-language documentation translator
Support for README.md and CHANGELOG.md translation with protection features
"""

import os
import re
import json
import time
import argparse
import shutil
import sys
from deep_translator import GoogleTranslator
from tqdm import tqdm
import colorama
from colorama import Fore, Style, init
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich import box

SOURCE_FILE = "README.md"
CHANGELOG_FILE = "CHANGELOG.md"
PACKAGE_JSON = "package.json"
OUTPUT_DIR = "docs/lang"
PROTECTED_FILE = "protected_phrases.json"
PROTECT_STATUS_FILE = ".protect_status"

# ---------------------- DISPLAY LANGUAGE SETTINGS ----------------------
DISPLAY_LANGUAGES = {
    "en": {
        "translating_readme": "📘 Translating README to {lang_name} ({lang_code})...",
        "readme_created": "✅ {path} successfully created",
        "translating_changelog": "📘 Translating CHANGELOG to {lang_name} ({lang_code})...",
        "changelog_created": "✅ {path} successfully created",
        "changelog_links_updated": "✅ Changelog links updated in {filename}",
        "all_translated": "🎉 All READMEs successfully translated!",
        "language_switcher_updated": "✅ Language switcher in {filename} updated",
        "file_deleted": "🗑️ File {filename} successfully deleted",
        "folder_deleted": "🗑️ Folder {folder} successfully deleted",
        "changelog_section_added": "✅ Changelog section added to README.md with proper spacing and separators",
        "changelog_spacing_fixed": "✅ Fixed changelog section spacing and separators in README.md",
        "github_url_detected": "🔍 GitHub Repository Detection Results:",
        "repo_url": "📦 Repository URL: {url}",
        "releases_url": "🚀 Releases URL: {url}",
        "sources_checked": "📋 Sources checked:",
        "no_github_url": "❌ Could not detect GitHub repository URL automatically.",
        "protection_reset": "🔁 File protected_phrases.json has been reset to default.",
        "phrase_added": "✅ Phrase '{phrase}' added to protection.",
        "phrase_removed": "🗑️ Phrase '{phrase}' removed from protection.",
        "protected_phrases_list": "📜 Protected phrases list:",
        "protection_enabled": "🟢 Protection enabled.",
        "protection_disabled": "🔴 Protection disabled.",
        "protection_status": "🧩 Protection status: {status}",
        "changelog_setup_completed": "✅ Changelog setup completed",
        "changelog_setup_failed": "❌ Changelog setup failed",
        "no_changelog_file": "❌ You don't have CHANGELOG.md file in root directory",
        "changelog_translated": "✅ Successfully translated CHANGELOG to {count} languages",
        "no_changelog_translated": "❌ No CHANGELOG files were successfully translated",
        "languages_removed": "🎉 Languages successfully removed: {langs}",
        "all_languages_removed": "🎉 All translation files successfully removed",
        "auto_setup_changelog": "🔧 Auto-setting up changelog section in README...",
        "checking_changelog_spacing": "🔧 Checking changelog section spacing...",
        "no_valid_language": "❌ No valid language codes provided.",
        "language_not_recognized": "❌ Language code '{code}' not recognized. Continuing...",
        "file_not_found": "⚠️ File {filename} not found",
        "folder_not_empty": "⚠️ Folder {folder} not empty, not deleted",
        "failed_delete_file": "❌ Failed to delete {filename}: {error}",
        "failed_delete_folder": "❌ Failed to delete folder: {error}",
        "failed_update_main": "❌ Failed to update main README: {error}",
        "failed_translate_changelog": "❌ Failed to translate CHANGELOG: {error}",
        "failed_update_changelog_links": "❌ Failed to update changelog links in {filename}: {error}",
        "failed_update_switcher": "❌ Failed to update language switcher in {filename}: {error}",
        "translation_failed": "❌ Translation failed: {error}",
        "reading_package_error": "❌ Error reading package.json: {error}",
        "reading_git_error": "❌ Error reading .git/config: {error}",
        "reading_github_error": "❌ Error searching GitHub URL in README: {error}",
        "changelog_section_exists": "ℹ️ Changelog section already exists in README.md",
        "no_changelog_file_root": "❌ No CHANGELOG.md file found in root directory",
        "no_translation_files": "ℹ️ No translated README files found",
        "language_not_supported": "⚠️ Display language '{code}' not supported, using default",
        "help_description": "MultiDoc Translator - Automated multi-language documentation translator",
        "help_epilog": """
Examples:
  # Translate README to Japanese and Chinese
  python multidoc_translator.py --lang jp,zh

  # Translate only CHANGELOG to all languages with Japanese notifications
  python multidoc_translator.py --translate-changelog all --display jp

  # Remove specific language files
  python multidoc_translator.py --remove-lang jp,zh

  # Auto setup changelog section in README
  python multidoc_translator.py --auto-setup-changelog

  # Detect GitHub repository URL
  python multidoc_translator.py --detect-github-url
        """,
        "help_lang": "Language codes to translate (comma-separated). Supported: pl, zh, jp, de, fr, es, ru, pt, id, kr",
        "help_remove_lang": "Remove specific translated language files (comma-separated)",
        "help_remove_all_lang": "Remove ALL translated language files and clean up folders",
        "help_add_protect": "Add a phrase to protection list (regex pattern supported)",
        "help_remove_protect": "Remove a phrase from protection list",
        "help_list_protect": "Show all currently protected phrases",
        "help_init_protect": "Reset protected_phrases.json to default values",
        "help_enable_protect": "Enable phrase protection during translation",
        "help_disable_protect": "Disable phrase protection during translation",
        "help_status_protect": "Check if phrase protection is currently enabled",
        "help_translate_changelog": "Translate only CHANGELOG.md (use 'all' for all languages or specify codes)",
        "help_auto_setup_changelog": "Automatically add changelog section to README.md if CHANGELOG.md exists",
        "help_detect_github_url": "Detect and display GitHub repository URL from various sources",
        "help_display": "Display language for terminal notifications (en, id, jp, de, es, fr, kr, pl, pt, ru, zh)",

        # NEW: CHANGELOG Only actions translations
        "changelog.onlyActions": "📋 CHANGELOG Only Actions",
        "changelog.generateRemoveOnly": "Generate/Remove CHANGELOG Only", 
        "changelog.onlyDescription": "These actions only affect CHANGELOG files, README files remain unchanged.",
        "changelog.generateOnly": "🌐 Generate CHANGELOG Only",
        "changelog.removeSelected": "🗑️ Remove CHANGELOG Selected",
        "changelog.affectsSelected": "Affects only selected languages: {0} languages",
        "changelog.generateWith": "📋 Generate with CHANGELOG",
        "changelog.checkedDescription": "When checked: Translates both README and CHANGELOG files",
        "changelog.uncheckedDescription": "When unchecked: Translates only README files",
        
        # NEW: Progress messages for CHANGELOG only
        "progress.translatingWithChangelog": "Translating README + CHANGELOG",
        "progress.translatingReadmeOnly": "Translating README only",
        "success.filesSavedWithChangelog": "READMEs and CHANGELOGs", 
        "success.filesSavedReadmeOnly": "READMEs only",
        "success.translationCompletedWithChangelog": "✅ {0} READMEs and CHANGELOGs successfully translated!",
        "success.translationCompletedReadmeOnly": "✅ {0} READMEs successfully translated!",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.md not found - skipping CHANGELOG translation",
        
        # NEW: Error and success messages for CHANGELOG only
        "errors.changelogGenerateFailed": "❌ CHANGELOG generation failed",
        "errors.changelogRemoveSelectedFailed": "❌ Failed to remove selected CHANGELOG files",
        "success.changelogGenerated": "✅ CHANGELOG successfully generated for {count} languages",
        "success.changelogRemovedSelected": "✅ {0} CHANGELOG files successfully removed",
        "confirmation.removeChangelogSelected": "Are you sure you want to remove CHANGELOG files for {0} selected languages? README files will not be affected.",
        
        # NEW: Command help texts
        "help_generate_changelog_only": "Generate CHANGELOG files only for selected languages (README files remain unchanged)",
        "help_remove_changelog_selected": "Remove CHANGELOG files for selected languages only (README files remain unchanged)", 
        "help_remove_changelog_only": "Remove ALL CHANGELOG files only (README files remain unchanged)",
        "help_with_changelog": "When enabled: Translate both README and CHANGELOG. When disabled: Translate only README",
        "errors.noLanguagesSelected": "❌ No languages selected",
        "errors.noLanguagesSelectedRemove": "❌ No languages selected for removal",
        "progress.startingTranslation": "🚀 Starting translation for {count} languages - {mode_text}",
        "progress.translatingLanguage": "📖 Translating {lang_name} ({current}/{total})...",
        "progress.waiting": "⏳ Waiting {seconds} seconds before next translation...",
        "progress.completed": "✅ Translation process completed",
        "progress.filesSaved": "💾 Files saved to: {path}",
        "progress.removingSelected": "🗑️ Removing selected CHANGELOG files...",
        "progress.fileCreated": "✅ Removed: {path}",
        "progress.removingChangelog": "🗑️ Removing all CHANGELOG files...",
        "changelog.translatingChangelog": "📘 Translating CHANGELOG for {count} languages...",
        "changelog.translating": "🔧 Translating CHANGELOG to {lang_name}...",
        "changelog.translated": "✅ CHANGELOG translated to {lang_name}",
        "changelog.autoSettingUp": "🔧 Auto-setting up changelog section...",
        "changelog.checkingSpacing": "🔧 Checking changelog section spacing...",
        "progress.changelogTranslated": "✅ CHANGELOG translated to {lang_name}",
        "errors.translationFailedShort": "❌ Translation failed for {lang_name}",
        "errors.translationFailed": "❌ Translation failed for {lang_code}: {error}",
        "errors.changelogTranslationFailed": "❌ CHANGELOG translation failed",
        "success.changelogTranslationCompleted": "✅ CHANGELOG translation completed",
        "errors.changelogRemoveFailed": "❌ Failed to remove CHANGELOG file",
        "info.noChangelogFiles": "ℹ️ No CHANGELOG files found",
        "success.changelogRemoved": "✅ {count} CHANGELOG files successfully removed",
        "confirmation.removeChangelog": "Are you sure you want to remove ALL CHANGELOG files? README files will not be affected."
,
        "menu_debug": "Toggle Debug Mode",
        "debug_enabled": "Debug mode is now ENABLED.",
        "debug_disabled": "Debug mode is now DISABLED.",
        "debug_current": "Current"
    },
    "id": {
        "translating_readme": "📘 Menerjemahkan README ke {lang_name} ({lang_code})...",
        "readme_created": "✅ {path} berhasil dibuat",
        "translating_changelog": "📘 Menerjemahkan CHANGELOG ke {lang_name} ({lang_code})...",
        "changelog_created": "✅ {path} berhasil dibuat",
        "changelog_links_updated": "✅ Link changelog diupdate di {filename}",
        "all_translated": "🎉 Semua README berhasil diterjemahkan!",
        "language_switcher_updated": "✅ Language switcher di {filename} diperbarui",
        "file_deleted": "🗑️ File {filename} berhasil dihapus",
        "folder_deleted": "🗑️ Folder {folder} berhasil dihapus",
        "changelog_section_added": "✅ Changelog section ditambahkan ke README.md dengan spacing dan pemisah yang benar",
        "changelog_spacing_fixed": "✅ Memperbaiki spacing dan pemisah section Changelog di README.md",
        "github_url_detected": "🔍 Hasil Deteksi Repository GitHub:",
        "repo_url": "📦 URL Repository: {url}",
        "releases_url": "🚀 URL Releases: {url}",
        "sources_checked": "📋 Sumber yang dicek:",
        "no_github_url": "❌ Tidak bisa mendeteksi URL repository GitHub secara otomatis.",
        "protection_reset": "🔁 File protected_phrases.json telah di-reset ke default.",
        "phrase_added": "✅ Frasa '{phrase}' ditambahkan ke proteksi.",
        "phrase_removed": "🗑️ Frasa '{phrase}' dihapus dari proteksi.",
        "protected_phrases_list": "📜 Daftar frasa yang diproteksi:",
        "protection_enabled": "🟢 Proteksi diaktifkan.",
        "protection_disabled": "🔴 Proteksi dinonaktifkan.",
        "protection_status": "🧩 Status proteksi: {status}",
        "changelog_setup_completed": "✅ Setup Changelog selesai",
        "changelog_setup_failed": "❌ Setup Changelog gagal",
        "no_changelog_file": "❌ Anda tidak memiliki file CHANGELOG.md di direktori root",
        "changelog_translated": "✅ Berhasil menerjemahkan CHANGELOG ke {count} bahasa",
        "no_changelog_translated": "❌ Tidak ada file CHANGELOG yang berhasil diterjemahkan",
        "languages_removed": "🎉 Bahasa berhasil dihapus: {langs}",
        "all_languages_removed": "🎉 Semua file bahasa terjemahan berhasil dihapus",
        "auto_setup_changelog": "🔧 Auto-setting up section changelog di README...",
        "checking_changelog_spacing": "🔧 Mengecek spacing section changelog...",
        "no_valid_language": "❌ Tidak ada kode bahasa yang valid.",
        "language_not_recognized": "❌ Kode bahasa '{code}' tidak dikenali. Dilanjutkan...",
        "file_not_found": "⚠️ File {filename} tidak ditemukan",
        "folder_not_empty": "⚠️ Folder {folder} tidak kosong, tidak dihapus",
        "failed_delete_file": "❌ Gagal menghapus {filename}: {error}",
        "failed_delete_folder": "❌ Gagal menghapus folder: {error}",
        "failed_update_main": "❌ Gagal update README utama: {error}",
        "failed_translate_changelog": "❌ Gagal menerjemahkan CHANGELOG: {error}",
        "failed_update_changelog_links": "❌ Gagal update link changelog di {filename}: {error}",
        "failed_update_switcher": "❌ Gagal update language switcher di {filename}: {error}",
        "translation_failed": "❌ Terjemahan gagal: {error}",
        "reading_package_error": "❌ Error membaca package.json: {error}",
        "reading_git_error": "❌ Error membaca .git/config: {error}",
        "reading_github_error": "❌ Error mencari URL GitHub di README: {error}",
        "changelog_section_exists": "ℹ️ Section Changelog sudah ada di README.md",
        "no_changelog_file_root": "❌ Tidak ada file CHANGELOG.md di direktori root",
        "no_translation_files": "ℹ️ Tidak ada file README terjemahan yang ditemukan",
        "language_not_supported": "⚠️ Bahasa display '{code}' tidak didukung, menggunakan default",
        "help_description": "MultiDoc Translator - Penerjemah dokumentasi multi-bahasa otomatis",
        "help_epilog": """
Contoh:
  # Terjemahkan README ke Jepang dan China
  python multidoc_translator.py --lang jp,zh

  # Hanya terjemahkan CHANGELOG ke semua bahasa dengan notifikasi Jepang
  python multidoc_translator.py --translate-changelog all --display jp

  # Hapus file bahasa tertentu
  python multidoc_translator.py --remove-lang jp,zh

  # Setup otomatis section changelog di README
  python multidoc_translator.py --auto-setup-changelog

  # Deteksi URL repository GitHub
  python multidoc_translator.py --detect-github-url
        """,
        "help_lang": "Kode bahasa untuk diterjemahkan (dipisahkan koma). Didukung: pl, zh, jp, de, fr, es, ru, pt, id, kr",
        "help_remove_lang": "Hapus file bahasa terjemahan tertentu (dipisahkan koma)",
        "help_remove_all_lang": "Hapus SEMUA file bahasa terjemahan dan bersihkan folder",
        "help_add_protect": "Tambahkan frasa ke daftar proteksi (pattern regex didukung)",
        "help_remove_protect": "Hapus frasa dari daftar proteksi",
        "help_list_protect": "Tampilkan semua frasa yang saat ini diproteksi",
        "help_init_protect": "Reset protected_phrases.json ke nilai default",
        "help_enable_protect": "Aktifkan proteksi frasa selama terjemahan",
        "help_disable_protect": "Nonaktifkan proteksi frasa selama terjemahan",
        "help_status_protect": "Periksa apakah proteksi frasa saat ini aktif",
        "help_translate_changelog": "Hanya terjemahkan CHANGELOG.md (gunakan 'all' untuk semua bahasa atau tentukan kode)",
        "help_auto_setup_changelog": "Otomatis tambahkan section changelog ke README.md jika CHANGELOG.md ada",
        "help_detect_github_url": "Deteksi dan tampilkan URL repository GitHub dari berbagai sumber",
        "help_display": "Bahasa untuk notifikasi terminal (en, id, jp, de, es, fr, kr, pl, pt, ru, zh)",

        "changelog.onlyActions": "📋 Aksi CHANGELOG Saja",
        "changelog.generateRemoveOnly": "Generate/Hapus CHANGELOG Saja",
        "changelog.onlyDescription": "Aksi ini hanya mempengaruhi file CHANGELOG, file README tidak berubah.",
        "changelog.generateOnly": "🌐 Generate CHANGELOG Saja",
        "changelog.removeSelected": "🗑️ Hapus CHANGELOG Terpilih",
        "changelog.affectsSelected": "Hanya mempengaruhi bahasa terpilih: {0} bahasa",
        "changelog.generateWith": "📋 Generate dengan CHANGELOG",
        "changelog.checkedDescription": "Jika dicentang: Menerjemahkan file README dan CHANGELOG",
        "changelog.uncheckedDescription": "Jika tidak dicentang: Hanya menerjemahkan file README",
        
        "progress.translatingWithChangelog": "Menerjemahkan README + CHANGELOG",
        "progress.translatingReadmeOnly": "Menerjemahkan README saja",
        "success.filesSavedWithChangelog": "README dan CHANGELOG",
        "success.filesSavedReadmeOnly": "README saja",
        "success.translationCompletedWithChangelog": "✅ {0} README dan CHANGELOG berhasil diterjemahkan!",
        "success.translationCompletedReadmeOnly": "✅ {0} README berhasil diterjemahkan!",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.md tidak ditemukan - melewati penerjemahan CHANGELOG",
        
        "errors.changelogGenerateFailed": "❌ Generate CHANGELOG gagal",
        "errors.changelogRemoveSelectedFailed": "❌ Gagal menghapus file CHANGELOG terpilih",
        "success.changelogGenerated": "✅ CHANGELOG berhasil digenerate untuk {0} bahasa",
        "success.changelogRemovedSelected": "✅ {0} file CHANGELOG berhasil dihapus",
        "confirmation.removeChangelogSelected": "Apakah Anda yakin ingin menghapus file CHANGELOG untuk {0} bahasa terpilih? File README tidak akan terpengaruh.",
        
        "help_generate_changelog_only": "Generate file CHANGELOG saja untuk bahasa terpilih (file README tidak berubah)",
        "help_remove_changelog_selected": "Hapus file CHANGELOG untuk bahasa terpilih saja (file README tidak berubah)",
        "help_remove_changelog_only": "Hapus SEMUA file CHANGELOG saja (file README tidak berubah)",
        "help_with_changelog": "Jika diaktifkan: Terjemahkan README dan CHANGELOG. Jika dinonaktifkan: Hanya terjemahkan README",
        "errors.noLanguagesSelected": "❌ Tidak ada bahasa yang dipilih",
        "errors.noLanguagesSelectedRemove": "❌ Tidak ada bahasa yang dipilih untuk dihapus",
        "progress.startingTranslation": "🚀 Memulai terjemahan untuk {count} bahasa - {mode_text}",
        "progress.translatingLanguage": "📖 Menerjemahkan {lang_name} ({current}/{total})...",
        "progress.waiting": "⏳ Menunggu {seconds} detik sebelum terjemahan berikutnya...",
        "progress.completed": "✅ Proses terjemahan selesai",
        "progress.filesSaved": "💾 File disimpan ke: {path}",
        "progress.removingSelected": "🗑️ Menghapus file CHANGELOG terpilih...",
        "progress.fileCreated": "✅ Dihapus: {path}",
        "progress.removingChangelog": "🗑️ Menghapus semua file CHANGELOG...",
        "changelog.translatingChangelog": "📘 Menerjemahkan CHANGELOG untuk {count} bahasa...",
        "changelog.translating": "🔧 Menerjemahkan CHANGELOG ke {lang_name}...",
        "changelog.translated": "✅ CHANGELOG diterjemahkan ke {lang_name}",
        "changelog.autoSettingUp": "🔧 Auto-setting up section changelog...",
        "changelog.checkingSpacing": "🔧 Mengecek spacing section changelog...",
        "progress.changelogTranslated": "✅ CHANGELOG diterjemahkan ke {lang_name}",
        "errors.translationFailedShort": "❌ Terjemahan gagal untuk {lang_name}",
        "errors.translationFailed": "❌ Terjemahan gagal untuk {lang_code}: {error}",
        "errors.changelogTranslationFailed": "❌ Terjemahan CHANGELOG gagal",
        "success.changelogTranslationCompleted": "✅ Terjemahan CHANGELOG selesai",
        "errors.changelogRemoveFailed": "❌ Gagal menghapus file CHANGELOG",
        "info.noChangelogFiles": "ℹ️ Tidak ada file CHANGELOG ditemukan",
        "success.changelogRemoved": "✅ {count} file CHANGELOG berhasil dihapus",
        "confirmation.removeChangelog": "Apakah Anda yakin ingin menghapus SEMUA file CHANGELOG? File README tidak akan terpengaruh."
,
        "menu_debug": "Alihkan Mode Debug",
        "debug_enabled": "Mode debug sekarang DIAKTIFKAN.",
        "debug_disabled": "Mode debug sekarang DINONAKTIFKAN.",
        "debug_current": "Saat ini"
    },
    "jp": {
        "translating_readme": "📘 READMEを{lang_name}に翻訳中 ({lang_code})...",
        "readme_created": "✅ {path} が正常に作成されました",
        "translating_changelog": "📘 CHANGELOGを{lang_name}に翻訳中 ({lang_code})...",
        "changelog_created": "✅ {path} が正常に作成されました",
        "changelog_links_updated": "✅ {filename} のチェンジログリンクを更新しました",
        "all_translated": "🎉 すべてのREADMEが正常に翻訳されました！",
        "language_switcher_updated": "✅ {filename} の言語スイッチャーを更新しました",
        "file_deleted": "🗑️ ファイル {filename} を削除しました",
        "folder_deleted": "🗑️ フォルダ {folder} を削除しました",
        "changelog_section_added": "✅ README.mdに適切な間隔と区切りでチェンジログセクションを追加しました",
        "changelog_spacing_fixed": "✅ README.mdのチェンジログセクションの間隔と区切りを修正しました",
        "github_url_detected": "🔍 GitHubリポジトリ検出結果:",
        "repo_url": "📦 リポジトリURL: {url}",
        "releases_url": "🚀 リリースURL: {url}",
        "sources_checked": "📋 チェックしたソース:",
        "no_github_url": "❌ GitHubリポジトリURLを自動的に検出できませんでした。",
        "protection_reset": "🔁 protected_phrases.jsonファイルをデフォルトにリセットしました。",
        "phrase_added": "✅ フレーズ「{phrase}」を保護に追加しました。",
        "phrase_removed": "🗑️ フレーズ「{phrase}」を保護から削除しました。",
        "protected_phrases_list": "📜 保護されたフレーズのリスト:",
        "protection_enabled": "🟢 保護を有効にしました。",
        "protection_disabled": "🔴 保護を無効にしました。",
        "protection_status": "🧩 保護ステータス: {status}",
        "changelog_setup_completed": "✅ チェンジログのセットアップが完了しました",
        "changelog_setup_failed": "❌ チェンジログのセットアップに失敗しました",
        "no_changelog_file": "❌ ルートディレクトリにCHANGELOG.mdファイルがありません",
        "changelog_translated": "✅ {count}言語にCHANGELOGを正常に翻訳しました",
        "no_changelog_translated": "❌ 翻訳されたCHANGELOGファイルはありません",
        "languages_removed": "🎉 言語が正常に削除されました: {langs}",
        "all_languages_removed": "🎉 すべての翻訳ファイルが正常に削除されました",
        "auto_setup_changelog": "🔧 READMEにチェンジログセクションを自動設定中...",
        "checking_changelog_spacing": "🔧 チェンジログセクションの間隔を確認中...",
        "no_valid_language": "❌ 有効な言語コードが提供されていません。",
        "language_not_recognized": "❌ 言語コード「{code}」は認識されません。続行します...",
        "file_not_found": "⚠️ ファイル {filename} が見つかりません",
        "folder_not_empty": "⚠️ フォルダ {folder} が空ではないため、削除しません",
        "failed_delete_file": "❌ {filename} の削除に失敗: {error}",
        "failed_delete_folder": "❌ フォルダの削除に失敗: {error}",
        "failed_update_main": "❌ メインREADMEの更新に失敗: {error}",
        "failed_translate_changelog": "❌ CHANGELOGの翻訳に失敗: {error}",
        "failed_update_changelog_links": "❌ {filename} のチェンジログリンク更新に失敗: {error}",
        "failed_update_switcher": "❌ {filename} の言語スイッチャー更新に失敗: {error}",
        "translation_failed": "❌ 翻訳に失敗: {error}",
        "reading_package_error": "❌ package.jsonの読み込みエラー: {error}",
        "reading_git_error": "❌ .git/configの読み込みエラー: {error}",
        "reading_github_error": "❌ READMEでのGitHub URL検索エラー: {error}",
        "changelog_section_exists": "ℹ️ チェンジログセクションは既にREADME.mdに存在します",
        "no_changelog_file_root": "❌ ルートディレクトリにCHANGELOG.mdファイルがありません",
        "no_translation_files": "ℹ️ 翻訳されたREADMEファイルが見つかりません",
        "language_not_supported": "⚠️ 表示言語「{code}」はサポートされていません、デフォルトを使用します",
                "help_description": "MultiDoc Translator - 自動化された多言語ドキュメント翻訳ツール",
        "help_epilog": """
使用例:
  # READMEを日本語と中国語に翻訳
  python multidoc_translator.py --lang jp,zh

  # 変更ログのみをすべての言語に翻訳（日本語通知付き）
  python multidoc_translator.py --translate-changelog all --display jp

  # 特定の言語ファイルを削除
  python multidoc_translator.py --remove-lang jp,zh

  # READMEに変更ログセクションを自動設定
  python multidoc_translator.py --auto-setup-changelog

  # GitHubリポジトリURLを検出
  python multidoc_translator.py --detect-github-url
        """,
        "help_lang": "翻訳する言語コード（カンマ区切り）。対応: pl, zh, jp, de, fr, es, ru, pt, id, kr",
        "help_remove_lang": "特定の翻訳言語ファイルを削除（カンマ区切り）",
        "help_remove_all_lang": "すべての翻訳ファイルを削除しフォルダを整理",
        "help_add_protect": "保護リストにフレーズを追加（正規表現パターン対応）",
        "help_remove_protect": "保護リストからフレーズを削除",
        "help_list_protect": "現在保護されているすべてのフレーズを表示",
        "help_init_protect": "protected_phrases.jsonをデフォルト値にリセット",
        "help_enable_protect": "翻訳中のフレーズ保護を有効化",
        "help_disable_protect": "翻訳中のフレーズ保護を無効化",
        "help_status_protect": "フレーズ保護が現在有効かどうかを確認",
        "help_translate_changelog": "CHANGELOG.mdのみ翻訳（全言語の場合は'all'、またはコード指定）",
        "help_auto_setup_changelog": "CHANGELOG.mdが存在する場合、README.mdに変更ログセクションを自動追加",
        "help_detect_github_url": "さまざまなソースからGitHubリポジトリURLを検出して表示",
        "help_display": "ターミナル通知の表示言語 (en, id, jp, de, es, fr, kr, pl, pt, ru, zh)",

        "changelog.onlyActions": "📋 CHANGELOGのみのアクション",
        "changelog.generateRemoveOnly": "CHANGELOGのみ生成/削除",
        "changelog.onlyDescription": "これらのアクションはCHANGELOGファイルのみに影響し、READMEファイルは変更されません。",
        "changelog.generateOnly": "🌐 CHANGELOGのみ生成",
        "changelog.removeSelected": "🗑️ 選択したCHANGELOGを削除",
        "changelog.affectsSelected": "選択した言語のみに影響: {0}言語",
        "changelog.generateWith": "📋 CHANGELOG付きで生成",
        "changelog.checkedDescription": "チェック時: READMEとCHANGELOGファイルの両方を翻訳",
        "changelog.uncheckedDescription": "未チェック時: READMEファイルのみ翻訳",
        
        "progress.translatingWithChangelog": "README + CHANGELOGを翻訳中",
        "progress.translatingReadmeOnly": "READMEのみ翻訳中",
        "success.filesSavedWithChangelog": "READMEとCHANGELOG",
        "success.filesSavedReadmeOnly": "READMEのみ",
        "success.translationCompletedWithChangelog": "✅ {0}個のREADMEとCHANGELOGが正常に翻訳されました！",
        "success.translationCompletedReadmeOnly": "✅ {0}個のREADMEが正常に翻訳されました！",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.mdが見つかりません - CHANGELOG翻訳をスキップします",
        
        "errors.changelogGenerateFailed": "❌ CHANGELOG生成に失敗しました",
        "errors.changelogRemoveSelectedFailed": "❌ 選択したCHANGELOGファイルの削除に失敗しました",
        "success.changelogGenerated": "✅ {0}言語のCHANGELOGが正常に生成されました",
        "success.changelogRemovedSelected": "✅ {0}個のCHANGELOGファイルが正常に削除されました",
        "confirmation.removeChangelogSelected": "選択した{0}言語のCHANGELOGファイルを削除してもよろしいですか？READMEファイルは影響を受けません。",
        
        "help_generate_changelog_only": "選択した言語のCHANGELOGファイルのみ生成（READMEファイルは変更されません）",
        "help_remove_changelog_selected": "選択した言語のCHANGELOGファイルのみ削除（READMEファイルは変更されません）",
        "help_remove_changelog_only": "すべてのCHANGELOGファイルのみ削除（READMEファイルは変更されません）",
        "help_with_changelog": "有効時: READMEとCHANGELOGを翻訳。無効時: READMEのみ翻訳",
        "errors.noLanguagesSelected": "❌ 言語が選択されていません",
        "errors.noLanguagesSelectedRemove": "❌ 削除する言語が選択されていません",
        "progress.startingTranslation": "🚀 {count}言語の翻訳を開始します - {mode_text}",
        "progress.translatingLanguage": "📖 {lang_name}を翻訳中 ({current}/{total})...",
        "progress.waiting": "⏳ 次の翻訳まで{seconds}秒待機中...",
        "progress.completed": "✅ 翻訳プロセスが完了しました",
        "progress.filesSaved": "💾 ファイルを保存しました: {path}",
        "progress.removingSelected": "🗑️ 選択したCHANGELOGファイルを削除中...",
        "progress.fileCreated": "✅ 削除しました: {path}",
        "progress.removingChangelog": "🗑️ すべてのCHANGELOGファイルを削除中...",
        "changelog.translatingChangelog": "📘 {count}言語のCHANGELOGを翻訳中...",
        "changelog.translating": "🔧 CHANGELOGを{lang_name}に翻訳中...",
        "changelog.translated": "✅ CHANGELOGを{lang_name}に翻訳しました",
        "changelog.autoSettingUp": "🔧 チェンジログセクションを自動設定中...",
        "changelog.checkingSpacing": "🔧 チェンジログセクションの間隔を確認中...",
        "progress.changelogTranslated": "✅ CHANGELOGを{lang_name}に翻訳しました",
        "errors.translationFailedShort": "❌ {lang_name}の翻訳に失敗しました",
        "errors.translationFailed": "❌ {lang_code}の翻訳に失敗しました: {error}",
        "errors.changelogTranslationFailed": "❌ CHANGELOGの翻訳に失敗しました",
        "success.changelogTranslationCompleted": "✅ CHANGELOGの翻訳が完了しました",
        "errors.changelogRemoveFailed": "❌ CHANGELOGファイルの削除に失敗しました",
        "info.noChangelogFiles": "ℹ️ CHANGELOGファイルが見つかりません",
        "success.changelogRemoved": "✅ {count}個のCHANGELOGファイルを削除しました",
        "confirmation.removeChangelog": "すべてのCHANGELOGファイルを削除してもよろしいですか？READMEファイルは影響を受けません。"
,
        "menu_debug": "デバッグモードの切り替え",
        "debug_enabled": "デバッグモードが【有効】になりました。",
        "debug_disabled": "デバッグモードが【無効】になりました。",
        "debug_current": "現在"
    },
    "de": {
        "translating_readme": "📘 Übersetze README in {lang_name} ({lang_code})...",
        "readme_created": "✅ {path} erfolgreich erstellt",
        "translating_changelog": "📘 Übersetze CHANGELOG in {lang_name} ({lang_code})...",
        "changelog_created": "✅ {path} erfolgreich erstellt",
        "changelog_links_updated": "✅ Changelog-Links in {filename} aktualisiert",
        "all_translated": "🎉 Alle READMEs erfolgreich übersetzt!",
        "language_switcher_updated": "✅ Sprachumschaltung in {filename} aktualisiert",
        "file_deleted": "🗑️ Datei {filename} erfolgreich gelöscht",
        "folder_deleted": "🗑️ Ordner {folder} erfolgreich gelöscht",
        "changelog_section_added": "✅ Changelog-Abschnitt zu README.md mit korrektem Abstand und Trennzeichen hinzugefügt",
        "changelog_spacing_fixed": "✅ Changelog-Abschnittsabstand und Trennzeichen in README.md behoben",
        "github_url_detected": "🔍 GitHub-Repository-Erkennungsergebnisse:",
        "repo_url": "📦 Repository-URL: {url}",
        "releases_url": "🚀 Releases-URL: {url}",
        "sources_checked": "📋 Geprüfte Quellen:",
        "no_github_url": "❌ GitHub-Repository-URL konnte nicht automatisch erkannt werden.",
        "protection_reset": "🔁 Datei protected_phrases.json wurde auf Standard zurückgesetzt.",
        "phrase_added": "✅ Ausdruck '{phrase}' zum Schutz hinzugefügt.",
        "phrase_removed": "🗑️ Ausdruck '{phrase}' aus Schutz entfernt.",
        "protected_phrases_list": "📜 Geschützte Ausdrücke Liste:",
        "protection_enabled": "🟢 Schutz aktiviert.",
        "protection_disabled": "🔴 Schutz deaktiviert.",
        "protection_status": "🧩 Schutzstatus: {status}",
        "changelog_setup_completed": "✅ Changelog-Einrichtung abgeschlossen",
        "changelog_setup_failed": "❌ Changelog-Einrichtung fehlgeschlagen",
        "no_changelog_file": "❌ Sie haben keine CHANGELOG.md-Datei im Root-Verzeichnis",
        "changelog_translated": "✅ CHANGELOG erfolgreich in {count} Sprachen übersetzt",
        "no_changelog_translated": "❌ Keine CHANGELOG-Dateien wurden erfolgreich übersetzt",
        "languages_removed": "🎉 Sprachen erfolgreich entfernt: {langs}",
        "all_languages_removed": "🎉 Alle Übersetzungsdateien erfolgreich entfernt",
        "auto_setup_changelog": "🔧 Automatische Einrichtung des Changelog-Abschnitts in README...",
        "checking_changelog_spacing": "🔧 Überprüfe Changelog-Abschnittsabstand...",
        "no_valid_language": "❌ Keine gültigen Sprachcodes angegeben.",
        "language_not_recognized": "❌ Sprachcode '{code}' nicht erkannt. Fortfahren...",
        "file_not_found": "⚠️ Datei {filename} nicht gefunden",
        "folder_not_empty": "⚠️ Ordner {folder} nicht leer, nicht gelöscht",
        "failed_delete_file": "❌ Löschen von {filename} fehlgeschlagen: {error}",
        "failed_delete_folder": "❌ Löschen des Ordners fehlgeschlagen: {error}",
        "failed_update_main": "❌ Aktualisierung der Haupt-README fehlgeschlagen: {error}",
        "failed_translate_changelog": "❌ Übersetzung von CHANGELOG fehlgeschlagen: {error}",
        "failed_update_changelog_links": "❌ Aktualisierung der Changelog-Links in {filename} fehlgeschlagen: {error}",
        "failed_update_switcher": "❌ Aktualisierung der Sprachumschaltung in {filename} fehlgeschlagen: {error}",
        "translation_failed": "❌ Übersetzung fehlgeschlagen: {error}",
        "reading_package_error": "❌ Fehler beim Lesen von package.json: {error}",
        "reading_git_error": "❌ Fehler beim Lesen von .git/config: {error}",
        "reading_github_error": "❌ Fehler bei der Suche nach GitHub-URL in README: {error}",
        "changelog_section_exists": "ℹ️ Changelog-Abschnitt existiert bereits in README.md",
        "no_changelog_file_root": "❌ Keine CHANGELOG.md-Datei im Root-Verzeichnis gefunden",
        "no_translation_files": "ℹ️ Keine übersetzten README-Dateien gefunden",
        "language_not_supported": "⚠️ Anzeigesprache '{code}' nicht unterstützt, verwende Standard",
        "help_description": "MultiDoc Translator - Automatisierter mehrsprachiger Dokumentationsübersetzer",
        "help_epilog": """
Beispiele:
  # README auf Japanisch und Chinesisch übersetzen
  python multidoc_translator.py --lang jp,zh

  # Nur CHANGELOG in alle Sprachen mit japanischen Benachrichtigungen übersetzen
  python multidoc_translator.py --translate-changelog all --display jp

  # Bestimmte Sprachdateien entfernen
  python multidoc_translator.py --remove-lang jp,zh

  # Changelog-Bereich automatisch in README einrichten
  python multidoc_translator.py --auto-setup-changelog

  # GitHub-Repository-URL erkennen
  python multidoc_translator.py --detect-github-url
        """,
        "help_lang": "Zu übersetzende Sprachcodes (kommagetrennt). Unterstützt: pl, zh, jp, de, fr, es, ru, pt, id, kr",
        "help_remove_lang": "Bestimmte übersetzte Sprachdateien entfernen (kommagetrennt)",
        "help_remove_all_lang": "ALLE übersetzten Sprachdateien entfernen und Ordner bereinigen",
        "help_add_protect": "Eine Phrase zur Schutzliste hinzufügen (Regex-Muster unterstützt)",
        "help_remove_protect": "Eine Phrase aus der Schutzliste entfernen",
        "help_list_protect": "Alle aktuell geschützten Phrasen anzeigen",
        "help_init_protect": "protected_phrases.json auf Standardwerte zurücksetzen",
        "help_enable_protect": "Phrasenschutz während der Übersetzung aktivieren",
        "help_disable_protect": "Phrasenschutz während der Übersetzung deaktivieren",
        "help_status_protect": "Überprüfen, ob Phrasenschutz aktuell aktiviert ist",
        "help_translate_changelog": "Nur CHANGELOG.md übersetzen ('all' für alle Sprachen oder Codes angeben)",
        "help_auto_setup_changelog": "Changelog-Bereich automatisch zu README.md hinzufügen, wenn CHANGELOG.md existiert",
        "help_detect_github_url": "GitHub-Repository-URL aus verschiedenen Quellen erkennen und anzeigen",
        "help_display": "Anzeigesprache für Terminalbenachrichtigungen (en, id, jp, de, es, fr, kr, pl, pt, ru, zh)",

        "changelog.onlyActions": "📋 Nur CHANGELOG Aktionen",
        "changelog.generateRemoveOnly": "CHANGELOG nur generieren/entfernen",
        "changelog.onlyDescription": "Diese Aktionen betreffen nur CHANGELOG-Dateien, README-Dateien bleiben unverändert.",
        "changelog.generateOnly": "🌐 Nur CHANGELOG generieren",
        "changelog.removeSelected": "🗑️ Ausgewählte CHANGELOGs entfernen",
        "changelog.affectsSelected": "Betrifft nur ausgewählte Sprachen: {0} Sprachen",
        "changelog.generateWith": "📋 Mit CHANGELOG generieren",
        "changelog.checkedDescription": "Wenn aktiviert: Übersetzt sowohl README- als auch CHANGELOG-Dateien",
        "changelog.uncheckedDescription": "Wenn deaktiviert: Übersetzt nur README-Dateien",
        
        "progress.translatingWithChangelog": "Übersetze README + CHANGELOG",
        "progress.translatingReadmeOnly": "Übersetze nur README",
        "success.filesSavedWithChangelog": "READMEs und CHANGELOGs",
        "success.filesSavedReadmeOnly": "Nur READMEs",
        "success.translationCompletedWithChangelog": "✅ {0} READMEs und CHANGELOGs erfolgreich übersetzt!",
        "success.translationCompletedReadmeOnly": "✅ {0} READMEs erfolgreich übersetzt!",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.md nicht gefunden - überspringe CHANGELOG-Übersetzung",
        
        "errors.changelogGenerateFailed": "❌ CHANGELOG-Generierung fehlgeschlagen",
        "errors.changelogRemoveSelectedFailed": "❌ Fehler beim Entfernen ausgewählter CHANGELOG-Dateien",
        "success.changelogGenerated": "✅ CHANGELOG erfolgreich für {0} Sprachen generiert",
        "success.changelogRemovedSelected": "✅ {0} CHANGELOG-Dateien erfolgreich entfernt",
        "confirmation.removeChangelogSelected": "Sind Sie sicher, dass Sie CHANGELOG-Dateien für {0} ausgewählte Sprachen entfernen möchten? README-Dateien werden nicht beeinflusst.",
        
        "help_generate_changelog_only": "Nur CHANGELOG-Dateien für ausgewählte Sprachen generieren (README-Dateien bleiben unverändert)",
        "help_remove_changelog_selected": "Nur CHANGELOG-Dateien für ausgewählte Sprachen entfernen (README-Dateien bleiben unverändert)",
        "help_remove_changelog_only": "Nur ALLE CHANGELOG-Dateien entfernen (README-Dateien bleiben unverändert)",
        "help_with_changelog": "Wenn aktiviert: Übersetze README und CHANGELOG. Wenn deaktiviert: Übersetze nur README",
        "errors.noLanguagesSelected": "❌ Keine Sprachen ausgewählt",
        "errors.noLanguagesSelectedRemove": "❌ Keine Sprachen zum Entfernen ausgewählt",
        "progress.startingTranslation": "🚀 Starte Übersetzung für {count} Sprachen - {mode_text}",
        "progress.translatingLanguage": "📖 Übersetze {lang_name} ({current}/{total})...",
        "progress.waiting": "⏳ Warte {seconds} Sekunden vor der nächsten Übersetzung...",
        "progress.completed": "✅ Übersetzungsprozess abgeschlossen",
        "progress.filesSaved": "💾 Dateien gespeichert in: {path}",
        "progress.removingSelected": "🗑️ Entferne ausgewählte CHANGELOG-Dateien...",
        "progress.fileCreated": "✅ Entfernt: {path}",
        "progress.removingChangelog": "🗑️ Entferne alle CHANGELOG-Dateien...",
        "changelog.translatingChangelog": "📘 Übersetze CHANGELOG für {count} Sprachen...",
        "changelog.translating": "🔧 Übersetze CHANGELOG in {lang_name}...",
        "changelog.translated": "✅ CHANGELOG in {lang_name} übersetzt",
        "changelog.autoSettingUp": "🔧 Automatische Einrichtung des Changelog-Abschnitts...",
        "changelog.checkingSpacing": "🔧 Überprüfe Changelog-Abschnittsabstand...",
        "progress.changelogTranslated": "✅ CHANGELOG in {lang_name} übersetzt",
        "errors.translationFailedShort": "❌ Übersetzung für {lang_name} fehlgeschlagen",
        "errors.translationFailed": "❌ Übersetzung für {lang_code} fehlgeschlagen: {error}",
        "errors.changelogTranslationFailed": "❌ CHANGELOG-Übersetzung fehlgeschlagen",
        "success.changelogTranslationCompleted": "✅ CHANGELOG-Übersetzung abgeschlossen",
        "errors.changelogRemoveFailed": "❌ CHANGELOG-Datei konnte nicht entfernt werden",
        "info.noChangelogFiles": "ℹ️ Keine CHANGELOG-Dateien gefunden",
        "success.changelogRemoved": "✅ {count} CHANGELOG-Dateien erfolgreich entfernt",
        "confirmation.removeChangelog": "Sind Sie sicher, dass Sie ALLE CHANGELOG-Dateien entfernen möchten? README-Dateien werden nicht beeinflusst."
,
        "menu_debug": "Debug-Modus umschalten",
        "debug_enabled": "Debug-Modus ist jetzt AKTIVIERT.",
        "debug_disabled": "Debug-Modus ist jetzt DEAKTIVIERT.",
        "debug_current": "Aktuell"
    },
    "es": {
        "translating_readme": "📘 Traduciendo README a {lang_name} ({lang_code})...",
        "readme_created": "✅ {path} creado exitosamente",
        "translating_changelog": "📘 Traduciendo CHANGELOG a {lang_name} ({lang_code})...",
        "changelog_created": "✅ {path} creado exitosamente",
        "changelog_links_updated": "✅ Enlaces del changelog actualizados en {filename}",
        "all_translated": "🎉 ¡Todos los READMEs traducidos exitosamente!",
        "language_switcher_updated": "✅ Selector de idioma actualizado en {filename}",
        "file_deleted": "🗑️ Archivo {filename} eliminado exitosamente",
        "folder_deleted": "🗑️ Carpeta {folder} eliminada exitosamente",
        "changelog_section_added": "✅ Sección de changelog añadida a README.md con espaciado y separadores adecuados",
        "changelog_spacing_fixed": "✅ Espaciado y separadores de la sección changelog corregidos en README.md",
        "github_url_detected": "🔍 Resultados de detección de repositorio GitHub:",
        "repo_url": "📦 URL del repositorio: {url}",
        "releases_url": "🚀 URL de releases: {url}",
        "sources_checked": "📋 Fuentes verificadas:",
        "no_github_url": "❌ No se pudo detectar automáticamente la URL del repositorio GitHub.",
        "protection_reset": "🔁 Archivo protected_phrases.json ha sido restablecido a predeterminado.",
        "phrase_added": "✅ Frase '{phrase}' añadida a protección.",
        "phrase_removed": "🗑️ Frase '{phrase}' eliminada de protección.",
        "protected_phrases_list": "📜 Lista de frases protegidas:",
        "protection_enabled": "🟢 Protección habilitada.",
        "protection_disabled": "🔴 Protección deshabilitada.",
        "protection_status": "🧩 Estado de protección: {status}",
        "changelog_setup_completed": "✅ Configuración de changelog completada",
        "changelog_setup_failed": "❌ Configuración de changelog fallida",
        "no_changelog_file": "❌ No tienes archivo CHANGELOG.md en el directorio raíz",
        "changelog_translated": "✅ CHANGELOG traducido exitosamente a {count} idiomas",
        "no_changelog_translated": "❌ No se tradujeron exitosamente archivos CHANGELOG",
        "languages_removed": "🎉 Idiomas eliminados exitosamente: {langs}",
        "all_languages_removed": "🎉 Todos los archivos de traducción eliminados exitosamente",
        "auto_setup_changelog": "🔧 Configuración automática de sección changelog en README...",
        "checking_changelog_spacing": "🔧 Verificando espaciado de sección changelog...",
        "no_valid_language": "❌ No se proporcionaron códigos de idioma válidos.",
        "language_not_recognized": "❌ Código de idioma '{code}' no reconocido. Continuando...",
        "file_not_found": "⚠️ Archivo {filename} no encontrado",
        "folder_not_empty": "⚠️ Carpeta {folder} no vacía, no eliminada",
        "failed_delete_file": "❌ Error al eliminar {filename}: {error}",
        "failed_delete_folder": "❌ Error al eliminar carpeta: {error}",
        "failed_update_main": "❌ Error al actualizar README principal: {error}",
        "failed_translate_changelog": "❌ Error al traducir CHANGELOG: {error}",
        "failed_update_changelog_links": "❌ Error al actualizar enlaces de changelog en {filename}: {error}",
        "failed_update_switcher": "❌ Error al actualizar selector de idioma en {filename}: {error}",
        "translation_failed": "❌ Error en traducción: {error}",
        "reading_package_error": "❌ Error leyendo package.json: {error}",
        "reading_git_error": "❌ Error leyendo .git/config: {error}",
        "reading_github_error": "❌ Error buscando URL de GitHub en README: {error}",
        "changelog_section_exists": "ℹ️ La sección changelog ya existe en README.md",
        "no_changelog_file_root": "❌ No se encontró archivo CHANGELOG.md en directorio raíz",
        "no_translation_files": "ℹ️ No se encontraron archivos README traducidos",
        "language_not_supported": "⚠️ Idioma de visualización '{code}' no soportado, usando predeterminado",
        "help_description": "MultiDoc Translator - Traductor automatizado de documentación multilingüe",
        "help_epilog": """
Ejemplos:
  # Traducir README a japonés y chino
  python multidoc_translator.py --lang jp,zh

  # Traducir solo CHANGELOG a todos los idiomas con notificaciones en japonés
  python multidoc_translator.py --translate-changelog all --display jp

  # Eliminar archivos de idiomas específicos
  python multidoc_translator.py --remove-lang jp,zh

  # Configuración automática de sección changelog en README
  python multidoc_translator.py --auto-setup-changelog

  # Detectar URL de repositorio GitHub
  python multidoc_translator.py --detect-github-url
        """,
        "help_lang": "Códigos de idioma a traducir (separados por comas). Soportados: pl, zh, jp, de, fr, es, ru, pt, id, kr",
        "help_remove_lang": "Eliminar archivos de idiomas traducidos específicos (separados por comas)",
        "help_remove_all_lang": "Eliminar TODOS los archivos de idiomas traducidos y limpiar carpetas",
        "help_add_protect": "Agregar una frase a la lista de protección (patrón regex compatible)",
        "help_remove_protect": "Eliminar una frase de la lista de protección",
        "help_list_protect": "Mostrar todas las frases actualmente protegidas",
        "help_init_protect": "Restablecer protected_phrases.json a valores predeterminados",
        "help_enable_protect": "Habilitar protección de frases durante la traducción",
        "help_disable_protect": "Deshabilitar protección de frases durante la traducción",
        "help_status_protect": "Verificar si la protección de frases está actualmente habilitada",
        "help_translate_changelog": "Traducir solo CHANGELOG.md (usar 'all' para todos los idiomas o especificar códigos)",
        "help_auto_setup_changelog": "Agregar automáticamente sección changelog a README.md si CHANGELOG.md existe",
        "help_detect_github_url": "Detectar y mostrar URL de repositorio GitHub desde varias fuentes",
        "help_display": "Idioma de visualización para notificaciones de terminal (en, id, jp, de, es, fr, kr, pl, pt, ru, zh)",

        "changelog.onlyActions": "📋 Acciones solo de CHANGELOG",
        "changelog.generateRemoveOnly": "Generar/Eliminar solo CHANGELOG",
        "changelog.onlyDescription": "Estas acciones solo afectan archivos CHANGELOG, los archivos README permanecen sin cambios.",
        "changelog.generateOnly": "🌐 Generar solo CHANGELOG",
        "changelog.removeSelected": "🗑️ Eliminar CHANGELOG seleccionado",
        "changelog.affectsSelected": "Afecta solo idiomas seleccionados: {0} idiomas",
        "changelog.generateWith": "📋 Generar con CHANGELOG",
        "changelog.checkedDescription": "Cuando está marcado: Traduce archivos README y CHANGELOG",
        "changelog.uncheckedDescription": "Cuando no está marcado: Traduce solo archivos README",
        
        "progress.translatingWithChangelog": "Traduciendo README + CHANGELOG",
        "progress.translatingReadmeOnly": "Traduciendo solo README",
        "success.filesSavedWithChangelog": "READMES y CHANGELOGs",
        "success.filesSavedReadmeOnly": "Solo READMEs",
        "success.translationCompletedWithChangelog": "✅ ¡{0} READMEs y CHANGELOGs traducidos exitosamente!",
        "success.translationCompletedReadmeOnly": "✅ ¡{0} READMEs traducidos exitosamente!",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.md no encontrado - omitiendo traducción de CHANGELOG",
        
        "errors.changelogGenerateFailed": "❌ Generación de CHANGELOG fallida",
        "errors.changelogRemoveSelectedFailed": "❌ Error al eliminar archivos CHANGELOG seleccionados",
        "success.changelogGenerated": "✅ CHANGELOG generado exitosamente para {0} idiomas",
        "success.changelogRemovedSelected": "✅ {0} archivos CHANGELOG eliminados exitosamente",
        "confirmation.removeChangelogSelected": "¿Está seguro de que desea eliminar archivos CHANGELOG para {0} idiomas seleccionados? Los archivos README no se verán afectados.",
        
        "help_generate_changelog_only": "Generar solo archivos CHANGELOG para idiomas seleccionados (los archivos README permanecen sin cambios)",
        "help_remove_changelog_selected": "Eliminar solo archivos CHANGELOG para idiomas seleccionados (los archivos README permanecen sin cambios)",
        "help_remove_changelog_only": "Eliminar solo TODOS los archivos CHANGELOG (los archivos README permanecen sin cambios)",
        "help_with_changelog": "Cuando está habilitado: Traduce README y CHANGELOG. Cuando está deshabilitado: Traduce solo README",
        "errors.noLanguagesSelected": "❌ No se seleccionaron idiomas",
        "errors.noLanguagesSelectedRemove": "❌ No se seleccionaron idiomas para eliminar",
        "progress.startingTranslation": "🚀 Iniciando traducción para {count} idiomas - {mode_text}",
        "progress.translatingLanguage": "📖 Traduciendo {lang_name} ({current}/{total})...",
        "progress.waiting": "⏳ Esperando {seconds} segundos antes de la siguiente traducción...",
        "progress.completed": "✅ Proceso de traducción completado",
        "progress.filesSaved": "💾 Archivos guardados en: {path}",
        "progress.removingSelected": "🗑️ Eliminando archivos CHANGELOG seleccionados...",
        "progress.fileCreated": "✅ Eliminado: {path}",
        "progress.removingChangelog": "🗑️ Eliminando todos los archivos CHANGELOG...",
        "changelog.translatingChangelog": "📘 Traduciendo CHANGELOG para {count} idiomas...",
        "changelog.translating": "🔧 Traduciendo CHANGELOG a {lang_name}...",
        "changelog.translated": "✅ CHANGELOG traducido a {lang_name}",
        "changelog.autoSettingUp": "🔧 Configuración automática de sección changelog...",
        "changelog.checkingSpacing": "🔧 Verificando espaciado de sección changelog...",
        "progress.changelogTranslated": "✅ CHANGELOG traducido a {lang_name}",
        "errors.translationFailedShort": "❌ Traducción fallida para {lang_name}",
        "errors.translationFailed": "❌ Traducción fallida para {lang_code}: {error}",
        "errors.changelogTranslationFailed": "❌ Traducción de CHANGELOG fallida",
        "success.changelogTranslationCompleted": "✅ Traducción de CHANGELOG completada",
        "errors.changelogRemoveFailed": "❌ Error al eliminar archivo CHANGELOG",
        "info.noChangelogFiles": "ℹ️ No se encontraron archivos CHANGELOG",
        "success.changelogRemoved": "✅ {count} archivos CHANGELOG eliminados exitosamente",
        "confirmation.removeChangelog": "¿Está seguro de que desea eliminar TODOS los archivos CHANGELOG? Los archivos README no se verán afectados."
,
        "menu_debug": "Alternar Modo Depuración",
        "debug_enabled": "El modo de depuración ahora está ACTIVADO.",
        "debug_disabled": "El modo de depuración ahora está DESACTIVADO.",
        "debug_current": "Actual"
    },
    "fr": {
        "translating_readme": "📘 Traduction du README en {lang_name} ({lang_code})...",
        "readme_created": "✅ {path} créé avec succès",
        "translating_changelog": "📘 Traduction du CHANGELOG en {lang_name} ({lang_code})...",
        "changelog_created": "✅ {path} créé avec succès",
        "changelog_links_updated": "✅ Liens du changelog mis à jour dans {filename}",
        "all_translated": "🎉 Tous les README traduits avec succès !",
        "language_switcher_updated": "✅ Sélecteur de langue mis à jour dans {filename}",
        "file_deleted": "🗑️ Fichier {filename} supprimé avec succès",
        "folder_deleted": "🗑️ Dossier {folder} supprimé avec succès",
        "changelog_section_added": "✅ Section changelog ajoutée à README.md avec espacement et séparateurs appropriés",
        "changelog_spacing_fixed": "✅ Espacement et séparateurs de section changelog corrigés dans README.md",
        "github_url_detected": "🔍 Résultats de détection du dépôt GitHub :",
        "repo_url": "📦 URL du dépôt : {url}",
        "releases_url": "🚀 URL des releases : {url}",
        "sources_checked": "📋 Sources vérifiées :",
        "no_github_url": "❌ Impossible de détecter automatiquement l'URL du dépôt GitHub.",
        "protection_reset": "🔁 Fichier protected_phrases.json a été réinitialisé par défaut.",
        "phrase_added": "✅ Expression '{phrase}' ajoutée à la protection.",
        "phrase_removed": "🗑️ Expression '{phrase}' retirée de la protection.",
        "protected_phrases_list": "📜 Liste des expressions protégées :",
        "protection_enabled": "🟢 Protection activée.",
        "protection_disabled": "🔴 Protection désactivée.",
        "protection_status": "🧩 Statut de protection : {status}",
        "changelog_setup_completed": "✅ Configuration du changelog terminée",
        "changelog_setup_failed": "❌ Échec de la configuration du changelog",
        "no_changelog_file": "❌ Vous n'avez pas de fichier CHANGELOG.md dans le répertoire racine",
        "changelog_translated": "✅ CHANGELOG traduit avec succès en {count} langues",
        "no_changelog_translated": "❌ Aucun fichier CHANGELOG n'a été traduit avec succès",
        "languages_removed": "🎉 Langues supprimées avec succès : {langs}",
        "all_languages_removed": "🎉 Tous les fichiers de traduction supprimés avec succès",
        "auto_setup_changelog": "🔧 Configuration automatique de la section changelog dans README...",
        "checking_changelog_spacing": "🔧 Vérification de l'espacement de la section changelog...",
        "no_valid_language": "❌ Aucun code de langue valide fourni.",
        "language_not_recognized": "❌ Code de langue '{code}' non reconnu. Continuation...",
        "file_not_found": "⚠️ Fichier {filename} non trouvé",
        "folder_not_empty": "⚠️ Dossier {folder} non vide, non supprimé",
        "failed_delete_file": "❌ Échec de la suppression de {filename} : {error}",
        "failed_delete_folder": "❌ Échec de la suppression du dossier : {error}",
        "failed_update_main": "❌ Échec de la mise à jour du README principal : {error}",
        "failed_translate_changelog": "❌ Échec de la traduction du CHANGELOG : {error}",
        "failed_update_changelog_links": "❌ Échec de la mise à jour des liens du changelog dans {filename} : {error}",
        "failed_update_switcher": "❌ Échec de la mise à jour du sélecteur de langue dans {filename} : {error}",
        "translation_failed": "❌ Échec de la traduction : {error}",
        "reading_package_error": "❌ Erreur de lecture de package.json : {error}",
        "reading_git_error": "❌ Erreur de lecture de .git/config : {error}",
        "reading_github_error": "❌ Erreur de recherche d'URL GitHub dans README : {error}",
        "changelog_section_exists": "ℹ️ La section changelog existe déjà dans README.md",
        "no_changelog_file_root": "❌ Aucun fichier CHANGELOG.md trouvé dans le répertoire racine",
        "no_translation_files": "ℹ️ Aucun fichier README traduit trouvé",
        "language_not_supported": "⚠️ Langue d'affichage '{code}' non supportée, utilisation par défaut",
        "help_description": "MultiDoc Translator - Traducteur automatisé de documentation multilingue",
        "help_epilog": """
Exemples :
  # Traduire README en japonais et chinois
  python multidoc_translator.py --lang jp,zh

  # Traduire seulement CHANGELOG dans toutes les langues avec notifications en japonais
  python multidoc_translator.py --translate-changelog all --display jp

  # Supprimer des fichiers de langue spécifiques
  python multidoc_translator.py --remove-lang jp,zh

  # Configuration automatique de la section changelog dans README
  python multidoc_translator.py --auto-setup-changelog

  # Détecter l'URL du dépôt GitHub
  python multidoc_translator.py --detect-github-url
        """,
        "help_lang": "Codes de langue à traduire (séparés par des virgules). Pris en charge : pl, zh, jp, de, fr, es, ru, pt, id, kr",
        "help_remove_lang": "Supprimer des fichiers de langue traduits spécifiques (séparés par des virgules)",
        "help_remove_all_lang": "Supprimer TOUS les fichiers de langue traduits et nettoyer les dossiers",
        "help_add_protect": "Ajouter une phrase à la liste de protection (modèle regex pris en charge)",
        "help_remove_protect": "Supprimer une phrase de la liste de protection",
        "help_list_protect": "Afficher toutes les phrases actuellement protégées",
        "help_init_protect": "Réinitialiser protected_phrases.json aux valeurs par défaut",
        "help_enable_protect": "Activer la protection des phrases pendant la traduction",
        "help_disable_protect": "Désactiver la protection des phrases pendant la traduction",
        "help_status_protect": "Vérifier si la protection des phrases est actuellement activée",
        "help_translate_changelog": "Traduire seulement CHANGELOG.md (utiliser 'all' pour toutes les langues ou spécifier des codes)",
        "help_auto_setup_changelog": "Ajouter automatiquement la section changelog à README.md si CHANGELOG.md existe",
        "help_detect_github_url": "Détecter et afficher l'URL du dépôt GitHub depuis diverses sources",
        "help_display": "Langue d'affichage pour les notifications du terminal (en, id, jp, de, es, fr, kr, pl, pt, ru, zh)",

        "changelog.onlyActions": "📋 Actions CHANGELOG uniquement",
        "changelog.generateRemoveOnly": "Générer/Supprimer CHANGELOG uniquement",
        "changelog.onlyDescription": "Ces actions n'affectent que les fichiers CHANGELOG, les fichiers README restent inchangés.",
        "changelog.generateOnly": "🌐 Générer CHANGELOG uniquement",
        "changelog.removeSelected": "🗑️ Supprimer CHANGELOG sélectionné",
        "changelog.affectsSelected": "Affecte uniquement les langues sélectionnées : {0} langues",
        "changelog.generateWith": "📋 Générer avec CHANGELOG",
        "changelog.checkedDescription": "Lorsqu'elle est cochée : Traduit les fichiers README et CHANGELOG",
        "changelog.uncheckedDescription": "Lorsqu'elle n'est pas cochée : Traduit uniquement les fichiers README",
        
        "progress.translatingWithChangelog": "Traduction README + CHANGELOG",
        "progress.translatingReadmeOnly": "Traduction README uniquement",
        "success.filesSavedWithChangelog": "READMES et CHANGELOGs",
        "success.filesSavedReadmeOnly": "READMES uniquement",
        "success.translationCompletedWithChangelog": "✅ {0} READMEs et CHANGELOGs traduits avec succès !",
        "success.translationCompletedReadmeOnly": "✅ {0} READMEs traduits avec succès !",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.md non trouvé - ignore la traduction CHANGELOG",
        
        "errors.changelogGenerateFailed": "❌ Échec de la génération CHANGELOG",
        "errors.changelogRemoveSelectedFailed": "❌ Échec de la suppression des fichiers CHANGELOG sélectionnés",
        "success.changelogGenerated": "✅ CHANGELOG généré avec succès pour {0} langues",
        "success.changelogRemovedSelected": "✅ {0} fichiers CHANGELOG supprimés avec succès",
        "confirmation.removeChangelogSelected": "Êtes-vous sûr de vouloir supprimer les fichiers CHANGELOG pour {0} langues sélectionnées ? Les fichiers README ne seront pas affectés.",
        
        "help_generate_changelog_only": "Générer uniquement les fichiers CHANGELOG pour les langues sélectionnées (les fichiers README restent inchangés)",
        "help_remove_changelog_selected": "Supprimer uniquement les fichiers CHANGELOG pour les langues sélectionnées (les fichiers README restent inchangés)",
        "help_remove_changelog_only": "Supprimer uniquement TOUS les fichiers CHANGELOG (les fichiers README restent inchangés)",
        "help_with_changelog": "Lorsqu'elle est activée : Traduit README et CHANGELOG. Lorsqu'elle est désactivée : Traduit uniquement README",
        "errors.noLanguagesSelected": "❌ Aucune langue sélectionnée",
        "errors.noLanguagesSelectedRemove": "❌ Aucune langue sélectionnée pour suppression",
        "progress.startingTranslation": "🚀 Démarrage de la traduction pour {count} langues - {mode_text}",
        "progress.translatingLanguage": "📖 Traduction de {lang_name} ({current}/{total})...",
        "progress.waiting": "⏳ Attente de {seconds} secondes avant la prochaine traduction...",
        "progress.completed": "✅ Processus de traduction terminé",
        "progress.filesSaved": "💾 Fichiers enregistrés dans: {path}",
        "progress.removingSelected": "🗑️ Suppression des fichiers CHANGELOG sélectionnés...",
        "progress.fileCreated": "✅ Supprimé: {path}",
        "progress.removingChangelog": "🗑️ Suppression de tous les fichiers CHANGELOG...",
        "changelog.translatingChangelog": "📘 Traduction de CHANGELOG pour {count} langues...",
        "changelog.translating": "🔧 Traduction de CHANGELOG en {lang_name}...",
        "changelog.translated": "✅ CHANGELOG traduit en {lang_name}",
        "changelog.autoSettingUp": "🔧 Configuration automatique de la section changelog...",
        "changelog.checkingSpacing": "🔧 Vérification de l'espacement de la section changelog...",
        "progress.changelogTranslated": "✅ CHANGELOG traduit en {lang_name}",
        "errors.translationFailedShort": "❌ Échec de la traduction pour {lang_name}",
        "errors.translationFailed": "❌ Échec de la traduction pour {lang_code}: {error}",
        "errors.changelogTranslationFailed": "❌ Échec de la traduction CHANGELOG",
        "success.changelogTranslationCompleted": "✅ Traduction CHANGELOG terminée",
        "errors.changelogRemoveFailed": "❌ Échec de la suppression du fichier CHANGELOG",
        "info.noChangelogFiles": "ℹ️ Aucun fichier CHANGELOG trouvé",
        "success.changelogRemoved": "✅ {count} fichiers CHANGELOG supprimés avec succès",
        "confirmation.removeChangelog": "Êtes-vous sûr de vouloir supprimer TOUS les fichiers CHANGELOG ? Les fichiers README ne seront pas affectés."
,
        "menu_debug": "Basculer le mode débogage",
        "debug_enabled": "Le mode débogage est maintenant ACTIVÉ.",
        "debug_disabled": "Le mode débogage est maintenant DÉSACTIVÉ.",
        "debug_current": "Actuel"
    },
    "kr": {
        "translating_readme": "📘 README를 {lang_name}({lang_code})로 번역 중...",
        "readme_created": "✅ {path}이(가) 성공적으로 생성됨",
        "translating_changelog": "📘 CHANGELOG를 {lang_name}({lang_code})로 번역 중...",
        "changelog_created": "✅ {path}이(가) 성공적으로 생성됨",
        "changelog_links_updated": "✅ {filename}에서 체인지로그 링크 업데이트됨",
        "all_translated": "🎉 모든 README가 성공적으로 번역됨!",
        "language_switcher_updated": "✅ {filename}에서 언어 전환기 업데이트됨",
        "file_deleted": "🗑️ 파일 {filename}이(가) 성공적으로 삭제됨",
        "folder_deleted": "🗑️ 폴더 {folder}이(가) 성공적으로 삭제됨",
        "changelog_section_added": "✅ README.md에 적절한 간격과 구분자로 체인지로그 섹션 추가됨",
        "changelog_spacing_fixed": "✅ README.md에서 체인지로그 섹션 간격과 구분자 수정됨",
        "github_url_detected": "🔍 GitHub 저장소 감지 결과:",
        "repo_url": "📦 저장소 URL: {url}",
        "releases_url": "🚀 릴리스 URL: {url}",
        "sources_checked": "📋 확인된 소스:",
        "no_github_url": "❌ GitHub 저장소 URL을 자동으로 감지할 수 없습니다.",
        "protection_reset": "🔁 protected_phrases.json 파일이 기본값으로 재설정되었습니다.",
        "phrase_added": "✅ '{phrase}' 문구가 보호에 추가됨",
        "phrase_removed": "🗑️ '{phrase}' 문구가 보호에서 제거됨",
        "protected_phrases_list": "📜 보호된 문구 목록:",
        "protection_enabled": "🟢 보호 활성화됨",
        "protection_disabled": "🔴 보호 비활성화됨",
        "protection_status": "🧩 보호 상태: {status}",
        "changelog_setup_completed": "✅ 체인지로그 설정 완료",
        "changelog_setup_failed": "❌ 체인지로그 설정 실패",
        "no_changelog_file": "❌ 루트 디렉토리에 CHANGELOG.md 파일이 없습니다",
        "changelog_translated": "✅ {count}개 언어로 CHANGELOG 성공적으로 번역됨",
        "no_changelog_translated": "❌ 성공적으로 번역된 CHANGELOG 파일이 없습니다",
        "languages_removed": "🎉 언어가 성공적으로 제거됨: {langs}",
        "all_languages_removed": "🎉 모든 번역 파일이 성공적으로 제거됨",
        "auto_setup_changelog": "🔧 README에서 체인지로그 섹션 자동 설정 중...",
        "checking_changelog_spacing": "🔧 체인지로그 섹션 간격 확인 중...",
        "no_valid_language": "❌ 유효한 언어 코드가 제공되지 않았습니다.",
        "language_not_recognized": "❌ '{code}' 언어 코드를 인식할 수 없습니다. 계속 진행합니다...",
        "file_not_found": "⚠️ {filename} 파일을 찾을 수 없습니다",
        "folder_not_empty": "⚠️ {folder} 폴더가 비어 있지 않아 삭제하지 않았습니다",
        "failed_delete_file": "❌ {filename} 삭제 실패: {error}",
        "failed_delete_folder": "❌ 폴더 삭제 실패: {error}",
        "failed_update_main": "❌ 메인 README 업데이트 실패: {error}",
        "failed_translate_changelog": "❌ CHANGELOG 번역 실패: {error}",
        "failed_update_changelog_links": "❌ {filename}에서 체인지로그 링크 업데이트 실패: {error}",
        "failed_update_switcher": "❌ {filename}에서 언어 전환기 업데이트 실패: {error}",
        "translation_failed": "❌ 번역 실패: {error}",
        "reading_package_error": "❌ package.json 읽기 오류: {error}",
        "reading_git_error": "❌ .git/config 읽기 오류: {error}",
        "reading_github_error": "❌ README에서 GitHub URL 검색 오류: {error}",
        "changelog_section_exists": "ℹ️ 체인지로그 섹션이 이미 README.md에 존재합니다",
        "no_changelog_file_root": "❌ 루트 디렉토리에 CHANGELOG.md 파일이 없습니다",
        "no_translation_files": "ℹ️ 번역된 README 파일을 찾을 수 없습니다",
        "language_not_supported": "⚠️ '{code}' 표시 언어는 지원되지 않으며, 기본값을 사용합니다",
        "help_description": "MultiDoc Translator - 자동화된 다국어 문서 번역기",
        "help_epilog": """
사용 예:
  # README를 일본어와 중국어로 번역
  python multidoc_translator.py --lang jp,zh

  # 일본어 알림으로 모든 언어에 대해 CHANGELOG만 번역
  python multidoc_translator.py --translate-changelog all --display jp

  # 특정 언어 파일 삭제
  python multidoc_translator.py --remove-lang jp,zh

  # README에 체인지로그 섹션 자동 설정
  python multidoc_translator.py --auto-setup-changelog

  # GitHub 저장소 URL 감지
  python multidoc_translator.py --detect-github-url
        """,
        "help_lang": "번역할 언어 코드 (쉼표로 구분). 지원: pl, zh, jp, de, fr, es, ru, pt, id, kr",
        "help_remove_lang": "특정 번역된 언어 파일 삭제 (쉼표로 구분)",
        "help_remove_all_lang": "모든 번역 파일 삭제 및 폴더 정리",
        "help_add_protect": "보호 목록에 문구 추가 (정규식 패턴 지원)",
        "help_remove_protect": "보호 목록에서 문구 제거",
        "help_list_protect": "현재 보호 중인 모든 문구 표시",
        "help_init_protect": "protected_phrases.json을 기본값으로 재설정",
        "help_enable_protect": "번역 중 문구 보호 활성화",
        "help_disable_protect": "번역 중 문구 보호 비활성화",
        "help_status_protect": "문구 보호가 현재 활성화되었는지 확인",
        "help_translate_changelog": "CHANGELOG.md만 번역 (모든 언어는 'all' 사용 또는 코드 지정)",
        "help_auto_setup_changelog": "CHANGELOG.md가 존재하면 README.md에 체인지로그 섹션 자동 추가",
        "help_detect_github_url": "다양한 소스에서 GitHub 저장소 URL 감지 및 표시",
        "help_display": "터미널 알림 표시 언어 (en, id, jp, de, es, fr, kr, pl, pt, ru, zh)",

        "changelog.onlyActions": "📋 CHANGELOG 전용 작업",
        "changelog.generateRemoveOnly": "CHANGELOG만 생성/삭제",
        "changelog.onlyDescription": "이 작업은 CHANGELOG 파일에만 영향을 미치며, README 파일은 변경되지 않습니다.",
        "changelog.generateOnly": "🌐 CHANGELOG만 생성",
        "changelog.removeSelected": "🗑️ 선택한 CHANGELOG 삭제",
        "changelog.affectsSelected": "선택한 언어만 영향: {0}개 언어",
        "changelog.generateWith": "📋 CHANGELOG 포함 생성",
        "changelog.checkedDescription": "체크 시: README와 CHANGELOG 파일 모두 번역",
        "changelog.uncheckedDescription": "체크 해제 시: README 파일만 번역",
        
        "progress.translatingWithChangelog": "README + CHANGELOG 번역 중",
        "progress.translatingReadmeOnly": "README만 번역 중",
        "success.filesSavedWithChangelog": "README와 CHANGELOG",
        "success.filesSavedReadmeOnly": "README만",
        "success.translationCompletedWithChangelog": "✅ {0}개 README와 CHANGELOG가 성공적으로 번역되었습니다!",
        "success.translationCompletedReadmeOnly": "✅ {0}개 README가 성공적으로 번역되었습니다!",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.md를 찾을 수 없음 - CHANGELOG 번역 건너뜀",
        
        "errors.changelogGenerateFailed": "❌ CHANGELOG 생성 실패",
        "errors.changelogRemoveSelectedFailed": "❌ 선택한 CHANGELOG 파일 삭제 실패",
        "success.changelogGenerated": "✅ {0}개 언어의 CHANGELOG가 성공적으로 생성되었습니다",
        "success.changelogRemovedSelected": "✅ {0}개 CHANGELOG 파일이 성공적으로 삭제되었습니다",
        "confirmation.removeChangelogSelected": "선택한 {0}개 언어의 CHANGELOG 파일을 삭제하시겠습니까? README 파일은 영향을 받지 않습니다.",
        
        "help_generate_changelog_only": "선택한 언어의 CHANGELOG 파일만 생성 (README 파일은 변경되지 않음)",
        "help_remove_changelog_selected": "선택한 언어의 CHANGELOG 파일만 삭제 (README 파일은 변경되지 않음)",
        "help_remove_changelog_only": "모든 CHANGELOG 파일만 삭제 (README 파일은 변경되지 않음)",
        "help_with_changelog": "활성화 시: README와 CHANGELOG 번역. 비활성화 시: README만 번역",
        "errors.noLanguagesSelected": "❌ 선택된 언어가 없습니다",
        "errors.noLanguagesSelectedRemove": "❌ 제거할 언어가 선택되지 않았습니다",
        "progress.startingTranslation": "🚀 {count}개 언어 번역 시작 - {mode_text}",
        "progress.translatingLanguage": "📖 {lang_name} 번역 중 ({current}/{total})...",
        "progress.waiting": "⏳ 다음 번역 전 {seconds}초 대기 중...",
        "progress.completed": "✅ 번역 프로세스 완료",
        "progress.filesSaved": "💾 파일 저장 위치: {path}",
        "progress.removingSelected": "🗑️ 선택한 CHANGELOG 파일 제거 중...",
        "progress.fileCreated": "✅ 제거됨: {path}",
        "progress.removingChangelog": "🗑️ 모든 CHANGELOG 파일 제거 중...",
        "changelog.translatingChangelog": "📘 {count}개 언어 CHANGELOG 번역 중...",
        "changelog.translating": "🔧 CHANGELOG를 {lang_name}로 번역 중...",
        "changelog.translated": "✅ CHANGELOG가 {lang_name}로 번역됨",
        "changelog.autoSettingUp": "🔧 체인지로그 섹션 자동 설정 중...",
        "changelog.checkingSpacing": "🔧 체인지로그 섹션 간격 확인 중...",
        "progress.changelogTranslated": "✅ CHANGELOG가 {lang_name}로 번역됨",
        "errors.translationFailedShort": "❌ {lang_name} 번역 실패",
        "errors.translationFailed": "❌ {lang_code} 번역 실패: {error}",
        "errors.changelogTranslationFailed": "❌ CHANGELOG 번역 실패",
        "success.changelogTranslationCompleted": "✅ CHANGELOG 번역 완료",
        "errors.changelogRemoveFailed": "❌ CHANGELOG 파일 제거 실패",
        "info.noChangelogFiles": "ℹ️ CHANGELOG 파일을 찾을 수 없습니다",
        "success.changelogRemoved": "✅ {count}개 CHANGELOG 파일 성공적으로 제거됨",
        "confirmation.removeChangelog": "모든 CHANGELOG 파일을 제거하시겠습니까? README 파일은 영향을 받지 않습니다."
,
        "menu_debug": "디버그 모드 전환",
        "debug_enabled": "디버그 모드가 이제 활성화되었습니다.",
        "debug_disabled": "디버그 모드가 이제 비활성화되었습니다.",
        "debug_current": "현재"
    },
    "pl": {
        "translating_readme": "📘 Tłumaczenie README na {lang_name} ({lang_code})...",
        "readme_created": "✅ {path} pomyślnie utworzony",
        "translating_changelog": "📘 Tłumaczenie CHANGELOG na {lang_name} ({lang_code})...",
        "changelog_created": "✅ {path} pomyślnie utworzony",
        "changelog_links_updated": "✅ Linki changelog zaktualizowane w {filename}",
        "all_translated": "🎉 Wszystkie README pomyślnie przetłumaczone!",
        "language_switcher_updated": "✅ Przełącznik języka zaktualizowany w {filename}",
        "file_deleted": "🗑️ Plik {filename} pomyślnie usunięty",
        "folder_deleted": "🗑️ Folder {folder} pomyślnie usunięty",
        "changelog_section_added": "✅ Sekcja changelog dodana do README.md z właściwymi odstępami i separatorami",
        "changelog_spacing_fixed": "✅ Naprawiono odstępy i separatory sekcji changelog w README.md",
        "github_url_detected": "🔍 Wyniki wykrywania repozytorium GitHub:",
        "repo_url": "📦 URL repozytorium: {url}",
        "releases_url": "🚀 URL wydań: {url}",
        "sources_checked": "📋 Sprawdzone źródła:",
        "no_github_url": "❌ Nie można automatycznie wykryć URL repozytorium GitHub.",
        "protection_reset": "🔁 Plik protected_phrases.json został zresetowany do domyślnych ustawień.",
        "phrase_added": "✅ Wyrażenie '{phrase}' dodane do ochrony.",
        "phrase_removed": "🗑️ Wyrażenie '{phrase}' usunięte z ochrony.",
        "protected_phrases_list": "📜 Lista chronionych wyrażeń:",
        "protection_enabled": "🟢 Ochrona włączona.",
        "protection_disabled": "🔴 Ochrona wyłączona.",
        "protection_status": "🧩 Status ochrony: {status}",
        "changelog_setup_completed": "✅ Konfiguracja changelog ukończona",
        "changelog_setup_failed": "❌ Konfiguracja changelog nie powiodła się",
        "no_changelog_file": "❌ Nie masz pliku CHANGELOG.md w katalogu głównym",
        "changelog_translated": "✅ Pomyślnie przetłumaczono CHANGELOG na {count} języków",
        "no_changelog_translated": "❌ Żadne pliki CHANGELOG nie zostały pomyślnie przetłumaczone",
        "languages_removed": "🎉 Języki pomyślnie usunięte: {langs}",
        "all_languages_removed": "🎉 Wszystkie pliki tłumaczeń pomyślnie usunięte",
        "auto_setup_changelog": "🔧 Automatyczna konfiguracja sekcji changelog w README...",
        "checking_changelog_spacing": "🔧 Sprawdzanie odstępów sekcji changelog...",
        "no_valid_language": "❌ Nie podano prawidłowych kodów języków.",
        "language_not_recognized": "❌ Kod języka '{code}' nierozpoznany. Kontynuowanie...",
        "file_not_found": "⚠️ Plik {filename} nie znaleziony",
        "folder_not_empty": "⚠️ Folder {folder} nie jest pusty, nie usunięto",
        "failed_delete_file": "❌ Nie udało się usunąć {filename}: {error}",
        "failed_delete_folder": "❌ Nie udało się usunąć folderu: {error}",
        "failed_update_main": "❌ Nie udało się zaktualizować głównego README: {error}",
        "failed_translate_changelog": "❌ Nie udało się przetłumaczyć CHANGELOG: {error}",
        "failed_update_changelog_links": "❌ Nie udało się zaktualizować linków changelog w {filename}: {error}",
        "failed_update_switcher": "❌ Nie udało się zaktualizować przełącznika języka w {filename}: {error}",
        "translation_failed": "❌ Tłumaczenie nie powiodło się: {error}",
        "reading_package_error": "❌ Błąd odczytu package.json: {error}",
        "reading_git_error": "❌ Błąd odczytu .git/config: {error}",
        "reading_github_error": "❌ Błąd wyszukiwania URL GitHub w README: {error}",
        "changelog_section_exists": "ℹ️ Sekcja changelog już istnieje w README.md",
        "no_changelog_file_root": "❌ Nie znaleziono pliku CHANGELOG.md w katalogu głównym",
        "no_translation_files": "ℹ️ Nie znaleziono przetłumaczonych plików README",
        "language_not_supported": "⚠️ Język wyświetlania '{code}' nie jest obsługiwany, używam domyślnego",
        "help_description": "MultiDoc Translator - Zautomatyzowany tłumacz dokumentacji wielojęzycznej",
        "help_epilog": """
Przykłady:
  # Tłumaczenie README na japoński i chiński
  python multidoc_translator.py --lang jp,zh

  # Tłumaczenie tylko CHANGELOG na wszystkie języki z japońskimi powiadomieniami
  python multidoc_translator.py --translate-changelog all --display jp

  # Usuwanie określonych plików językowych
  python multidoc_translator.py --remove-lang jp,zh

  # Automatyczna konfiguracja sekcji changelog w README
  python multidoc_translator.py --auto-setup-changelog

  # Wykrywanie URL repozytorium GitHub
  python multidoc_translator.py --detect-github-url
        """,
        "help_lang": "Kody języków do tłumaczenia (oddzielone przecinkami). Obsługiwane: pl, zh, jp, de, fr, es, ru, pt, id, kr",
        "help_remove_lang": "Usuwanie określonych przetłumaczonych plików językowych (oddzielone przecinkami)",
        "help_remove_all_lang": "Usuwanie WSZYSTKICH przetłumaczonych plików językowych i czyszczenie folderów",
        "help_add_protect": "Dodawanie frazy do listy ochrony (wzorzec regex obsługiwany)",
        "help_remove_protect": "Usuwanie frazy z listy ochrony",
        "help_list_protect": "Wyświetlanie wszystkich obecnie chronionych fraz",
        "help_init_protect": "Resetowanie protected_phrases.json do wartości domyślnych",
        "help_enable_protect": "Włączanie ochrony fraz podczas tłumaczenia",
        "help_disable_protect": "Wyłączanie ochrony fraz podczas tłumaczenia",
        "help_status_protect": "Sprawdzanie, czy ochrona fraz jest obecnie włączona",
        "help_translate_changelog": "Tłumaczenie tylko CHANGELOG.md (użyj 'all' dla wszystkich języków lub określ kody)",
        "help_auto_setup_changelog": "Automatyczne dodawanie sekcji changelog do README.md, jeśli CHANGELOG.md istnieje",
        "help_detect_github_url": "Wykrywanie i wyświetlanie URL repozytorium GitHub z różnych źródeł",
        "help_display": "Język wyświetlania powiadomień terminala (en, id, jp, de, es, fr, kr, pl, pt, ru, zh)",

        "changelog.onlyActions": "📋 Akcje tylko CHANGELOG",
        "changelog.generateRemoveOnly": "Tylko generuj/usuń CHANGELOG",
        "changelog.onlyDescription": "Te działania dotyczą tylko plików CHANGELOG, pliki README pozostają niezmienione.",
        "changelog.generateOnly": "🌐 Tylko generuj CHANGELOG",
        "changelog.removeSelected": "🗑️ Usuń wybrane CHANGELOG",
        "changelog.affectsSelected": "Wpływa tylko na wybrane języki: {0} języków",
        "changelog.generateWith": "📋 Generuj z CHANGELOG",
        "changelog.checkedDescription": "Gdy zaznaczone: Tłumaczy zarówno pliki README jak i CHANGELOG",
        "changelog.uncheckedDescription": "Gdy niezaznaczone: Tłumaczy tylko pliki README",
        
        "progress.translatingWithChangelog": "Tłumaczenie README + CHANGELOG",
        "progress.translatingReadmeOnly": "Tłumaczenie tylko README",
        "success.filesSavedWithChangelog": "READMES i CHANGELOGs",
        "success.filesSavedReadmeOnly": "Tylko READMEs",
        "success.translationCompletedWithChangelog": "✅ {0} READMEs i CHANGELOGs pomyślnie przetłumaczone!",
        "success.translationCompletedReadmeOnly": "✅ {0} READMEs pomyślnie przetłumaczone!",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.md nie znaleziono - pomijam tłumaczenie CHANGELOG",
        
        "errors.changelogGenerateFailed": "❌ Generowanie CHANGELOG nie powiodło się",
        "errors.changelogRemoveSelectedFailed": "❌ Nie udało się usunąć wybranych plików CHANGELOG",
        "success.changelogGenerated": "✅ CHANGELOG pomyślnie wygenerowany dla {0} języków",
        "success.changelogRemovedSelected": "✅ {0} plików CHANGELOG pomyślnie usunięto",
        "confirmation.removeChangelogSelected": "Czy na pewno chcesz usunąć pliki CHANGELOG dla {0} wybranych języków? Pliki README nie zostaną naruszone.",
        
        "help_generate_changelog_only": "Tylko generuj pliki CHANGELOG dla wybranych języków (pliki README pozostają niezmienione)",
        "help_remove_changelog_selected": "Tylko usuń pliki CHANGELOG dla wybranych języków (pliki README pozostają niezmienione)",
        "help_remove_changelog_only": "Tylko usuń WSZYSTKIE pliki CHANGELOG (pliki README pozostają niezmienione)",
        "help_with_changelog": "Gdy włączone: Tłumacz README i CHANGELOG. Gdy wyłączone: Tłumacz tylko README",
        "errors.noLanguagesSelected": "❌ Nie wybrano języków",
        "errors.noLanguagesSelectedRemove": "❌ Nie wybrano języków do usunięcia",
        "progress.startingTranslation": "🚀 Rozpoczynanie tłumaczenia dla {count} języków - {mode_text}",
        "progress.translatingLanguage": "📖 Tłumaczenie {lang_name} ({current}/{total})...",
        "progress.waiting": "⏳ Oczekiwanie {seconds} sekund przed następnym tłumaczeniem...",
        "progress.completed": "✅ Proces tłumaczenia zakończony",
        "progress.filesSaved": "💾 Pliki zapisane w: {path}",
        "progress.removingSelected": "🗑️ Usuwanie wybranych plików CHANGELOG...",
        "progress.fileCreated": "✅ Usunięto: {path}",
        "progress.removingChangelog": "🗑️ Usuwanie wszystkich plików CHANGELOG...",
        "changelog.translatingChangelog": "📘 Tłumaczenie CHANGELOG dla {count} języków...",
        "changelog.translating": "🔧 Tłumaczenie CHANGELOG na {lang_name}...",
        "changelog.translated": "✅ CHANGELOG przetłumaczony na {lang_name}",
        "changelog.autoSettingUp": "🔧 Automatyczna konfiguracja sekcji changelog...",
        "changelog.checkingSpacing": "🔧 Sprawdzanie odstępów sekcji changelog...",
        "progress.changelogTranslated": "✅ CHANGELOG przetłumaczony na {lang_name}",
        "errors.translationFailedShort": "❌ Tłumaczenie nie powiodło się dla {lang_name}",
        "errors.translationFailed": "❌ Tłumaczenie nie powiodło się dla {lang_code}: {error}",
        "errors.changelogTranslationFailed": "❌ Tłumaczenie CHANGELOG nie powiodło się",
        "success.changelogTranslationCompleted": "✅ Tłumaczenie CHANGELOG ukończone",
        "errors.changelogRemoveFailed": "❌ Nie udało się usunąć pliku CHANGELOG",
        "info.noChangelogFiles": "ℹ️ Nie znaleziono plików CHANGELOG",
        "success.changelogRemoved": "✅ {count} plików CHANGELOG pomyślnie usunięto",
        "confirmation.removeChangelog": "Czy na pewno chcesz usunąć WSZYSTKIE pliki CHANGELOG? Pliki README nie zostaną naruszone."
,
        "menu_debug": "Przełącz tryb debugowania",
        "debug_enabled": "Tryb debugowania jest teraz WŁĄCZONY.",
        "debug_disabled": "Tryb debugowania jest teraz WYŁĄCZONY.",
        "debug_current": "Obecny"
    },
    "pt": {
        "translating_readme": "📘 Traduzindo README para {lang_name} ({lang_code})...",
        "readme_created": "✅ {path} criado com sucesso",
        "translating_changelog": "📘 Traduzindo CHANGELOG para {lang_name} ({lang_code})...",
        "changelog_created": "✅ {path} criado com sucesso",
        "changelog_links_updated": "✅ Links do changelog atualizados em {filename}",
        "all_translated": "🎉 Todos os READMEs traduzidos com sucesso!",
        "language_switcher_updated": "✅ Seletor de idioma atualizado em {filename}",
        "file_deleted": "🗑️ Arquivo {filename} excluído com sucesso",
        "folder_deleted": "🗑️ Pasta {folder} excluída com sucesso",
        "changelog_section_added": "✅ Seção changelog adicionada ao README.md com espaçamento e separadores adequados",
        "changelog_spacing_fixed": "✅ Espaçamento e separadores da seção changelog corrigidos no README.md",
        "github_url_detected": "🔍 Resultados da detecção do repositório GitHub:",
        "repo_url": "📦 URL do repositório: {url}",
        "releases_url": "🚀 URL de releases: {url}",
        "sources_checked": "📋 Fontes verificadas:",
        "no_github_url": "❌ Não foi possível detectar automaticamente a URL do repositório GitHub.",
        "protection_reset": "🔁 Arquivo protected_phrases.json foi redefinido para o padrão.",
        "phrase_added": "✅ Frase '{phrase}' adicionada à proteção.",
        "phrase_removed": "🗑️ Frase '{phrase}' removida da proteção.",
        "protected_phrases_list": "📜 Lista de frases protegidas:",
        "protection_enabled": "🟢 Proteção ativada.",
        "protection_disabled": "🔴 Proteção desativada.",
        "protection_status": "🧩 Status da proteção: {status}",
        "changelog_setup_completed": "✅ Configuração do changelog concluída",
        "changelog_setup_failed": "❌ Configuração do changelog falhou",
        "no_changelog_file": "❌ Você não tem o arquivo CHANGELOG.md no diretório raiz",
        "changelog_translated": "✅ CHANGELOG traduzido com sucesso para {count} idiomas",
        "no_changelog_translated": "❌ Nenhum arquivo CHANGELOG foi traduzido com sucesso",
        "languages_removed": "🎉 Idiomas removidos com sucesso: {langs}",
        "all_languages_removed": "🎉 Todos os arquivos de tradução removidos com sucesso",
        "auto_setup_changelog": "🔧 Configurando automaticamente a seção changelog no README...",
        "checking_changelog_spacing": "🔧 Verificando espaçamento da seção changelog...",
        "no_valid_language": "❌ Nenhum código de idioma válido fornecido.",
        "language_not_recognized": "❌ Código de idioma '{code}' não reconhecido. Continuando...",
        "file_not_found": "⚠️ Arquivo {filename} não encontrado",
        "folder_not_empty": "⚠️ Pasta {folder} não está vazia, não excluída",
        "failed_delete_file": "❌ Falha ao excluir {filename}: {error}",
        "failed_delete_folder": "❌ Falha ao excluir pasta: {error}",
        "failed_update_main": "❌ Falha ao atualizar README principal: {error}",
        "failed_translate_changelog": "❌ Falha ao traduzir CHANGELOG: {error}",
        "failed_update_changelog_links": "❌ Falha ao atualizar links do changelog em {filename}: {error}",
        "failed_update_switcher": "❌ Falha ao atualizar seletor de idioma em {filename}: {error}",
        "translation_failed": "❌ Falha na tradução: {error}",
        "reading_package_error": "❌ Erro lendo package.json: {error}",
        "reading_git_error": "❌ Erro lendo .git/config: {error}",
        "reading_github_error": "❌ Erro pesquisando URL do GitHub no README: {error}",
        "changelog_section_exists": "ℹ️ Seção changelog já existe no README.md",
        "no_changelog_file_root": "❌ Nenhum arquivo CHANGELOG.md encontrado no diretório raiz",
        "no_translation_files": "ℹ️ Nenhum arquivo README traduzido encontrado",
        "language_not_supported": "⚠️ Idioma de exibição '{code}' não suportado, usando padrão",
        "help_description": "MultiDoc Translator - Tradutor automatizado de documentação multilíngue",
        "help_epilog": """
Exemplos:
  # Traduzir README para japonês e chinês
  python multidoc_translator.py --lang jp,zh

  # Traduzir apenas CHANGELOG para todos os idiomas com notificações em japonês
  python multidoc_translator.py --translate-changelog all --display jp

  # Remover arquivos de idiomas específicos
  python multidoc_translator.py --remove-lang jp,zh

  # Configuração automática da seção changelog no README
  python multidoc_translator.py --auto-setup-changelog

  # Detectar URL do repositório GitHub
  python multidoc_translator.py --detect-github-url
        """,
        "help_lang": "Códigos de idioma para traduzir (separados por vírgula). Suportados: pl, zh, jp, de, fr, es, ru, pt, id, kr",
        "help_remove_lang": "Remover arquivos de idiomas traduzidos específicos (separados por vírgula)",
        "help_remove_all_lang": "Remover TODOS os arquivos de idiomas traduzidos e limpar pastas",
        "help_add_protect": "Adicionar uma frase à lista de proteção (padrão regex suportado)",
        "help_remove_protect": "Remover uma frase da lista de proteção",
        "help_list_protect": "Mostrar todas as frases atualmente protegidas",
        "help_init_protect": "Redefinir protected_phrases.json para valores padrão",
        "help_enable_protect": "Habilitar proteção de frases durante a tradução",
        "help_disable_protect": "Desabilitar proteção de frases durante a tradução",
        "help_status_protect": "Verificar se a proteção de frases está atualmente habilitada",
        "help_translate_changelog": "Traduzir apenas CHANGELOG.md (use 'all' para todos os idiomas ou especifique códigos)",
        "help_auto_setup_changelog": "Adicionar automaticamente seção changelog ao README.md se CHANGELOG.md existir",
        "help_detect_github_url": "Detectar e exibir URL do repositório GitHub de várias fontes",
        "help_display": "Idioma de exibição para notificações do terminal (en, id, jp, de, es, fr, kr, pl, pt, ru, zh)",

        "changelog.onlyActions": "📋 Ações apenas CHANGELOG",
        "changelog.generateRemoveOnly": "Gerar/Remover apenas CHANGELOG",
        "changelog.onlyDescription": "Estas ações afetam apenas arquivos CHANGELOG, arquivos README permanecem inalterados.",
        "changelog.generateOnly": "🌐 Gerar apenas CHANGELOG",
        "changelog.removeSelected": "🗑️ Remover CHANGELOG selecionado",
        "changelog.affectsSelected": "Afeta apenas idiomas selecionados: {0} idiomas",
        "changelog.generateWith": "📋 Gerar com CHANGELOG",
        "changelog.checkedDescription": "Quando marcado: Traduz arquivos README e CHANGELOG",
        "changelog.uncheckedDescription": "Quando desmarcado: Traduz apenas arquivos README",
        
        "progress.translatingWithChangelog": "Traduzindo README + CHANGELOG",
        "progress.translatingReadmeOnly": "Traduzindo apenas README",
        "success.filesSavedWithChangelog": "READMES e CHANGELOGs",
        "success.filesSavedReadmeOnly": "Apenas READMEs",
        "success.translationCompletedWithChangelog": "✅ {0} READMEs e CHANGELOGs traduzidos com sucesso!",
        "success.translationCompletedReadmeOnly": "✅ {0} READMEs traduzidos com sucesso!",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.md não encontrado - ignorando tradução CHANGELOG",
        
        "errors.changelogGenerateFailed": "❌ Falha na geração CHANGELOG",
        "errors.changelogRemoveSelectedFailed": "❌ Falha ao remover arquivos CHANGELOG selecionados",
        "success.changelogGenerated": "✅ CHANGELOG gerado com sucesso para {0} idiomas",
        "success.changelogRemovedSelected": "✅ {0} arquivos CHANGELOG removidos com sucesso",
        "confirmation.removeChangelogSelected": "Tem certeza de que deseja remover arquivos CHANGELOG para {0} idiomas selecionados? Arquivos README não serão afetados.",
        
        "help_generate_changelog_only": "Apenas gerar arquivos CHANGELOG para idiomas selecionados (arquivos README permanecem inalterados)",
        "help_remove_changelog_selected": "Apenas remover arquivos CHANGELOG para idiomas selecionados (arquivos README permanecem inalterados)",
        "help_remove_changelog_only": "Apenas remover TODOS os arquivos CHANGELOG (arquivos README permanecem inalterados)",
        "help_with_changelog": "Quando habilitado: Traduz README e CHANGELOG. Quando desabilitado: Traduz apenas README",
        "errors.noLanguagesSelected": "❌ Nenhum idioma selecionado",
        "errors.noLanguagesSelectedRemove": "❌ Nenhum idioma selecionado para remoção",
        "progress.startingTranslation": "🚀 Iniciando tradução para {count} idiomas - {mode_text}",
        "progress.translatingLanguage": "📖 Traduzindo {lang_name} ({current}/{total})...",
        "progress.waiting": "⏳ Aguardando {seconds} segundos antes da próxima tradução...",
        "progress.completed": "✅ Processo de tradução concluído",
        "progress.filesSaved": "💾 Arquivos salvos em: {path}",
        "progress.removingSelected": "🗑️ Removendo arquivos CHANGELOG selecionados...",
        "progress.fileCreated": "✅ Removido: {path}",
        "progress.removingChangelog": "🗑️ Removendo todos os arquivos CHANGELOG...",
        "changelog.translatingChangelog": "📘 Traduzindo CHANGELOG para {count} idiomas...",
        "changelog.translating": "🔧 Traduzindo CHANGELOG para {lang_name}...",
        "changelog.translated": "✅ CHANGELOG traduzido para {lang_name}",
        "changelog.autoSettingUp": "🔧 Configuração automática da seção changelog...",
        "changelog.checkingSpacing": "🔧 Verificando espaçamento da seção changelog...",
        "progress.changelogTranslated": "✅ CHANGELOG traduzido para {lang_name}",
        "errors.translationFailedShort": "❌ Falha na tradução para {lang_name}",
        "errors.translationFailed": "❌ Falha na tradução para {lang_code}: {error}",
        "errors.changelogTranslationFailed": "❌ Falha na tradução do CHANGELOG",
        "success.changelogTranslationCompleted": "✅ Tradução do CHANGELOG concluída",
        "errors.changelogRemoveFailed": "❌ Falha ao remover arquivo CHANGELOG",
        "info.noChangelogFiles": "ℹ️ Nenhum arquivo CHANGELOG encontrado",
        "success.changelogRemoved": "✅ {count} arquivos CHANGELOG removidos com sucesso",
        "confirmation.removeChangelog": "Tem certeza de que deseja remover TODOS os arquivos CHANGELOG? Os arquivos README não serão afetados."
,
        "menu_debug": "Alternar Modo de Depuração",
        "debug_enabled": "O modo de depuração agora está ATIVADO.",
        "debug_disabled": "O modo de depuração agora está DESATIVADO.",
        "debug_current": "Atual"
    },
    "ru": {
        "translating_readme": "📘 Перевод README на {lang_name} ({lang_code})...",
        "readme_created": "✅ {path} успешно создан",
        "translating_changelog": "📘 Перевод CHANGELOG на {lang_name} ({lang_code})...",
        "changelog_created": "✅ {path} успешно создан",
        "changelog_links_updated": "✅ Ссылки на changelog обновлены в {filename}",
        "all_translated": "🎉 Все README успешно переведены!",
        "language_switcher_updated": "✅ Переключатель языка обновлен в {filename}",
        "file_deleted": "🗑️ Файл {filename} успешно удален",
        "folder_deleted": "🗑️ Папка {folder} успешно удалена",
        "changelog_section_added": "✅ Раздел changelog добавлен в README.md с правильными отступами и разделителями",
        "changelog_spacing_fixed": "✅ Исправлены отступы и разделители раздела changelog в README.md",
        "github_url_detected": "🔍 Результаты обнаружения репозитория GitHub:",
        "repo_url": "📦 URL репозитория: {url}",
        "releases_url": "🚀 URL релизов: {url}",
        "sources_checked": "📋 Проверенные источники:",
        "no_github_url": "❌ Не удалось автоматически определить URL репозитория GitHub.",
        "protection_reset": "🔁 Файл protected_phrases.json сброшен к значениям по умолчанию.",
        "phrase_added": "✅ Фраза '{phrase}' добавлена в защиту.",
        "phrase_removed": "🗑️ Фраза '{phrase}' удалена из защиты.",
        "protected_phrases_list": "📜 Список защищенных фраз:",
        "protection_enabled": "🟢 Защита включена.",
        "protection_disabled": "🔴 Защита отключена.",
        "protection_status": "🧩 Статус защиты: {status}",
        "changelog_setup_completed": "✅ Настройка changelog завершена",
        "changelog_setup_failed": "❌ Настройка changelog не удалась",
        "no_changelog_file": "❌ У вас нет файла CHANGELOG.md в корневом каталоге",
        "changelog_translated": "✅ CHANGELOG успешно переведен на {count} языков",
        "no_changelog_translated": "❌ Ни один файл CHANGELOG не был успешно переведен",
        "languages_removed": "🎉 Языки успешно удалены: {langs}",
        "all_languages_removed": "🎉 Все файлы переводов успешно удалены",
        "auto_setup_changelog": "🔧 Автоматическая настройка раздела changelog в README...",
        "checking_changelog_spacing": "🔧 Проверка отступов раздела changelog...",
        "no_valid_language": "❌ Не предоставлено действительных кодов языков.",
        "language_not_recognized": "❌ Код языка '{code}' не распознан. Продолжение...",
        "file_not_found": "⚠️ Файл {filename} не найден",
        "folder_not_empty": "⚠️ Папка {folder} не пуста, не удалена",
        "failed_delete_file": "❌ Не удалось удалить {filename}: {error}",
        "failed_delete_folder": "❌ Не удалось удалить папку: {error}",
        "failed_update_main": "❌ Не удалось обновить основной README: {error}",
        "failed_translate_changelog": "❌ Не удалось перевести CHANGELOG: {error}",
        "failed_update_changelog_links": "❌ Не удалось обновить ссылки на changelog в {filename}: {error}",
        "failed_update_switcher": "❌ Не удалось обновить переключатель языка в {filename}: {error}",
        "translation_failed": "❌ Ошибка перевода: {error}",
        "reading_package_error": "❌ Ошибка чтения package.json: {error}",
        "reading_git_error": "❌ Ошибка чтения .git/config: {error}",
        "reading_github_error": "❌ Ошибка поиска URL GitHub в README: {error}",
        "changelog_section_exists": "ℹ️ Раздел changelog уже существует в README.md",
        "no_changelog_file_root": "❌ Файл CHANGELOG.md не найден в корневом каталоге",
        "no_translation_files": "ℹ️ Переведенные файлы README не найдены",
        "language_not_supported": "⚠️ Язык отображения '{code}' не поддерживается, используется по умолчанию",
        "help_description": "MultiDoc Translator - Автоматизированный переводчик многоязычной документации",
        "help_epilog": """
Примеры:
  # Перевод README на японский и китайский
  python multidoc_translator.py --lang jp,zh

  # Перевод только CHANGELOG на все языки с японскими уведомлениями
  python multidoc_translator.py --translate-changelog all --display jp

  # Удаление определенных языковых файлов
  python multidoc_translator.py --remove-lang jp,zh

  # Автоматическая настройка раздела changelog в README
  python multidoc_translator.py --auto-setup-changelog

  # Обнаружение URL репозитория GitHub
  python multidoc_translator.py --detect-github-url
        """,
        "help_lang": "Коды языков для перевода (разделены запятыми). Поддерживаются: pl, zh, jp, de, fr, es, ru, pt, id, kr",
        "help_remove_lang": "Удаление определенных переведенных языковых файлов (разделены запятыми)",
        "help_remove_all_lang": "Удаление ВСЕХ переведенных языковых файлов и очистка папок",
        "help_add_protect": "Добавление фразы в список защиты (поддерживается regex-шаблон)",
        "help_remove_protect": "Удаление фразы из списка защиты",
        "help_list_protect": "Показать все текущие защищенные фразы",
        "help_init_protect": "Сброс protected_phrases.json к значениям по умолчанию",
        "help_enable_protect": "Включить защиту фраз во время перевода",
        "help_disable_protect": "Отключить защиту фраз во время перевода",
        "help_status_protect": "Проверить, включена ли в настоящее время защита фраз",
        "help_translate_changelog": "Перевести только CHANGELOG.md (использовать 'all' для всех языков или указать коды)",
        "help_auto_setup_changelog": "Автоматически добавить раздел changelog в README.md, если CHANGELOG.md существует",
        "help_detect_github_url": "Обнаружить и отобразить URL репозитория GitHub из различных источников",
        "help_display": "Язык отображения для уведомлений терминала (en, id, jp, de, es, fr, kr, pl, pt, ru, zh)",

        "changelog.onlyActions": "📋 Действия только с CHANGELOG",
        "changelog.generateRemoveOnly": "Только генерировать/удалять CHANGELOG",
        "changelog.onlyDescription": "Эти действия затрагивают только файлы CHANGELOG, файлы README остаются неизменными.",
        "changelog.generateOnly": "🌐 Только генерировать CHANGELOG",
        "changelog.removeSelected": "🗑️ Удалить выбранные CHANGELOG",
        "changelog.affectsSelected": "Затрагивает только выбранные языки: {0} языков",
        "changelog.generateWith": "📋 Генерировать с CHANGELOG",
        "changelog.checkedDescription": "Когда отмечено: Переводит файлы README и CHANGELOG",
        "changelog.uncheckedDescription": "Когда не отмечено: Переводит только файлы README",
        
        "progress.translatingWithChangelog": "Перевод README + CHANGELOG",
        "progress.translatingReadmeOnly": "Перевод только README",
        "success.filesSavedWithChangelog": "READMES и CHANGELOGs",
        "success.filesSavedReadmeOnly": "Только READMEs",
        "success.translationCompletedWithChangelog": "✅ {0} READMEs и CHANGELOGs успешно переведены!",
        "success.translationCompletedReadmeOnly": "✅ {0} READMEs успешно переведены!",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.md не найден - пропускаю перевод CHANGELOG",
        
        "errors.changelogGenerateFailed": "❌ Ошибка генерации CHANGELOG",
        "errors.changelogRemoveSelectedFailed": "❌ Ошибка удаления выбранных файлов CHANGELOG",
        "success.changelogGenerated": "✅ CHANGELOG успешно сгенерирован для {0} языков",
        "success.changelogRemovedSelected": "✅ {0} файлов CHANGELOG успешно удалено",
        "confirmation.removeChangelogSelected": "Вы уверены, что хотите удалить файлы CHANGELOG для {0} выбранных языков? Файлы README не будут затронуты.",
        
        "help_generate_changelog_only": "Только генерировать файлы CHANGELOG для выбранных языков (файлы README остаются неизменными)",
        "help_remove_changelog_selected": "Только удалять файлы CHANGELOG для выбранных языков (файлы README остаются неизменными)",
        "help_remove_changelog_only": "Только удалять ВСЕ файлы CHANGELOG (файлы README остаются неизменными)",
        "help_with_changelog": "Когда включено: Переводит README и CHANGELOG. Когда выключено: Переводит только README",
        "errors.noLanguagesSelected": "❌ Языки не выбраны",
        "errors.noLanguagesSelectedRemove": "❌ Языки для удаления не выбраны",
        "progress.startingTranslation": "🚀 Начало перевода для {count} языков - {mode_text}",
        "progress.translatingLanguage": "📖 Перевод {lang_name} ({current}/{total})...",
        "progress.waiting": "⏳ Ожидание {seconds} секунд перед следующим переводом...",
        "progress.completed": "✅ Процесс перевода завершен",
        "progress.filesSaved": "💾 Файлы сохранены в: {path}",
        "progress.removingSelected": "🗑️ Удаление выбранных файлов CHANGELOG...",
        "progress.fileCreated": "✅ Удалено: {path}",
        "progress.removingChangelog": "🗑️ Удаление всех файлов CHANGELOG...",
        "changelog.translatingChangelog": "📘 Перевод CHANGELOG для {count} языков...",
        "changelog.translating": "🔧 Перевод CHANGELOG на {lang_name}...",
        "changelog.translated": "✅ CHANGELOG переведен на {lang_name}",
        "changelog.autoSettingUp": "🔧 Автоматическая настройка раздела changelog...",
        "changelog.checkingSpacing": "🔧 Проверка отступов раздела changelog...",
        "progress.changelogTranslated": "✅ CHANGELOG переведен на {lang_name}",
        "errors.translationFailedShort": "❌ Ошибка перевода для {lang_name}",
        "errors.translationFailed": "❌ Ошибка перевода для {lang_code}: {error}",
        "errors.changelogTranslationFailed": "❌ Ошибка перевода CHANGELOG",
        "success.changelogTranslationCompleted": "✅ Перевод CHANGELOG завершен",
        "errors.changelogRemoveFailed": "❌ Ошибка удаления файла CHANGELOG",
        "info.noChangelogFiles": "ℹ️ Файлы CHANGELOG не найдены",
        "success.changelogRemoved": "✅ {count} файлов CHANGELOG успешно удалено",
        "confirmation.removeChangelog": "Вы уверены, что хотите удалить ВСЕ файлы CHANGELOG? Файлы README не будут затронуты."
,
        "menu_debug": "Переключить режим отладки",
        "debug_enabled": "Режим отладки теперь ВКЛЮЧЕН.",
        "debug_disabled": "Режим отладки теперь ВЫКЛЮЧЕН.",
        "debug_current": "Текущий"
    },
    "zh": {
        "translating_readme": "📘 正在将 README 翻译为 {lang_name} ({lang_code})...",
        "readme_created": "✅ {path} 成功创建",
        "translating_changelog": "📘 正在将 CHANGELOG 翻译为 {lang_name} ({lang_code})...",
        "changelog_created": "✅ {path} 成功创建",
        "changelog_links_updated": "✅ 已在 {filename} 中更新更新日志链接",
        "all_translated": "🎉 所有 README 已成功翻译！",
        "language_switcher_updated": "✅ 已在 {filename} 中更新语言切换器",
        "file_deleted": "🗑️ 文件 {filename} 已成功删除",
        "folder_deleted": "🗑️ 文件夹 {folder} 已成功删除",
        "changelog_section_added": "✅ 已使用适当的间距和分隔符将更新日志部分添加到 README.md",
        "changelog_spacing_fixed": "✅ 已修复 README.md 中的更新日志部分间距和分隔符",
        "github_url_detected": "🔍 GitHub 仓库检测结果：",
        "repo_url": "📦 仓库 URL：{url}",
        "releases_url": "🚀 发布版本 URL：{url}",
        "sources_checked": "📋 已检查的来源：",
        "no_github_url": "❌ 无法自动检测 GitHub 仓库 URL。",
        "protection_reset": "🔁 文件 protected_phrases.json 已重置为默认值。",
        "phrase_added": "✅ 短语 '{phrase}' 已添加到保护。",
        "phrase_removed": "🗑️ 短语 '{phrase}' 已从保护中移除。",
        "protected_phrases_list": "📜 受保护短语列表：",
        "protection_enabled": "🟢 保护已启用。",
        "protection_disabled": "🔴 保护已禁用。",
        "protection_status": "🧩 保护状态：{status}",
        "changelog_setup_completed": "✅ 更新日志设置已完成",
        "changelog_setup_failed": "❌ 更新日志设置失败",
        "no_changelog_file": "❌ 您在根目录中没有 CHANGELOG.md 文件",
        "changelog_translated": "✅ 已成功将 CHANGELOG 翻译为 {count} 种语言",
        "no_changelog_translated": "❌ 没有 CHANGELOG 文件被成功翻译",
        "languages_removed": "🎉 语言已成功移除：{langs}",
        "all_languages_removed": "🎉 所有翻译文件已成功移除",
        "auto_setup_changelog": "🔧 正在自动设置 README 中的更新日志部分...",
        "checking_changelog_spacing": "🔧 正在检查更新日志部分间距...",
        "no_valid_language": "❌ 未提供有效的语言代码。",
        "language_not_recognized": "❌ 语言代码 '{code}' 无法识别。继续...",
        "file_not_found": "⚠️ 文件 {filename} 未找到",
        "folder_not_empty": "⚠️ 文件夹 {folder} 不为空，未删除",
        "failed_delete_file": "❌ 删除 {filename} 失败：{error}",
        "failed_delete_folder": "❌ 删除文件夹失败：{error}",
        "failed_update_main": "❌ 更新主 README 失败：{error}",
        "failed_translate_changelog": "❌ 翻译 CHANGELOG 失败：{error}",
        "failed_update_changelog_links": "❌ 在 {filename} 中更新更新日志链接失败：{error}",
        "failed_update_switcher": "❌ 在 {filename} 中更新语言切换器失败：{error}",
        "translation_failed": "❌ 翻译失败：{error}",
        "reading_package_error": "❌ 读取 package.json 时出错：{error}",
        "reading_git_error": "❌ 读取 .git/config 时出错：{error}",
        "reading_github_error": "❌ 在 README 中搜索 GitHub URL 时出错：{error}",
        "changelog_section_exists": "ℹ️ 更新日志部分已存在于 README.md 中",
        "no_changelog_file_root": "❌ 在根目录中未找到 CHANGELOG.md 文件",
        "no_translation_files": "ℹ️ 未找到翻译的 README 文件",
        "language_not_supported": "⚠️ 显示语言 '{code}' 不受支持，使用默认值",
        "help_description": "MultiDoc Translator - 自动化多语言文档翻译器",
        "help_epilog": """
示例：
  # 将 README 翻译为日语和中文
  python multidoc_translator.py --lang jp,zh

  # 仅将 CHANGELOG 翻译为所有语言，使用日语通知
  python multidoc_translator.py --translate-changelog all --display jp

  # 删除特定语言文件
  python multidoc_translator.py --remove-lang jp,zh

  # 自动设置 README 中的更新日志部分
  python multidoc_translator.py --auto-setup-changelog

  # 检测 GitHub 仓库 URL
  python multidoc_translator.py --detect-github-url
        """,
        "help_lang": "要翻译的语言代码（逗号分隔）。支持：pl, zh, jp, de, fr, es, ru, pt, id, kr",
        "help_remove_lang": "删除特定翻译语言文件（逗号分隔）",
        "help_remove_all_lang": "删除所有翻译文件并清理文件夹",
        "help_add_protect": "添加短语到保护列表（支持正则表达式模式）",
        "help_remove_protect": "从保护列表中删除短语",
        "help_list_protect": "显示所有当前受保护的短语",
        "help_init_protect": "将 protected_phrases.json 重置为默认值",
        "help_enable_protect": "在翻译期间启用短语保护",
        "help_disable_protect": "在翻译期间禁用短语保护",
        "help_status_protect": "检查短语保护当前是否启用",
        "help_translate_changelog": "仅翻译 CHANGELOG.md（对所有语言使用 'all' 或指定代码）",
        "help_auto_setup_changelog": "如果 CHANGELOG.md 存在，则自动将更新日志部分添加到 README.md",
        "help_detect_github_url": "从各种来源检测并显示 GitHub 仓库 URL",
        "help_display": "终端通知的显示语言 (en, id, jp, de, es, fr, kr, pl, pt, ru, zh)",

        "changelog.onlyActions": "📋 仅 CHANGELOG 操作",
        "changelog.generateRemoveOnly": "仅生成/删除 CHANGELOG",
        "changelog.onlyDescription": "这些操作仅影响 CHANGELOG 文件，README 文件保持不变。",
        "changelog.generateOnly": "🌐 仅生成 CHANGELOG",
        "changelog.removeSelected": "🗑️ 删除选中的 CHANGELOG",
        "changelog.affectsSelected": "仅影响选中的语言：{0} 种语言",
        "changelog.generateWith": "📋 生成包含 CHANGELOG",
        "changelog.checkedDescription": "勾选时：翻译 README 和 CHANGELOG 文件",
        "changelog.uncheckedDescription": "未勾选时：仅翻译 README 文件",
        
        "progress.translatingWithChangelog": "正在翻译 README + CHANGELOG",
        "progress.translatingReadmeOnly": "仅翻译 README",
        "success.filesSavedWithChangelog": "README 和 CHANGELOG",
        "success.filesSavedReadmeOnly": "仅 README",
        "success.translationCompletedWithChangelog": "✅ {0} 个 README 和 CHANGELOG 成功翻译！",
        "success.translationCompletedReadmeOnly": "✅ {0} 个 README 成功翻译！",
        "info.noChangelogFileSkipping": "⚠️ 未找到 CHANGELOG.md - 跳过 CHANGELOG 翻译",
        
        "errors.changelogGenerateFailed": "❌ CHANGELOG 生成失败",
        "errors.changelogRemoveSelectedFailed": "❌ 删除选中的 CHANGELOG 文件失败",
        "success.changelogGenerated": "✅ 成功为 {0} 种语言生成 CHANGELOG",
        "success.changelogRemovedSelected": "✅ {0} 个 CHANGELOG 文件成功删除",
        "confirmation.removeChangelogSelected": "您确定要删除 {0} 种选中语言的 CHANGELOG 文件吗？README 文件将不受影响。",
        
        "help_generate_changelog_only": "仅为选中的语言生成 CHANGELOG 文件（README 文件保持不变）",
        "help_remove_changelog_selected": "仅删除选中的语言的 CHANGELOG 文件（README 文件保持不变）",
        "help_remove_changelog_only": "仅删除所有 CHANGELOG 文件（README 文件保持不变）",
        "help_with_changelog": "启用时：翻译 README 和 CHANGELOG。禁用时：仅翻译 README",
        "errors.noLanguagesSelected": "❌ 未选择语言",
        "errors.noLanguagesSelectedRemove": "❌ 未选择要删除的语言",
        "progress.startingTranslation": "🚀 开始翻译 {count} 种语言 - {mode_text}",
        "progress.translatingLanguage": "📖 正在翻译 {lang_name} ({current}/{total})...",
        "progress.waiting": "⏳ 等待 {seconds} 秒后进行下一个翻译...",
        "progress.completed": "✅ 翻译过程已完成",
        "progress.filesSaved": "💾 文件已保存至: {path}",
        "progress.removingSelected": "🗑️ 正在删除选中的 CHANGELOG 文件...",
        "progress.fileCreated": "✅ 已删除: {path}",
        "progress.removingChangelog": "🗑️ 正在删除所有 CHANGELOG 文件...",
        "changelog.translatingChangelog": "📘 正在为 {count} 种语言翻译 CHANGELOG...",
        "changelog.translating": "🔧 正在将 CHANGELOG 翻译为 {lang_name}...",
        "changelog.translated": "✅ CHANGELOG 已翻译为 {lang_name}",
        "changelog.autoSettingUp": "🔧 自动设置更新日志部分...",
        "changelog.checkingSpacing": "🔧 检查更新日志部分间距...",
        "progress.changelogTranslated": "✅ CHANGELOG 已翻译为 {lang_name}",
        "errors.translationFailedShort": "❌ {lang_name} 翻译失败",
        "errors.translationFailed": "❌ {lang_code} 翻译失败: {error}",
        "errors.changelogTranslationFailed": "❌ CHANGELOG 翻译失败",
        "success.changelogTranslationCompleted": "✅ CHANGELOG 翻译已完成",
        "errors.changelogRemoveFailed": "❌ 删除 CHANGELOG 文件失败",
        "info.noChangelogFiles": "ℹ️ 未找到 CHANGELOG 文件",
        "success.changelogRemoved": "✅ {count} 个 CHANGELOG 文件已成功删除",
        "confirmation.removeChangelog": "您确定要删除所有 CHANGELOG 文件吗？README 文件将不受影响。"
,
        "menu_debug": "切换调试模式",
        "debug_enabled": "调试模式现在已启用。",
        "debug_disabled": "调试模式现在已禁用。",
        "debug_current": "当前"
    }
}

# Global variable for display language
DISPLAY_LANG = "en"

def set_display_language(lang_code):
    """Set display language for notifications"""
    global DISPLAY_LANG
    if lang_code in DISPLAY_LANGUAGES:
        DISPLAY_LANG = lang_code
    else:
        print(DISPLAY_LANGUAGES["en"]["language_not_supported"].format(code=lang_code))

def t(key, **kwargs):
    """Translation function for notifications - will be populated globally"""
    global DISPLAY_LANG
    try:
        # Try to get translation from current display language
        if DISPLAY_LANG in DISPLAY_LANGUAGES and key in DISPLAY_LANGUAGES[DISPLAY_LANG]:
            return DISPLAY_LANGUAGES[DISPLAY_LANG][key].format(**kwargs)
        # Fallback to English
        elif key in DISPLAY_LANGUAGES["en"]:
            return DISPLAY_LANGUAGES["en"][key].format(**kwargs)
        else:
            # Return key as placeholder - will be filled globally
            return f"{key}"
    except Exception as e:
        # Return key on error - will be filled globally
        return f"{key}"

def get_display_language():
    """Get current display language"""
    return DISPLAY_LANG

def get_available_languages():
    """Get list of available languages"""
    return list(DISPLAY_LANGUAGES.keys())

# ---------------------- LANGUAGE SETTINGS ----------------------
LANGUAGES = {
    "pl": ("Polski", "pl", "🌐 Dostępne w innych językach:"),
    "zh": ("中文", "zh-CN", "🌐 提供其他语言版本："),
    "jp": ("日本語", "ja", "🌐 他の言語でも利用可能:"),
    "de": ("Deutsch", "de", "🌐 In anderen Sprachen verfügbar:"),
    "fr": ("Français", "fr", "🌐 Disponible dans d'autres langues :"),
    "es": ("Español", "es", "🌐 Disponible en otros idiomas:"),
    "ru": ("Русский", "ru", "🌐 Доступно na innych językach:"),
    "pt": ("Português", "pt", "🌐 Disponível em outros idiomas:"),
    "id": ("Bahasa Indonesia", "id", "🌐 Tersedia dalam bahasa lain:"),
    "kr": ("한국어", "ko", "🌐 다른 언어로도 사용 가능:"),
}

DEFAULT_PROTECTED = {
    "protected_phrases": [
        r"MIT\s+License(?:\s*©)?(?:\s*\d{4})?",
        r"https?:\/\/\S+",
        r"\(LICENSE\)",
        r"\(\.\./\.\./LICENSE\)",
        r"\*\*1\.85\.0\*\*",
        r"\*\*Windows\*\*",
        r"\*\*macOS\*\*", 
        r"\*\*Linux\*\*",
        r"\*\*Windows,\s*macOS\s*et\s*Linux\*\*",
        r"Visual Studio Code",
        r"VS Code",
        r"Google Translate",
        r"API",
        r"GitHub",
        r"README\.md",
        r"CHANGELOG\.md",
        r"Markdown"
    ]
}

# ---------------------- GITHUB URL DETECTION ----------------------
def get_github_repo_url():
    """Detect GitHub repository URL from various sources"""
    # Try from package.json first
    try:
        if os.path.exists(PACKAGE_JSON):
            with open(PACKAGE_JSON, "r", encoding="utf-8") as f:
                package_data = json.load(f)
            
            if package_data.get("repository"):
                repo_url = ""
                if isinstance(package_data["repository"], str):
                    repo_url = package_data["repository"]
                elif isinstance(package_data["repository"], dict) and package_data["repository"].get("url"):
                    repo_url = package_data["repository"]["url"]
                
                # Normalize URL
                if repo_url:
                    # Handle git+https:// format
                    repo_url = repo_url.replace("git+", "")
                    # Handle git@github.com: format
                    repo_url = repo_url.replace("git@github.com:", "https://github.com/")
                    # Handle .git suffix
                    repo_url = repo_url.replace(".git", "")
                    # Ensure it's a GitHub URL
                    if "github.com" in repo_url:
                        return repo_url
    except Exception as e:
        print(t("reading_package_error", error=e))
    
    # Try from .git/config
    try:
        git_config_path = os.path.join(".git", "config")
        if os.path.exists(git_config_path):
            with open(git_config_path, "r", encoding="utf-8") as f:
                git_config = f.read()
            
            url_match = re.search(r'url\s*=\s*(.+)', git_config)
            if url_match and url_match.group(1):
                repo_url = url_match.group(1).strip()
                # Normalize URL
                repo_url = repo_url.replace("git@github.com:", "https://github.com/")
                repo_url = repo_url.replace(".git", "")
                if "github.com" in repo_url:
                    return repo_url
    except Exception as e:
        print(t("reading_git_error", error=e))
    
    # Fallback: search in README.md
    try:
        if os.path.exists(SOURCE_FILE):
            with open(SOURCE_FILE, "r", encoding="utf-8") as f:
                readme_content = f.read()
            
            github_url_match = re.search(r'https://github\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9-_.]+', readme_content)
            if github_url_match:
                return github_url_match.group(0)
    except Exception as e:
        print(t("reading_github_error", error=e))
    
    return None

def get_github_releases_url():
    """Generate GitHub Releases URL from repository URL"""
    repo_url = get_github_repo_url()
    if repo_url:
        return f"{repo_url}/releases"
    
    # Fallback default (for this extension itself)
    return "https://github.com/fatonyahmadfauzi/Auto-Translate-Readmes/releases"

def detect_github_url():
    """Function to detect and display GitHub URL"""
    repo_url = get_github_repo_url()
    releases_url = get_github_releases_url()
    
    if repo_url:
        print(t("github_url_detected"))
        print(t("repo_url", url=repo_url))
        print(t("releases_url", url=releases_url))
        print("\n" + t("sources_checked"))
        print("• package.json (repository field)")
        print("• .git/config")
        print("• README.md (GitHub URL patterns)")
        return True
    else:
        print(t("no_github_url"))
        print("\nPlease check:")
        print("• package.json has 'repository' field")
        print("• .git/config has remote URL") 
        print("• Or add GitHub URL manually to README")
        return False

def create_square_panel(content, title=None, align_center=False, expand=True):
    panel_content = Align.center(content) if align_center else content
    return Panel(
        panel_content,
        title=title,
        title_align="left",
        border_style="cyan",
        box=box.SQUARE,
        expand=expand
    )


def get_translation_file_names(lang_code):
    if lang_code == "jp":
        readme_name = "README-JP.md"
        changelog_name = "CHANGELOG-JP.md"
    elif lang_code == "zh":
        readme_name = "README-ZH.md"
        changelog_name = "CHANGELOG-ZH.md"
    elif lang_code == "kr":
        readme_name = "README-KR.md"
        changelog_name = "CHANGELOG-KR.md"
    else:
        uppercase_code = lang_code.upper()
        readme_name = f"README-{uppercase_code}.md"
        changelog_name = f"CHANGELOG-{uppercase_code}.md"

    return readme_name, changelog_name


def resolve_translation_output_dirs(base_output_dir=None, target_dir=None):
    candidate_dirs = []

    if base_output_dir:
        candidate_dirs.append(base_output_dir)
        nested_output_dir = os.path.join(base_output_dir, OUTPUT_DIR)
        if nested_output_dir not in candidate_dirs:
            candidate_dirs.append(nested_output_dir)
    elif target_dir:
        candidate_dirs.append(os.path.join(target_dir, OUTPUT_DIR))
    else:
        candidate_dirs.append(os.path.abspath(OUTPUT_DIR))

    return candidate_dirs


def create_translation_status_table(base_output_dir=None, target_dir=None):
    table = Table(
        show_header=True,
        header_style="bold cyan",
        box=box.SIMPLE_HEAVY,
        expand=True,
        pad_edge=False
    )
    table.add_column("Code / Language", style="cyan", ratio=3)
    table.add_column("README", justify="center", ratio=2)
    table.add_column("CHANGELOG", justify="center", ratio=2)

    output_dirs = resolve_translation_output_dirs(base_output_dir, target_dir)
    has_missing_translations = False

    for lang_code, (lang_name, _, _) in LANGUAGES.items():
        readme_name, changelog_name = get_translation_file_names(lang_code)
        readme_available = any(os.path.exists(os.path.join(output_dir, readme_name)) for output_dir in output_dirs)
        changelog_available = any(os.path.exists(os.path.join(output_dir, changelog_name)) for output_dir in output_dirs)

        if not readme_available or not changelog_available:
            has_missing_translations = True

        readme_status = "[bold green]AVAILABLE[/bold green]" if readme_available else "[bold red]MISSING[/bold red]"
        changelog_status = "[bold green]AVAILABLE[/bold green]" if changelog_available else "[bold red]MISSING[/bold red]"
        table.add_row(f"{lang_code.upper()} | {lang_name}", readme_status, changelog_status)

    return table, has_missing_translations


def setup_paths_menu():
    """Setup paths for input and output directories using .path_config"""
    console = Console(width=90)
    config_file = ".path_config"
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Load current config from .path_config
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {'target_dir': os.getcwd(), 'output_base_dir': None}
        
        target_dir = config.get('target_dir', os.getcwd())
        output_base_dir = config.get('output_base_dir')
        
        # Header Panel
        header_text = Text("Setup Paths", style="bold green")
        console.print(create_square_panel(header_text, align_center=True))
        
        # Menu Panel
        menu_text = Text()
        menu_text.append("[1] Set Target Directory\n", style="green")
        menu_text.append(f"    Current: {target_dir}\n\n", style="dim")
        menu_text.append("[2] Set Output Base Directory\n", style="green")
        menu_text.append(f"    Current: {output_base_dir if output_base_dir else 'Not set'}\n\n", style="dim")
        menu_text.append("[3] View Current Config\n", style="green")
        menu_text.append("[0] Back", style="white")
        console.print(create_square_panel(menu_text, title="Setup Paths"))

        choice = console.input("\n[bold yellow][+] Select option: [/bold yellow]").strip()
        
        if choice == '1':
            print(Fore.CYAN + "Enter target directory path:")
            print(Fore.LIGHTBLACK_EX + "  • Type 'root' to use project root")
            print(Fore.LIGHTBLACK_EX + "  • Type '.' for current directory")
            print(Fore.LIGHTBLACK_EX + "  • Leave empty to cancel")
            new_target = input(Fore.CYAN + "Path: " + Fore.WHITE).strip()
            
            if not new_target:
                print(Fore.YELLOW + "⏭️  Cancelled. No changes made.")
                time.sleep(1)
            elif new_target.lower() == 'root':
                # Get project root (parent of script directory)
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                # Show confirmation if changing existing directory
                if target_dir != project_root:
                    print(Fore.YELLOW + f"⚠️  This will replace the current directory:")
                    print(Fore.LIGHTBLACK_EX + f"   Old: {target_dir}")
                    print(Fore.LIGHTBLACK_EX + f"   New: {project_root}")
                    confirm = input(Fore.YELLOW + "Do you want to continue? (y/n): " + Fore.WHITE).strip().lower()
                    if confirm != 'y':
                        print(Fore.YELLOW + "⏭️  Cancelled. No changes made.")
                        time.sleep(1)
                        continue
                config['target_dir'] = project_root
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print(Fore.GREEN + f"✅ Target directory set to project root: {config['target_dir']}")
                time.sleep(1)
            elif new_target == '.':
                current_path = os.getcwd()
                # Show confirmation if changing existing directory
                if target_dir != current_path:
                    print(Fore.YELLOW + f"⚠️  This will replace the current directory:")
                    print(Fore.LIGHTBLACK_EX + f"   Old: {target_dir}")
                    print(Fore.LIGHTBLACK_EX + f"   New: {current_path}")
                    confirm = input(Fore.YELLOW + "Do you want to continue? (y/n): " + Fore.WHITE).strip().lower()
                    if confirm != 'y':
                        print(Fore.YELLOW + "⏭️  Cancelled. No changes made.")
                        time.sleep(1)
                        continue
                config['target_dir'] = current_path
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print(Fore.GREEN + f"✅ Target directory set to current: {config['target_dir']}")
                time.sleep(1)
            else:
                # Validate path exists - check if it's a file or directory
                if os.path.isfile(new_target):
                    # If it's a file, extract the directory
                    abs_path = os.path.dirname(os.path.abspath(new_target))
                    print(Fore.CYAN + f"📄 File path detected. Using parent directory: {abs_path}")
                    # Show confirmation if changing existing directory
                    if target_dir != abs_path:
                        print(Fore.YELLOW + f"⚠️  This will replace the current directory:")
                        print(Fore.LIGHTBLACK_EX + f"   Old: {target_dir}")
                        print(Fore.LIGHTBLACK_EX + f"   New: {abs_path}")
                        confirm = input(Fore.YELLOW + "Do you want to continue? (y/n): " + Fore.WHITE).strip().lower()
                        if confirm != 'y':
                            print(Fore.YELLOW + "⏭️  Cancelled. No changes made.")
                            time.sleep(1)
                            continue
                    config['target_dir'] = abs_path
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=2)
                    print(Fore.GREEN + f"✅ Target directory set to: {config['target_dir']}")
                    time.sleep(1)
                elif os.path.isdir(new_target):
                    abs_path = os.path.abspath(new_target)
                    # Show confirmation if changing existing directory
                    if target_dir != abs_path:
                        print(Fore.YELLOW + f"⚠️  This will replace the current directory:")
                        print(Fore.LIGHTBLACK_EX + f"   Old: {target_dir}")
                        print(Fore.LIGHTBLACK_EX + f"   New: {abs_path}")
                        confirm = input(Fore.YELLOW + "Do you want to continue? (y/n): " + Fore.WHITE).strip().lower()
                        if confirm != 'y':
                            print(Fore.YELLOW + "⏭️  Cancelled. No changes made.")
                            time.sleep(1)
                            continue
                    config['target_dir'] = abs_path
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=2)
                    print(Fore.GREEN + f"✅ Target directory set to: {config['target_dir']}")
                    time.sleep(1)
                else:
                    print(Fore.RED + f"❌ Path not found: {new_target}")
                    print(Fore.LIGHTBLACK_EX + f"   Please check if directory or file exists.")
                    time.sleep(2)
        
        elif choice == '2':
            print(Fore.CYAN + "Enter output base directory path:")
            print(Fore.LIGHTBLACK_EX + "  • Type 'root' to use project root")
            print(Fore.LIGHTBLACK_EX + "  • Type '.' for current directory")
            print(Fore.LIGHTBLACK_EX + "  • Leave empty to unset (use default docs/lang)")
            new_output = input(Fore.CYAN + "Path: " + Fore.WHITE).strip()
            
            if not new_output:
                # Show confirmation if unsetting existing directory
                if output_base_dir:
                    print(Fore.YELLOW + f"⚠️  This will unset the output directory:")
                    print(Fore.LIGHTBLACK_EX + f"   Current: {output_base_dir}")
                    print(Fore.LIGHTBLACK_EX + f"   Will use default: {OUTPUT_DIR}")
                    confirm = input(Fore.YELLOW + "Do you want to continue? (y/n): " + Fore.WHITE).strip().lower()
                    if confirm != 'y':
                        print(Fore.YELLOW + "⏭️  Cancelled. No changes made.")
                        time.sleep(1)
                        continue
                config['output_base_dir'] = None
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print(Fore.GREEN + f"✅ Output directory unset (will use default: {OUTPUT_DIR})")
                time.sleep(1)
            elif new_output.lower() == 'root':
                # Get project root
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                # Show confirmation if changing existing directory
                if output_base_dir and output_base_dir != project_root:
                    print(Fore.YELLOW + f"⚠️  This will replace the current output directory:")
                    print(Fore.LIGHTBLACK_EX + f"   Old: {output_base_dir}")
                    print(Fore.LIGHTBLACK_EX + f"   New: {project_root}")
                    confirm = input(Fore.YELLOW + "Do you want to continue? (y/n): " + Fore.WHITE).strip().lower()
                    if confirm != 'y':
                        print(Fore.YELLOW + "⏭️  Cancelled. No changes made.")
                        time.sleep(1)
                        continue
                config['output_base_dir'] = project_root
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print(Fore.GREEN + f"✅ Output directory set to project root: {config['output_base_dir']}")
                time.sleep(1)
            elif new_output == '.':
                current_path = os.getcwd()
                # Show confirmation if changing existing directory
                if output_base_dir and output_base_dir != current_path:
                    print(Fore.YELLOW + f"⚠️  This will replace the current output directory:")
                    print(Fore.LIGHTBLACK_EX + f"   Old: {output_base_dir}")
                    print(Fore.LIGHTBLACK_EX + f"   New: {current_path}")
                    confirm = input(Fore.YELLOW + "Do you want to continue? (y/n): " + Fore.WHITE).strip().lower()
                    if confirm != 'y':
                        print(Fore.YELLOW + "⏭️  Cancelled. No changes made.")
                        time.sleep(1)
                        continue
                config['output_base_dir'] = current_path
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print(Fore.GREEN + f"✅ Output directory set to current: {config['output_base_dir']}")
                time.sleep(1)
            else:
                # Validate path exists - check if it's a file or directory
                if os.path.isfile(new_output):
                    # If it's a file, extract the directory
                    abs_path = os.path.dirname(os.path.abspath(new_output))
                    print(Fore.CYAN + f"📄 File path detected. Using parent directory: {abs_path}")
                    # Show confirmation if changing existing directory
                    if output_base_dir and output_base_dir != abs_path:
                        print(Fore.YELLOW + f"⚠️  This will replace the current output directory:")
                        print(Fore.LIGHTBLACK_EX + f"   Old: {output_base_dir}")
                        print(Fore.LIGHTBLACK_EX + f"   New: {abs_path}")
                        confirm = input(Fore.YELLOW + "Do you want to continue? (y/n): " + Fore.WHITE).strip().lower()
                        if confirm != 'y':
                            print(Fore.YELLOW + "⏭️  Cancelled. No changes made.")
                            time.sleep(1)
                            continue
                    config['output_base_dir'] = abs_path
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=2)
                    print(Fore.GREEN + f"✅ Output directory set to: {config['output_base_dir']}")
                    time.sleep(1)
                elif os.path.isdir(new_output):
                    abs_path = os.path.abspath(new_output)
                    # Show confirmation if changing existing directory
                    if output_base_dir and output_base_dir != abs_path:
                        print(Fore.YELLOW + f"⚠️  This will replace the current output directory:")
                        print(Fore.LIGHTBLACK_EX + f"   Old: {output_base_dir}")
                        print(Fore.LIGHTBLACK_EX + f"   New: {abs_path}")
                        confirm = input(Fore.YELLOW + "Do you want to continue? (y/n): " + Fore.WHITE).strip().lower()
                        if confirm != 'y':
                            print(Fore.YELLOW + "⏭️  Cancelled. No changes made.")
                            time.sleep(1)
                            continue
                    config['output_base_dir'] = abs_path
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=2)
                    print(Fore.GREEN + f"✅ Output directory set to: {config['output_base_dir']}")
                    time.sleep(1)
                else:
                    print(Fore.RED + f"❌ Path not found: {new_output}")
                    print(Fore.LIGHTBLACK_EX + f"   Please check if directory or file exists.")
                    time.sleep(2)
        
        elif choice == '3':
            print(Fore.CYAN + "\nCurrent Configuration:")
            print(json.dumps(config, indent=2, ensure_ascii=False))
            input(Fore.YELLOW + "\nPress Enter to continue...")
        
        elif choice == '0':
            break

# ---------------------- PROTECTION UTILITIES ----------------------
def load_protected_phrases():
    if not os.path.exists(PROTECTED_FILE):
        save_protected_phrases(DEFAULT_PROTECTED)
    with open(PROTECTED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_protected_phrases(data):
    with open(PROTECTED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_protect_enabled():
    return os.path.exists(PROTECT_STATUS_FILE)

def set_protect_status(enabled):
    if enabled:
        open(PROTECT_STATUS_FILE, "w").close()
    else:
        if os.path.exists(PROTECT_STATUS_FILE):
            os.remove(PROTECT_STATUS_FILE)

# ---------------------- CHANGELOG DETECTION ----------------------
def has_changelog_file():
    """Check if CHANGELOG.md file exists in root"""
    return os.path.exists(CHANGELOG_FILE)

def has_changelog_section_in_readme():
    """Check if README.md has Changelog section"""
    
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check patterns for Changelog section
    patterns = [
        r"##\s+🧾\s+Changelog",
        r"##\s+Changelog",
        r"#+\s+Changelog",
        r"##\s+📝\s+Changelog",  # Tambahkan pattern alternatif
        r"##\s+.*[Cc]hangelog"   # Pattern lebih fleksibel
    ]
    
    for pattern in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    
    return False

def fix_existing_changelog_spacing():
    """Fix spacing and separators for existing Changelog section"""
    if not has_changelog_section_in_readme():
        return False
    
    try:
        with open(SOURCE_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        changes_made = False
        
        # 1. Fix pattern: --- directly followed by ## 🧾 Changelog
        # Becomes: --- + 1 empty line + ## 🧾 Changelog
        old_pattern = r'---\s*\n\s*## 🧾 Changelog'
        new_pattern = '---\n\n## 🧾 Changelog'
        
        if re.search(old_pattern, content):
            content = re.sub(old_pattern, new_pattern, content)
            changes_made = True
        
        # 2. Check if there's separator between Changelog and License
        if '## 🧾 Changelog' in content and '## 🧾 License' in content:
            # Check if there's --- between Changelog and License
            between_sections = re.search(r'## 🧾 Changelog.*?(## 🧾 License)', content, re.DOTALL)
            if between_sections:
                section_content = between_sections.group(0)
                if '---' not in section_content:
                    # Add --- before License
                    content = re.sub(
                        r'(## 🧾 Changelog.*?)(## 🧾 License)',
                        r'\1\n\n---\n\n\2',
                        content,
                        flags=re.DOTALL
                    )
                    changes_made = True
        
        if changes_made:
            with open(SOURCE_FILE, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(t("changelog_spacing_fixed"))
            return True
        
        return False
        
    except Exception as e:
        print(t("failed_update_main", error=e))
        return False

def add_changelog_section_to_readme():
    """Add Changelog section to README.md if not exists with proper spacing and separators"""
    if not has_changelog_file():
        print(t("no_changelog_file_root"))
        return False
    
    if has_changelog_section_in_readme():
        print(t("changelog_section_exists"))
        # Fix spacing if already exists
        fix_existing_changelog_spacing()
        return True
    
    try:
        with open(SOURCE_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Get dynamic GitHub Releases URL
        github_releases_url = get_github_releases_url()
        
        # Find position before License section to add Changelog
        license_pattern = r'##\s+🧾\s+License'
        license_match = re.search(license_pattern, content, re.IGNORECASE)
        
        # Changelog section with correct format including separators
        changelog_section = f"""

---

## 🧾 Changelog

See all notable changes for each version in the [CHANGELOG.md](CHANGELOG.md) file.

> 📦 You can also view release notes directly on the [GitHub Releases page]({github_releases_url}).

"""
        
        if license_match:
            # Insert before License section
            position = license_match.start()
            
            # Check if there's already --- before License
            content_before_license = content[:position].rstrip()
            if content_before_license.endswith('---'):
                # If there's already ---, we only need to add Changelog section
                # Remove existing --- and replace with complete section
                last_dash_pos = content_before_license.rfind('---')
                new_content = content[:last_dash_pos].rstrip() + changelog_section + content[position:]
            else:
                # If no ---, add complete section with ---
                new_content = content[:position] + changelog_section + content[position:]
        else:
            # Add at end of file before License if exists
            if "## 🧾 License" in content:
                license_pos = content.find("## 🧾 License")
                content_before_license = content[:license_pos].rstrip()
                
                if content_before_license.endswith('---'):
                    # If there's already ---, replace with complete section
                    last_dash_pos = content_before_license.rfind('---')
                    new_content = content[:last_dash_pos].rstrip() + changelog_section + content[license_pos:]
                else:
                    # If no ---, add complete section
                    new_content = content[:license_pos] + changelog_section + content[license_pos:]
            else:
                # Add at end of file with separator
                if content.strip().endswith('---'):
                    new_content = content.rstrip() + f'\n\n## 🧾 Changelog\n\nSee all notable changes for each version in the [CHANGELOG.md](CHANGELOG.md) file.\n\n> 📦 You can also view release notes directly on the [GitHub Releases page]({github_releases_url}).'
                else:
                    new_content = content.strip() + f'\n\n---\n\n## 🧾 Changelog\n\nSee all notable changes for each version in the [CHANGELOG.md](CHANGELOG.md) file.\n\n> 📦 You can also view release notes directly on the [GitHub Releases page]({github_releases_url}).'
        
        # Final cleanup: ensure correct format
        # Pattern: --- followed by 1 empty line, then ## 🧾 Changelog
        new_content = re.sub(r'---\s*\n\s*## 🧾 Changelog', '---\n\n## 🧾 Changelog', new_content)
        
        # Also ensure there's --- before License
        if '## 🧾 Changelog' in new_content and '## 🧾 License' in new_content:
            # Check if there's --- between Changelog and License
            between_sections = re.search(r'## 🧾 Changelog.*?(## 🧾 License)', new_content, re.DOTALL)
            if between_sections:
                section_content = between_sections.group(0)
                if '---' not in section_content:
                    # Add --- before License
                    new_content = re.sub(
                        r'(## 🧾 Changelog.*?)(## 🧾 License)',
                        r'\1\n\n---\n\n\2',
                        new_content,
                        flags=re.DOTALL
                    )
        
        # Also fix if there are multiple empty lines
        new_content = re.sub(r'\n\n\n+', '\n\n', new_content)
        
        with open(SOURCE_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print(t("changelog_section_added"))
        print(f"🔗 GitHub Releases URL: {github_releases_url}")
        return True
        
    except Exception as e:
        print(t("changelog_setup_failed"))
        return False

# ---------------------- TRANSLATION FUNCTIONS ----------------------
def translate_text(text, dest):
    if not text.strip():
        return text
    try:
        # Tambahkan timeout dan retry mechanism
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return GoogleTranslator(source="auto", target=dest).translate(text)
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
                    continue
                raise e
    except Exception as e:
        print(t("translation_failed", error=e))
        # Return original text instead of failing completely
        return text

def get_existing_translated_languages():
    """Get list of languages that already have README files"""
    existing_langs = []
    if not os.path.exists(OUTPUT_DIR):
        return existing_langs
        
    for code in LANGUAGES:
        # Special filename format for jp, zh, kr
        if code == "jp":
            readme_path = os.path.join(OUTPUT_DIR, "README-JP.md")
        elif code == "zh":
            readme_path = os.path.join(OUTPUT_DIR, "README-ZH.md")
        elif code == "kr":
            readme_path = os.path.join(OUTPUT_DIR, "README-KR.md")
        else:
            readme_path = os.path.join(OUTPUT_DIR, f"README-{code.upper()}.md")
            
        if os.path.exists(readme_path):
            existing_langs.append(code)
    return existing_langs

def update_language_switcher(new_languages=None, removed_languages=None):
    """Update language switcher in main README and all translated READMEs"""
    
    # Get all existing languages
    existing_langs = get_existing_translated_languages()
    
    # If there are new languages, add to existing list
    if new_languages:
        for lang in new_languages:
            if lang not in existing_langs:
                existing_langs.append(lang)
    
    # If there are removed languages, remove from existing list
    if removed_languages:
        for lang in removed_languages:
            if lang in existing_langs:
                existing_langs.remove(lang)
    
    # Update main README (English)
    try:
        with open(SOURCE_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Create link list for main README with desired order
        lang_links = []
        # Order: pl, zh, jp, de, fr, es, ru, pt, id, kr
        ordered_langs = ["pl", "zh", "jp", "de", "fr", "es", "ru", "pt", "id", "kr"]
        ordered_existing = [lang for lang in ordered_langs if lang in existing_langs]
        
        for code in ordered_existing:
            if code in LANGUAGES:
                name = LANGUAGES[code][0]
                # Special filename format for links
                if code == "jp":
                    lang_links.append(f"[{name}](docs/lang/README-JP.md)")
                elif code == "zh":
                    lang_links.append(f"[{name}](docs/lang/README-ZH.md)")
                elif code == "kr":
                    lang_links.append(f"[{name}](docs/lang/README-KR.md)")
                else:
                    lang_links.append(f"[{name}](docs/lang/README-{code.upper()}.md)")
        
        if lang_links:
            switcher = f"> 🌐 Available in other languages: {' | '.join(lang_links)}"
            
            # 1. Start by stripping ALL previous switchers to fix duplicates
            content = re.sub(r'> 🌐 Available in other languages:[^\n]*\n?', '', content)
            
            # Strip multiple empty lines
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            # 2. Insert new switcher at the proper position
            match = re.search(r"\n-{3,}\n", content)
            if match:
                position = match.start()
                content = content[:position] + "\n\n" + switcher + "\n" + content[position:]
            else:
                # Insert just below H1 title and any badges
                header_match = re.search(r'^(#\s+[^\n]+(?:\n(?:\[!\[|!\[|<a)[^\n]*)*)', content, re.MULTILINE)
                if header_match:
                    position = header_match.end()
                    content = content[:position] + "\n\n" + switcher + "\n" + content[position:]
                else:
                    content = switcher + "\n\n" + content.strip()
        else:
            # Remove entirely
            content = re.sub(r'> 🌐 Available in other languages:[^\n]*\n?', '', content)
            content = re.sub(r'\n{3,}', '\n\n', content)
        
        with open(SOURCE_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print(t("language_switcher_updated", filename="main README"))
        if ordered_existing:
            print(f"   Languages: {', '.join(ordered_existing)}")
        else:
            print(f"   {t('no_translation_files')}")
    
    except Exception as e:
        print(t("failed_update_switcher", filename="main README", error=e))
    
    # Update all translated READMEs
    for lang_code in existing_langs:
        if lang_code in LANGUAGES:
            lang_name, _, intro_text = LANGUAGES[lang_code]
            # Special filename format for jp, zh, kr
            if lang_code == "jp":
                readme_path = os.path.join(OUTPUT_DIR, "README-JP.md")
            elif lang_code == "zh":
                readme_path = os.path.join(OUTPUT_DIR, "README-ZH.md")
            elif lang_code == "kr":
                readme_path = os.path.join(OUTPUT_DIR, "README-KR.md")
            else:
                readme_path = os.path.join(OUTPUT_DIR, f"README-{lang_code.upper()}.md")
            
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Create link list for this language (all languages except itself)
                    links = ["[English](../../README.md)"]
                    # Order: pl, zh, jp, de, fr, es, ru, pt, id, kr
                    ordered_langs = ["pl", "zh", "jp", "de", "fr", "es", "ru", "pt", "id", "kr"]
                    ordered_others = [code for code in ordered_langs if code in existing_langs and code != lang_code]
                    
                    for code in ordered_others:
                        name = LANGUAGES[code][0]
                        # Special filename format for links
                        if code == "jp":
                            links.append(f"[{name}](README-JP.md)")
                        elif code == "zh":
                            links.append(f"[{name}](README-ZH.md)")
                        elif code == "kr":
                            links.append(f"[{name}](README-KR.md)")
                        else:
                            links.append(f"[{name}](README-{code.upper()}.md)")
                    
                    links_text = " | ".join(links)
                    new_switcher_line = f"> {intro_text} {links_text}"
                    
                    # 1. Stripe all previous switchers
                    escaped_intro = re.escape(intro_text)
                    content = re.sub(fr'> {escaped_intro}[^\n]*\n?', '', content)
                    content = re.sub(r'> 🌐 Available in other languages:[^\n]*\n?', '', content)
                    content = re.sub(r'\n{3,}', '\n\n', content)
                    
                    # 2. Insert new switcher
                    match = re.search(r"\n-{3,}\n", content)
                    if match:
                        position = match.start()
                        content = content[:position] + "\n\n" + new_switcher_line + "\n" + content[position:]
                    else:
                        header_match = re.search(r'^(#\s+[^\n]+(?:\n(?:\[!\[|!\[|<a)[^\n]*)*)', content, re.MULTILINE)
                        if header_match:
                            position = header_match.end()
                            content = content[:position] + "\n\n" + new_switcher_line + "\n" + content[position:]
                        else:
                            content = new_switcher_line + "\n\n" + content.strip()
                    
                    with open(readme_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(t("language_switcher_updated", filename=f"README-{lang_code.upper()}"))
                
                except Exception as e:
                    print(t("failed_update_switcher", filename=f"README-{lang_code.upper()}", error=e))

def remove_language_files(lang_codes):
    """Remove README files for specific languages and update language switcher"""
    removed_langs = []
    
    for lang_code in lang_codes:
        if lang_code in LANGUAGES:
            # Special filename format for jp, zh, kr
            if lang_code == "jp":
                readme_path = os.path.join(OUTPUT_DIR, "README-JP.md")
                changelog_path = os.path.join(OUTPUT_DIR, "CHANGELOG-JP.md")
            elif lang_code == "zh":
                readme_path = os.path.join(OUTPUT_DIR, "README-ZH.md")
                changelog_path = os.path.join(OUTPUT_DIR, "CHANGELOG-ZH.md")
            elif lang_code == "kr":
                readme_path = os.path.join(OUTPUT_DIR, "README-KR.md")
                changelog_path = os.path.join(OUTPUT_DIR, "CHANGELOG-KR.md")
            else:
                readme_path = os.path.join(OUTPUT_DIR, f"README-{lang_code.upper()}.md")
                changelog_path = os.path.join(OUTPUT_DIR, f"CHANGELOG-{lang_code.upper()}.md")
            
            # Remove README file
            if os.path.exists(readme_path):
                try:
                    os.remove(readme_path)
                    removed_langs.append(lang_code)
                    print(t("file_deleted", filename=os.path.basename(readme_path)))
                except Exception as e:
                    print(t("failed_delete_file", filename=os.path.basename(readme_path), error=e))
            else:
                print(t("file_not_found", filename=os.path.basename(readme_path)))
            
            # Remove CHANGELOG file if exists
            if os.path.exists(changelog_path):
                try:
                    os.remove(changelog_path)
                    print(t("file_deleted", filename=os.path.basename(changelog_path)))
                except Exception as e:
                    print(t("failed_delete_file", filename=os.path.basename(changelog_path), error=e))
        else:
            print(t("language_not_recognized", code=lang_code))
    
    # Update language switcher after removing files
    if removed_langs:
        update_language_switcher(removed_languages=removed_langs)
        
        # Remove docs/lang folder if empty, then docs if also empty
        if not get_existing_translated_languages():
            try:
                if os.path.exists(OUTPUT_DIR) and not os.listdir(OUTPUT_DIR):
                    shutil.rmtree(OUTPUT_DIR)
                    print(t("folder_deleted", folder=OUTPUT_DIR))
                    
                    # Check if docs folder is also empty, if yes remove
                    docs_dir = os.path.dirname(OUTPUT_DIR)
                    if os.path.exists(docs_dir) and not os.listdir(docs_dir):
                        shutil.rmtree(docs_dir)
                        print(t("folder_deleted", folder=docs_dir))
            except Exception as e:
                print(t("failed_delete_folder", error=e))
    
    return removed_langs

def remove_all_language_files():
    """Remove all translated README files and docs/lang folder and docs if empty"""
    existing_langs = get_existing_translated_languages()
    
    if not existing_langs:
        print(t("no_translation_files"))
        return
    
    # Remove all README and CHANGELOG files
    for lang_code in existing_langs:
        # Special filename format for jp, zh, kr
        if lang_code == "jp":
            readme_path = os.path.join(OUTPUT_DIR, "README-JP.md")
            changelog_path = os.path.join(OUTPUT_DIR, "CHANGELOG-JP.md")
        elif lang_code == "zh":
            readme_path = os.path.join(OUTPUT_DIR, "README-ZH.md")
            changelog_path = os.path.join(OUTPUT_DIR, "CHANGELOG-ZH.md")
        elif lang_code == "kr":
            readme_path = os.path.join(OUTPUT_DIR, "README-KR.md")
            changelog_path = os.path.join(OUTPUT_DIR, "CHANGELOG-KR.md")
        else:
            readme_path = os.path.join(OUTPUT_DIR, f"README-{lang_code.upper()}.md")
            changelog_path = os.path.join(OUTPUT_DIR, f"CHANGELOG-{lang_code.upper()}.md")
        
        try:
            if os.path.exists(readme_path):
                os.remove(readme_path)
                print(t("file_deleted", filename=os.path.basename(readme_path)))
            
            if os.path.exists(changelog_path):
                os.remove(changelog_path)
                print(t("file_deleted", filename=os.path.basename(changelog_path)))
        except Exception as e:
            print(t("failed_delete_file", filename=f"for {lang_code}", error=e))
    
    # Remove docs/lang folder if empty, then docs if also empty
    try:
        if os.path.exists(OUTPUT_DIR):
            if not os.listdir(OUTPUT_DIR):
                shutil.rmtree(OUTPUT_DIR)
                print(t("folder_deleted", folder=OUTPUT_DIR))
                
                # Check if docs folder is also empty, if yes remove
                docs_dir = os.path.dirname(OUTPUT_DIR)
                if os.path.exists(docs_dir) and not os.listdir(docs_dir):
                    shutil.rmtree(docs_dir)
                    print(t("folder_deleted", folder=docs_dir))
            else:
                print(t("folder_not_empty", folder=OUTPUT_DIR))
    except Exception as e:
        print(t("failed_delete_folder", error=e))
    
    # Update main README to remove language switcher and clean up empty lines
    try:
        with open(SOURCE_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Remove language switcher
        content = re.sub(r'> 🌐 Available in other languages:.*\n', '', content)
        
        # Clean up excess empty lines
        content = re.sub(r'\n\n\n', '\n\n', content)
        content = re.sub(r'\n\n\n', '\n\n', content)
        
        with open(SOURCE_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(t("language_switcher_updated", filename="main README"))
    
    except Exception as e:
        print(t("failed_update_main", error=e))

def protect_specific_phrases(text, lang_code):
    """Special protection for important phrases after translation"""
    
    # Protection for version
    text = re.sub(r'(\*\*)?1\.85\.0(\*\*)?', '**1.85.0**', text)
    
    # Protection for operating systems
    text = re.sub(r'(\*\*)?Windows(\*\*)?', '**Windows**', text, flags=re.IGNORECASE)
    text = re.sub(r'(\*\*)?macOS(\*\*)?', '**macOS**', text, flags=re.IGNORECASE)
    text = re.sub(r'(\*\*)?Linux(\*\*)?', '**Linux**', text, flags=re.IGNORECASE)
    
    # Special protection for OS list format
    text = re.sub(r'\*\*Windows\*\*,?\s*\*\*macOS\*\*,?\s*(et|and|und|y|и)\s*\*\*Linux\*\*', '**Windows**, **macOS** et **Linux**', text, flags=re.IGNORECASE)
    text = re.sub(r'\*\*Windows\*\*,?\s*\*\*macOS\*\*,?\s*\*\*Linux\*\*', '**Windows**, **macOS** et **Linux**', text, flags=re.IGNORECASE)
    
    return text

# ---------------------- CHANGELOG TRANSLATION ----------------------
def translate_changelog(lang_code, lang_info, protected):
    """Translate CHANGELOG.md file to target language"""
    if not has_changelog_file():
        return False
    
    lang_name, translate_code, _ = lang_info
    # Special filename format for jp, zh, kr
    if lang_code == "jp":
        changelog_dest_path = os.path.join(OUTPUT_DIR, "CHANGELOG-JP.md")
    elif lang_code == "zh":
        changelog_dest_path = os.path.join(OUTPUT_DIR, "CHANGELOG-ZH.md")
    elif lang_code == "kr":
        changelog_dest_path = os.path.join(OUTPUT_DIR, "CHANGELOG-KR.md")
    else:
        changelog_dest_path = os.path.join(OUTPUT_DIR, f"CHANGELOG-{lang_code.upper()}.md")
    
    print(t("translating_changelog", lang_name=lang_name, lang_code=lang_code.upper()))
    
    try:
        with open(CHANGELOG_FILE, "r", encoding="utf-8") as f:
            changelog_content = f.read()
        
        # Separate CHANGELOG header and body
        parts = re.split(r'\n-{3,}\n', changelog_content, 1)
        changelog_header = parts[0] if len(parts) > 0 else ""
        changelog_body = parts[1] if len(parts) > 1 else ""
        
        # Translate CHANGELOG title
        translated_title = translate_text("Changelog", translate_code)
        
        # Create translated header
        if "# Changelog" in changelog_header:
            translated_header = changelog_header.replace("# Changelog", f"# {translated_title}")
        else:
            translated_header = f"# {translated_title}\n\n{changelog_header}"
        
        # Process CHANGELOG body translation
        body_lines = changelog_body.split("\n")
        translated_lines = []
        in_code_block = False
        
        for line in body_lines:
            # Detect code blocks
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                translated_lines.append(line)
                continue
            
            # If in code block, don't translate
            if in_code_block:
                translated_lines.append(line)
                continue
            
            # Detect version (format: ## [1.0.0] - 2024-01-01)
            version_match = re.match(r'^(##\s+\[[\d\.]+\]\s*-\s*\d{4}-\d{2}-\d{2})', line)
            if version_match:
                translated_lines.append(line)  # Don't translate version line
                continue
            
            # Detect structural elements
            is_structural = (
                re.match(r"^\s*[-=]+\s*$", line) or  # Separator lines
                not line.strip() or                   # Empty lines
                re.match(r"^\s*\[.*?\]:\s*", line)   # Link references
            )
            
            if is_structural:
                translated_lines.append(line)
                continue
            
            # Protect text before translation
            temp_line = line
            placeholders = {}
            counter = 0
            
            def protect(pattern, text, flags=0):
                nonlocal counter
                def repl(m):
                    nonlocal counter
                    key = f"__p{counter}__"
                    placeholders[key] = m.group(0)
                    counter += 1
                    return key
                return re.sub(pattern, repl, text, flags=flags)
            
            # Protection for all important patterns
            if is_protect_enabled():
                for p in protected["protected_phrases"]:
                    temp_line = protect(p, temp_line)
            
            # Additional protection specifically for CHANGELOG
            temp_line = protect(r"https?://[^\s\)]+", temp_line)           # URLs
            temp_line = protect(r"`[^`]+`", temp_line)                     # Inline code
            temp_line = protect(r"\[.*?\]\([^)]+\)", temp_line)            # Markdown links
            temp_line = protect(r"\[[\d\.]+\]:\s*\S+", temp_line)          # Version links
            
            # Translate text
            translated = translate_text(temp_line, translate_code)
            
            # Restore placeholders to original text
            for key, val in placeholders.items():
                translated = translated.replace(key, val)
            
            translated_lines.append(translated)
        
        translated_body = "\n".join(translated_lines)
        
        # Combine header and body
        final_changelog = f"{translated_header}\n\n---\n{translated_body}"
        
        # Cleanup remaining placeholders
        final_changelog = re.sub(r"__p\d+__", "", final_changelog)
        
        # Write translated CHANGELOG file
        with open(changelog_dest_path, "w", encoding="utf-8") as f:
            f.write(final_changelog)
        
        print(t("changelog_created", path=changelog_dest_path))
        return True
        
    except Exception as e:
        print(t("failed_translate_changelog", error=e))
        return False

def update_changelog_links_in_readme(lang_code, lang_info):
    """Update CHANGELOG links in translated README"""
    # Special filename format for jp, zh, kr
    if lang_code == "jp":
        readme_path = os.path.join(OUTPUT_DIR, "README-JP.md")
        changelog_dest_path = "CHANGELOG-JP.md"
    elif lang_code == "zh":
        readme_path = os.path.join(OUTPUT_DIR, "README-ZH.md")
        changelog_dest_path = "CHANGELOG-ZH.md"
    elif lang_code == "kr":
        readme_path = os.path.join(OUTPUT_DIR, "README-KR.md")
        changelog_dest_path = "CHANGELOG-KR.md"
    else:
        readme_path = os.path.join(OUTPUT_DIR, f"README-{lang_code.upper()}.md")
        changelog_dest_path = f"CHANGELOG-{lang_code.upper()}.md"
    
    if not os.path.exists(readme_path):
        return
    
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Translate "Changelog" and "release notes" text
        _, translate_code, _ = lang_info
        translated_changelog = translate_text("Changelog", translate_code)
        translated_release_notes = translate_text("release notes", translate_code)
        translated_view = translate_text("view", translate_code)
        translated_also = translate_text("also", translate_code)
        translated_you_can = translate_text("You can", translate_code)
        
        # Get dynamic GitHub Releases URL
        github_releases_url = get_github_releases_url()
        
        # Update Changelog section title
        content = re.sub(
            r'##\s+🧾\s+Changelog',
            f'## 🧾 {translated_changelog}',
            content,
            flags=re.IGNORECASE
        )
        
        # Update link to translated CHANGELOG file
        content = re.sub(
            r'\[CHANGELOG\.md\]\(CHANGELOG\.md\)',
            f'[{translated_changelog}]({changelog_dest_path})',
            content
        )
        
        # Update release notes text with dynamic URL
        old_release_pattern = r'You can also view release notes directly on the \[GitHub Releases page\]\([^)]+\)'
        new_release_text = f'{translated_you_can} {translated_also} {translated_view} {translated_release_notes} directly on the [GitHub Releases page]({github_releases_url})'
        
        content = re.sub(old_release_pattern, new_release_text, content, flags=re.IGNORECASE)
        
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(t("changelog_links_updated", filename=f"README-{lang_code.upper()}"))
        
    except Exception as e:
        print(t("failed_update_changelog_links", filename=f"README-{lang_code.upper()}", error=e))

def translate_changelog_only(lang_codes=None):
    """Translate only CHANGELOG without README"""
    if not has_changelog_file():
        print(t("no_changelog_file"))
        return False
    
    protected = load_protected_phrases()
    
    # If no languages specified, use all languages
    if not lang_codes:
        lang_codes = LANGUAGES.keys()
    
    success_count = 0
    for lang_code in lang_codes:
        if lang_code in LANGUAGES:
            if translate_changelog(lang_code, LANGUAGES[lang_code], protected):
                success_count += 1
                
                # Update links in README if it exists
                update_changelog_links_in_readme(lang_code, LANGUAGES[lang_code])
            
            time.sleep(1)  # Delay to avoid rate limiting
    
    if success_count > 0:
        print(t("changelog_translated", count=success_count))
        return True
    else:
        print(t("no_changelog_translated"))
        return False

# ---------------------- NEW CHANGELOG ONLY FUNCTIONS ----------------------

def generate_changelog_only(lang_codes=None):
    """Generate CHANGELOG files only for selected languages (README files remain unchanged)"""
    if not has_changelog_file():
        print(t("no_changelog_file"))
        return False
    
    if not lang_codes:
        print(t("errors.noLanguagesSelected"))
        return False
    
    # Filter valid language codes
    valid_langs = [code for code in lang_codes if code in LANGUAGES and code != 'en']
    
    if not valid_langs:
        print(t("errors.noLanguagesSelected"))
        return False
    
    protected = load_protected_phrases()
    success_count = 0
    
    print(t("changelog.translatingChangelog", count=len(valid_langs)))
    
    for lang_code in valid_langs:
        lang_name = LANGUAGES[lang_code][0]
        print(t("changelog.translating", lang_name=lang_name))
        
        try:
            if translate_changelog(lang_code, LANGUAGES[lang_code], protected):
                update_changelog_links_in_readme(lang_code, LANGUAGES[lang_code])
                success_count += 1
                print(t("changelog.translated", lang_name=lang_name))
            else:
                print(t("errors.translationFailedShort", lang_name=lang_name))
            
            time.sleep(2)  # Delay to avoid rate limiting
            
        except Exception as e:
            error_msg = t("errors.translationFailed", lang_code=lang_code, error=str(e))
            print(f"❌ {error_msg}")
    
    if success_count > 0:
        print(t("success.changelogTranslationCompleted"))
        print(t("progress.filesSaved", path=os.path.join(OUTPUT_DIR)))
        print(t("success.changelogGenerated", count=success_count))
        return True
    else:
        print(t("errors.changelogTranslationFailed"))
        return False

def remove_changelog_selected(lang_codes):
    """Remove CHANGELOG files for selected languages only (README files remain unchanged)"""
    if not lang_codes:
        print(t("errors.noLanguagesSelectedRemove"))
        return False
    
    # Filter valid language codes
    valid_langs = [code for code in lang_codes if code in LANGUAGES and code != 'en']
    
    if not valid_langs:
        print(t("errors.noLanguagesSelectedRemove"))
        return False
    
    # Confirmation prompt
    confirmation = input(t("confirmation.removeChangelogSelected", count=len(valid_langs)) + " (y/N): ")
    if confirmation.lower() not in ['y', 'yes']:
        print("Operation cancelled.")
        return False
    
    print(t("progress.removingSelected", count=len(valid_langs)))
    
    removed_count = 0
    for lang_code in valid_langs:
        # Special filename format for jp, zh, kr
        if lang_code == "jp":
            changelog_path = os.path.join(OUTPUT_DIR, "CHANGELOG-JP.md")
        elif lang_code == "zh":
            changelog_path = os.path.join(OUTPUT_DIR, "CHANGELOG-ZH.md")
        elif lang_code == "kr":
            changelog_path = os.path.join(OUTPUT_DIR, "CHANGELOG-KR.md")
        else:
            changelog_path = os.path.join(OUTPUT_DIR, f"CHANGELOG-{lang_code.upper()}.md")
        
        if os.path.exists(changelog_path):
            try:
                os.remove(changelog_path)
                removed_count += 1
                lang_name = LANGUAGES[lang_code][0]
                print(t("progress.fileCreated", path=lang_name))
            except Exception as e:
                print(t("errors.changelogRemoveFailed"))
        else:
            print(t("info.noChangelogFiles"))
    
    if removed_count > 0:
        print(t("success.changelogRemovedSelected", count=removed_count))
        return True
    else:
        print(t("info.noChangelogFiles"))
        return False

def remove_changelog_only():
    """Remove ALL CHANGELOG files only (README files remain unchanged)"""
    # Confirmation prompt
    confirmation = input(t("confirmation.removeChangelog") + " (y/N): ")
    if confirmation.lower() not in ['y', 'yes']:
        print("Operation cancelled.")
        return False
    
    print(t("progress.removingChangelog"))
    
    removed_count = 0
    output_dir = OUTPUT_DIR
    
    if os.path.exists(output_dir):
        try:
            files = os.listdir(output_dir)
            changelog_files = [f for f in files if f.startswith("CHANGELOG-") and f.endswith(".md")]
            
            for file in changelog_files:
                try:
                    file_path = os.path.join(output_dir, file)
                    os.remove(file_path)
                    removed_count += 1
                    print(f"✅ Removed: {file}")
                except Exception as e:
                    print(f"❌ Failed to remove: {file}")
            
            # Remove empty directories
            try:
                if os.path.exists(output_dir):
                    remaining_files = os.listdir(output_dir)
                    if not remaining_files:
                        shutil.rmtree(output_dir)
                        print(f"📁 Folder {output_dir} deleted (empty)")
                        
                        # Check if docs folder is also empty
                        docs_dir = os.path.dirname(output_dir)
                        if os.path.exists(docs_dir) and not os.listdir(docs_dir):
                            shutil.rmtree(docs_dir)
                            print(f"📁 Folder {docs_dir} deleted (empty)")
            except Exception as e:
                print(f"❌ Failed to delete folder: {e}")
                
        except Exception as e:
            print(f"❌ Error reading directory: {e}")
    
    if removed_count > 0:
        print(t("success.changelogRemoved", count=removed_count))
        return True
    else:
        print(t("info.noChangelogFiles"))
        return False

def translate_with_changelog(lang_codes, with_changelog=True):
    """
    Translate README with option to include CHANGELOG
    """
    if not lang_codes:
        print(t("errors.noLanguagesSelected"))
        return False
    
    valid_langs = [code for code in lang_codes if code in LANGUAGES and code != 'en']
    
    if not valid_langs:
        print(t("errors.noLanguagesSelected"))
        return False
    
    # Auto setup changelog only if with_changelog is True AND CHANGELOG file exists
    if with_changelog and has_changelog_file() and not has_changelog_section_in_readme():
        print(t("changelog.autoSettingUp"))
        add_changelog_section_to_readme()
    elif with_changelog and has_changelog_section_in_readme():
        print(t("changelog.checkingSpacing"))
        fix_existing_changelog_spacing()
    
    protected = load_protected_phrases()
    
    # Show progress mode
    mode_text = t("progress.translatingWithChangelog") if with_changelog else t("progress.translatingReadmeOnly")
    print(t("progress.startingTranslation", count=len(valid_langs), mode_text=mode_text))
    
    success_count = 0
    
    for i, lang_code in enumerate(valid_langs):
        lang_name = LANGUAGES[lang_code][0]
        progress_msg = t("progress.translatingLanguage", 
                        lang_name=lang_name, 
                        current=i+1, 
                        total=len(valid_langs))
        print(progress_msg)
        
        try:
            # Translate README first
            translate_readme(lang_code, LANGUAGES[lang_code], protected)
            
            # Translate CHANGELOG only if option is enabled AND CHANGELOG file exists
            if with_changelog and has_changelog_file():
                print(t("changelog.translating", lang_name=lang_name))
                translate_changelog(lang_code, LANGUAGES[lang_code], protected)
                print(t("progress.changelogTranslated", lang_name=lang_name))
            elif with_changelog and not has_changelog_file():
                print(t("info.noChangelogFileSkipping"))
            
            success_count += 1
            
            # Delay to avoid rate limiting
            print(t("progress.waiting", seconds=3))
            time.sleep(3)
            
        except Exception as e:
            error_msg = t("errors.translationFailed", lang_code=lang_code, error=str(e))
            print(f"❌ {error_msg}")
    
    # Update language switcher for ALL existing languages (including English)
    all_langs_for_switcher = ['en'] + valid_langs
    update_language_switcher(all_langs_for_switcher)
    
    # Show summary
    print(t("progress.completed"))
    
    mode_summary = t("success.filesSavedWithChangelog") if with_changelog else t("success.filesSavedReadmeOnly")
    print(t("progress.filesSaved", path=os.path.join(OUTPUT_DIR)))
    
    success_message = (t("success.translationCompletedWithChangelog", count=success_count) 
                      if with_changelog else 
                      t("success.translationCompletedReadmeOnly", count=success_count))
    print(success_message)
    
    return success_count > 0

# ---------------------- MAIN README TRANSLATION FUNCTION ----------------------
def translate_readme(lang_code, lang_info, protected):
    lang_name, translate_code, intro_text = lang_info
    
    # Special filename format for jp, zh, kr
    if lang_code == "jp":
        dest_path = os.path.join(OUTPUT_DIR, "README-JP.md")
    elif lang_code == "zh":
        dest_path = os.path.join(OUTPUT_DIR, "README-ZH.md")
    elif lang_code == "kr":
        dest_path = os.path.join(OUTPUT_DIR, "README-KR.md")
    else:
        dest_path = os.path.join(OUTPUT_DIR, f"README-{lang_code.upper()}.md")

    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        src_text = f.read()

    parts = re.split(r'\n-{3,}\n', src_text, 1)
    if len(parts) > 1:
        src_header, src_body = parts[0], parts[1]
    else:
        # Jika tidak ada pembatas '---', cari '# JudulUtama' atau baris pertama
        match = re.search(r'^(#\s+[^\n]+(?:\n(?:\[!\[|!\[|<a)[^\n]*)*)', src_text, re.MULTILINE)
        if match:
            split_pos = match.end()
            src_header = src_text[:split_pos].strip()
            src_body = src_text[split_pos:].lstrip()
        else:
            # Fallback jika tidak ditemukan (# Judul)
            lines = src_text.split('\n', 1)
            src_header = lines[0] if len(lines) > 0 else src_text
            src_body = lines[1] if len(lines) > 1 else ""

    # Clean existing language switcher from header
    cleaned_header = re.sub(r'^\s*>\s*🌐.*$', '', src_header, flags=re.MULTILINE).strip()
    
    # Get all existing languages to create language switcher
    existing_langs = get_existing_translated_languages()
    
    # Create language switcher for this language
    links = ["[English](../../README.md)"]
    for code in existing_langs:
        if code != lang_code:
            name = LANGUAGES[code][0]
            # Special filename format for links
            if code == "jp":
                links.append(f"[{name}](README-JP.md)")
            elif code == "zh":
                links.append(f"[{name}](README-ZH.md)")
            elif code == "kr":
                links.append(f"[{name}](README-KR.md)")
            else:
                links.append(f"[{name}](README-{code.upper()}.md)")
    
    links_text = " | ".join(links)
    final_header = f"{cleaned_header}\n\n> {intro_text} {links_text}"

    print(t("translating_readme", lang_name=lang_name, lang_code=lang_code.upper()))

    body_lines = src_body.split("\n")
    translated_lines = []
    in_code_block = False
    in_example_block = False

    for i, line in enumerate(body_lines):
        # Detect code blocks
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            translated_lines.append(line)
            continue

        # Detect example sections (Before/After)
        if re.match(r'^\*\*Before:\*\*$', line, re.IGNORECASE):
            in_example_block = True
            # Translate "Before:" according to target language
            translated_before = translate_text("Before:", translate_code)
            translated_lines.append(f"**{translated_before}**")
            continue
        
        if re.match(r'^\*\*After \(Translated\):\*\*$', line, re.IGNORECASE):
            in_example_block = True
            # Translate "After (Translated):" according to target language
            translated_after = translate_text("After (Translated):", translate_code)
            translated_lines.append(f"**{translated_after}**")
            continue

        # If in code block or example, don't translate code content
        if in_code_block or in_example_block:
            translated_lines.append(line)
            # Reset example block status if finding empty line after example
            if in_example_block and not line.strip():
                in_example_block = False
            continue

        # Detect structural elements (empty lines, etc)
        is_structural = (re.match(r"^\s*\|?[-:|\s]+\|?\s*$", line) or 
                        not line.strip())
        if is_structural:
            translated_lines.append(line)
            continue

        temp_line = line
        placeholders = {}
        counter = 0

        def protect(pattern, text, flags=0):
            nonlocal counter
            def repl(m):
                nonlocal counter
                key = f"__p{counter}__"
                placeholders[key] = m.group(0)
                counter += 1
                return key
            return re.sub(pattern, repl, text, flags=flags)

        # Protection for all important patterns
        if is_protect_enabled():
            for p in protected["protected_phrases"]:
                temp_line = protect(p, temp_line)

        # Additional protection for important components
        temp_line = protect(r"\[.*?\]\(https?://[^\)]+\)", temp_line)  # Markdown links with URL
        temp_line = protect(r"\[.*?\]\(mailto:[^\)]+\)", temp_line)     # Email links
        temp_line = protect(r"https?://[^\s\)]+", temp_line)           # URL standalone
        temp_line = protect(r"MIT\s+License", temp_line, re.IGNORECASE)  # MIT License
        temp_line = protect(r"\(LICENSE\)", temp_line)                   # (LICENSE)
        temp_line = protect(r"\(\.\./\.\./LICENSE\)", temp_line)         # (../../LICENSE)
        temp_line = protect(r"`[^`]+`", temp_line)                       # Inline code
        temp_line = protect(r"`auto-translate-readmes\.run`", temp_line) # Command ID
        
        # Special protection for version and operating systems
        temp_line = protect(r"\*\*1\.85\.0\*\*", temp_line)             # Specific version 1.85.0
        temp_line = protect(r"\*\*Windows\*\*", temp_line)              # Windows
        temp_line = protect(r"\*\*macOS\*\*", temp_line)                # macOS
        temp_line = protect(r"\*\*Linux\*\*", temp_line)                # Linux
        
        # Translate text
        translated = translate_text(temp_line, translate_code)

        # Restore placeholders to original text
        for key, val in placeholders.items():
            translated = translated.replace(key, val)

        translated_lines.append(translated)

    translated_body = "\n".join(translated_lines)
    
    # --- GENERIC FIXES ---
    # 1. Fix bullet points
    translated_body = re.sub(r'^-(?=\w)', '- ', translated_body, flags=re.MULTILINE)
    
    # 2. Fix non-breaking space
    translated_body = translated_body.replace('\xa0', ' ')
    
    # 3. FIX: Fix colon formatting WITHOUT breaking bold text
    translated_body = re.sub(
        r'(\w+)\s*:\s*(\*\*(?!.*\*\*:\*\*))',
        r'\1 : \2',
        translated_body
    )
    
    # 4. MAIN FIX: Fix extra parenthesis
    translated_body = re.sub(
        r'(\[.*?\]\([^)]+\)\.)\)',
        r'\1',
        translated_body
    )
    
    # 5. Fix bold format
    translated_body = re.sub(r'(\*\*)(\d+\.\d+\.\d+)(\*\*)', r'**\2**', translated_body)
    
    # 6. ADDITIONAL FIX: Fix bold text broken by colon formatting
    translated_body = re.sub(
        r'\*\*(\w+)\s*:\s*\*\*',
        r'**\1:**',
        translated_body
    )
    
    # Ensure LICENSE link remains consistent
    final_text = f"{final_header}\n\n---\n{translated_body}"
    final_text = re.sub(r"\(LICENSE\)", "(../../LICENSE)", final_text)
    final_text = re.sub(r"__p\d+__", "", final_text)
    # 🔽 Tambahkan baris ini agar tabel diterjemahkan otomatis
    # Di fungsi translate_readme, tambahkan error handling untuk translate_markdown_table
    try:
        final_text = translate_markdown_table(final_text, lang_code)
    except Exception as e:
        print(f"Warning: Table translation failed: {e}")
        # Continue with untranslated tables

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(t("readme_created", path=dest_path))

    # After successfully translating README, handle CHANGELOG
    if has_changelog_file() and has_changelog_section_in_readme():
        # Translate CHANGELOG
        translate_changelog(lang_code, lang_info, protected)
        
        # Update CHANGELOG link in translated README
        update_changelog_links_in_readme(lang_code, lang_info)

def translate_markdown_table(content: str, lang_code: str) -> str:
    """
    Automatically detect markdown tables and translate header + specific columns.
    Keeps Command ID and Default Shortcut columns untranslated.
    """
    table_pattern = re.compile(
        r"(\|[^\n]+\|\s*\n\|(?:\s*:?[-]+:?[\s|]+)+\n(?:\|[^\n]+\n?)+)",
        re.MULTILINE
    )

    tables = table_pattern.findall(content)
    if not tables:
        return content

    for table in tables:
        lines = [line.strip() for line in table.strip().split("\n") if line.strip()]
        if len(lines) < 3:
            continue

        header = [h.strip() for h in lines[0].split("|") if h.strip()]
        separator = lines[1]
        rows = lines[2:]

        # Cek apakah tabel adalah tabel Commands (dari README)
        if not any("Command Name" in h for h in header):
            continue

        # Tentukan kolom mana yang diterjemahkan
        try:
            idx_command_name = header.index("Command Name")
        except ValueError:
            idx_command_name = None
        try:
            idx_desc = header.index("Description")
        except ValueError:
            idx_desc = None

        # Terjemahkan header seluruhnya
        translated_header = []
        for h in header:
            try:
                translated_header.append(GoogleTranslator(source="en", target=lang_code).translate(h))
            except Exception:
                translated_header.append(h)

        # Terjemahkan baris data
        translated_rows = []
        for row in rows:
            cols = [c.strip() for c in row.split("|") if c.strip()]
            new_cols = []
            for i, col in enumerate(cols):
                if i in (idx_command_name, idx_desc):
                    try:
                        new_cols.append(GoogleTranslator(source="en", target=lang_code).translate(col))
                    except Exception:
                        new_cols.append(col)
                else:
                    new_cols.append(col)
            translated_rows.append("| " + " | ".join(new_cols) + " |")

        # Gabungkan ulang tabel
        translated_table = (
            "| " + " | ".join(translated_header) + " |\n" +
            separator + "\n" +
            "\n".join(translated_rows)
        )

        # Ganti di konten asli
        content = content.replace(table, translated_table)

    return content

# ---------------------- INTERACTIVE MENU ----------------------
def repair_translations():
    """Repair language switchers positioning, remove duplicates, and detect translation failures."""
    print(Fore.CYAN + "\n[+] Starting Translation Repair Tool...")
    
    # 1. Update/fix all switchers globally
    print(Fore.YELLOW + "1. Cleaning up duplicate switchers and fixing their positions in all READMEs...")
    update_language_switcher()
    
    # 2. Detect translation failures
    print(Fore.YELLOW + "\n2. Scanning translated documents for failures (API errors / unchanged English)...")
    existing_langs = get_existing_translated_languages()
    failed_langs = []
    
    if not os.path.exists(SOURCE_FILE):
        print(Fore.RED + "   Error: Root README.md not found.")
        return False
        
    try:
        with open(SOURCE_FILE, "r", encoding="utf-8") as f:
            src_content = f.read()
    except Exception as e:
        print(Fore.RED + f"   Failed to read source file: {e}")
        return False
        
    for lang_code in existing_langs:
        if lang_code == "jp":
            readme_path = os.path.join(OUTPUT_DIR, "README-JP.md")
        elif lang_code == "zh":
            readme_path = os.path.join(OUTPUT_DIR, "README-ZH.md")
        elif lang_code == "kr":
            readme_path = os.path.join(OUTPUT_DIR, "README-KR.md")
        else:
            readme_path = os.path.join(OUTPUT_DIR, f"README-{lang_code.upper()}.md")
            
        if os.path.exists(readme_path):
            try:
                with open(readme_path, "r", encoding="utf-8") as f:
                    trans_content = f.read()
                
                # Strip markdown syntax and compare structural words
                def strip_md(text):
                    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
                    text = re.sub(r'\[.*?\]\(.*?\)', '', text)
                    text = re.sub(r'\W+', ' ', text).lower()
                    return text
                    
                src_words = strip_md(src_content).split()
                tr_words = strip_md(trans_content).split()
                
                if src_words and tr_words:
                    common_words = set(src_words).intersection(set(tr_words))
                    overlap_ratio = len(common_words) / len(set(src_words)) if set(src_words) else 0
                    
                    if overlap_ratio > 0.65:
                        print(Fore.RED + f"   - [FAIL] {LANGUAGES[lang_code][0]} ({lang_code}): High English overlap ({int(overlap_ratio*100)}%)")
                        failed_langs.append(lang_code)
                    else:
                        print(Fore.GREEN + f"   - [OK] {LANGUAGES[lang_code][0]} ({lang_code}) looks properly translated.")
            except Exception as e:
                print(Fore.RED + f"   - [ERROR] {lang_code}: Could not scan ({e})")
                
    if failed_langs:
        print(Fore.CYAN + f"\n3. Re-translating {len(failed_langs)} failed files: {', '.join(failed_langs)}")
        translate_with_changelog(failed_langs, with_changelog=has_changelog_file())
        print(Fore.GREEN + "\nRepair completed! Missing translations have been fixed.")
    else:
        print(Fore.GREEN + "\nNo failed translations detected. All files are clean and fully repaired!")
        
    return True

def ask_target_directory():
    target_path = input(Fore.CYAN + "\nEnter project folder or README path\n(Type 'root' to use current directory, or leave empty to cancel): " + Fore.WHITE).strip()
    
    if not target_path:
        print(Fore.YELLOW + "Action cancelled. Returning to main menu...\n")
        return False
        
    if target_path.lower() == 'root':
        print(Fore.GREEN + f"Using current root directory: {os.getcwd()}\n")
        return True
        
    target_path = target_path.strip('"\'')
    if os.path.isfile(target_path):
        target_dir = os.path.dirname(target_path)
    elif os.path.isdir(target_path):
        target_dir = target_path
    else:
        print(Fore.RED + "Invalid path. Returning to main menu...\n")
        return False
        
    try:
        os.chdir(target_dir)
        print(Fore.GREEN + f"Target directory set to: {os.getcwd()}\n")
    except Exception as e:
        print(Fore.RED + f"Failed to change directory: {e}\n")
        return False
        
    return True

def interactive_menu():
    console = Console(width=90)

    while True:
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')

        # Load configuration from .path_config
        config_file = ".path_config"
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            target_dir = config.get('target_dir', os.getcwd())
            output_base_dir = config.get('output_base_dir')
        else:
            target_dir = os.getcwd()
            output_base_dir = None

        # Check project status
        readme_exists = os.path.isfile(SOURCE_FILE)
        changelog_exists = os.path.isfile(CHANGELOG_FILE)

        # Header Panel
        header_text = Text()
        header_text.append("🌍 MultiDoc Translator - CLI Menu\n", style="bold green")
        header_text.append("Developer: Fatony Ahmad Fauzi", style="green")
        console.print(create_square_panel(header_text, align_center=True, expand=True))

        # Current Status Panel
        status_text = Text()
        status_text.append("✅ ", style="bold green")
        status_text.append(f"Current project path: {target_dir}\n", style="white")
        output_display = output_base_dir if output_base_dir else 'Not set'
        status_text.append("📁 ", style="yellow")
        status_text.append(f"Output Directory: {output_display}", style="white")
        console.print(create_square_panel(status_text, title="Current Status"))

        # Source Files Panel
        files_text = Text()
        files_text.append("✅ " if readme_exists else "❌ ", style="bold green" if readme_exists else "red")
        files_text.append(f"README.md: {'AVAILABLE' if readme_exists else 'NOT FOUND'}\n", style="white")
        files_text.append("✅ " if changelog_exists else "❌ ", style="bold green" if changelog_exists else "red")
        files_text.append(f"CHANGELOG.md: {'AVAILABLE' if changelog_exists else 'NOT FOUND'}", style="white")
        console.print(create_square_panel(files_text, title="Source Files"))

        # Warning message if output directory not set
        if not output_base_dir:
            warning_text = Text()
            warning_text.append("⚠️ ", style="bold yellow")
            warning_text.append("Output directory not set!\n", style="bold yellow")
            warning_text.append("Please use option [7] Setup Paths first.", style="yellow")
            console.print(create_square_panel(warning_text, title="Warning"))

        # Main Menu Panel
        menu_text = Text()
        menu_text.append("[1] Translate\n", style="green")
        menu_text.append("[2] Remove Translated Languages\n", style="green")
        menu_text.append("[3] Protection Settings (Phrases)\n", style="green")
        menu_text.append("[4] Auto Setup Changelog Section\n", style="green")
        menu_text.append("[5] Detect GitHub URL\n", style="green")
        menu_text.append("[6] Repair Translations (Fix Duplicates & Failures)\n", style="red")
        menu_text.append("[7] Setup Paths\n", style="green")
        menu_text.append("[0] Exit", style="white")
        console.print(create_square_panel(menu_text, title="Main Menu"))

        # Get user input
        choice = console.input("\n[bold yellow][+] Select option: [/bold yellow]").strip()
        if choice == '1':
            # Show translate submenu
            os.system('cls' if os.name == 'nt' else 'clear')
            translation_status_table, has_missing_translations = create_translation_status_table(output_base_dir, target_dir)
            console.print(
                create_square_panel(
                    translation_status_table,
                    title="Translation Status"
                )
            )
            if has_missing_translations:
                fallback_text = Text()
                fallback_text.append("⚠️ ", style="bold yellow")
                fallback_text.append("Some translations are still missing.\n", style="bold yellow")
                fallback_text.append(
                    "Use [1], [2], or [3] below to generate the missing README / CHANGELOG files.",
                    style="yellow"
                )
                console.print(create_square_panel(fallback_text, title="Fallback Info"))

            translate_menu = Text()
            translate_menu.append("[1] Translate README & CHANGELOG\n", style="green")
            translate_menu.append("[2] Translate README Only\n", style="green")
            translate_menu.append("[3] Translate CHANGELOG Only\n", style="green")
            translate_menu.append("[0] Back", style="white")
            console.print(create_square_panel(translate_menu, title="Translation Options"))

            trans_choice = console.input("\n[bold yellow][+] Select option: [/bold yellow]").strip()
            
            if trans_choice == '1':
                # Translate README & CHANGELOG
                if not ask_target_directory():
                    input("\nPress Enter to continue...")
                    continue
                print(Fore.CYAN + "Supported: pl, zh, jp, de, fr, es, ru, pt, id, kr")
                langs = input(Fore.CYAN + "Enter language codes (comma-separated, or 'all'): " + Fore.WHITE).strip()
                if langs.lower() == 'all':
                    langs_list = list(LANGUAGES.keys())
                else:
                    langs_list = [l.strip() for l in langs.split(',') if l.strip() in LANGUAGES]
                if langs_list:
                    translate_with_changelog(langs_list, with_changelog=True)
                else:
                    print(Fore.RED + "Invalid languages.")
                input("\nPress Enter to continue...")
                
            elif trans_choice == '2':
                # Translate README Only
                if not ask_target_directory():
                    input("\nPress Enter to continue...")
                    continue
                print(Fore.CYAN + "Supported: pl, zh, jp, de, fr, es, ru, pt, id, kr")
                langs = input(Fore.CYAN + "Enter language codes (comma-separated, or 'all'): " + Fore.WHITE).strip()
                if langs.lower() == 'all':
                    langs_list = list(LANGUAGES.keys())
                else:
                    langs_list = [l.strip() for l in langs.split(',') if l.strip() in LANGUAGES]
                if langs_list:
                    translate_with_changelog(langs_list, with_changelog=False)
                else:
                    print(Fore.RED + "Invalid languages.")
                input("\nPress Enter to continue...")
                
            elif trans_choice == '3':
                # Translate CHANGELOG Only
                if not ask_target_directory():
                    input("\nPress Enter to continue...")
                    continue
                print(Fore.CYAN + "Supported: pl, zh, jp, de, fr, es, ru, pt, id, kr")
                langs = input(Fore.CYAN + "Enter language codes (comma-separated, or 'all'): " + Fore.WHITE).strip()
                if langs.lower() == 'all':
                    langs_list = list(LANGUAGES.keys())
                else:
                    langs_list = [l.strip() for l in langs.split(',') if l.strip() in LANGUAGES]
                if langs_list:
                    translate_changelog_only(langs_list)
                else:
                    print(Fore.RED + "Invalid languages.")
                input("\nPress Enter to continue...")
            
        elif choice == '2':
            # Remove Translated Languages (was option 4)
            if not ask_target_directory():
                input("\nPress Enter to continue...")
                continue
            remove_menu = Text()
            remove_menu.append("[1] Remove Specific Languages\n", style="green")
            remove_menu.append("[2] Remove ALL Translated Languages\n", style="red")
            remove_menu.append("[0] Back", style="white")
            console.print(create_square_panel(remove_menu, title="Remove Translations"))

            sub_choice = console.input("\n[bold yellow][+] Select option: [/bold yellow]").strip()
            if sub_choice == '1':
                langs = input(Fore.CYAN + "Enter language codes to remove: " + Fore.WHITE).strip()
                lang_codes = [l.strip() for l in langs.split(',')]
                removed = remove_language_files(lang_codes)
                if removed:
                    print(Fore.GREEN + f"Removed: {', '.join(removed)}")
            elif sub_choice == '2':
                remove_all_language_files()
                print(Fore.GREEN + "All translated languages removed.")
            input("\nPress Enter to continue...")
            
        elif choice == '3':
            # Protection Settings (was option 5)
            if not ask_target_directory():
                input("\nPress Enter to continue...")
                continue
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                protected = load_protected_phrases()
                status = "ACTIVE" if is_protect_enabled() else "INACTIVE"
                protection_text = Text()
                protection_text.append("Status: ", style="white")
                protection_text.append(
                    f"{status}\n",
                    style="bold green" if is_protect_enabled() else "bold red"
                )
                protection_text.append("[1] Toggle Protection Status\n", style="green")
                protection_text.append("[2] Add Protected Phrase\n", style="green")
                protection_text.append("[3] Remove Protected Phrase\n", style="green")
                protection_text.append("[4] List Protected Phrases\n", style="green")
                protection_text.append("[5] Reset to Default\n", style="yellow")
                protection_text.append("[0] Back", style="white")
                console.print(create_square_panel(protection_text, title="Protection Settings"))
                p_choice = console.input("\n[bold yellow][+] Select option: [/bold yellow]").strip()
                
                if p_choice == '1':
                    set_protect_status(not is_protect_enabled())
                elif p_choice == '2':
                    phrase = input(Fore.CYAN + "Enter phrase to protect (leave empty to cancel): " + Fore.WHITE).strip()
                    if phrase:
                        protected['protected_phrases'].append(phrase)
                        save_protected_phrases(protected)
                        print(Fore.GREEN + f"Added: {phrase}")
                        time.sleep(1)
                elif p_choice == '3':
                    phrase = input(Fore.CYAN + "Enter phrase to remove (leave empty to cancel): " + Fore.WHITE).strip()
                    if phrase:
                        if phrase in protected['protected_phrases']:
                            protected['protected_phrases'].remove(phrase)
                            save_protected_phrases(protected)
                            print(Fore.GREEN + f"Removed: {phrase}")
                        else:
                            print(Fore.RED + "Phrase not found.")
                        time.sleep(1)
                elif p_choice == '4':
                    print("\nProtected Phrases:")
                    for p in protected['protected_phrases']:
                        print(f"- {p}")
                    input("\nPress Enter to continue...")
                elif p_choice == '5':
                    save_protected_phrases(DEFAULT_PROTECTED)
                    print(Fore.GREEN + "Reset to defaults.")
                    time.sleep(1)
                elif p_choice == '0':
                    break

        elif choice == '4':
            # Auto Setup Changelog Section (was option 6)
            if not ask_target_directory():
                input("\nPress Enter to continue...")
                continue
            if add_changelog_section_to_readme():
                print(Fore.GREEN + "Changelog setup completed.")
            else:
                print(Fore.RED + "Changelog setup failed.")
            input("\nPress Enter to continue...")
            
        elif choice == '5':
            # Detect GitHub URL (was option 7)
            if not ask_target_directory():
                input("\nPress Enter to continue...")
                continue
            detect_github_url()
            input("\nPress Enter to continue...")
            
        elif choice == '6':
            # Repair Translations (was option 8)
            if not ask_target_directory():
                input("\nPress Enter to continue...")
                continue
            repair_translations()
            input("\nPress Enter to continue...")
            
        elif choice == '7':
            # Setup Paths (NEW)
            setup_paths_menu()
            input("\nPress Enter to continue...")
            
        elif choice == '0':
            print(Fore.GREEN + "Exiting...")
            break

# ---------------------- MAIN PROGRAM ----------------------
def main():
    if len(sys.argv) == 1:
        interactive_menu()
        return

    display_lang = "en"
    
    # Check --display parameter
    for i, arg in enumerate(sys.argv):
        if arg == "--display" and i + 1 < len(sys.argv):
            display_lang = sys.argv[i + 1]
            break
        elif arg.startswith("--display="):
            display_lang = arg.split("=")[1]
            break
    
    help_lang = display_lang if display_lang in DISPLAY_LANGUAGES else "en"
    
    parser = argparse.ArgumentParser(
        description=DISPLAY_LANGUAGES[help_lang]["help_description"],
        epilog=DISPLAY_LANGUAGES[help_lang]["help_epilog"],
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Existing arguments
    parser.add_argument("--lang", help=DISPLAY_LANGUAGES[help_lang]["help_lang"])
    parser.add_argument("--remove-lang", help=DISPLAY_LANGUAGES[help_lang]["help_remove_lang"])
    parser.add_argument("--remove-all-lang", action="store_true", help=DISPLAY_LANGUAGES[help_lang]["help_remove_all_lang"])
    parser.add_argument("--add-protect", help=DISPLAY_LANGUAGES[help_lang]["help_add_protect"])
    parser.add_argument("--remove-protect", help=DISPLAY_LANGUAGES[help_lang]["help_remove_protect"])
    parser.add_argument("--list-protect", action="store_true", help=DISPLAY_LANGUAGES[help_lang]["help_list_protect"])
    parser.add_argument("--init-protect", action="store_true", help=DISPLAY_LANGUAGES[help_lang]["help_init_protect"])
    parser.add_argument("--enable-protect", action="store_true", help=DISPLAY_LANGUAGES[help_lang]["help_enable_protect"])
    parser.add_argument("--disable-protect", action="store_true", help=DISPLAY_LANGUAGES[help_lang]["help_disable_protect"])
    parser.add_argument("--status-protect", action="store_true", help=DISPLAY_LANGUAGES[help_lang]["help_status_protect"])
    parser.add_argument("--translate-changelog", help=DISPLAY_LANGUAGES[help_lang]["help_translate_changelog"])
    parser.add_argument("--auto-setup-changelog", action="store_true", help=DISPLAY_LANGUAGES[help_lang]["help_auto_setup_changelog"])
    parser.add_argument("--detect-github-url", action="store_true", help=DISPLAY_LANGUAGES[help_lang]["help_detect_github_url"])
    parser.add_argument("--display", help=DISPLAY_LANGUAGES[help_lang]["help_display"], default="en", choices=["en", "id", "jp", "de", "es", "fr", "kr", "pl", "pt", "ru", "zh"])
    
    # NEW: CHANGELOG Only arguments
    parser.add_argument("--generate-changelog-only", help=DISPLAY_LANGUAGES[help_lang]["help_generate_changelog_only"])
    parser.add_argument("--remove-changelog-selected", help=DISPLAY_LANGUAGES[help_lang]["help_remove_changelog_selected"])
    parser.add_argument("--remove-changelog-only", action="store_true", help=DISPLAY_LANGUAGES[help_lang]["help_remove_changelog_only"])
    parser.add_argument("--with-changelog", action="store_true", default=True, help=DISPLAY_LANGUAGES[help_lang]["help_with_changelog"])
    parser.add_argument("--without-changelog", action="store_true", help="Translate only README files (no CHANGELOG)")
    
    args = parser.parse_args()

    # Set display language for notifications
    set_display_language(args.display)

    protected = load_protected_phrases()

    # Handle GitHub URL detection commands
    if args.detect_github_url:
        detect_github_url()
        return

    # Handle protection commands (existing)
    if args.init_protect:
        save_protected_phrases(DEFAULT_PROTECTED)
        print(t("protection_reset"))
        return
    if args.add_protect:
        protected["protected_phrases"].append(args.add_protect)
        save_protected_phrases(protected)
        print(t("phrase_added", phrase=args.add_protect))
        return
    if args.remove_protect:
        protected["protected_phrases"] = [p for p in protected["protected_phrases"] if p != args.remove_protect]
        save_protected_phrases(protected)
        print(t("phrase_removed", phrase=args.remove_protect))
        return
    if args.list_protect:
        print(t("protected_phrases_list"))
        for p in protected["protected_phrases"]:
            print(f"- {p}")
        return
    if args.enable_protect:
        set_protect_status(True)
        print(t("protection_enabled"))
        return
    if args.disable_protect:
        set_protect_status(False)
        print(t("protection_disabled"))
        return
    if args.status_protect:
        status = "ACTIVE ✅" if is_protect_enabled() else "INACTIVE ❌"
        print(t("protection_status", status=status))
        return

    # Handle NEW CHANGELOG Only commands
    if args.generate_changelog_only:
        if args.generate_changelog_only.lower() == 'all':
            lang_codes = list(LANGUAGES.keys())
        else:
            lang_codes = [lang.strip().lower() for lang in args.generate_changelog_only.split(',')]
            lang_codes = [code for code in lang_codes if code in LANGUAGES]
        
        if not lang_codes:
            print(t("no_valid_language"))
            return
        
        generate_changelog_only(lang_codes)
        return
    
    if args.remove_changelog_selected:
        lang_codes = [lang.strip().lower() for lang in args.remove_changelog_selected.split(',')]
        lang_codes = [code for code in lang_codes if code in LANGUAGES]
        
        if not lang_codes:
            print(t("no_valid_language"))
            return
        
        remove_changelog_selected(lang_codes)
        return
    
    if args.remove_changelog_only:
        remove_changelog_only()
        return

    # Handle existing CHANGELOG commands
    if args.auto_setup_changelog:
        if add_changelog_section_to_readme():
            print(t("changelog_setup_completed"))
        else:
            print(t("changelog_setup_failed"))
        return
    
    if args.translate_changelog:
        if not has_changelog_file():
            print(t("no_changelog_file"))
            return
        
        if args.translate_changelog.lower() == 'all':
            lang_codes = None
        else:
            lang_codes = [lang.strip().lower() for lang in args.translate_changelog.split(',')]
            lang_codes = [code for code in lang_codes if code in LANGUAGES]
            
            if not lang_codes:
                print(t("no_valid_language"))
                return
        
        translate_changelog_only(lang_codes)
        return

    # Handle language file removal (existing)
    if args.remove_lang:
        lang_codes = [lang.strip() for lang in args.remove_lang.split(',')]
        removed = remove_language_files(lang_codes)
        if removed:
            print(t("languages_removed", langs=', '.join(removed)))
        return
    
    if args.remove_all_lang:
        remove_all_language_files()
        print(t("all_languages_removed"))
        return

    # Run translate with CHANGELOG option
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Determine CHANGELOG option
    with_changelog = args.with_changelog and not args.without_changelog
    
    # Auto setup changelog only if with_changelog is True AND CHANGELOG file exists
    if with_changelog and has_changelog_file() and not has_changelog_section_in_readme():
        print(t("auto_setup_changelog"))
        add_changelog_section_to_readme()
    elif with_changelog and has_changelog_section_in_readme():
        print(t("checking_changelog_spacing"))
        fix_existing_changelog_spacing()
    
    if args.lang:
        # Parse multiple languages if comma-separated
        lang_codes = [lang.strip() for lang in args.lang.split(',')]
        valid_langs = []
        
        for lang_code in lang_codes:
            if lang_code in LANGUAGES:
                valid_langs.append(lang_code)
            else:
                print(t("language_not_recognized", code=lang_code))
        
        if valid_langs:
            # Translate selected languages with CHANGELOG option
            translate_with_changelog(valid_langs, with_changelog)
        else:
            print(t("no_valid_language"))
    else:
        # Translate all languages with CHANGELOG option
        all_langs = list(LANGUAGES.keys())
        translate_with_changelog(all_langs, with_changelog)
    
    print("\n" + t("all_translated") + "\n")

if __name__ == "__main__":
    main()
