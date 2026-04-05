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
import types
import functools
import webbrowser
import urllib.request
import urllib.parse
import requests
from deep_translator import GoogleTranslator
from tqdm import tqdm
import colorama
from colorama import Fore, Style, init

init(autoreset=True)

DEBUG_MODE = False
DEBUG_LOGS = []
DEBUG_MAX_LINES = 1000

# Simple ANSI constants and helpers to mimic pixiv style coloring
class Ansi:
    CYAN = Fore.CYAN
    GREEN = Fore.GREEN
    RESET = Style.RESET_ALL


def colorize(text: str, color_code: str, color_on: bool):
    if not color_on:
        return text
    return f"{color_code}{text}{Ansi.RESET}"


def debug_print(msg: str, color_on: bool = True):
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{stamp} | {msg}"
    DEBUG_LOGS.append(log_message)
    if len(DEBUG_LOGS) > DEBUG_MAX_LINES:
        del DEBUG_LOGS[:-DEBUG_MAX_LINES]

    if os.getenv("DEBUG", "0") in ("1", "true", "True") or DEBUG_MODE:
        if color_on:
            print(Fore.YELLOW + "[DEBUG] " + log_message + Style.RESET_ALL)
        else:
            print("[DEBUG] " + log_message)


def _copy_to_clipboard(text: str) -> bool:
    if not text:
        return False
    try:
        if sys.platform == "win32":
            import subprocess
            subprocess.run(["clip"], input=text, text=True, check=True)
            return True
        if sys.platform == "darwin":
            import subprocess
            subprocess.run(["pbcopy"], input=text, text=True, check=True)
            return True
        import subprocess
        if shutil.which("xclip"):
            subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True, check=True)
            return True
        if shutil.which("xsel"):
            subprocess.run(["xsel", "--clipboard", "--input"], input=text, text=True, check=True)
            return True
    except Exception:
        return False
    return False


def open_debug_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n{Fore.CYAN}Debug{Style.RESET_ALL}\n")
        if DEBUG_LOGS:
            for line in DEBUG_LOGS:
                print(line)
        else:
            print(f"{Fore.LIGHTBLACK_EX}(No debug logs yet){Style.RESET_ALL}")

        print()
        print(f"{Fore.GREEN}[1] Copy debug{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[2] Clear debug{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}[0] Exit{Style.RESET_ALL}")

        debug_choice = input(f"\n{Fore.YELLOW}[+] Select option: {Fore.WHITE}").strip()
        if debug_choice == '1':
            copied = _copy_to_clipboard("\n".join(DEBUG_LOGS))
            if copied:
                debug_print("Debug copied.", color_on=False)
            else:
                debug_print("Failed to copy debug (clipboard tool unavailable).", color_on=False)
        elif debug_choice == '2':
            DEBUG_LOGS.clear()
            debug_print("Debug logs cleared.", color_on=False)
        elif debug_choice == '0':
            break

# Fix emoji encoding for Windows
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SOURCE_FILE = "README.md"
CHANGELOG_FILE = "CHANGELOG.md"
PACKAGE_JSON = "package.json"
OUTPUT_DIR = "docs/lang"
PROTECTED_FILE = "protected_phrases.json"
PROTECT_STATUS_FILE = ".protect_status"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PATH_CONFIG_FILE = os.path.join(PROJECT_ROOT, ".path_config")
LANG_CONFIG_FILE = os.path.join(PROJECT_ROOT, ".lang_config")

def check_internet_connection(test_url="https://www.google.com", timeout=5):
    """Check if internet connection is available by contacting a reliable URL."""
    try:
        urllib.request.urlopen(test_url, timeout=timeout)
        return True
    except Exception:
        return False


def _check_internet_blocking(color_on: bool):
    """
    Fungsi ringan untuk menahan aliran CLI program agar tidak masuk menu
    utama sebelum ada koneksi internet (seperti Loading Screen GUI).
    """
    def is_connected():
        try:
            requests.get("https://raw.githubusercontent.com", timeout=3, stream=False)
            return True
        except Exception:
            return False

    # Match pixiv_login visual exactly
    print(Fore.CYAN + "[i] Checking internet connection..." + Style.RESET_ALL)

    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    idx = 0

    while True:
        sys.stdout.write(f"\r{Fore.WHITE}Menunggu koneksi internet... {colorize(frames[idx], Ansi.CYAN, color_on)}{Style.RESET_ALL}")
        sys.stdout.flush()

        if is_connected():
            # Clear line and print success in Pixiv style
            sys.stdout.write("\r" + " " * 80 + "\r")
            sys.stdout.write(Fore.GREEN + "[+] Connected" + Style.RESET_ALL + "\n")
            sys.stdout.flush()
            time.sleep(0.7)
            break

        idx = (idx + 1) % len(frames)
        time.sleep(0.1)


def ensure_internet_connection(retry_interval=3, max_attempts=None):
    """Ensure internet connection is active before showing the menu."""
    spinner = ['|', '/', '-', '\\']
    attempt = 0

    while True:
        attempt += 1
        print(Fore.CYAN + "🌍 Checking internet connection... " + Style.RESET_ALL, end='')

        connected = False
        for i in range(4):
            sys.stdout.write(spinner[i] + '\r')
            sys.stdout.flush()
            time.sleep(0.2)
            if check_internet_connection():
                connected = True
                break

        if connected:
            print(Fore.GREEN + "✅ Internet connection OK." + Style.RESET_ALL)
            return True

        print(Fore.RED + "❌ No internet connection detected." + Style.RESET_ALL)
        if max_attempts and attempt >= max_attempts:
            print(Fore.YELLOW + "Max attempts reached. Stopping internet connect retries." + Style.RESET_ALL)
            return False

        answer = input(Fore.CYAN + "Retry internet check? [Y/n]: " + Fore.WHITE).strip().lower()
        if answer in ('n', 'no'):
            print(Fore.YELLOW + "Internet connection is required for translation/repair operations." + Style.RESET_ALL)
            return False

        print(Fore.BLUE + f"Retrying in {retry_interval} seconds..." + Style.RESET_ALL)
        time.sleep(retry_interval)

# ---------------------- DISPLAY LANGUAGE SETTINGS ----------------------
DISPLAY_LANGUAGES = {
    "en": {
        "ui.codeLanguage": "Code/Language",
        "ui.changelogTitle": "CHANGELOG",
        "ui.warningDifferentProject": "⚠️  WARNING: Output Directory is in a different project!",
        "ui.pathOutsideProject": "(Path is outside the current project folder)",
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
        "no_internet": "❌ No internet connection detected. Please connect to the internet and try again.",
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
        "changelog.affectsSelected": "Affects only selected languages: {count} languages",
        "changelog.generateWith": "📋 Generate with CHANGELOG",
        "changelog.checkedDescription": "When checked: Translates both README and CHANGELOG files",
        "changelog.uncheckedDescription": "When unchecked: Translates only README files",
        
        # NEW: Progress messages for CHANGELOG only
        "progress.translatingWithChangelog": "Translating README + CHANGELOG",
        "progress.translatingReadmeOnly": "Translating README only",
        "progress.translatingChangelogOnly": "Translating CHANGELOG only",
        "success.filesSavedWithChangelog": "READMEs and CHANGELOGs",
        "success.filesSavedReadmeOnly": "READMEs only",
        "success.filesSavedChangelogOnly": "CHANGELOGs only",
        "success.translationCompletedWithChangelog": "✅ {count} READMEs and CHANGELOGs successfully translated!",
        "success.translationCompletedReadmeOnly": "✅ {count} READMEs successfully translated!",
        "success.translationCompletedChangelogOnly": "✅ {count} CHANGELOGs successfully translated!",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.md not found - skipping CHANGELOG translation",
        "ui.cannotTranslateBoth": "⚠️  Cannot translate README & CHANGELOG.",
        "ui.missingReadmeForBoth": "README.md is missing. Use option [2] to translate README only.",
        "ui.missingChangelogForBoth": "CHANGELOG.md is missing. Use option [3] to translate CHANGELOG only.",
        "ui.missingBothFiles": "Both README.md and CHANGELOG.md are missing.",
        "ui.cannotTranslateReadmeOnly": "⚠️  Cannot translate README only.",
        "ui.missingReadme": "README.md is missing.",
        "ui.cannotTranslateChangelogOnly": "⚠️  Cannot translate CHANGELOG only.",
        "ui.missingChangelog": "CHANGELOG.md is missing.",
        
        # NEW: Error and success messages for CHANGELOG only
        "errors.changelogGenerateFailed": "❌ CHANGELOG generation failed",
        "errors.changelogRemoveSelectedFailed": "❌ Failed to remove selected CHANGELOG files",
        "success.changelogGenerated": "✅ CHANGELOG successfully generated for {count} languages",
        "success.changelogRemovedSelected": "✅ {count} CHANGELOG files successfully removed",
        "confirmation.removeChangelogSelected": "Are you sure you want to remove CHANGELOG files for {count} selected languages? README files will not be affected.",
        
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
        "progress.barLabel": "Progress:",
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
        "debug_current": "Current",
        "ui.changeLanguage": "Change Language",
        "ui.currentLanguage": "Current language",
        "ui.languageChanged": "✅ Display language changed to {name}",
        "ui.languageSelector": "Select display language for CLI notifications",
        "ui.translate": "Translate",
        "ui.removeTranslated": "Remove Translated Languages",
        "ui.protectionSettings": "Protection Settings (Phrases)",
        "ui.autoSetupChangelog": "Auto Setup Changelog Section",
        "ui.detectGithub": "Detect GitHub URL",
        "ui.repairTranslations": "Repair Translations (Fix Duplicates & Failures)",
        "ui.setupPaths": "Setup Paths",
        "ui.exit": "Exit",
        "ui.selectOption": "Select option:",
        "ui.currentProjectPath": "Current project path",
        "ui.outputDirectory": "Output Directory",
        "ui.folderProject": "Folder Project",
        "ui.available": "AVAILABLE",
        "ui.notFound": "NOT FOUND",
        "ui.notSet": "Not set",
        "ui.developer": "Developer",
        "ui.exiting": "Exiting...",
        "ui.chooseLanguageCode": "Choose language code (empty to cancel):",
        "ui.translationStatus": "Translation Status:",
        "ui.translateBoth": "Translate README & CHANGELOG",
        "ui.translateReadme": "Translate README Only",
        "ui.translateChangelog": "Translate CHANGELOG Only",
        "ui.removeBoth": "Remove README & CHANGELOG",
        "ui.removeReadme": "Remove README Only",
        "ui.removeChangelog": "Remove CHANGELOG Only",
        "ui.back": "Back",
        "ui.missing": "MISSING",
        "ui.enterLangCodes": "Enter language codes (comma-separated, or 'all'):",
        "ui.invalidOption": "Invalid option.",
        "ui.invalidLanguages": "Invalid languages.",
        "ui.pressEnter": "Press Enter to continue...",
        "ui.status": "Status: ",
        "ui.active": "ACTIVE",
        "ui.inactive": "INACTIVE",
        "ui.protectedPhrases": "Protected Phrases:",
        "ui.noProtectedDir": "- No protected phrases configured.",
        "ui.toggleProtection": "Toggle Protection Status",
        "ui.addProtection": "Add Protected Phrase",
        "ui.removeProtection": "Remove Protected Phrase",
        "ui.resetDefault": "Reset to Default",
        "ui.enterPhraseAdd": "Enter phrase to protect (leave empty to cancel): ",
        "ui.addedPhrase": "Added: {phrase}",
        "ui.enterPhraseRemove": "Enter phrase to remove (leave empty to cancel): ",
        "ui.removedPhrase": "Removed: {phrase}",
        "ui.phraseNotFound": "Phrase not found.",
        "ui.resetSuccess": "Reset to defaults.",
        "ui.changelogComplete": "Changelog setup completed.",
        "ui.changelogFailed": "Changelog setup failed.",
        "ui.setupPathsMenu": "Setup Paths",
        "ui.setTargetDir": "Set Target Directory",
        "ui.currentDir": "Current: {path}",
        "ui.setOutputBaseDir": "Set Output Base Directory",
        "ui.enterTargetDir": "Enter target directory path:",
        "ui.enterOutputDir": "Enter output base directory path:",
        "ui.typeRoot": "  • Type 'root' to use project root",
        "ui.typeAuto": "  • Type 'auto' to find/use docs/lang in current project",
        "ui.leaveEmpty": "  • Leave empty to cancel",
        "ui.path": "Path: ",
        "ui.cancelled": "⏭️ Cancelled. No changes made.",
        "ui.replaceCurrentDir": "⚠️ This will replace the current directory:",
        "ui.oldPath": "   Old: {path}",
        "ui.newPath": "   New: {path}",
        "ui.continueYN": "Do you want to continue? (y/n): ",
        "ui.targetSet": "✅ Target directory set to: {path}",
        "ui.outputSet": "✅ Output directory set to: {path}",
        "ui.targetAlreadySet": "⚠️ Target directory already set to current working directory.",
        "ui.fileDetected": "📄 File path detected. Using parent directory: {path}",
        "ui.pathNotFound": "❌ Path not found: {path} \nPlease check if directory or file exists.",
        "ui.setOutputAuto": "Set output base directory to docs/lang in this project? (y/n): ",
        "ui.autoSetSuccess": "✅ Output directory automatically set to: {path}",
        "ui.autoSetFailed": "❌ Could not find docs/lang directory in the current project.",
        "ui.repairStarting": "Starting Translation Repair Tool...",
        "ui.repairStep1": "1. Cleaning up duplicate switchers and fixing their positions in all READMEs...",
        "ui.repairStep2": "2. Scanning translated documents for failures (API errors / unchanged English)...",
        "ui.repairLanguages": "Languages: {langs}",
        "ui.looksTranslated": "looks properly translated.",
        "ui.repairSuccess": "No failed translations detected. All files are clean and fully repaired!",
        "ui.highEnglishOverlap": "High English overlap ({percent}%)",
        "ui.repairErrorScan": "Could not scan ({error})",
        "ui.retranslatingFailed": "Re-translating {count} failed files: {langs}",
        "ui.repairFixed": "Repair completed! Missing translations have been fixed.",
        "ui.enterLangCodesRemove": "Enter language codes to remove (comma-separated, or 'all'): ",
        "ui.actionCancelled": "Action cancelled. Returning to remove menu...",
        "ui.allRemoved": "All translated languages removed.",
        "ui.removedList": "Removed: {langs}",
        "ui.enterLangCodesRemoveReadme": "Enter README language codes to remove (comma-separated, or 'all'): ",
        "ui.removedReadmeList": "Removed README: {langs}",
        "ui.enterLangCodesRemoveChangelog": "Enter CHANGELOG language codes to remove (comma-separated, or 'all'): ",
        "ui.removedChangelogFiles": "Selected CHANGELOG files removed.",
        "ui.statusLabel": "Status: ",
        "ui.protectedPhrasesList": "Protected Phrases:",
        "ui.pkgRepoField": "• package.json (repository field)",
        "ui.gitConfig": "• .git/config",
        "ui.readmeGitPattern": "• README.md (GitHub URL patterns)",
        "ui.pleaseCheck": "\nPlease check:",
        "ui.checkPkgRepo": "• package.json has 'repository' field",
        "ui.checkGitRemote": "• .git/config has remote URL",
        "ui.checkReadmeUrl": "• Or add GitHub URL manually to README",
        "ui.noTranslatedFilesRemove": "⚠️  No translated files found to remove.",
        "ui.noFilesInOutputDir": "There are no CHANGELOG files in the output directory.",

        # API Settings
        "ui.apiSettings": "API Settings (Optional)",
        "ui.apiList": "API List",
        "ui.apiAdd": "Add API",
        "ui.apiEdit": "Edit API",
        "ui.apiDelete": "Delete API",
        "ui.apiToggle": "Enable/Disable API",
        "ui.apiName": "API Name",
        "ui.apiProvider": "Provider",
        "ui.apiToken": "API Token",
        "ui.apiStatus": "Status",
        "ui.apiActive": "🟢 Active",
        "ui.apiInactive": "🔴 Inactive",
        "ui.apiNoEntries": "No APIs configured. Using Google Translate (free) by default.",
        "ui.apiAdded": "✅ API '{name}' added successfully.",
        "ui.apiDeleted": "🗑️ API '{name}' deleted.",
        "ui.apiUpdated": "✅ API '{name}' updated.",
        "ui.apiEnabled": "🟢 API '{name}' enabled.",
        "ui.apiDisabled": "🔴 API '{name}' disabled.",
        "ui.apiUsing": "🔌 Using API: {name} ({provider})",
        "ui.apiFallback": "⚠️  Falling back to Google Translate (free).",
        "ui.apiSelectProvider": "Select provider",
        "ui.apiEnterToken": "Enter API token (leave blank for free providers)",
        "ui.apiEnterName": "Enter a name for this API",
        "ui.apiSelectToEdit": "Enter API number to edit",
        "ui.apiSelectToDelete": "Enter API number to delete",
        "ui.apiSelectToToggle": "Enter API number to enable/disable",
        "ui.apiConfirmDelete": "Are you sure you want to delete API '{name}'? [y/N]",
        "ui.apiTestSuccess": "✅ API test successful: {result}",
        "ui.apiTestFailed": "❌ API test failed: {error}",
        "ui.apiTesting": "🔍 Testing API connection...",
        "ui.apiInvalidNumber": "Invalid API number.",
        "ui.apiSavedNote": "💡 API tokens are saved in api_config.json (keep this file private!)",
        "ui.apiMenuTitle": "🔌 API Settings — Optional Translation APIs",
        "ui.apiActiveCount": "Active APIs: {count}/{total}",
        "ui.apiUsingFree": "Using Google Translate (default, no API needed)",
        "ui.apiCancelHint": "(empty to cancel)",
        "ui.apiTableName": "Name",
        "ui.apiTableProvider": "Provider",
        "ui.apiTableStatus": "Status",
        "ui.apiProviders": "Providers:",
        "ui.apiCancel": "Cancel",
        "ui.apiEditing": "Editing: {name} ({provider})",
        "ui.apiNewName": "New name [{name}] (Enter to keep, q=cancel)",
        "ui.apiNewToken": "New token (Enter to keep, q=cancel)",
        "ui.apiActiveLabel": "active",
        "ui.provider_google": "Google Translate (Free, no token needed)",
        "ui.provider_deepl": "DeepL (Free/Pro — token required)",
        "ui.provider_mymemory": "MyMemory (Free with optional token for higher quota)",
        "ui.provider_libretranslate": "LibreTranslate (Free self-hosted / public servers)",
        "ui.provider_yandex": "Yandex Translate (token required — free tier available)",
        "ui.provider_microsoft": "Microsoft Azure Translator (token required — free tier 2M chars/month)",
        "ui.provider_papago": "Papago / Naver (best for Korean — client_id:secret_key format)",
        "ui.provider_custom": "Custom REST API (any HTTP endpoint with Bearer token)",
        "ui.aiSettings": "AI Settings (Optional)",
        "ui.aiMenuTitle": "🤖 AI Settings — Optional AI Providers",
        "ui.aiSavedNote": "💡 AI config saved in ai_config.json (keep private!)",
        "ui.aiNoEntries": "No AI providers configured.",
        "ui.aiAdd": "Add AI Provider",
        "ui.aiEdit": "Edit AI Provider",
        "ui.aiDelete": "Delete AI Provider",
        "ui.aiToggle": "Enable/Disable AI Provider",
        "ui.aiActive": "🟢 Active",
        "ui.aiInactive": "🔴 Inactive",
        "ui.aiActiveCount": "Active AI: {count}/{total}",
        "ui.aiUsingDefault": "Using standard translation APIs (default)",
        "ui.aiAdded": "✅ AI '{name}' added.",
        "ui.aiDeleted": "🗑️ AI '{name}' deleted.",
        "ui.aiUpdated": "✅ AI '{name}' updated.",
        "ui.aiEnabled": "🟢 AI '{name}' enabled.",
        "ui.aiDisabled": "🔴 AI '{name}' disabled.",
        "ui.aiSelectProvider": "Select AI provider",
        "ui.aiProviders": "AI Providers:",
        "ui.aiEnterName": "Enter a name for this AI",
        "ui.aiAuthType": "Authentication method",
        "ui.aiAuthKey": "API Key / Token",
        "ui.aiAuthBrowser": "(removed)",
        "ui.aiEnterKey": "Enter API key or token",
        "ui.aiBrowserOpening": "Browser login removed. Use API key/token.",
        "ui.aiBrowserNote": "Use API key/token authentication.",
        "ui.aiSelectToEdit": "Enter AI number to edit",
        "ui.aiSelectToDelete": "Enter AI number to delete",
        "ui.aiSelectToToggle": "Enter AI number to enable/disable",
        "ui.aiConfirmDelete": "Delete AI '{name}'? [y/N]",
        "ui.aiInvalidNumber": "Invalid AI number.",
        "ui.aiActiveLabel": "active",
        "ui.aiTableName": "Name",
        "ui.aiTableProvider": "Provider",
        "ui.aiTableStatus": "Status",
        "ui.aiTableAuth": "Auth",
        "ui.aiEditing": "Editing: {name} ({provider})",
        "ui.aiNewName": "New name [{name}] (Enter to keep, q=cancel)",
        "ui.aiNewKey": "New API key (Enter to keep, q=cancel)",
        "ui.aiCancelHint": "(empty to cancel)",
        "ui.ai_provider_openai": "OpenAI ChatGPT (API key)",
        "ui.ai_provider_gemini": "Google Gemini (API key)",
        "ui.ai_provider_claude": "Anthropic Claude (API key)",
        "ui.ai_provider_copilot": "Microsoft Copilot (API key)",
        "ui.ai_provider_mistral": "Mistral AI (API key)",
        "ui.ai_provider_perplexity": "Perplexity AI (API key)",
        "ui.ai_provider_custom": "Custom AI (API endpoint + token)",
        "ui.tableLimit": "Limit",
        "ui.enterLimit": "Usage limit (Enter to use default, e.g. 500k/month)",
        "ui.limitDefault": "Default: {value}",
        "ui.apiLimit": "Limit (Recharge)",
        "ui.aiLimit": "Limit (Recharge)",
        "ui.tableAccount": "Account",
        "ui.enterAccount": "Account username (optional, ex: fatonyahmadfauzi)",
    },
    "id": {
        "ui.codeLanguage": "Kode/Bahasa",
        "ui.changelogTitle": "CHANGELOG",
        "ui.warningDifferentProject": "⚠️  PERINGATAN: Direktori Output berada di proyek yang berbeda!",
        "ui.pathOutsideProject": "(Path berada di luar folder proyek saat ini)",
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
        "changelog.affectsSelected": "Hanya mempengaruhi bahasa terpilih: {count} bahasa",
        "changelog.generateWith": "📋 Generate dengan CHANGELOG",
        "changelog.checkedDescription": "Jika dicentang: Menerjemahkan file README dan CHANGELOG",
        "changelog.uncheckedDescription": "Jika tidak dicentang: Hanya menerjemahkan file README",
        
        "progress.translatingWithChangelog": "Menerjemahkan README + CHANGELOG",
        "progress.translatingReadmeOnly": "Menerjemahkan README saja",
        "success.filesSavedWithChangelog": "README dan CHANGELOG",
        "success.filesSavedReadmeOnly": "README saja",
        "success.translationCompletedWithChangelog": "✅ {count} README dan CHANGELOG berhasil diterjemahkan!",
        "success.translationCompletedReadmeOnly": "✅ {count} README berhasil diterjemahkan!",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.md tidak ditemukan - melewati penerjemahan CHANGELOG",
        
        "errors.changelogGenerateFailed": "❌ Generate CHANGELOG gagal",
        "errors.changelogRemoveSelectedFailed": "❌ Gagal menghapus file CHANGELOG terpilih",
        "success.changelogGenerated": "✅ CHANGELOG berhasil digenerate untuk {count} bahasa",
        "success.changelogRemovedSelected": "✅ {count} file CHANGELOG berhasil dihapus",
        "confirmation.removeChangelogSelected": "Apakah Anda yakin ingin menghapus file CHANGELOG untuk {count} bahasa terpilih? File README tidak akan terpengaruh.",
        
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
        "debug_current": "Saat ini",
        "ui.changeLanguage": "Ubah Bahasa Tampilan",
        "ui.currentLanguage": "Bahasa saat ini",
        "ui.languageChanged": "✅ Bahasa tampilan berubah ke {name}",
        "ui.languageSelector": "Pilih bahasa tampilan untuk notifikasi CLI",
        "ui.translate": "Terjemahkan",
        "ui.removeTranslated": "Hapus Bahasa Terjemahan",
        "ui.protectionSettings": "Pengaturan Perlindungan (Frasa)",
        "ui.autoSetupChangelog": "Setup Otomatis Bagian Changelog",
        "ui.detectGithub": "Deteksi URL GitHub",
        "ui.repairTranslations": "Perbaiki Terjemahan (Duplikat & Gagal)",
        "ui.setupPaths": "Atur Direktori",
        "ui.exit": "Keluar",
        "ui.selectOption": "Pilih opsi:",
        "ui.currentProjectPath": "Jalur proyek saat ini",
        "ui.outputDirectory": "Direktori Output",
        "ui.folderProject": "Folder Proyek",
        "ui.available": "TERSEDIA",
        "ui.notFound": "TIDAK DITEMUKAN",
        "ui.notSet": "Belum diatur",
        "ui.developer": "Pengembang",
        "ui.exiting": "Keluar...",
        "ui.chooseLanguageCode": "Pilih kode bahasa (kosong untuk membatalkan):",
        "ui.translationStatus": "Status Terjemahan:",
        "ui.translateBoth": "Terjemahkan README & CHANGELOG",
        "ui.translateReadme": "Terjemahkan README Saja",
        "ui.translateChangelog": "Terjemahkan CHANGELOG Saja",
        "ui.removeBoth": "Hapus README & CHANGELOG",
        "ui.removeReadme": "Hapus README Saja",
        "ui.removeChangelog": "Hapus CHANGELOG Saja",
        "ui.back": "Kembali",
        "ui.missing": "TIDAK ADA",
        "ui.enterLangCodes": "Masukkan kode bahasa (pisahkan dengan koma, atau 'all'):",
        "ui.invalidOption": "Opsi tidak valid.",
        "ui.invalidLanguages": "Bahasa tidak valid.",
        "ui.pressEnter": "Tekan Enter untuk melanjutkan...",
        "ui.status": "Status: ",
        "ui.active": "AKTIF",
        "ui.inactive": "NONAKTIF",
        "ui.protectedPhrases": "Frasa yang Dilindungi:",
        "ui.noProtectedDir": "- Tidak ada frasa yang dilindungi.",
        "ui.toggleProtection": "Ganti Status Perlindungan",
        "ui.addProtection": "Tambah Frasa yang Dilindungi",
        "ui.removeProtection": "Hapus Frasa yang Dilindungi",
        "ui.resetDefault": "Kembalikan ke Default",
        "ui.enterPhraseAdd": "Masukkan frasa untuk dilindungi (kosongkan untuk batal): ",
        "ui.addedPhrase": "Ditambahkan: {phrase}",
        "ui.enterPhraseRemove": "Masukkan frasa untuk dihapus (kosongkan untuk batal): ",
        "ui.removedPhrase": "Dihapus: {phrase}",
        "ui.phraseNotFound": "Frasa tidak ditemukan.",
        "ui.resetSuccess": "Dikembalikan ke default.",
        "ui.changelogComplete": "Penyiapan Changelog selesai.",
        "ui.changelogFailed": "Penyiapan Changelog gagal.",
        "ui.setupPathsMenu": "Pengaturan Path",
        "ui.setTargetDir": "Atur Direktori Target",
        "ui.currentDir": "Saat ini: {path}",
        "ui.setOutputBaseDir": "Atur Direktori Basis Output",
        "ui.enterTargetDir": "Masukkan path direktori target:",
        "ui.enterOutputDir": "Masukkan path direktori basis output:",
        "ui.typeRoot": "  • Ketik 'root' untuk menggunakan root proyek",
        "ui.typeAuto": "  • Ketik 'auto' untuk mencari docs/lang di proyek",
        "ui.leaveEmpty": "  • Kosongkan untuk batal",
        "ui.path": "Path: ",
        "ui.cancelled": "⏭️ Dibatalkan. Tidak ada perubahan yang dibuat.",
        "ui.replaceCurrentDir": "⚠️ Ini akan menggantikan direktori saat ini:",
        "ui.oldPath": "   Lama: {path}",
        "ui.newPath": "   Baru: {path}",
        "ui.continueYN": "Apakah Anda ingin melanjutkan? (y/n): ",
        "ui.targetSet": "✅ Direktori target diatur ke: {path}",
        "ui.outputSet": "✅ Direktori output diatur ke: {path}",
        "ui.targetAlreadySet": "⚠️ Direktori target sudah berada di direktori saat ini.",
        "ui.fileDetected": "📄 Path file terdeteksi. Menggunakan parent directory: {path}",
        "ui.pathNotFound": "❌ Path tidak ditemukan: {path} \nHarap periksa apakah file/direktori ada.",
        "ui.setOutputAuto": "Atur direktori output base ke docs/lang di proyek ini? (y/n): ",
        "ui.autoSetSuccess": "✅ Direktori output secara otomatis diatur ke: {path}",
        "ui.autoSetFailed": "❌ Tidak dapat menemukan direktori docs/lang di proyek ini.",
        "ui.repairStarting": "Memulai Alat Perbaikan Terjemahan...",
        "ui.repairStep1": "1. Membersihkan switcher ganda dan memperbaiki posisinya di semua README...",
        "ui.repairStep2": "2. Memindai kegagalan dokumen (Kesalahan API / tidak diterjemahkan)...",
        "ui.repairLanguages": "Bahasa: {langs}",
        "ui.looksTranslated": "tampak diterjemahkan dengan benar.",
        "ui.repairSuccess": "Tidak ada terjemahan gagal yang terdeteksi. Semua file bersih dan diperbaiki!",
        "ui.highEnglishOverlap": "Bahasa Inggris terlalu dominan ({percent}%)",
        "ui.repairErrorScan": "Tidak dapat memindai ({error})",
        "ui.retranslatingFailed": "Menerjemahkan ulang {count} file gagal: {langs}",
        "ui.repairFixed": "Perbaikan selesai! Terjemahan yang hilang telah diperbaiki.",
        "ui.enterLangCodesRemove": "Masukkan kode bahasa untuk dihapus (pisahkan koma, atau 'all'): ",
        "ui.actionCancelled": "Aksi dibatalkan. Kembali ke menu hapus...",
        "ui.allRemoved": "Semua bahasa terjemahan telah dihapus.",
        "ui.removedList": "Dihapus: {langs}",
        "ui.enterLangCodesRemoveReadme": "Masukkan kode bahasa README untuk dihapus (pisahkan koma, atau 'all'): ",
        "ui.removedReadmeList": "README dihapus: {langs}",
        "ui.enterLangCodesRemoveChangelog": "Masukkan kode bahasa CHANGELOG untuk dihapus (pisahkan koma, atau 'all'): ",
        "ui.removedChangelogFiles": "File CHANGELOG yang dipilih telah dihapus.",
        "ui.statusLabel": "Status: ",
        "ui.protectedPhrasesList": "Frasa yang Diproteksi:",
        "ui.pkgRepoField": "• package.json (field repository)",
        "ui.gitConfig": "• .git/config",
        "ui.readmeGitPattern": "• README.md (Pola URL GitHub)",
        "ui.pleaseCheck": "\nHarap periksa:",
        "ui.checkPkgRepo": "• package.json memiliki field 'repository'",
        "ui.checkGitRemote": "• .git/config memiliki URL remote",
        "ui.checkReadmeUrl": "• Atau tambahkan URL GitHub secara manual ke README",
        "ui.noTranslatedFilesRemove": "⚠️  Tidak ada file terjemahan yang ditemukan untuk dihapus.",
        "ui.noFilesInOutputDir": "Tidak ada file Changelog (Log Perubahan) di direktori output.",
        "progress.translatingChangelogOnly": "Menerjemahkan hanya Changelog (Log Perubahan)",
        "success.translationCompletedChangelogOnly": "✅ {count} Changelog (Log Perubahan) berhasil diterjemahkan!",
        "ui.cannotTranslateBoth": "⚠️  Tidak bisa menerjemahkan README & CHANGELOG.",
        "ui.missingReadmeForBoth": "README.md tidak ada. Gunakan opsi [2] untuk menerjemahkan README saja.",
        "ui.missingChangelogForBoth": "CHANGELOG.md tidak ada. Gunakan opsi [3] untuk menerjemahkan CHANGELOG saja.",
        "ui.missingBothFiles": "README.md dan CHANGELOG.md keduanya tidak ada.",
        "ui.cannotTranslateReadmeOnly": "⚠️  Tidak bisa menerjemahkan README saja.",
        "ui.missingReadme": "README.md tidak ditemukan.",
        "ui.cannotTranslateChangelogOnly": "⚠️  Tidak bisa menerjemahkan CHANGELOG saja.",
        "ui.missingChangelog": "CHANGELOG.md tidak ditemukan.",

        # API Settings
        "ui.apiSettings": "Pengaturan API (Opsional)",
        "ui.apiList": "Daftar API",
        "ui.apiAdd": "Tambah API",
        "ui.apiEdit": "Edit API",
        "ui.apiDelete": "Hapus API",
        "ui.apiToggle": "Aktifkan/Nonaktifkan API",
        "ui.apiName": "Nama API",
        "ui.apiProvider": "Provider",
        "ui.apiToken": "Token API",
        "ui.apiStatus": "Status",
        "ui.apiActive": "🟢 Aktif",
        "ui.apiInactive": "🔴 Nonaktif",
        "ui.apiNoEntries": "Belum ada API. Menggunakan Google Translate (gratis) secara default.",
        "ui.apiAdded": "✅ API '{name}' berhasil ditambahkan.",
        "ui.apiDeleted": "🗑️ API '{name}' dihapus.",
        "ui.apiUpdated": "✅ API '{name}' diperbarui.",
        "ui.apiEnabled": "🟢 API '{name}' diaktifkan.",
        "ui.apiDisabled": "🔴 API '{name}' dinonaktifkan.",
        "ui.apiUsing": "🔌 Menggunakan API: {name} ({provider})",
        "ui.apiFallback": "⚠️  Kembali ke Google Translate (gratis).",
        "ui.apiSelectProvider": "Pilih provider",
        "ui.apiEnterToken": "Masukkan token API (kosongkan untuk provider gratis)",
        "ui.apiEnterName": "Masukkan nama untuk API ini",
        "ui.apiSelectToEdit": "Masukkan nomor API untuk diedit",
        "ui.apiSelectToDelete": "Masukkan nomor API untuk dihapus",
        "ui.apiSelectToToggle": "Masukkan nomor API untuk aktifkan/nonaktifkan",
        "ui.apiConfirmDelete": "Yakin ingin menghapus API '{name}'? [y/N]",
        "ui.apiTestSuccess": "✅ Test API berhasil: {result}",
        "ui.apiTestFailed": "❌ Test API gagal: {error}",
        "ui.apiTesting": "🔍 Menguji koneksi API...",
        "ui.apiInvalidNumber": "Nomor API tidak valid.",
        "ui.apiSavedNote": "💡 Token API disimpan di api_config.json (jaga kerahasiaannya!)",
        "ui.apiMenuTitle": "🔌 Pengaturan API — API Terjemahan Opsional",
        "ui.apiActiveCount": "API Aktif: {count}/{total}",
        "ui.apiUsingFree": "Menggunakan Google Translate (default, tidak butuh API)",
        "ui.apiCancelHint": "(kosongkan untuk batal)",
        "ui.apiTableName": "Nama",
        "ui.apiTableProvider": "Provider",
        "ui.apiTableStatus": "Status",
        "ui.apiProviders": "Provider:",
        "ui.apiCancel": "Batal",
        "ui.apiEditing": "Mengedit: {name} ({provider})",
        "ui.apiNewName": "Nama baru [{name}] (Enter untuk pertahankan, q=batal)",
        "ui.apiNewToken": "Token baru (Enter untuk pertahankan, q=batal)",
        "ui.apiActiveLabel": "aktif",
        "ui.provider_google": "Google Translate (Gratis, tidak perlu token)",
        "ui.provider_deepl": "DeepL (Gratis/Pro — memerlukan token)",
        "ui.provider_mymemory": "MyMemory (Gratis dengan token opsional untuk kuota lebih)",
        "ui.provider_libretranslate": "LibreTranslate (Self-hosted gratis / server publik)",
        "ui.provider_yandex": "Yandex Translate (memerlukan token — tersedia tier gratis)",
        "ui.provider_microsoft": "Microsoft Azure Translator (memerlukan token — tier gratis 2M kar/bulan)",
        "ui.provider_papago": "Papago / Naver (terbaik untuk Korea — format client_id:secret_key)",
        "ui.provider_custom": "Custom REST API (endpoint HTTP apapun dengan Bearer token)",
        "ui.aiSettings": "Pengaturan AI (Opsional)",
        "ui.aiMenuTitle": "🤖 Pengaturan AI — Provider AI Opsional",
        "ui.aiSavedNote": "💡 Konfigurasi AI disimpan di ai_config.json (jaga kerahasiaannya!)",
        "ui.aiNoEntries": "Tidak ada provider AI yang dikonfigurasi.",
        "ui.aiAdd": "Tambah Provider AI",
        "ui.aiEdit": "Edit Provider AI",
        "ui.aiDelete": "Hapus Provider AI",
        "ui.aiToggle": "Aktifkan/Nonaktifkan Provider AI",
        "ui.aiActive": "🟢 Aktif",
        "ui.aiInactive": "🔴 Nonaktif",
        "ui.aiActiveCount": "AI Aktif: {count}/{total}",
        "ui.aiUsingDefault": "Menggunakan API terjemahan standar (default)",
        "ui.aiAdded": "✅ AI '{name}' berhasil ditambahkan.",
        "ui.aiDeleted": "🗑️ AI '{name}' dihapus.",
        "ui.aiUpdated": "✅ AI '{name}' diperbarui.",
        "ui.aiEnabled": "🟢 AI '{name}' diaktifkan.",
        "ui.aiDisabled": "🔴 AI '{name}' dinonaktifkan.",
        "ui.aiSelectProvider": "Pilih provider AI",
        "ui.aiProviders": "Provider AI:",
        "ui.aiEnterName": "Masukkan nama untuk AI ini",
        "ui.aiAuthType": "Metode autentikasi",
        "ui.aiAuthKey": "API Key / Token",
        "ui.aiAuthBrowser": "(dihapus)",
        "ui.aiEnterKey": "Masukkan API key atau token",
        "ui.aiBrowserOpening": "Login browser dihapus. Gunakan API key/token.",
        "ui.aiBrowserNote": "Gunakan autentikasi API key/token.",
        "ui.aiSelectToEdit": "Masukkan nomor AI untuk diedit",
        "ui.aiSelectToDelete": "Masukkan nomor AI untuk dihapus",
        "ui.aiSelectToToggle": "Masukkan nomor AI untuk aktifkan/nonaktifkan",
        "ui.aiConfirmDelete": "Hapus AI '{name}'? [y/N]",
        "ui.aiInvalidNumber": "Nomor AI tidak valid.",
        "ui.aiActiveLabel": "aktif",
        "ui.aiTableName": "Nama",
        "ui.aiTableProvider": "Provider",
        "ui.aiTableStatus": "Status",
        "ui.aiTableAuth": "Auth",
        "ui.aiEditing": "Mengedit: {name} ({provider})",
        "ui.aiNewName": "Nama baru [{name}] (Enter untuk pertahankan, q=batal)",
        "ui.aiNewKey": "API key baru (Enter untuk pertahankan, q=batal)",
        "ui.aiCancelHint": "(kosongkan untuk batal)",
        "ui.ai_provider_openai": "OpenAI ChatGPT (API key)",
        "ui.ai_provider_gemini": "Google Gemini (API key)",
        "ui.ai_provider_claude": "Anthropic Claude (API key)",
        "ui.ai_provider_copilot": "Microsoft Copilot (API key)",
        "ui.ai_provider_mistral": "Mistral AI (API key)",
        "ui.ai_provider_perplexity": "Perplexity AI (API key)",
        "ui.ai_provider_custom": "AI Kustom (endpoint API + token)",
        "ui.tableLimit": "Limit",
        "ui.enterLimit": "Batas penggunaan (Enter untuk pakai default, mis. 500k/bulan)",
        "ui.limitDefault": "Default: {value}",
        "ui.apiLimit": "Limit (Recharge)",
        "ui.aiLimit": "Limit (Recharge)",
        "ui.tableAccount": "Akun",
        "ui.enterAccount": "Username akun (opsional, cth: fatonyahmadfauzi)",
    },
    "jp": {
        "ui.codeLanguage": "コード/言語",
        "ui.changelogTitle": "チェンジログ",
        "ui.warningDifferentProject": "⚠️  警告: 出力ディレクトリが別のプロジェクトにあります！",
        "ui.pathOutsideProject": "(パスは現在のプロジェクトフォルダの外にあります)",
        "translating_readme": "📘 READMEを{lang_name}に翻訳中 ({lang_code})...",
        "readme_created": "✅ {path} が正常に作成されました",
        "translating_changelog": "📘 チェンジログを{lang_name}に翻訳中 ({lang_code})...",
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
        "changelog_translated": "✅ {count}言語にチェンジログを正常に翻訳しました",
        "no_changelog_translated": "❌ 翻訳されたチェンジログファイルはありません",
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
        "failed_translate_changelog": "❌ チェンジログの翻訳に失敗: {error}",
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
        "help_translate_changelog": "チェンジログ(CHANGELOG.md)のみ翻訳（全言語の場合は'all'、またはコード指定）",
        "help_auto_setup_changelog": "CHANGELOG.mdが存在する場合、README.mdにチェンジログセクションを自動追加",
        "help_detect_github_url": "さまざまなソースからGitHubリポジトリURLを検出して表示",
        "help_display": "ターミナル通知の表示言語 (en, id, jp, de, es, fr, kr, pl, pt, ru, zh)",

        "changelog.onlyActions": "📋 チェンジログのみのアクション",
        "changelog.generateRemoveOnly": "チェンジログのみ生成/削除",
        "changelog.onlyDescription": "これらのアクションはチェンジログファイルのみに影響し、READMEファイルは変更されません。",
        "changelog.generateOnly": "🌐 チェンジログのみ生成",
        "changelog.removeSelected": "🗑️ 選択したチェンジログを削除",
        "changelog.affectsSelected": "選択した言語のみに影響: {count}言語",
        "changelog.generateWith": "📋 チェンジログ付きで生成",
        "changelog.checkedDescription": "チェック時: READMEとチェンジログの両方を翻訳",
        "changelog.uncheckedDescription": "未チェック時: READMEファイルのみ翻訳",
        
        "progress.translatingWithChangelog": "README + チェンジログを翻訳中",
        "progress.translatingReadmeOnly": "READMEのみ翻訳中",
        "success.filesSavedWithChangelog": "READMEとチェンジログ",
        "success.filesSavedReadmeOnly": "READMEのみ",
        "success.translationCompletedWithChangelog": "✅ {count}個のREADMEとチェンジログが正常に翻訳されました！",
        "success.translationCompletedReadmeOnly": "✅ {count}個のREADMEが正常に翻訳されました！",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.mdが見つかりません - チェンジログ翻訳をスキップします",
        
        "errors.changelogGenerateFailed": "❌ チェンジログ生成に失敗しました",
        "errors.changelogRemoveSelectedFailed": "❌ 選択したチェンジログファイルの削除に失敗しました",
        "success.changelogGenerated": "✅ {count}言語のチェンジログが正常に生成されました",
        "success.changelogRemovedSelected": "✅ {count}個のチェンジログファイルが正常に削除されました",
        "confirmation.removeChangelogSelected": "選択した{count}言語のチェンジログファイルを削除してもよろしいですか？READMEファイルは影響を受けません。",
        
        "help_generate_changelog_only": "選択した言語のチェンジログファイルのみ生成（READMEファイルは変更されません）",
        "help_remove_changelog_selected": "選択した言語のチェンジログファイルのみ削除（READMEファイルは変更されません）",
        "help_remove_changelog_only": "すべてのチェンジログファイルのみ削除（READMEファイルは変更されません）",
        "help_with_changelog": "有効時: READMEとチェンジログを翻訳。無効時: READMEのみ翻訳",
        "errors.noLanguagesSelected": "❌ 言語が選択されていません",
        "errors.noLanguagesSelectedRemove": "❌ 削除する言語が選択されていません",
        "progress.startingTranslation": "🚀 {count}言語の翻訳を開始します - {mode_text}",
        "progress.translatingLanguage": "📖 {lang_name}を翻訳中 ({current}/{total})...",
        "progress.waiting": "⏳ 次の翻訳まで{seconds}秒待機中...",
        "progress.completed": "✅ 翻訳プロセスが完了しました",
        "progress.barLabel": "進捗:",
        "progress.filesSaved": "💾 ファイルを保存しました: {path}",
        "progress.removingSelected": "🗑️ 選択したチェンジログファイルを削除中...",
        "progress.fileCreated": "✅ 削除しました: {path}",
        "progress.removingChangelog": "🗑️ すべてのチェンジログファイルを削除中...",
        "changelog.translatingChangelog": "📘 {count}言語のチェンジログを翻訳中...",
        "changelog.translating": "🔧 チェンジログを{lang_name}に翻訳中...",
        "changelog.translated": "✅ チェンジログを{lang_name}に翻訳しました",
        "changelog.autoSettingUp": "🔧 チェンジログセクションを自動設定中...",
        "changelog.checkingSpacing": "🔧 チェンジログセクションの間隔を確認中...",
        "progress.changelogTranslated": "✅ チェンジログを{lang_name}に翻訳しました",
        "errors.translationFailedShort": "❌ {lang_name}の翻訳に失敗しました",
        "errors.translationFailed": "❌ {lang_code}の翻訳に失敗しました: {error}",
        "errors.changelogTranslationFailed": "❌ チェンジログの翻訳に失敗しました",
        "success.changelogTranslationCompleted": "✅ チェンジログの翻訳が完了しました",
        "errors.changelogRemoveFailed": "❌ チェンジログファイルの削除に失敗しました",
        "info.noChangelogFiles": "ℹ️ チェンジログファイルが見つかりません",
        "success.changelogRemoved": "✅ {count}個のチェンジログファイルを削除しました",
        "confirmation.removeChangelog": "すべてのチェンジログファイルを削除してもよろしいですか？READMEファイルは影響を受けません。"
,
        "menu_debug": "デバッグモードの切り替え",
        "debug_enabled": "デバッグモードが【有効】になりました。",
        "debug_disabled": "デバッグモードが【無効】になりました。",
        "debug_current": "現在",
        "ui.changeLanguage": "表示言語を変更",
        "ui.currentLanguage": "現在の言語",
        "ui.languageChanged": "✅ 表示言語を {name} に変更しました",
        "ui.languageSelector": "CLI通知の表示言語を選択",
        "ui.translate": "翻訳する",
        "ui.removeTranslated": "翻訳済み言語の削除",
        "ui.protectionSettings": "保護設定（フレーズ）",
        "ui.autoSetupChangelog": "チェンジログセクションの自動追加",
        "ui.detectGithub": "GitHub URLの検出",
        "ui.repairTranslations": "翻訳の修復（重複と失敗の修正）",
        "ui.setupPaths": "パスの設定",
        "ui.exit": "終了",
        "ui.selectOption": "オプションを選択:",
        "ui.currentProjectPath": "現在のプロジェクトパス",
        "ui.outputDirectory": "出力ディレクトリ",
        "ui.folderProject": "プロジェクトフォルダ",
        "ui.available": "利用可能",
        "ui.notFound": "見つかりません",
        "ui.notSet": "未設定",
        "ui.developer": "開発者",
        "ui.exiting": "終了しています...",
        "ui.chooseLanguageCode": "言語コードを選択してください（空でキャンセル）:",
        "ui.translationStatus": "翻訳ステータス:",
        "ui.translateBoth": "READMEとチェンジログを翻訳する",
        "ui.translateReadme": "READMEのみ翻訳する",
        "ui.translateChangelog": "チェンジログのみ翻訳する",
        "ui.removeBoth": "READMEとチェンジログを削除する",
        "ui.removeReadme": "READMEのみ削除する",
        "ui.removeChangelog": "チェンジログのみ削除する",
        "ui.back": "戻る",
        "ui.missing": "欠落",
        "ui.enterLangCodes": "言語コードを入力（カンマ区切り、または'all'）:",
        "ui.invalidOption": "無効なオプションです。",
        "ui.invalidLanguages": "無効な言語です。",
        "ui.pressEnter": "Enterキーを押して続行...",
        "ui.status": "ステータス: ",
        "ui.active": "有効",
        "ui.inactive": "無効",
        "ui.protectedPhrases": "保護されたフレーズ:",
        "ui.noProtectedDir": "- 保護されたフレーズは設定されていません。",
        "ui.toggleProtection": "保護ステータスの切り替え",
        "ui.addProtection": "保護フレーズを追加する",
        "ui.removeProtection": "保護フレーズを削除する",
        "ui.resetDefault": "デフォルトにリセット",
        "ui.enterPhraseAdd": "保護するフレーズを入力してください（空でキャンセル）: ",
        "ui.addedPhrase": "追加しました: {phrase}",
        "ui.enterPhraseRemove": "削除するフレーズを入力してください（空でキャンセル）: ",
        "ui.removedPhrase": "削除しました: {phrase}",
        "ui.phraseNotFound": "フレーズが見つかりません。",
        "ui.resetSuccess": "デフォルトにリセットされました。",
        "ui.changelogComplete": "チェンジログのセットアップが完了しました。",
        "ui.changelogFailed": "チェンジログのセットアップに失敗しました。",
        "ui.setupPathsMenu": "パスの設定",
        "ui.setTargetDir": "ターゲットディレクトリの設定",
        "ui.currentDir": "現在: {path}",
        "ui.setOutputBaseDir": "出力ベースディレクトリの設定",
        "ui.enterTargetDir": "ターゲットディレクトリパスを入力:",
        "ui.enterOutputDir": "出力ベースディレクトリパスを入力:",
        "ui.typeRoot": "  • 'root'と入力するとプロジェクトのルートを使用します",
        "ui.typeAuto": "  • 'auto'と入力すると自動でdocs/langを検索します",
        "ui.leaveEmpty": "  • 空でキャンセル",
        "ui.path": "パス: ",
        "ui.cancelled": "⏭️ キャンセルしました。変更は行われません。",
        "ui.replaceCurrentDir": "⚠️ 現在のディレクトリを置き換えます:",
        "ui.oldPath": "   旧: {path}",
        "ui.newPath": "   新: {path}",
        "ui.continueYN": "続行しますか？ (y/n): ",
        "ui.targetSet": "✅ ターゲットディレクトリをセットしました: {path}",
        "ui.outputSet": "✅ 出力ディレクトリをセットしました: {path}",
        "ui.targetAlreadySet": "⚠️ ターゲットディレクトリは既に設定済みです。",
        "ui.fileDetected": "📄 ファイルパスを検出しました。親ディレクトリを使用します: {path}",
        "ui.pathNotFound": "❌ パスが見つかりません: {path} \n存在するか確認してください。",
        "ui.setOutputAuto": "出力ベースディレクトリを現在のdocs/langにセットしますか？ (y/n): ",
        "ui.autoSetSuccess": "✅ 出力ディレクトリを自動セットしました: {path}",
        "ui.autoSetFailed": "❌ プロジェクトでdocs/langが見つかりませんでした。",
        "ui.repairStarting": "翻訳修復ツールを起動しています...",
        "ui.repairStep1": "1. すべてのREADME上の重複スイッチャーをクリーンアップし位置を修正しています...",
        "ui.repairStep2": "2. 翻訳失敗（APIエラー/英語のまま）がないかスキャン中...",
        "ui.repairLanguages": "言語: {langs}",
        "ui.looksTranslated": "は正しく翻訳されているようです。",
        "ui.repairSuccess": "失敗した翻訳は検出されませんでした。すべてのファイルは正常に修復されました！",
        "ui.highEnglishOverlap": "高い英語の重複率 ({percent}%)",
        "ui.repairErrorScan": "スキャンできませんでした ({error})",
        "ui.retranslatingFailed": "{count}個の失敗したファイルを再翻訳中: {langs}",
        "ui.repairFixed": "修復完了！不足していた翻訳が修正されました。",
        "ui.enterLangCodesRemove": "削除する言語コードを入力（カンマ区切り、または'all'）: ",
        "ui.actionCancelled": "キャンセルしました。削除メニューに戻ります...",
        "ui.allRemoved": "すべての翻訳言語を削除しました。",
        "ui.removedList": "削除しました: {langs}",
        "ui.enterLangCodesRemoveReadme": "削除するREADMEの言語コードを入力（カンマ区切り、または'all'）: ",
        "ui.removedReadmeList": "READMEを削除しました: {langs}",
        "ui.enterLangCodesRemoveChangelog": "削除するチェンジログの言語コードを入力（カンマ区切り、または'all'）: ",
        "ui.removedChangelogFiles": "選択したチェンジログファイルを削除しました。",
        "ui.statusLabel": "ステータス: ",
        "ui.protectedPhrasesList": "保護されたフレーズ:",
        "ui.pkgRepoField": "• package.json (repository フィールド)",
        "ui.gitConfig": "• .git/config",
        "ui.readmeGitPattern": "• README.md (GitHub URLパターン)",
        "ui.pleaseCheck": "\n以下をご確認ください:",
        "ui.checkPkgRepo": "• package.json に 'repository' フィールドがあるか",
        "ui.checkGitRemote": "• .git/config にリモート URL があるか",
        "ui.checkReadmeUrl": "• または GitHub URL を README に手動で追加してください",
        "ui.noTranslatedFilesRemove": "⚠️  削除する翻訳ファイルが見つかりません。",
        "ui.noFilesInOutputDir": "出力ディレクトリにチェンジログ (CHANGELOG) ファイルがありません。",
        "progress.translatingChangelogOnly": "チェンジログ (CHANGELOG) のみ翻訳中",
        "success.translationCompletedChangelogOnly": "✅ {count} 個のチェンジログ (CHANGELOG) の翻訳が完了しました！",
        "ui.cannotTranslateBoth": "⚠️  README と CHANGELOG の両方を翻訳できません。",
        "ui.missingReadmeForBoth": "README.md がありません。オプション [2] で README のみを翻訳してください。",
        "ui.missingChangelogForBoth": "CHANGELOG.md がありません。オプション [3] で CHANGELOG のみを翻訳してください。",
        "ui.missingBothFiles": "README.md と CHANGELOG.md の両方がありません。",
        "ui.cannotTranslateReadmeOnly": "⚠️  README のみを翻訳できません。",
        "ui.missingReadme": "README.md が見つかりません。",
        "ui.cannotTranslateChangelogOnly": "⚠️  チェンジログのみを翻訳できません。",
        "ui.missingChangelog": "CHANGELOG.md が見つかりません。",

        # API Settings
        "ui.apiSettings": "API設定（オプション）",
        "ui.apiList": "APIリスト",
        "ui.apiAdd": "APIを追加",
        "ui.apiEdit": "APIを編集",
        "ui.apiDelete": "APIを削除",
        "ui.apiToggle": "APIを有効/無効",
        "ui.apiName": "API名",
        "ui.apiProvider": "プロバイダー",
        "ui.apiToken": "APIトークン",
        "ui.apiStatus": "ステータス",
        "ui.apiActive": "🟢 有効",
        "ui.apiInactive": "🔴 無効",
        "ui.apiNoEntries": "APIが設定されていません。デフォルトでGoogle翻訳（無料）を使用します。",
        "ui.apiAdded": "✅ API '{name}' を追加しました。",
        "ui.apiDeleted": "🗑️ API '{name}' を削除しました。",
        "ui.apiUpdated": "✅ API '{name}' を更新しました。",
        "ui.apiEnabled": "🟢 API '{name}' を有効にしました。",
        "ui.apiDisabled": "🔴 API '{name}' を無効にしました。",
        "ui.apiUsing": "🔌 使用中のAPI: {name} ({provider})",
        "ui.apiFallback": "⚠️  Google翻訳（無料）にフォールバックします。",
        "ui.apiSelectProvider": "プロバイダーを選択",
        "ui.apiEnterToken": "APIトークンを入力（無料プロバイダーは空白可）",
        "ui.apiEnterName": "このAPIの名前を入力",
        "ui.apiSelectToEdit": "編集するAPI番号を入力",
        "ui.apiSelectToDelete": "削除するAPI番号を入力",
        "ui.apiSelectToToggle": "有効/無効にするAPI番号を入力",
        "ui.apiConfirmDelete": "API '{name}' を削除してもよいですか？ [y/N]",
        "ui.apiTestSuccess": "✅ APIテスト成功: {result}",
        "ui.apiTestFailed": "❌ APIテスト失敗: {error}",
        "ui.apiTesting": "🔍 API接続をテスト中...",
        "ui.apiInvalidNumber": "無効なAPI番号です。",
        "ui.apiSavedNote": "💡 APIトークンはapi_config.jsonに保存されます（非公開にしてください）",
        "ui.apiMenuTitle": "🔌 API設定 — オプション翻訳API",
        "ui.apiActiveCount": "有効なAPI: {count}/{total}",
        "ui.apiUsingFree": "Google翻訳（デフォルト、API不要）を使用中",
        "ui.apiCancelHint": "（空で中止）",
        "ui.apiTableName": "名前",
        "ui.apiTableProvider": "プロバイダー",
        "ui.apiTableStatus": "ステータス",
        "ui.apiProviders": "プロバイダー一覧:",
        "ui.apiCancel": "キャンセル",
        "ui.apiEditing": "編集中: {name} ({provider})",
        "ui.apiNewName": "新しい名前 [{name}] (そのままにするにはEnter、q=キャンセル)",
        "ui.apiNewToken": "新しいトークン (そのままにするにはEnter、q=キャンセル)",
        "ui.apiActiveLabel": "アクティブ",
        "ui.provider_google": "Google翻訳（無料、トークン不要）",
        "ui.provider_deepl": "DeepL（無料/Pro — トークン必要）",
        "ui.provider_mymemory": "MyMemory（無料、より多くのクォータにはトークン任意）",
        "ui.provider_libretranslate": "LibreTranslate（無料セルフホスト / 公開サーバー）",
        "ui.provider_yandex": "Yandex翻訳（トークン必要 — 無料枠あり）",
        "ui.provider_microsoft": "Microsoft Azure翻訳（トークン必要 — 無料枠月200万文字）",
        "ui.provider_papago": "Papago / Naver（韓国語最適 — client_id:secret_key形式）",
        "ui.provider_custom": "カスタムREST API（Bearerトークン付きのHTTPエンドポイント）",
        "ui.aiSettings": "AI設定（オプション）",
        "ui.aiMenuTitle": "🤖 AI設定 — オプションAIプロバイダー",
        "ui.aiSavedNote": "💡 AI設定はai_config.jsonに保存されます（非公開に！）",
        "ui.aiNoEntries": "AIプロバイダーが設定されていません。",
        "ui.aiAdd": "AIプロバイダーを追加",
        "ui.aiEdit": "AIプロバイダーを編集",
        "ui.aiDelete": "AIプロバイダーを削除",
        "ui.aiToggle": "AIプロバイダーを有効/無効",
        "ui.aiActive": "🟢 有効",
        "ui.aiInactive": "🔴 無効",
        "ui.aiActiveCount": "有効なAI: {count}/{total}",
        "ui.aiUsingDefault": "標準翻訳APIを使用中（デフォルト）",
        "ui.aiAdded": "✅ AI '{name}' を追加しました。",
        "ui.aiDeleted": "🗑️ AI '{name}' を削除しました。",
        "ui.aiUpdated": "✅ AI '{name}' を更新しました。",
        "ui.aiEnabled": "🟢 AI '{name}' を有効にしました。",
        "ui.aiDisabled": "🔴 AI '{name}' を無効にしました。",
        "ui.aiSelectProvider": "AIプロバイダーを選択",
        "ui.aiProviders": "AIプロバイダー一覧:",
        "ui.aiEnterName": "このAIの名前を入力",
        "ui.aiAuthType": "認証方法",
        "ui.aiAuthKey": "[1] APIキー",
        "ui.aiAuthBrowser": "[2] ブラウザでログイン",
        "ui.aiEnterKey": "APIキーを入力",
        "ui.aiBrowserOpening": "🌐 ブラウザを開いています...",
        "ui.aiBrowserNote": "ブラウザが開きました。ログイン後、Enterを押してください。",
        "ui.aiSelectToEdit": "編集するAI番号を入力",
        "ui.aiSelectToDelete": "削除するAI番号を入力",
        "ui.aiSelectToToggle": "有効/無効にするAI番号を入力",
        "ui.aiConfirmDelete": "AI '{name}' を削除しますか？ [y/N]",
        "ui.aiInvalidNumber": "無効なAI番号です。",
        "ui.aiActiveLabel": "アクティブ",
        "ui.aiTableName": "名前",
        "ui.aiTableProvider": "プロバイダー",
        "ui.aiTableStatus": "ステータス",
        "ui.aiTableAuth": "認証",
        "ui.aiEditing": "編集中: {name} ({provider})",
        "ui.aiNewName": "新しい名前 [{name}] (Enter=そのまま, q=中止)",
        "ui.aiNewKey": "新しいAPIキー (Enter=そのまま, q=中止)",
        "ui.aiCancelHint": "（空で中止）",
        "ui.ai_provider_openai": "OpenAI ChatGPT（APIキーまたはブラウザログイン）",
        "ui.ai_provider_gemini": "Google Gemini（APIキーまたはブラウザログイン）",
        "ui.ai_provider_claude": "Anthropic Claude（APIキーまたはブラウザログイン）",
        "ui.ai_provider_copilot": "Microsoft Copilot（ブラウザログイン）",
        "ui.ai_provider_mistral": "Mistral AI（APIキーまたはブラウザログイン）",
        "ui.ai_provider_perplexity": "Perplexity AI（APIキーまたはブラウザログイン）",
        "ui.ai_provider_custom": "カスタムAI（APIエンドポイント＋キー）",
        "ui.tableLimit": "制限",
        "ui.enterLimit": "使用制限 (Enterでデフォルト使用、例: 50万文字/月)",
        "ui.limitDefault": "デフォルト: {value}",
        "ui.apiLimit": "制限 (再充電が必要)",
        "ui.aiLimit": "制限 (再充電が必要)",
        "ui.tableAccount": "アカウント",
        "ui.enterAccount": "アカウント名 (任意, 例: fatonyahmadfauzi)",
    },
    "de": {
        "ui.codeLanguage": "Code/Sprache",
        "ui.changelogTitle": "CHANGELOG",
        "ui.warningDifferentProject": "⚠️ WARNUNG: Das Ausgabeverzeichnis befindet sich in einem anderen Projekt!",
        "ui.pathOutsideProject": "(Pfad liegt außerhalb des aktuellen Projektordners)",
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
        "changelog.affectsSelected": "Betrifft nur ausgewählte Sprachen: {count} Sprachen",
        "changelog.generateWith": "📋 Mit CHANGELOG generieren",
        "changelog.checkedDescription": "Wenn aktiviert: Übersetzt sowohl README- als auch CHANGELOG-Dateien",
        "changelog.uncheckedDescription": "Wenn deaktiviert: Übersetzt nur README-Dateien",
        
        "progress.translatingWithChangelog": "Übersetze README + CHANGELOG",
        "progress.translatingReadmeOnly": "Übersetze nur README",
        "success.filesSavedWithChangelog": "READMEs und CHANGELOGs",
        "success.filesSavedReadmeOnly": "Nur READMEs",
        "success.translationCompletedWithChangelog": "✅ {count} READMEs und CHANGELOGs erfolgreich übersetzt!",
        "success.translationCompletedReadmeOnly": "✅ {count} READMEs erfolgreich übersetzt!",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.md nicht gefunden - überspringe CHANGELOG-Übersetzung",
        
        "errors.changelogGenerateFailed": "❌ CHANGELOG-Generierung fehlgeschlagen",
        "errors.changelogRemoveSelectedFailed": "❌ Fehler beim Entfernen ausgewählter CHANGELOG-Dateien",
        "success.changelogGenerated": "✅ CHANGELOG erfolgreich für {count} Sprachen generiert",
        "success.changelogRemovedSelected": "✅ {count} CHANGELOG-Dateien erfolgreich entfernt",
        "confirmation.removeChangelogSelected": "Sind Sie sicher, dass Sie CHANGELOG-Dateien für {count} ausgewählte Sprachen entfernen möchten? README-Dateien werden nicht beeinflusst.",
        
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
        "debug_current": "Aktuell",
        "ui.changeLanguage": "Anzeigesprache ändern",
        "ui.currentLanguage": "Aktuelle Sprache",
        "ui.languageChanged": "✅ Anzeigesprache auf {name} geändert",
        "ui.languageSelector": "Anzeigesprache für CLI-Benachrichtigungen auswählen",
        "ui.translate": "Übersetzen",
        "ui.removeTranslated": "Übersetzte Sprachen entfernen",
        "ui.protectionSettings": "Schutzeinstellungen (Phrasen)",
        "ui.autoSetupChangelog": "Changelog-Bereich automatisch einrichten",
        "ui.detectGithub": "GitHub-URL erkennen",
        "ui.repairTranslations": "Übersetzungen reparieren (Duplikate & Fehler beheben)",
        "ui.setupPaths": "Pfade einrichten",
        "ui.exit": "Beenden",
        "ui.selectOption": "Option wählen:",
        "ui.currentProjectPath": "Aktueller Projektpfad",
        "ui.outputDirectory": "Ausgabeverzeichnis",
        "ui.folderProject": "Projektordner",
        "ui.available": "VERFÜGBAR",
        "ui.notFound": "NICHT GEFUNDEN",
        "ui.notSet": "Nicht festgelegt",
        "ui.developer": "Entwickler",
        "ui.exiting": "Wird beendet...",
        "ui.chooseLanguageCode": "Sprachcode wählen (leer zum Abbrechen):",
        "ui.translationStatus": "Übersetzungsstatus:",
        "ui.translateBoth": "README & CHANGELOG übersetzen",
        "ui.translateReadme": "Nur README übersetzen",
        "ui.translateChangelog": "Nur CHANGELOG übersetzen",
        "ui.removeBoth": "README & CHANGELOG entfernen",
        "ui.removeReadme": "Nur README entfernen",
        "ui.removeChangelog": "Nur CHANGELOG entfernen",
        "ui.back": "Zurück",
        "ui.missing": "FEHLT",
        "ui.enterLangCodes": "Sprachcodes eingeben (kommasepariert, oder 'all'):",
        "ui.invalidOption": "Ungültige Option.",
        "ui.invalidLanguages": "Ungültige Sprachen.",
        "ui.pressEnter": "Drücken Sie die Eingabetaste, um fortzufahren...",
        "ui.status": "Status: ",
        "ui.active": "AKTIV",
        "ui.inactive": "INAKTIV",
        "ui.protectedPhrases": "Geschützte Phrasen:",
        "ui.noProtectedDir": "- Keine geschützten Phrasen konfiguriert.",
        "ui.toggleProtection": "Schutzstatus umschalten",
        "ui.addProtection": "Geschützte Phrase hinzufügen",
        "ui.removeProtection": "Geschützte Phrase entfernen",
        "ui.resetDefault": "Auf Standard zurücksetzen",
        "ui.enterPhraseAdd": "Phrase zum Schützen eingeben (leer zum Abbrechen): ",
        "ui.addedPhrase": "Hinzugefügt: {phrase}",
        "ui.enterPhraseRemove": "Phrase zum Entfernen eingeben (leer zum Abbrechen): ",
        "ui.removedPhrase": "Entfernt: {phrase}",
        "ui.phraseNotFound": "Phrase nicht gefunden.",
        "ui.resetSuccess": "Auf Standard zurückgesetzt.",
        "ui.changelogComplete": "Changelog-Setup abgeschlossen.",
        "ui.changelogFailed": "Changelog-Setup fehlgeschlagen.",
        "ui.setupPathsMenu": "Setup Paths",
        "ui.setTargetDir": "Set Target Directory",
        "ui.currentDir": "Current: {path}",
        "ui.setOutputBaseDir": "Set Output Base Directory",
        "ui.enterTargetDir": "Enter target directory path:",
        "ui.enterOutputDir": "Enter output base directory path:",
        "ui.typeRoot": "  • Type 'root' to use project root",
        "ui.typeAuto": "  • Type 'auto' to find/use docs/lang in current project",
        "ui.leaveEmpty": "  • Leave empty to cancel",
        "ui.path": "Path: ",
        "ui.cancelled": "⏭️ Cancelled. No changes made.",
        "ui.replaceCurrentDir": "⚠️ This will replace the current directory:",
        "ui.oldPath": "   Old: {path}",
        "ui.newPath": "   New: {path}",
        "ui.continueYN": "Do you want to continue? (y/n): ",
        "ui.targetSet": "✅ Target directory set to: {path}",
        "ui.outputSet": "✅ Output directory set to: {path}",
        "ui.targetAlreadySet": "⚠️ Target directory already set to current working directory.",
        "ui.fileDetected": "📄 File path detected. Using parent directory: {path}",
        "ui.pathNotFound": "❌ Path not found: {path} \nPlease check if directory or file exists.",
        "ui.setOutputAuto": "Set output base directory to docs/lang in this project? (y/n): ",
        "ui.autoSetSuccess": "✅ Output directory automatically set to: {path}",
        "ui.autoSetFailed": "❌ Could not find docs/lang directory in the current project.",
        "ui.repairStarting": "Starting Translation Repair Tool...",
        "ui.repairStep1": "1. Cleaning up duplicate switchers and fixing their positions in all READMEs...",
        "ui.repairStep2": "2. Scanning translated documents for failures (API errors / unchanged English)...",
        "ui.repairLanguages": "Languages: {langs}",
        "ui.looksTranslated": "looks properly translated.",
        "ui.repairSuccess": "No failed translations detected. All files are clean and fully repaired!",
        "ui.highEnglishOverlap": "High English overlap ({percent}%)",
        "ui.repairErrorScan": "Could not scan ({error})",
        "ui.retranslatingFailed": "Re-translating {count} failed files: {langs}",
        "ui.repairFixed": "Repair completed! Missing translations have been fixed.",
        "ui.enterLangCodesRemove": "Enter language codes to remove (comma-separated, or 'all'): ",
        "ui.actionCancelled": "Action cancelled. Returning to remove menu...",
        "ui.allRemoved": "All translated languages removed.",
        "ui.removedList": "Removed: {langs}",
        "ui.enterLangCodesRemoveReadme": "Enter README language codes to remove (comma-separated, or 'all'): ",
        "ui.removedReadmeList": "Removed README: {langs}",
        "ui.enterLangCodesRemoveChangelog": "Enter CHANGELOG language codes to remove (comma-separated, or 'all'): ",
        "ui.removedChangelogFiles": "Selected CHANGELOG files removed.",
        "ui.statusLabel": "Status: ",
        "ui.protectedPhrasesList": "Protected Phrases:",
        "ui.pkgRepoField": "• package.json (repository field)",
        "ui.gitConfig": "• .git/config",
        "ui.readmeGitPattern": "• README.md (GitHub URL patterns)",
        "ui.pleaseCheck": "\nPlease check:",
        "ui.checkPkgRepo": "• package.json has 'repository' field",
        "ui.checkGitRemote": "• .git/config has remote URL",
        "ui.checkReadmeUrl": "• Or add GitHub URL manually to README",
        "ui.noTranslatedFilesRemove": "⚠️  Keine übersetzten Dateien zum Entfernen gefunden.",
        "ui.noFilesInOutputDir": "Es gibt keine CHANGELOG-Dateien im Ausgabeverzeichnis.",
        "progress.translatingChangelogOnly": "Nur Änderungsprotokoll (CHANGELOG) übersetzen",
        "success.translationCompletedChangelogOnly": "✅ {count} Änderungsprotokolle (CHANGELOGs) erfolgreich übersetzt!",
        "ui.cannotTranslateBoth": "⚠️  README & CHANGELOG können nicht übersetzt werden.",
        "ui.missingReadmeForBoth": "README.md fehlt. Verwende Option [2] um nur README zu übersetzen.",
        "ui.missingChangelogForBoth": "CHANGELOG.md fehlt. Verwende Option [3] um nur CHANGELOG zu übersetzen.",
        "ui.missingBothFiles": "Sowohl README.md als auch CHANGELOG.md fehlen.",
        "ui.cannotTranslateReadmeOnly": "⚠️  Nur-README-Übersetzung nicht möglich.",
        "ui.missingReadme": "README.md fehlt.",
        "ui.cannotTranslateChangelogOnly": "⚠️  Nur-CHANGELOG-Übersetzung nicht möglich.",
        "ui.missingChangelog": "CHANGELOG.md fehlt.",

        # API Settings
        "ui.apiSettings": "API-Einstellungen (Optional)",
        "ui.apiList": "API-Liste",
        "ui.apiAdd": "API hinzufügen",
        "ui.apiEdit": "API bearbeiten",
        "ui.apiDelete": "API löschen",
        "ui.apiToggle": "API aktivieren/deaktivieren",
        "ui.apiName": "API-Name",
        "ui.apiProvider": "Anbieter",
        "ui.apiToken": "API-Token",
        "ui.apiStatus": "Status",
        "ui.apiActive": "🟢 Aktiv",
        "ui.apiInactive": "🔴 Inaktiv",
        "ui.apiNoEntries": "Keine APIs konfiguriert. Standard: Google Translate (kostenlos).",
        "ui.apiAdded": "✅ API '{name}' erfolgreich hinzugefügt.",
        "ui.apiDeleted": "🗑️ API '{name}' gelöscht.",
        "ui.apiUpdated": "✅ API '{name}' aktualisiert.",
        "ui.apiEnabled": "🟢 API '{name}' aktiviert.",
        "ui.apiDisabled": "🔴 API '{name}' deaktiviert.",
        "ui.apiUsing": "🔌 Verwendete API: {name} ({provider})",
        "ui.apiFallback": "⚠️  Fallback auf Google Translate (kostenlos).",
        "ui.apiSelectProvider": "Anbieter auswählen",
        "ui.apiEnterToken": "API-Token eingeben (bei kostenlosen Anbietern leer lassen)",
        "ui.apiEnterName": "Name für diese API eingeben",
        "ui.apiSelectToEdit": "API-Nummer zum Bearbeiten eingeben",
        "ui.apiSelectToDelete": "API-Nummer zum Löschen eingeben",
        "ui.apiSelectToToggle": "API-Nummer zum Aktivieren/Deaktivieren eingeben",
        "ui.apiConfirmDelete": "API '{name}' wirklich löschen? [y/N]",
        "ui.apiTestSuccess": "✅ API-Test erfolgreich: {result}",
        "ui.apiTestFailed": "❌ API-Test fehlgeschlagen: {error}",
        "ui.apiTesting": "🔍 API-Verbindung wird getestet...",
        "ui.apiInvalidNumber": "Ungültige API-Nummer.",
        "ui.apiSavedNote": "💡 API-Tokens werden in api_config.json gespeichert (privat halten!)",
        "ui.apiMenuTitle": "🔌 API-Einstellungen — Optionale Übersetzungs-APIs",
        "ui.apiActiveCount": "Aktive APIs: {count}/{total}",
        "ui.apiUsingFree": "Google Translate wird verwendet (Standard, kein API erforderlich)",
        "ui.apiCancelHint": "(leer = abbrechen)",
        "ui.apiTableName": "Name",
        "ui.apiTableProvider": "Anbieter",
        "ui.apiTableStatus": "Status",
        "ui.apiProviders": "Anbieter:",
        "ui.apiCancel": "Abbrechen",
        "ui.apiEditing": "Bearbeitung: {name} ({provider})",
        "ui.apiNewName": "Neuer Name [{name}] (Enter = behalten, q=abbrechen)",
        "ui.apiNewToken": "Neues Token (Enter = behalten, q=abbrechen)",
        "ui.apiActiveLabel": "aktiv",
        "ui.provider_google": "Google Translate (Kostenlos, kein Token erforderlich)",
        "ui.provider_deepl": "DeepL (Kostenlos/Pro — Token erforderlich)",
        "ui.provider_mymemory": "MyMemory (Kostenlos mit optionalem Token für mehr Kontingent)",
        "ui.provider_libretranslate": "LibreTranslate (Kostenlos self-hosted / öffentliche Server)",
        "ui.provider_yandex": "Yandex Übersetzer (Token erforderlich — kostenlose Stufe verfügbar)",
        "ui.provider_microsoft": "Microsoft Azure Übersetzer (Token erforderlich — kostenlose Stufe 2M Zeichen/Monat)",
        "ui.provider_papago": "Papago / Naver (am besten für Koreanisch — client_id:secret_key Format)",
        "ui.provider_custom": "Benutzerdefinierte REST API (beliebiger HTTP-Endpunkt mit Bearer-Token)",
        "ui.aiSettings": "KI-Einstellungen (Optional)",
        "ui.aiMenuTitle": "🤖 KI-Einstellungen — Optionale KI-Anbieter",
        "ui.aiSavedNote": "💡 KI-Konfiguration in ai_config.json gespeichert (privat halten!)",
        "ui.aiNoEntries": "Keine KI-Anbieter konfiguriert.",
        "ui.aiAdd": "KI-Anbieter hinzufügen",
        "ui.aiEdit": "KI-Anbieter bearbeiten",
        "ui.aiDelete": "KI-Anbieter löschen",
        "ui.aiToggle": "KI-Anbieter aktivieren/deaktivieren",
        "ui.aiActive": "🟢 Aktiv",
        "ui.aiInactive": "🔴 Inaktiv",
        "ui.aiActiveCount": "Aktive KI: {count}/{total}",
        "ui.aiUsingDefault": "Standard-Übersetzungs-APIs werden verwendet (Standard)",
        "ui.aiAdded": "✅ KI '{name}' hinzugefügt.",
        "ui.aiDeleted": "🗑️ KI '{name}' gelöscht.",
        "ui.aiUpdated": "✅ KI '{name}' aktualisiert.",
        "ui.aiEnabled": "🟢 KI '{name}' aktiviert.",
        "ui.aiDisabled": "🔴 KI '{name}' deaktiviert.",
        "ui.aiSelectProvider": "KI-Anbieter auswählen",
        "ui.aiProviders": "KI-Anbieter:",
        "ui.aiEnterName": "Name für diese KI eingeben",
        "ui.aiAuthType": "Authentifizierungsmethode",
        "ui.aiAuthKey": "[1] API-Schlüssel",
        "ui.aiAuthBrowser": "[2] Browser-Login",
        "ui.aiEnterKey": "API-Schlüssel eingeben",
        "ui.aiBrowserOpening": "🌐 Browser wird geöffnet...",
        "ui.aiBrowserNote": "Browser geöffnet. Einloggen, dann Enter drücken.",
        "ui.aiSelectToEdit": "KI-Nummer zum Bearbeiten eingeben",
        "ui.aiSelectToDelete": "KI-Nummer zum Löschen eingeben",
        "ui.aiSelectToToggle": "KI-Nummer zum Aktivieren/Deaktivieren eingeben",
        "ui.aiConfirmDelete": "KI '{name}' löschen? [y/N]",
        "ui.aiInvalidNumber": "Ungültige KI-Nummer.",
        "ui.aiActiveLabel": "aktiv",
        "ui.aiTableName": "Name",
        "ui.aiTableProvider": "Anbieter",
        "ui.aiTableStatus": "Status",
        "ui.aiTableAuth": "Auth",
        "ui.aiEditing": "Bearbeitung: {name} ({provider})",
        "ui.aiNewName": "Neuer Name [{name}] (Enter=behalten, q=abbrechen)",
        "ui.aiNewKey": "Neuer API-Schlüssel (Enter=behalten, q=abbrechen)",
        "ui.aiCancelHint": "(leer = abbrechen)",
        "ui.ai_provider_openai": "OpenAI ChatGPT (API-Schlüssel)",
        "ui.ai_provider_gemini": "Google Gemini (API-Schlüssel)",
        "ui.ai_provider_claude": "Anthropic Claude (API-Schlüssel)",
        "ui.ai_provider_copilot": "Microsoft Copilot (API-Schlüssel)",
        "ui.ai_provider_mistral": "Mistral AI (API-Schlüssel)",
        "ui.ai_provider_perplexity": "Perplexity AI (API-Schlüssel)",
        "ui.ai_provider_custom": "Benutzerdefinierte KI (API-Endpunkt + Schlüssel)",
        "ui.tableLimit": "Limit",
        "ui.enterLimit": "Nutzungslimit (Enter für Standard, z.B. 500k/Monat)",
        "ui.limitDefault": "Standard: {value}",
        "ui.apiLimit": "Limit (Aufladen)",
        "ui.aiLimit": "Limit (Aufladen)",
        "ui.tableAccount": "Konto",
        "ui.enterAccount": "Kontoname (optional, Bsp.: fatonyahmadfauzi)",
    },
    "es": {
        "ui.codeLanguage": "Código/Idioma",
        "ui.changelogTitle": "REGISTRO DE CAMBIOS",
        "ui.warningDifferentProject": "⚠️ ADVERTENCIA: ¡El directorio de salida está en un proyecto diferente!",
        "ui.pathOutsideProject": "(La ruta está fuera de la carpeta del proyecto actual)",
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
        "changelog.affectsSelected": "Afecta solo idiomas seleccionados: {count} idiomas",
        "changelog.generateWith": "📋 Generar con CHANGELOG",
        "changelog.checkedDescription": "Cuando está marcado: Traduce archivos README y CHANGELOG",
        "changelog.uncheckedDescription": "Cuando no está marcado: Traduce solo archivos README",
        
        "progress.translatingWithChangelog": "Traduciendo README + CHANGELOG",
        "progress.translatingReadmeOnly": "Traduciendo solo README",
        "success.filesSavedWithChangelog": "READMES y CHANGELOGs",
        "success.filesSavedReadmeOnly": "Solo READMEs",
        "success.translationCompletedWithChangelog": "✅ ¡{count} READMEs y CHANGELOGs traducidos exitosamente!",
        "success.translationCompletedReadmeOnly": "✅ ¡{count} READMEs traducidos exitosamente!",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.md no encontrado - omitiendo traducción de CHANGELOG",
        
        "errors.changelogGenerateFailed": "❌ Generación de CHANGELOG fallida",
        "errors.changelogRemoveSelectedFailed": "❌ Error al eliminar archivos CHANGELOG seleccionados",
        "success.changelogGenerated": "✅ CHANGELOG generado exitosamente para {count} idiomas",
        "success.changelogRemovedSelected": "✅ {count} archivos CHANGELOG eliminados exitosamente",
        "confirmation.removeChangelogSelected": "¿Está seguro de que desea eliminar archivos CHANGELOG para {count} idiomas seleccionados? Los archivos README no se verán afectados.",
        
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
        "debug_current": "Actual",
        "ui.changeLanguage": "Cambiar idioma de visualización",
        "ui.currentLanguage": "Idioma actual",
        "ui.languageChanged": "✅ Idioma de visualización cambiado a {name}",
        "ui.languageSelector": "Seleccionar idioma de visualización para notificaciones CLI",
        "ui.translate": "Traducir",
        "ui.removeTranslated": "Eliminar idiomas traducidos",
        "ui.protectionSettings": "Configuración de protección (Frases)",
        "ui.autoSetupChangelog": "Configuración automática de Changelog",
        "ui.detectGithub": "Detectar URL de GitHub",
        "ui.repairTranslations": "Reparar traducciones (Corregir duplicados y fallos)",
        "ui.setupPaths": "Configurar rutas",
        "ui.exit": "Salir",
        "ui.selectOption": "Seleccione una opción:",
        "ui.currentProjectPath": "Ruta actual del proyecto",
        "ui.outputDirectory": "Directorio de salida",
        "ui.folderProject": "Carpeta del proyecto",
        "ui.available": "DISPONIBLE",
        "ui.notFound": "NO ENCONTRADO",
        "ui.notSet": "No establecido",
        "ui.developer": "Desarrollador",
        "ui.exiting": "Saliendo...",
        "ui.chooseLanguageCode": "Elija código de idioma (vacío para cancelar):",
        "ui.translationStatus": "Estado de traducción:",
        "ui.translateBoth": "Traducir README y CHANGELOG",
        "ui.translateReadme": "Traducir solo README",
        "ui.translateChangelog": "Traducir solo CHANGELOG",
        "ui.removeBoth": "Eliminar README y CHANGELOG",
        "ui.removeReadme": "Eliminar solo README",
        "ui.removeChangelog": "Eliminar solo CHANGELOG",
        "ui.back": "Atrás",
        "ui.missing": "FALTA",
        "ui.enterLangCodes": "Ingresar códigos de idioma (separados por coma, o 'all'):",
        "ui.invalidOption": "Opción no válida.",
        "ui.invalidLanguages": "Idiomas no válidos.",
        "ui.pressEnter": "Presione Enter para continuar...",
        "ui.status": "Estado: ",
        "ui.active": "ACTIVO",
        "ui.inactive": "INACTIVO",
        "ui.protectedPhrases": "Frases protegidas:",
        "ui.noProtectedDir": "- No hay frases protegidas configuradas.",
        "ui.toggleProtection": "Alternar estado de protección",
        "ui.addProtection": "Agregar frase protegida",
        "ui.removeProtection": "Eliminar frase protegida",
        "ui.resetDefault": "Restablecer a valores predeterminados",
        "ui.enterPhraseAdd": "Ingrese frase a proteger (vacío para cancelar): ",
        "ui.addedPhrase": "Agregado: {phrase}",
        "ui.enterPhraseRemove": "Ingrese frase a eliminar (vacío para cancelar): ",
        "ui.removedPhrase": "Eliminado: {phrase}",
        "ui.phraseNotFound": "Frase no encontrada.",
        "ui.resetSuccess": "Restablecido a predeterminado.",
        "ui.changelogComplete": "Configuración de Changelog completada.",
        "ui.changelogFailed": "Configuración de Changelog fallida.",
        "ui.setupPathsMenu": "Configurar Rutas",
        "ui.setTargetDir": "Fijar Directorio Objetivo",
        "ui.currentDir": "Actual: {path}",
        "ui.setOutputBaseDir": "Fijar Directorio Base de Salida",
        "ui.enterTargetDir": "Introduzca la ruta del directorio objetivo:",
        "ui.enterOutputDir": "Introduzca la ruta base de salida:",
        "ui.typeRoot": "  • Escriba 'root' para usar raíz del proyecto",
        "ui.typeAuto": "  • Escriba 'auto' para buscar docs/lang",
        "ui.leaveEmpty": "  • Deje en blanco para cancelar",
        "ui.path": "Ruta: ",
        "ui.cancelled": "⏭️ Cancelado. Sin cambios.",
        "ui.replaceCurrentDir": "⚠️ Esto reemplazará el directorio actual:",
        "ui.oldPath": "   Viejo: {path}",
        "ui.newPath": "   Nuevo: {path}",
        "ui.continueYN": "¿Desea continuar? (y/n): ",
        "ui.targetSet": "✅ Directorio objetivo ajustado a: {path}",
        "ui.outputSet": "✅ Directorio de salida ajustado a: {path}",
        "ui.targetAlreadySet": "⚠️ Directorio objetivo ya ajustado al actual.",
        "ui.fileDetected": "📄 Archivo detectado. Usando directorio padre: {path}",
        "ui.pathNotFound": "❌ Ruta no encontrada: {path}",
        "ui.setOutputAuto": "¿Ajustar base de salida a docs/lang? (y/n): ",
        "ui.autoSetSuccess": "✅ Salida ajustada automáticamente a: {path}",
        "ui.autoSetFailed": "❌ No se encontró docs/lang en el proyecto.",
        "ui.repairStarting": "Iniciando Herramienta de Reparación de Traducción...",
        "ui.repairStep1": "1. Limpiando selectores duplicados y ajustando posición...",
        "ui.repairStep2": "2. Escaneando documentos traducidos por errores...",
        "ui.repairLanguages": "Idiomas: {langs}",
        "ui.looksTranslated": "parece estar correctamente traducido.",
        "ui.repairSuccess": "No hay traducciones fallidas. ¡Reparación completa!",
        "ui.highEnglishOverlap": "Alta superposición en inglés ({percent}%)",
        "ui.repairErrorScan": "No se pudo escanear ({error})",
        "ui.retranslatingFailed": "Retraduciendo {count} archivos fallidos: {langs}",
        "ui.repairFixed": "Reparación completada. Traducciones arregladas.",
        "ui.enterLangCodesRemove": "Introduzca los códigos de idioma a eliminar (separados por comas, o 'all'): ",
        "ui.actionCancelled": "Acción cancelada. Volviendo al menú de eliminación...",
        "ui.allRemoved": "Todos los idiomas traducidos eliminados.",
        "ui.removedList": "Eliminado: {langs}",
        "ui.enterLangCodesRemoveReadme": "Introduzca códigos de idioma README a eliminar (separados por comas, o 'all'): ",
        "ui.removedReadmeList": "README eliminado: {langs}",
        "ui.enterLangCodesRemoveChangelog": "Introduzca códigos de idioma CHANGELOG a eliminar (separados por comas, o 'all'): ",
        "ui.removedChangelogFiles": "Archivos CHANGELOG seleccionados eliminados.",
        "ui.statusLabel": "Estado: ",
        "ui.protectedPhrasesList": "Frases Protegidas:",
        "ui.pkgRepoField": "• package.json (campo repository)",
        "ui.gitConfig": "• .git/config",
        "ui.readmeGitPattern": "• README.md (Patrones de URL de GitHub)",
        "ui.pleaseCheck": "\nPor favor, compruebe:",
        "ui.checkPkgRepo": "• Que package.json tenga el campo 'repository'",
        "ui.checkGitRemote": "• Que .git/config tenga una URL remota",
        "ui.checkReadmeUrl": "• O añada la URL de GitHub manualmente al README",
        "ui.noTranslatedFilesRemove": "⚠️  No se encontraron archivos traducidos para eliminar.",
        "ui.noFilesInOutputDir": "No hay archivos CHANGELOG (Registro de Cambios) en el directorio de salida.",
        "progress.translatingChangelogOnly": "Traduciendo solo CHANGELOG (Registro de Cambios)",
        "success.translationCompletedChangelogOnly": "✅ ¡{count} CHANGELOG (Registros de Cambios) traducidos exitosamente!",
        "ui.cannotTranslateBoth": "⚠️  No se puede traducir README & CHANGELOG.",
        "ui.missingReadmeForBoth": "Falta README.md. Use la opción [2] para traducir solo el README.",
        "ui.missingChangelogForBoth": "Falta CHANGELOG.md. Use la opción [3] para traducir solo el CHANGELOG.",
        "ui.missingBothFiles": "Faltan tanto README.md como CHANGELOG.md.",
        "ui.cannotTranslateReadmeOnly": "⚠️  No se puede traducir solo el README.",
        "ui.missingReadme": "Falta README.md.",
        "ui.cannotTranslateChangelogOnly": "⚠️  No se puede traducir solo el CHANGELOG.",
        "ui.missingChangelog": "Falta CHANGELOG.md.",

        # API Settings
        "ui.apiSettings": "Configuración de API (Opcional)",
        "ui.apiList": "Lista de APIs",
        "ui.apiAdd": "Agregar API",
        "ui.apiEdit": "Editar API",
        "ui.apiDelete": "Eliminar API",
        "ui.apiToggle": "Activar/Desactivar API",
        "ui.apiName": "Nombre de API",
        "ui.apiProvider": "Proveedor",
        "ui.apiToken": "Token de API",
        "ui.apiStatus": "Estado",
        "ui.apiActive": "🟢 Activo",
        "ui.apiInactive": "🔴 Inactivo",
        "ui.apiNoEntries": "Sin APIs configuradas. Usando Google Translate (gratis) por defecto.",
        "ui.apiAdded": "✅ API '{name}' agregada exitosamente.",
        "ui.apiDeleted": "🗑️ API '{name}' eliminada.",
        "ui.apiUpdated": "✅ API '{name}' actualizada.",
        "ui.apiEnabled": "🟢 API '{name}' activada.",
        "ui.apiDisabled": "🔴 API '{name}' desactivada.",
        "ui.apiUsing": "🔌 Usando API: {name} ({provider})",
        "ui.apiFallback": "⚠️  Recurriendo a Google Translate (gratis).",
        "ui.apiSelectProvider": "Seleccionar proveedor",
        "ui.apiEnterToken": "Ingrese token de API (en blanco para proveedores gratuitos)",
        "ui.apiEnterName": "Ingrese un nombre para esta API",
        "ui.apiSelectToEdit": "Ingrese número de API a editar",
        "ui.apiSelectToDelete": "Ingrese número de API a eliminar",
        "ui.apiSelectToToggle": "Ingrese número de API a activar/desactivar",
        "ui.apiConfirmDelete": "¿Eliminar API '{name}'? [y/N]",
        "ui.apiTestSuccess": "✅ Prueba de API exitosa: {result}",
        "ui.apiTestFailed": "❌ Prueba de API fallida: {error}",
        "ui.apiTesting": "🔍 Probando conexión de API...",
        "ui.apiInvalidNumber": "Número de API inválido.",
        "ui.apiSavedNote": "💡 Los tokens se guardan en api_config.json (¡manténgalo privado!)",
        "ui.apiMenuTitle": "🔌 Configuración de API — APIs de traducción opcionales",
        "ui.apiActiveCount": "APIs activas: {count}/{total}",
        "ui.apiUsingFree": "Usando Google Translate (por defecto, sin API necesaria)",
        "ui.apiCancelHint": "(vacío para cancelar)",
        "ui.apiTableName": "Nombre",
        "ui.apiTableProvider": "Proveedor",
        "ui.apiTableStatus": "Estado",
        "ui.apiProviders": "Proveedores:",
        "ui.apiCancel": "Cancelar",
        "ui.apiEditing": "Editando: {name} ({provider})",
        "ui.apiNewName": "Nuevo nombre [{name}] (Enter = mantener, q=cancelar)",
        "ui.apiNewToken": "Nuevo token (Enter = mantener, q=cancelar)",
        "ui.apiActiveLabel": "activo",
        "ui.provider_google": "Google Translate (Gratis, sin token necesario)",
        "ui.provider_deepl": "DeepL (Gratis/Pro — token requerido)",
        "ui.provider_mymemory": "MyMemory (Gratis con token opcional para mayor cuota)",
        "ui.provider_libretranslate": "LibreTranslate (Self-hosted gratis / servidores públicos)",
        "ui.provider_yandex": "Yandex Translate (token requerido — nivel gratuito disponible)",
        "ui.provider_microsoft": "Microsoft Azure Translator (token requerido — nivel gratuito 2M car/mes)",
        "ui.provider_papago": "Papago / Naver (mejor para coreano — formato client_id:secret_key)",
        "ui.provider_custom": "API REST personalizada (cualquier endpoint HTTP con Bearer token)",
        "ui.aiSettings": "Configuración de IA (Opcional)",
        "ui.aiMenuTitle": "🤖 Configuración de IA — Proveedores de IA opcionales",
        "ui.aiSavedNote": "💡 Configuración de IA guardada en ai_config.json (¡manténgalo privado!)",
        "ui.aiNoEntries": "No hay proveedores de IA configurados.",
        "ui.aiAdd": "Agregar proveedor de IA",
        "ui.aiEdit": "Editar proveedor de IA",
        "ui.aiDelete": "Eliminar proveedor de IA",
        "ui.aiToggle": "Activar/Desactivar proveedor de IA",
        "ui.aiActive": "🟢 Activo",
        "ui.aiInactive": "🔴 Inactivo",
        "ui.aiActiveCount": "IA activas: {count}/{total}",
        "ui.aiUsingDefault": "Usando APIs de traducción estándar (por defecto)",
        "ui.aiAdded": "✅ IA '{name}' agregada.",
        "ui.aiDeleted": "🗑️ IA '{name}' eliminada.",
        "ui.aiUpdated": "✅ IA '{name}' actualizada.",
        "ui.aiEnabled": "🟢 IA '{name}' activada.",
        "ui.aiDisabled": "🔴 IA '{name}' desactivada.",
        "ui.aiSelectProvider": "Seleccionar proveedor de IA",
        "ui.aiProviders": "Proveedores de IA:",
        "ui.aiEnterName": "Ingrese un nombre para esta IA",
        "ui.aiAuthType": "Método de autenticación",
        "ui.aiAuthKey": "[1] Clave API",
        "ui.aiAuthBrowser": "[2] Iniciar sesión en el navegador",
        "ui.aiEnterKey": "Ingrese la clave API",
        "ui.aiBrowserOpening": "🌐 Abriendo el navegador para iniciar sesión...",
        "ui.aiBrowserNote": "Navegador abierto. Inicie sesión y presione Enter.",
        "ui.aiSelectToEdit": "Ingrese el número de IA a editar",
        "ui.aiSelectToDelete": "Ingrese el número de IA a eliminar",
        "ui.aiSelectToToggle": "Ingrese el número de IA a activar/desactivar",
        "ui.aiConfirmDelete": "¿Eliminar IA '{name}'? [y/N]",
        "ui.aiInvalidNumber": "Número de IA inválido.",
        "ui.aiActiveLabel": "activo",
        "ui.aiTableName": "Nombre",
        "ui.aiTableProvider": "Proveedor",
        "ui.aiTableStatus": "Estado",
        "ui.aiTableAuth": "Auth",
        "ui.aiEditing": "Editando: {name} ({provider})",
        "ui.aiNewName": "Nuevo nombre [{name}] (Enter=mantener, q=cancelar)",
        "ui.aiNewKey": "Nueva clave API (Enter=mantener, q=cancelar)",
        "ui.aiCancelHint": "(vacío para cancelar)",
        "ui.ai_provider_openai": "OpenAI ChatGPT (clave API o inicio de sesión en navegador)",
        "ui.ai_provider_gemini": "Google Gemini (clave API o inicio de sesión en navegador)",
        "ui.ai_provider_claude": "Anthropic Claude (clave API o inicio de sesión en navegador)",
        "ui.ai_provider_copilot": "Microsoft Copilot (inicio de sesión en navegador)",
        "ui.ai_provider_mistral": "Mistral AI (clave API o inicio de sesión en navegador)",
        "ui.ai_provider_perplexity": "Perplexity AI (clave API o inicio de sesión en navegador)",
        "ui.ai_provider_custom": "IA personalizada (endpoint API + clave)",
        "ui.tableLimit": "Límite",
        "ui.enterLimit": "Límite de uso (Enter para default, ej. 500k/mes)",
        "ui.limitDefault": "Predeterminado: {value}",
        "ui.apiLimit": "Límite (Recargar)",
        "ui.aiLimit": "Límite (Recargar)",
        "ui.tableAccount": "Cuenta",
        "ui.enterAccount": "Nombre de cuenta (opcional, ej: fatonyahmadfauzi)",
    },
    "fr": {
        "ui.codeLanguage": "Code/Langue",
        "ui.changelogTitle": "JOURNAL DES CHANGEMENTS",
        "ui.warningDifferentProject": "⚠️ AVERTISSEMENT : le répertoire de sortie se trouve dans un projet différent !",
        "ui.pathOutsideProject": "(Le chemin est en dehors du dossier du projet actuel)",
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
        "changelog.affectsSelected": "Affecte uniquement les langues sélectionnées : {count} langues",
        "changelog.generateWith": "📋 Générer avec CHANGELOG",
        "changelog.checkedDescription": "Lorsqu'elle est cochée : Traduit les fichiers README et CHANGELOG",
        "changelog.uncheckedDescription": "Lorsqu'elle n'est pas cochée : Traduit uniquement les fichiers README",
        
        "progress.translatingWithChangelog": "Traduction README + CHANGELOG",
        "progress.translatingReadmeOnly": "Traduction README uniquement",
        "success.filesSavedWithChangelog": "READMES et CHANGELOGs",
        "success.filesSavedReadmeOnly": "READMES uniquement",
        "success.translationCompletedWithChangelog": "✅ {count} READMEs et CHANGELOGs traduits avec succès !",
        "success.translationCompletedReadmeOnly": "✅ {count} READMEs traduits avec succès !",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.md non trouvé - ignore la traduction CHANGELOG",
        
        "errors.changelogGenerateFailed": "❌ Échec de la génération CHANGELOG",
        "errors.changelogRemoveSelectedFailed": "❌ Échec de la suppression des fichiers CHANGELOG sélectionnés",
        "success.changelogGenerated": "✅ CHANGELOG généré avec succès pour {count} langues",
        "success.changelogRemovedSelected": "✅ {count} fichiers CHANGELOG supprimés avec succès",
        "confirmation.removeChangelogSelected": "Êtes-vous sûr de vouloir supprimer les fichiers CHANGELOG pour {count} langues sélectionnées ? Les fichiers README ne seront pas affectés.",
        
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
        "debug_current": "Actuel",
        "ui.changeLanguage": "Changer la langue d'affichage",
        "ui.currentLanguage": "Langue actuelle",
        "ui.languageChanged": "✅ Langue d'affichage changée vers {name}",
        "ui.languageSelector": "Sélectionner la langue d'affichage pour les notifications CLI",
        "ui.translate": "Traduire",
        "ui.removeTranslated": "Supprimer les langues traduites",
        "ui.protectionSettings": "Paramètres de protection (Phrases)",
        "ui.autoSetupChangelog": "Configuration automatique du Changelog",
        "ui.detectGithub": "Détecter l'URL GitHub",
        "ui.repairTranslations": "Réparer les traductions (Corriger doublons et échecs)",
        "ui.setupPaths": "Configurer les chemins",
        "ui.exit": "Quitter",
        "ui.selectOption": "Sélectionnez une option :",
        "ui.currentProjectPath": "Chemin actuel du projet",
        "ui.outputDirectory": "Répertoire de sortie",
        "ui.folderProject": "Dossier du projet",
        "ui.available": "DISPONIBLE",
        "ui.notFound": "INTROUVABLE",
        "ui.notSet": "Non défini",
        "ui.developer": "Développeur",
        "ui.exiting": "Fermeture...",
        "ui.chooseLanguageCode": "Choisissez le code de langue (vide pour annuler) :",
        "ui.translationStatus": "Statut de traduction:",
        "ui.translateBoth": "Traduire README & CHANGELOG",
        "ui.translateReadme": "Traduire uniquement README",
        "ui.translateChangelog": "Traduire uniquement CHANGELOG",
        "ui.removeBoth": "Supprimer README & CHANGELOG",
        "ui.removeReadme": "Supprimer uniquement README",
        "ui.removeChangelog": "Supprimer uniquement CHANGELOG",
        "ui.back": "Retour",
        "ui.missing": "MANQUANT",
        "ui.enterLangCodes": "Entrez les codes de langue (séparés par des virgules, ou 'all'):",
        "ui.invalidOption": "Option invalide.",
        "ui.invalidLanguages": "Langues invalides.",
        "ui.pressEnter": "Appuyez sur Entrée pour continuer...",
        "ui.status": "Statut : ",
        "ui.active": "ACTIF",
        "ui.inactive": "INACTIF",
        "ui.protectedPhrases": "Phrases protégées :",
        "ui.noProtectedDir": "- Aucune phrase protégée configurée.",
        "ui.toggleProtection": "Basculer l'état de protection",
        "ui.addProtection": "Ajouter une phrase protégée",
        "ui.removeProtection": "Supprimer une phrase protégée",
        "ui.resetDefault": "Réinitialiser par défaut",
        "ui.enterPhraseAdd": "Entrez la phrase à protéger (vide pour annuler) : ",
        "ui.addedPhrase": "Ajouté : {phrase}",
        "ui.enterPhraseRemove": "Entrez la phrase à supprimer (vide pour annuler) : ",
        "ui.removedPhrase": "Supprimé : {phrase}",
        "ui.phraseNotFound": "Phrase introuvable.",
        "ui.resetSuccess": "Réinitialisé aux valeurs par défaut.",
        "ui.changelogComplete": "Aménagement du journal des modifications terminé.",
        "ui.changelogFailed": "Échec de l'aménagement.",
        "ui.setupPathsMenu": "Setup Paths",
        "ui.setTargetDir": "Set Target Directory",
        "ui.currentDir": "Current: {path}",
        "ui.setOutputBaseDir": "Set Output Base Directory",
        "ui.enterTargetDir": "Enter target directory path:",
        "ui.enterOutputDir": "Enter output base directory path:",
        "ui.typeRoot": "  • Type 'root' to use project root",
        "ui.typeAuto": "  • Type 'auto' to find/use docs/lang in current project",
        "ui.leaveEmpty": "  • Leave empty to cancel",
        "ui.path": "Path: ",
        "ui.cancelled": "⏭️ Cancelled. No changes made.",
        "ui.replaceCurrentDir": "⚠️ This will replace the current directory:",
        "ui.oldPath": "   Old: {path}",
        "ui.newPath": "   New: {path}",
        "ui.continueYN": "Do you want to continue? (y/n): ",
        "ui.targetSet": "✅ Target directory set to: {path}",
        "ui.outputSet": "✅ Output directory set to: {path}",
        "ui.targetAlreadySet": "⚠️ Target directory already set to current working directory.",
        "ui.fileDetected": "📄 File path detected. Using parent directory: {path}",
        "ui.pathNotFound": "❌ Path not found: {path} \nPlease check if directory or file exists.",
        "ui.setOutputAuto": "Set output base directory to docs/lang in this project? (y/n): ",
        "ui.autoSetSuccess": "✅ Répertoire de sortie automatiquement défini sur : {path}",
        "ui.autoSetFailed": "❌ Impossible de trouver le répertoire docs/lang dans le projet actuel.",
        "ui.repairStarting": "Démarrage de l'outil de réparation des traductions...",
        "ui.repairStep1": "1. Nettoyage des sélecteurs en double et correction de leurs positions dans tous les READMEs...",
        "ui.repairStep2": "2. Analyse des documents traduits pour détecter les échecs (erreurs API / anglais inchangé)...",
        "ui.repairLanguages": "Langues : {langs}",
        "ui.looksTranslated": "semble correctement traduit.",
        "ui.repairSuccess": "Aucune traduction échouée détectée. Tous les fichiers sont propres et entièrement réparés !",
        "ui.highEnglishOverlap": "Chevauchement élevé en anglais ({percent}%)",
        "ui.repairErrorScan": "Impossible d'analyser ({error})",
        "ui.retranslatingFailed": "Retraduction de {count} fichiers échoués : {langs}",
        "ui.repairFixed": "Réparation terminée ! Les traductions manquantes ont été corrigées.",
        "ui.enterLangCodesRemove": "Entrez les codes de langue à supprimer (séparés par des virgules, ou 'all') : ",
        "ui.actionCancelled": "Action annulée. Retour au menu de suppression...",
        "ui.allRemoved": "Toutes les langues traduites ont été supprimées.",
        "ui.removedList": "Supprimé : {langs}",
        "ui.enterLangCodesRemoveReadme": "Entrez les codes de langue README à supprimer (séparés par des virgules, ou 'all') : ",
        "ui.removedReadmeList": "README supprimé : {langs}",
        "ui.enterLangCodesRemoveChangelog": "Entrez les codes de langue CHANGELOG à supprimer (séparés par des virgules, ou 'all') : ",
        "ui.removedChangelogFiles": "Fichiers CHANGELOG sélectionnés supprimés.",
        "ui.statusLabel": "Statut : ",
        "ui.protectedPhrasesList": "Phrases protégées :",
        "ui.pkgRepoField": "• package.json (champ repository)",
        "ui.gitConfig": "• .git/config",
        "ui.readmeGitPattern": "• README.md (modèles d'URL GitHub)",
        "ui.pleaseCheck": "\nVeuillez vérifier :",
        "ui.checkPkgRepo": "• package.json contient le champ 'repository'",
        "ui.checkGitRemote": "• .git/config contient l'URL distante",
        "ui.checkReadmeUrl": "• Ou ajoutez l'URL GitHub manuellement dans README",
        "ui.noTranslatedFilesRemove": "⚠️  Aucun fichier traduit trouvé à supprimer.",
        "ui.noFilesInOutputDir": "Il n'y a pas de fichiers CHANGELOG (Journal des Changements) dans le répertoire de sortie.",
        "progress.translatingChangelogOnly": "Traduction du Journal des Changements (CHANGELOG) uniquement",

        "success.translationCompletedChangelogOnly": "✅ {count} Journaux des Changements (CHANGELOG) traduits avec succès !",

        "ui.cannotTranslateBoth": "⚠️  Impossible de traduire README & CHANGELOG.",
        "ui.missingReadmeForBoth": "README.md est manquant. Utilisez l'option [2] pour traduire uniquement le README.",
        "ui.missingChangelogForBoth": "CHANGELOG.md est manquant. Utilisez l'option [3] pour traduire uniquement le CHANGELOG.",
        "ui.missingBothFiles": "README.md et CHANGELOG.md sont tous les deux manquants.",
        "ui.cannotTranslateReadmeOnly": "⚠️  Impossible de traduire uniquement le README.",
        "ui.missingReadme": "README.md est manquant.",
        "ui.cannotTranslateChangelogOnly": "⚠️  Impossible de traduire uniquement le CHANGELOG.",
        "ui.missingChangelog": "CHANGELOG.md est manquant.",

        # API Settings
        "ui.apiSettings": "Paramètres API (Optionnel)",
        "ui.apiList": "Liste des APIs",
        "ui.apiAdd": "Ajouter une API",
        "ui.apiEdit": "Modifier l'API",
        "ui.apiDelete": "Supprimer l'API",
        "ui.apiToggle": "Activer/Désactiver l'API",
        "ui.apiName": "Nom de l'API",
        "ui.apiProvider": "Fournisseur",
        "ui.apiToken": "Jeton API",
        "ui.apiStatus": "Statut",
        "ui.apiActive": "🟢 Actif",
        "ui.apiInactive": "🔴 Inactif",
        "ui.apiNoEntries": "Aucune API configurée. Google Traduction (gratuit) utilisé par défaut.",
        "ui.apiAdded": "✅ API '{name}' ajoutée avec succès.",
        "ui.apiDeleted": "🗑️ API '{name}' supprimée.",
        "ui.apiUpdated": "✅ API '{name}' mise à jour.",
        "ui.apiEnabled": "🟢 API '{name}' activée.",
        "ui.apiDisabled": "🔴 API '{name}' désactivée.",
        "ui.apiUsing": "🔌 API utilisée : {name} ({provider})",
        "ui.apiFallback": "⚠️  Utilisation de Google Traduction (gratuit) en repli.",
        "ui.apiSelectProvider": "Sélectionner le fournisseur",
        "ui.apiEnterToken": "Entrez le jeton API (laisser vide pour les fournisseurs gratuits)",
        "ui.apiEnterName": "Entrez un nom pour cette API",
        "ui.apiSelectToEdit": "Entrez le numéro d'API à modifier",
        "ui.apiSelectToDelete": "Entrez le numéro d'API à supprimer",
        "ui.apiSelectToToggle": "Entrez le numéro d'API à activer/désactiver",
        "ui.apiConfirmDelete": "Supprimer l'API '{name}' ? [y/N]",
        "ui.apiTestSuccess": "✅ Test API réussi : {result}",
        "ui.apiTestFailed": "❌ Échec du test API : {error}",
        "ui.apiTesting": "🔍 Test de connexion API en cours...",
        "ui.apiInvalidNumber": "Numéro d'API invalide.",
        "ui.apiSavedNote": "💡 Les jetons sont sauvegardés dans api_config.json (gardez ce fichier privé !)",
        "ui.apiMenuTitle": "🔌 Paramètres API — APIs de traduction optionnelles",
        "ui.apiActiveCount": "APIs actives : {count}/{total}",
        "ui.apiUsingFree": "Google Traduction utilisé (par défaut, aucune API requise)",
        "ui.apiCancelHint": "(vide pour annuler)",
        "ui.apiTableName": "Nom",
        "ui.apiTableProvider": "Fournisseur",
        "ui.apiTableStatus": "Statut",
        "ui.apiProviders": "Fournisseurs :",
        "ui.apiCancel": "Annuler",
        "ui.apiEditing": "Modification : {name} ({provider})",
        "ui.apiNewName": "Nouveau nom [{name}] (Enter = garder, q=annuler)",
        "ui.apiNewToken": "Nouveau jeton (Enter = garder, q=annuler)",
        "ui.apiActiveLabel": "actif",
        "ui.provider_google": "Google Traduction (Gratuit, aucun jeton requis)",
        "ui.provider_deepl": "DeepL (Gratuit/Pro — jeton requis)",
        "ui.provider_mymemory": "MyMemory (Gratuit avec jeton optionnel pour plus de quota)",
        "ui.provider_libretranslate": "LibreTranslate (Auto-hébergé gratuit / serveurs publics)",
        "ui.provider_yandex": "Yandex Traduction (jeton requis — niveau gratuit disponible)",
        "ui.provider_microsoft": "Microsoft Azure Traduction (jeton requis — niveau gratuit 2M car/mois)",
        "ui.provider_papago": "Papago / Naver (meilleur pour le coréen — format client_id:secret_key)",
        "ui.provider_custom": "API REST personnalisée (tout endpoint HTTP avec jeton Bearer)",
        "ui.aiSettings": "Paramètres IA (Optionnel)",
        "ui.aiMenuTitle": "🤖 Paramètres IA — Fournisseurs IA optionnels",
        "ui.aiSavedNote": "💡 Config IA sauvegardée dans ai_config.json (garder privé !)",
        "ui.aiNoEntries": "Aucun fournisseur IA configuré.",
        "ui.aiAdd": "Ajouter un fournisseur IA",
        "ui.aiEdit": "Modifier un fournisseur IA",
        "ui.aiDelete": "Supprimer un fournisseur IA",
        "ui.aiToggle": "Activer/Désactiver un fournisseur IA",
        "ui.aiActive": "🟢 Actif",
        "ui.aiInactive": "🔴 Inactif",
        "ui.aiActiveCount": "IA actives : {count}/{total}",
        "ui.aiUsingDefault": "Utilisation des APIs de traduction standard (défaut)",
        "ui.aiAdded": "✅ IA '{name}' ajoutée.",
        "ui.aiDeleted": "🗑️ IA '{name}' supprimée.",
        "ui.aiUpdated": "✅ IA '{name}' mise à jour.",
        "ui.aiEnabled": "🟢 IA '{name}' activée.",
        "ui.aiDisabled": "🔴 IA '{name}' désactivée.",
        "ui.aiSelectProvider": "Sélectionner un fournisseur IA",
        "ui.aiProviders": "Fournisseurs IA :",
        "ui.aiEnterName": "Entrez un nom pour cette IA",
        "ui.aiAuthType": "Méthode d'authentification",
        "ui.aiAuthKey": "[1] Clé API",
        "ui.aiAuthBrowser": "[2] Connexion via le navigateur",
        "ui.aiEnterKey": "Entrez la clé API",
        "ui.aiBrowserOpening": "🌐 Ouverture du navigateur pour la connexion...",
        "ui.aiBrowserNote": "Navigateur ouvert. Connectez-vous, puis appuyez sur Enter.",
        "ui.aiSelectToEdit": "Entrez le numéro de l'IA à modifier",
        "ui.aiSelectToDelete": "Entrez le numéro de l'IA à supprimer",
        "ui.aiSelectToToggle": "Entrez le numéro de l'IA à activer/désactiver",
        "ui.aiConfirmDelete": "Supprimer l'IA '{name}' ? [y/N]",
        "ui.aiInvalidNumber": "Numéro d'IA invalide.",
        "ui.aiActiveLabel": "actif",
        "ui.aiTableName": "Nom",
        "ui.aiTableProvider": "Fournisseur",
        "ui.aiTableStatus": "Statut",
        "ui.aiTableAuth": "Auth",
        "ui.aiEditing": "Modification : {name} ({provider})",
        "ui.aiNewName": "Nouveau nom [{name}] (Enter=garder, q=annuler)",
        "ui.aiNewKey": "Nouvelle clé API (Enter=garder, q=annuler)",
        "ui.aiCancelHint": "(vide pour annuler)",
        "ui.ai_provider_openai": "OpenAI ChatGPT (clé API ou connexion navigateur)",
        "ui.ai_provider_gemini": "Google Gemini (clé API ou connexion navigateur)",
        "ui.ai_provider_claude": "Anthropic Claude (clé API ou connexion navigateur)",
        "ui.ai_provider_copilot": "Microsoft Copilot (connexion navigateur)",
        "ui.ai_provider_mistral": "Mistral AI (clé API ou connexion navigateur)",
        "ui.ai_provider_perplexity": "Perplexity AI (clé API ou connexion navigateur)",
        "ui.ai_provider_custom": "IA personnalisée (endpoint API + clé)",
        "ui.tableLimit": "Limite",
        "ui.enterLimit": "Limite d'utilisation (Enter pour défaut, ex. 500k/mois)",
        "ui.limitDefault": "Défaut : {value}",
        "ui.apiLimit": "Limite (Recharger)",
        "ui.aiLimit": "Limite (Recharger)",
        "ui.tableAccount": "Compte",
        "ui.enterAccount": "Nom de compte (optionnel, ex: fatonyahmadfauzi)",
        "progress.barLabel": "Progression :",
    },
    "kr": {
        "ui.codeLanguage": "코드/언어",
        "ui.changelogTitle": "변경 로그",
        "ui.warningDifferentProject": "⚠️ 경고: 출력 디렉터리가 다른 프로젝트에 있습니다!",
        "ui.pathOutsideProject": "(경로는 현재 프로젝트 폴더 외부에 있습니다)",
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
        "changelog.affectsSelected": "선택한 언어만 영향: {count}개 언어",
        "changelog.generateWith": "📋 CHANGELOG 포함 생성",
        "changelog.checkedDescription": "체크 시: README와 CHANGELOG 파일 모두 번역",
        "changelog.uncheckedDescription": "체크 해제 시: README 파일만 번역",
        
        "progress.translatingWithChangelog": "README + CHANGELOG 번역 중",
        "progress.translatingReadmeOnly": "README만 번역 중",
        "success.filesSavedWithChangelog": "README와 CHANGELOG",
        "success.filesSavedReadmeOnly": "README만",
        "success.translationCompletedWithChangelog": "✅ {count}개 README와 CHANGELOG가 성공적으로 번역되었습니다!",
        "success.translationCompletedReadmeOnly": "✅ {count}개 README가 성공적으로 번역되었습니다!",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.md를 찾을 수 없음 - CHANGELOG 번역 건너뜀",
        
        "errors.changelogGenerateFailed": "❌ CHANGELOG 생성 실패",
        "errors.changelogRemoveSelectedFailed": "❌ 선택한 CHANGELOG 파일 삭제 실패",
        "success.changelogGenerated": "✅ {count}개 언어의 CHANGELOG가 성공적으로 생성되었습니다",
        "success.changelogRemovedSelected": "✅ {count}개 CHANGELOG 파일이 성공적으로 삭제되었습니다",
        "confirmation.removeChangelogSelected": "선택한 {count}개 언어의 CHANGELOG 파일을 삭제하시겠습니까? README 파일은 영향을 받지 않습니다.",
        
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
        "debug_current": "현재",
        "ui.changeLanguage": "표시 언어 변경",
        "ui.currentLanguage": "현재 언어",
        "ui.languageChanged": "✅ 표시 언어가 {name}(으)로 변경되었습니다",
        "ui.languageSelector": "CLI 알림의 표시 언어 선택",
        "ui.translate": "번역하기",
        "ui.removeTranslated": "번역된 언어 삭제",
        "ui.protectionSettings": "보호 설정 (구문)",
        "ui.autoSetupChangelog": "Changelog 섹션 자동 설정",
        "ui.detectGithub": "GitHub URL 감지",
        "ui.repairTranslations": "번역 수정 (중복 및 오류 수정)",
        "ui.setupPaths": "경로 설정",
        "ui.exit": "종료",
        "ui.selectOption": "옵션 선택:",
        "ui.currentProjectPath": "현재 프로젝트 경로",
        "ui.outputDirectory": "출력 디렉토리",
        "ui.folderProject": "프로젝트 폴더",
        "ui.available": "사용 가능",
        "ui.notFound": "찾을 수 없음",
        "ui.notSet": "설정되지 않음",
        "ui.developer": "개발자",
        "ui.exiting": "종료 중...",
        "ui.chooseLanguageCode": "언어 코드 선택 (비워두면 취소):",
        "ui.translationStatus": "번역 상태:",
        "ui.translateBoth": "README 및 CHANGELOG 번역",
        "ui.translateReadme": "README만 번역",
        "ui.translateChangelog": "CHANGELOG만 번역",
        "ui.removeBoth": "README 및 CHANGELOG 삭제",
        "ui.removeReadme": "README만 삭제",
        "ui.removeChangelog": "CHANGELOG만 삭제",
        "ui.back": "뒤로",
        "ui.missing": "누락됨",
        "ui.enterLangCodes": "언어 코드 입력 (쉼표로 구분, 또는 'all'):",
        "ui.invalidOption": "잘못된 옵션입니다.",
        "ui.invalidLanguages": "잘못된 언어입니다.",
        "ui.pressEnter": "계속하려면 Enter를 누르세요...",
        "ui.status": "상태: ",
        "ui.active": "활성",
        "ui.inactive": "비활성",
        "ui.protectedPhrases": "보호된 구문:",
        "ui.noProtectedDir": "- 보호된 구문이 설정되지 않았습니다.",
        "ui.toggleProtection": "보호 상태 전환",
        "ui.addProtection": "보호 구문 추가",
        "ui.removeProtection": "보호 구문 제거",
        "ui.resetDefault": "기본값으로 재설정",
        "ui.enterPhraseAdd": "보호할 구문 입력 (비워두면 취소): ",
        "ui.addedPhrase": "추가됨: {phrase}",
        "ui.enterPhraseRemove": "제거할 구문 입력 (비워두면 취소): ",
        "ui.removedPhrase": "제거됨: {phrase}",
        "ui.phraseNotFound": "구문을 찾을 수 없습니다.",
        "ui.resetSuccess": "기본값으로 재설정되었습니다.",
        "ui.changelogComplete": "Changelog 설정이 완료되었습니다.",
        "ui.changelogFailed": "Changelog 설정에 실패했습니다.",
        "ui.setupPathsMenu": "경로 설정",
        "ui.setTargetDir": "대상 디렉토리 설정",
        "ui.currentDir": "현재: {path}",
        "ui.setOutputBaseDir": "출력 기본 디렉토리 설정",
        "ui.enterTargetDir": "대상 디렉토리 경로 입력:",
        "ui.enterOutputDir": "출력 기본 디렉토리 경로 입력:",
        "ui.typeRoot": "  • 프로젝트 루트를 사용하려면 'root' 입력",
        "ui.typeAuto": "  • 현재 프로젝트에서 docs/lang을 찾으려면 'auto' 입력",
        "ui.leaveEmpty": "  • 비워두면 취소",
        "ui.path": "경로: ",
        "ui.cancelled": "⏭️ 취소되었습니다. 변경사항 없음.",
        "ui.replaceCurrentDir": "⚠️ 현재 디렉토리를 변경합니다:",
        "ui.oldPath": "   이전: {path}",
        "ui.newPath": "   새로: {path}",
        "ui.continueYN": "계속 하시겠습니까? (y/n): ",
        "ui.targetSet": "✅ 대상 디렉토리가 설정되었습니다: {path}",
        "ui.outputSet": "✅ 출력 디렉토리가 설정되었습니다: {path}",
        "ui.targetAlreadySet": "⚠️ 대상 디렉토리가 이미 현재 작업 디렉토리로 설정되어 있습니다.",
        "ui.fileDetected": "📄 파일 경로가 감지되었습니다. 상위 디렉토리 사용: {path}",
        "ui.pathNotFound": "❌ 경로를 찾을 수 없음: {path} \n디렉토리 또는 파일이 있는지 확인하세요.",
        "ui.setOutputAuto": "출력 디렉토리를 현재 프로젝트의 docs/lang으로 설정하시겠습니까? (y/n): ",
        "ui.autoSetSuccess": "✅ 출력 디렉토리가 자동으로 설정되었습니다: {path}",
        "ui.autoSetFailed": "❌ 현재 프로젝트에서 docs/lang 디렉토리를 찾을 수 없습니다.",
        "ui.repairStarting": "번역 복구 도구 시작 중...",
        "ui.repairStep1": "1. 모든 README에서 중복된 스위처를 정리하고 위치를 수정 중...",
        "ui.repairStep2": "2. 번역 문서의 오류(API 오류 / 영문 그대로 남은 부분) 스캔 중...",
        "ui.repairLanguages": "언어: {langs}",
        "ui.looksTranslated": "정상적으로 번역된 것 같습니다.",
        "ui.repairSuccess": "실패한 번역이 감지되지 않았습니다. 모든 파일이 정상적으로 복구되었습니다!",
        "ui.highEnglishOverlap": "영어 중복 비율 높음 ({percent}%)",
        "ui.repairErrorScan": "스캔할 수 없음 ({error})",
        "ui.retranslatingFailed": "{count}개의 실패한 파일 다시 번역 중: {langs}",
        "ui.repairFixed": "복구 완료! 누락된 번역이 수정되었습니다.",
        "ui.enterLangCodesRemove": "삭제할 언어 코드 입력 (쉼표로 구분, 또는 'all'): ",
        "ui.actionCancelled": "취소됨. 삭제 메뉴로 돌아갑니다...",
        "ui.allRemoved": "모든 번역 언어가 삭제되었습니다.",
        "ui.removedList": "삭제됨: {langs}",
        "ui.enterLangCodesRemoveReadme": "삭제할 README 언어 코드 입력 (쉼표로 구분, 또는 'all'): ",
        "ui.removedReadmeList": "README 삭제됨: {langs}",
        "ui.enterLangCodesRemoveChangelog": "삭제할 CHANGELOG 언어 코드 입력 (쉼표로 구분, 또는 'all'): ",
        "ui.removedChangelogFiles": "선택한 CHANGELOG 파일이 삭제되었습니다.",
        "ui.statusLabel": "상태: ",
        "ui.protectedPhrasesList": "보호된 구문:",
        "ui.pkgRepoField": "• package.json (repository 필드)",
        "ui.gitConfig": "• .git/config",
        "ui.readmeGitPattern": "• README.md (GitHub URL 패턴)",
        "ui.pleaseCheck": "\n다음을 확인해 주세요:",
        "ui.checkPkgRepo": "• package.json에 'repository' 필드가 있는지",
        "ui.checkGitRemote": "• .git/config에 원격 URL이 있는지",
        "ui.checkReadmeUrl": "• 또는 GitHub URL을 README에 수동으로 추가하세요",
        "ui.noTranslatedFilesRemove": "⚠️  제거할 번역 파일을 찾을 수 없습니다.",
        "ui.noFilesInOutputDir": "출력 디렉토리에 변경 로그 (CHANGELOG) 파일이 없습니다.",
        "progress.translatingChangelogOnly": "변경 로그 (CHANGELOG)만 번역 중",
        "success.translationCompletedChangelogOnly": "✅ {count}개 변경 로그 (CHANGELOG) 번역 성공!",
        "ui.cannotTranslateBoth": "⚠️  README 와 CHANGELOG를 번역할 수 없습니다.",
        "ui.missingReadmeForBoth": "README.md가 없습니다. [2]로 README만 번역하세요.",
        "ui.missingChangelogForBoth": "CHANGELOG.md가 없습니다. [3]으로 CHANGELOG만 번역하세요.",
        "ui.missingBothFiles": "README.md와 CHANGELOG.md 둘 다 없습니다.",
        "ui.cannotTranslateReadmeOnly": "⚠️  README만 번역할 수 없습니다.",
        "ui.missingReadme": "README.md를 찾을 수 없습니다.",
        "ui.cannotTranslateChangelogOnly": "⚠️  CHANGELOG만 번역할 수 없습니다.",
        "ui.missingChangelog": "CHANGELOG.md를 찾을 수 없습니다.",

        # API Settings
        "ui.apiSettings": "API 설정 (선택 사항)",
        "ui.apiList": "API 목록",
        "ui.apiAdd": "API 추가",
        "ui.apiEdit": "API 편집",
        "ui.apiDelete": "API 삭제",
        "ui.apiToggle": "API 활성화/비활성화",
        "ui.apiName": "API 이름",
        "ui.apiProvider": "제공자",
        "ui.apiToken": "API 토큰",
        "ui.apiStatus": "상태",
        "ui.apiActive": "🟢 활성",
        "ui.apiInactive": "🔴 비활성",
        "ui.apiNoEntries": "API가 설정되지 않았습니다. 기본값: Google 번역 (무료).",
        "ui.apiAdded": "✅ API '{name}'이(가) 추가되었습니다.",
        "ui.apiDeleted": "🗑️ API '{name}'이(가) 삭제되었습니다.",
        "ui.apiUpdated": "✅ API '{name}'이(가) 업데이트되었습니다.",
        "ui.apiEnabled": "🟢 API '{name}'이(가) 활성화되었습니다.",
        "ui.apiDisabled": "🔴 API '{name}'이(가) 비활성화되었습니다.",
        "ui.apiUsing": "🔌 사용 중인 API: {name} ({provider})",
        "ui.apiFallback": "⚠️  Google 번역(무료)으로 대체합니다.",
        "ui.apiSelectProvider": "제공자 선택",
        "ui.apiEnterToken": "API 토큰 입력 (무료 제공자는 빈칸 가능)",
        "ui.apiEnterName": "이 API의 이름을 입력하세요",
        "ui.apiSelectToEdit": "편집할 API 번호 입력",
        "ui.apiSelectToDelete": "삭제할 API 번호 입력",
        "ui.apiSelectToToggle": "활성화/비활성화할 API 번호 입력",
        "ui.apiConfirmDelete": "API '{name}'을(를) 삭제하시겠습니까? [y/N]",
        "ui.apiTestSuccess": "✅ API 테스트 성공: {result}",
        "ui.apiTestFailed": "❌ API 테스트 실패: {error}",
        "ui.apiTesting": "🔍 API 연결 테스트 중...",
        "ui.apiInvalidNumber": "잘못된 API 번호입니다.",
        "ui.apiSavedNote": "💡 API 토큰은 api_config.json에 저장됩니다 (비공개 유지!)",
        "ui.apiMenuTitle": "🔌 API 설정 — 선택적 번역 API",
        "ui.apiActiveCount": "활성 API: {count}/{total}",
        "ui.apiUsingFree": "Google 번역 사용 중 (기본값, API 불필요)",
        "ui.apiCancelHint": "(비워서 취소)",
        "ui.apiTableName": "이름",
        "ui.apiTableProvider": "제공자",
        "ui.apiTableStatus": "상태",
        "ui.apiProviders": "제공자 목록:",
        "ui.apiCancel": "취소",
        "ui.apiEditing": "편집 중: {name} ({provider})",
        "ui.apiNewName": "새 이름 [{name}] (Enter = 유지, q=취소)",
        "ui.apiNewToken": "새 토큰 (Enter = 유지, q=취소)",
        "ui.apiActiveLabel": "활성",
        "ui.provider_google": "Google 번역 (무료, 토큰 불필요)",
        "ui.provider_deepl": "DeepL (무료/Pro — 토큰 필요)",
        "ui.provider_mymemory": "MyMemory (무료, 더 많은 할당량에는 선택적 토큰)",
        "ui.provider_libretranslate": "LibreTranslate (무료 셀프호스팅 / 공개 서버)",
        "ui.provider_yandex": "Yandex 번역 (토큰 필요 — 무료 티어 제공)",
        "ui.provider_microsoft": "Microsoft Azure 번역 (토큰 필요 — 무료 티어 월 200만 자)",
        "ui.provider_papago": "Papago / Naver (한국어에 최적 — client_id:secret_key 형식)",
        "ui.provider_custom": "커스텀 REST API (Bearer 토큰이 있는 HTTP 엔드포인트)",
        "ui.aiSettings": "AI 설정 (선택)",
        "ui.aiMenuTitle": "🤖 AI 설정 — 선택적 AI 제공자",
        "ui.aiSavedNote": "💡 AI 설정이 ai_config.json에 저장됩니다 (비공개 유지!)",
        "ui.aiNoEntries": "AI 제공자가 없습니다.",
        "ui.aiAdd": "AI 제공자 추가",
        "ui.aiEdit": "AI 제공자 편집",
        "ui.aiDelete": "AI 제공자 삭제",
        "ui.aiToggle": "AI 제공자 활성/비활성화",
        "ui.aiActive": "🟢 활성",
        "ui.aiInactive": "🔴 비활성",
        "ui.aiActiveCount": "활성 AI: {count}/{total}",
        "ui.aiUsingDefault": "표준 번역 API 사용 중 (기본값)",
        "ui.aiAdded": "✅ AI '{name}' 추가됨.",
        "ui.aiDeleted": "🗑️ AI '{name}' 삭제됨.",
        "ui.aiUpdated": "✅ AI '{name}' 업데이트됨.",
        "ui.aiEnabled": "🟢 AI '{name}' 활성화됨.",
        "ui.aiDisabled": "🔴 AI '{name}' 비활성화됨.",
        "ui.aiSelectProvider": "AI 제공자 선택",
        "ui.aiProviders": "AI 제공자 목록:",
        "ui.aiEnterName": "이 AI의 이름을 입력하세요",
        "ui.aiAuthType": "인증 방법",
        "ui.aiAuthKey": "[1] API 키",
        "ui.aiAuthBrowser": "[2] 브라우저로 로그인",
        "ui.aiEnterKey": "API 키를 입력하세요",
        "ui.aiBrowserOpening": "🌐 브라우저를 열는 중...",
        "ui.aiBrowserNote": "브라우저가 열렸습니다. 로그인 후 Enter를 누르세요.",
        "ui.aiSelectToEdit": "편집할 AI 번호를 입력하세요",
        "ui.aiSelectToDelete": "삭제할 AI 번호를 입력하세요",
        "ui.aiSelectToToggle": "활성/비활성화할 AI 번호를 입력하세요",
        "ui.aiConfirmDelete": "AI '{name}' 을 삭제하시겠습니까? [y/N]",
        "ui.aiInvalidNumber": "유효하지 않은 AI 번호입니다.",
        "ui.aiActiveLabel": "활성",
        "ui.aiTableName": "이름",
        "ui.aiTableProvider": "제공자",
        "ui.aiTableStatus": "상태",
        "ui.aiTableAuth": "인증",
        "ui.aiEditing": "편집 중: {name} ({provider})",
        "ui.aiNewName": "새 이름 [{name}] (Enter=유지, q=취소)",
        "ui.aiNewKey": "새 API 키 (Enter=유지, q=취소)",
        "ui.aiCancelHint": "(비워서 취소)",
        "ui.ai_provider_openai": "OpenAI ChatGPT (API 키)",
        "ui.ai_provider_gemini": "Google Gemini (API 키)",
        "ui.ai_provider_claude": "Anthropic Claude (API 키)",
        "ui.ai_provider_copilot": "Microsoft Copilot (API 키)",
        "ui.ai_provider_mistral": "Mistral AI (API 키)",
        "ui.ai_provider_perplexity": "Perplexity AI (API 키)",
        "ui.ai_provider_custom": "커스텀 AI (API 엔드포인트 + 키)",
        "ui.tableLimit": "제한",
        "ui.enterLimit": "사용 제한 (기본값 Enter, 예: 50만/월)",
        "ui.limitDefault": "기본값: {value}",
        "ui.apiLimit": "제한 (충전 필요)",
        "ui.aiLimit": "제한 (충전 필요)",
        "ui.tableAccount": "계정",
        "ui.enterAccount": "계정 이름 (선택, 예: fatonyahmadfauzi)",
    },
    "pl": {
        "ui.codeLanguage": "Kod/język",
        "ui.changelogTitle": "LOG ZMIAN",
        "ui.warningDifferentProject": "⚠️ OSTRZEŻENIE: Katalog wyjściowy znajduje się w innym projekcie!",
        "ui.pathOutsideProject": "(Ścieżka znajduje się poza bieżącym folderem projektu)",
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
        "changelog.affectsSelected": "Wpływa tylko na wybrane języki: {count} języków",
        "changelog.generateWith": "📋 Generuj z CHANGELOG",
        "changelog.checkedDescription": "Gdy zaznaczone: Tłumaczy zarówno pliki README jak i CHANGELOG",
        "changelog.uncheckedDescription": "Gdy niezaznaczone: Tłumaczy tylko pliki README",
        
        "progress.translatingWithChangelog": "Tłumaczenie README + CHANGELOG",
        "progress.translatingReadmeOnly": "Tłumaczenie tylko README",
        "success.filesSavedWithChangelog": "READMES i CHANGELOGs",
        "success.filesSavedReadmeOnly": "Tylko READMEs",
        "success.translationCompletedWithChangelog": "✅ {count} READMEs i CHANGELOGs pomyślnie przetłumaczone!",
        "success.translationCompletedReadmeOnly": "✅ {count} READMEs pomyślnie przetłumaczone!",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.md nie znaleziono - pomijam tłumaczenie CHANGELOG",
        
        "errors.changelogGenerateFailed": "❌ Generowanie CHANGELOG nie powiodło się",
        "errors.changelogRemoveSelectedFailed": "❌ Nie udało się usunąć wybranych plików CHANGELOG",
        "success.changelogGenerated": "✅ CHANGELOG pomyślnie wygenerowany dla {count} języków",
        "success.changelogRemovedSelected": "✅ {count} plików CHANGELOG pomyślnie usunięto",
        "confirmation.removeChangelogSelected": "Czy na pewno chcesz usunąć pliki CHANGELOG dla {count} wybranych języków? Pliki README nie zostaną naruszone.",
        
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
        "debug_current": "Obecny",
        "ui.changeLanguage": "Zmień język wyświetlania",
        "ui.currentLanguage": "Aktualny język",
        "ui.languageChanged": "✅ Język wyświetlania zmieniony na {name}",
        "ui.languageSelector": "Wybierz język wyświetlania dla powiadomień CLI",
        "ui.translate": "Tłumacz",
        "ui.removeTranslated": "Usuń przetłumaczone języki",
        "ui.protectionSettings": "Ustawienia ochrony (Frazy)",
        "ui.autoSetupChangelog": "Automatyczna konfiguracja sekcji Changelog",
        "ui.detectGithub": "Wykryj adres URL GitHub",
        "ui.repairTranslations": "Napraw tłumaczenia (Napraw duplikaty i błędy)",
        "ui.setupPaths": "Skonfiguruj ścieżki",
        "ui.exit": "Wyjście",
        "ui.selectOption": "Wybierz opcję:",
        "ui.currentProjectPath": "Obecna ścieżka projektu",
        "ui.outputDirectory": "Katalog wyjściowy",
        "ui.folderProject": "Folder projektu",
        "ui.available": "DOSTĘPNE",
        "ui.notFound": "NIE ZNALEZIONO",
        "ui.notSet": "Nie ustawiono",
        "ui.developer": "Deweloper",
        "ui.exiting": "Zamykanie...",
        "ui.chooseLanguageCode": "Wybierz kod języka (puste aby anulować):",
        "ui.translationStatus": "Status tłumaczenia:",
        "ui.translateBoth": "Tłumacz README i CHANGELOG",
        "ui.translateReadme": "Tłumacz tylko README",
        "ui.translateChangelog": "Tłumacz tylko CHANGELOG",
        "ui.removeBoth": "Usuń README i CHANGELOG",
        "ui.removeReadme": "Usuń tylko README",
        "ui.removeChangelog": "Usuń tylko CHANGELOG",
        "ui.back": "Wstecz",
        "ui.missing": "BRAKUJĄCE",
        "ui.enterLangCodes": "Wprowadź kody języków (oddzielone przecinkami, lub 'all'):",
        "ui.invalidOption": "Nieprawidłowa opcja.",
        "ui.invalidLanguages": "Nieprawidłowe języki.",
        "ui.pressEnter": "Naciśnij Enter, aby kontynuować...",
        "ui.status": "Status: ",
        "ui.active": "AKTYWNY",
        "ui.inactive": "NIEAKTYWNY",
        "ui.protectedPhrases": "Chronione frazy:",
        "ui.noProtectedDir": "- Brak skonfigurowanych chronionych fraz.",
        "ui.toggleProtection": "Przełącz status ochrony",
        "ui.addProtection": "Dodaj chronioną frazę",
        "ui.removeProtection": "Usuń chronioną frazę",
        "ui.resetDefault": "Przywróć ustawienia domyślne",
        "ui.enterPhraseAdd": "Wprowadź frazę do ochrony (puste aby anulować): ",
        "ui.addedPhrase": "Dodano: {phrase}",
        "ui.enterPhraseRemove": "Wprowadź frazę do usunięcia (puste aby anulować): ",
        "ui.removedPhrase": "Usunięto: {phrase}",
        "ui.phraseNotFound": "Nie znaleziono frazy.",
        "ui.resetSuccess": "Zresetowano do ustawień domyślnych.",
        "ui.changelogComplete": "Konfiguracja dziennika zmian zakończona.",
        "ui.changelogFailed": "Konfiguracja dziennika zmian nie powiodła się.",
        "ui.setupPathsMenu": "Setup Paths",
        "ui.setTargetDir": "Set Target Directory",
        "ui.currentDir": "Current: {path}",
        "ui.setOutputBaseDir": "Set Output Base Directory",
        "ui.enterTargetDir": "Enter target directory path:",
        "ui.enterOutputDir": "Enter output base directory path:",
        "ui.typeRoot": "  • Type 'root' to use project root",
        "ui.typeAuto": "  • Type 'auto' to find/use docs/lang in current project",
        "ui.leaveEmpty": "  • Leave empty to cancel",
        "ui.path": "Path: ",
        "ui.cancelled": "⏭️ Cancelled. No changes made.",
        "ui.replaceCurrentDir": "⚠️ This will replace the current directory:",
        "ui.oldPath": "   Old: {path}",
        "ui.newPath": "   New: {path}",
        "ui.continueYN": "Do you want to continue? (y/n): ",
        "ui.targetSet": "✅ Target directory set to: {path}",
        "ui.outputSet": "✅ Output directory set to: {path}",
        "ui.targetAlreadySet": "⚠️ Target directory already set to current working directory.",
        "ui.fileDetected": "📄 File path detected. Using parent directory: {path}",
        "ui.pathNotFound": "❌ Path not found: {path} \nPlease check if directory or file exists.",
        "ui.setOutputAuto": "Set output base directory to docs/lang in this project? (y/n): ",
        "ui.autoSetSuccess": "✅ Output directory automatically set to: {path}",
        "ui.autoSetFailed": "❌ Could not find docs/lang directory in the current project.",
        "ui.repairStarting": "Starting Translation Repair Tool...",
        "ui.repairStep1": "1. Cleaning up duplicate switchers and fixing their positions in all READMEs...",
        "ui.repairStep2": "2. Scanning translated documents for failures (API errors / unchanged English)...",
        "ui.repairLanguages": "Languages: {langs}",
        "ui.looksTranslated": "looks properly translated.",
        "ui.repairSuccess": "No failed translations detected. All files are clean and fully repaired!",
        "ui.highEnglishOverlap": "High English overlap ({percent}%)",
        "ui.repairErrorScan": "Could not scan ({error})",
        "ui.retranslatingFailed": "Re-translating {count} failed files: {langs}",
        "ui.repairFixed": "Repair completed! Missing translations have been fixed.",
        "ui.enterLangCodesRemove": "Enter language codes to remove (comma-separated, or 'all'): ",
        "ui.actionCancelled": "Action cancelled. Returning to remove menu...",
        "ui.allRemoved": "All translated languages removed.",
        "ui.removedList": "Removed: {langs}",
        "ui.enterLangCodesRemoveReadme": "Enter README language codes to remove (comma-separated, or 'all'): ",
        "ui.removedReadmeList": "Removed README: {langs}",
        "ui.enterLangCodesRemoveChangelog": "Enter CHANGELOG language codes to remove (comma-separated, or 'all'): ",
        "ui.removedChangelogFiles": "Selected CHANGELOG files removed.",
        "ui.statusLabel": "Status: ",
        "ui.protectedPhrasesList": "Protected Phrases:",
        "ui.pkgRepoField": "• package.json (repository field)",
        "ui.gitConfig": "• .git/config",
        "ui.readmeGitPattern": "• README.md (GitHub URL patterns)",
        "ui.pleaseCheck": "\nPlease check:",
        "ui.checkPkgRepo": "• package.json has 'repository' field",
        "ui.checkGitRemote": "• .git/config has remote URL",
        "ui.checkReadmeUrl": "• Or add GitHub URL manually to README",
        "ui.noTranslatedFilesRemove": "⚠️  Nie znaleziono przetłumaczonych plików do usunięcia.",
        "ui.noFilesInOutputDir": "W katalogu wyjściowym nie ma plików CHANGELOG (Log Zmian).",
        "progress.translatingChangelogOnly": "Tłumaczenie tylko CHANGELOG (Log Zmian)",
        "success.translationCompletedChangelogOnly": "✅ {count} CHANGELOG (Log Zmian) przetłumaczone pomyślnie!",
        "ui.cannotTranslateBoth": "⚠️  Nie można przetłumaczyć README i CHANGELOG.",
        "ui.missingReadmeForBoth": "Brak README.md. Użyj opcji [2] aby przełumaczyć tylko README.",
        "ui.missingChangelogForBoth": "Brak CHANGELOG.md. Użyj opcji [3] aby przełumaczyć tylko CHANGELOG.",
        "ui.missingBothFiles": "Brak zarówno README.md jak i CHANGELOG.md.",
        "ui.cannotTranslateReadmeOnly": "⚠️  Nie można przełumaczyć tylko README.",
        "ui.missingReadme": "Brak pliku README.md.",
        "ui.cannotTranslateChangelogOnly": "⚠️  Nie można przełumaczyć tylko CHANGELOG.",
        "ui.missingChangelog": "Brak pliku CHANGELOG.md.",

        # API Settings
        "ui.apiSettings": "Ustawienia API (Opcjonalne)",
        "ui.apiList": "Lista API",
        "ui.apiAdd": "Dodaj API",
        "ui.apiEdit": "Edytuj API",
        "ui.apiDelete": "Usuń API",
        "ui.apiToggle": "Włącz/Wyłącz API",
        "ui.apiName": "Nazwa API",
        "ui.apiProvider": "Dostawca",
        "ui.apiToken": "Token API",
        "ui.apiStatus": "Status",
        "ui.apiActive": "🟢 Aktywny",
        "ui.apiInactive": "🔴 Nieaktywny",
        "ui.apiNoEntries": "Brak skonfigurowanych API. Domyślnie: Google Translate (bezpłatny).",
        "ui.apiAdded": "✅ API '{name}' dodane pomyślnie.",
        "ui.apiDeleted": "🗑️ API '{name}' usunięte.",
        "ui.apiUpdated": "✅ API '{name}' zaktualizowane.",
        "ui.apiEnabled": "🟢 API '{name}' włączone.",
        "ui.apiDisabled": "🔴 API '{name}' wyłączone.",
        "ui.apiUsing": "🔌 Używane API: {name} ({provider})",
        "ui.apiFallback": "⚠️  Powrót do Google Translate (bezpłatny).",
        "ui.apiSelectProvider": "Wybierz dostawcę",
        "ui.apiEnterToken": "Wpisz token API (puste dla bezpłatnych dostawców)",
        "ui.apiEnterName": "Wpisz nazwę dla tego API",
        "ui.apiSelectToEdit": "Wpisz numer API do edycji",
        "ui.apiSelectToDelete": "Wpisz numer API do usunięcia",
        "ui.apiSelectToToggle": "Wpisz numer API do włączenia/wyłączenia",
        "ui.apiConfirmDelete": "Czy chcesz usunąć API '{name}'? [y/N]",
        "ui.apiTestSuccess": "✅ Test API udany: {result}",
        "ui.apiTestFailed": "❌ Test API nieudany: {error}",
        "ui.apiTesting": "🔍 Testowanie połączenia API...",
        "ui.apiInvalidNumber": "Nieprawidłowy numer API.",
        "ui.apiSavedNote": "💡 Tokeny API zapisane w api_config.json (zachowaj prywatność!)",
        "ui.apiMenuTitle": "🔌 Ustawienia API — Opcjonalne API tłumaczeń",
        "ui.apiActiveCount": "Aktywne API: {count}/{total}",
        "ui.apiUsingFree": "Używam Google Translate (domyślny, bez API)",
        "ui.apiCancelHint": "(puste = anuluj)",
        "ui.apiTableName": "Nazwa",
        "ui.apiTableProvider": "Dostawca",
        "ui.apiTableStatus": "Status",
        "ui.apiProviders": "Dostawcy:",
        "ui.apiCancel": "Anuluj",
        "ui.apiEditing": "Edytowanie: {name} ({provider})",
        "ui.apiNewName": "Nowa nazwa [{name}] (Enter = zachowaj, q=anuluj)",
        "ui.apiNewToken": "Nowy token (Enter = zachowaj, q=anuluj)",
        "ui.apiActiveLabel": "aktywne",
        "ui.provider_google": "Google Tłumacz (Darmowy, brak tokenu)",
        "ui.provider_deepl": "DeepL (Darmowy/Pro — wymagany token)",
        "ui.provider_mymemory": "MyMemory (Darmowy z opcjonalnym tokenem dla większego limitu)",
        "ui.provider_libretranslate": "LibreTranslate (Darmowy self-hosted / publiczne serwery)",
        "ui.provider_yandex": "Yandex Tłumacz (wymagany token — dostępny bezpłatny poziom)",
        "ui.provider_microsoft": "Microsoft Azure Tłumacz (wymagany token — bezpłatny poziom 2M znaków/mies.)",
        "ui.provider_papago": "Papago / Naver (najlepszy dla koreańskiego — format client_id:secret_key)",
        "ui.provider_custom": "Niestandardowe API REST (dowolny endpoint HTTP z tokenem Bearer)",
        "ui.aiSettings": "Ustawienia AI (Opcjonalne)",
        "ui.aiMenuTitle": "🤖 Ustawienia AI — Opcjonalni dostawcy AI",
        "ui.aiSavedNote": "💡 Konfiguracja AI zapisana w ai_config.json (zachowaj prywatność!)",
        "ui.aiNoEntries": "Brak skonfigurowanych dostawców AI.",
        "ui.aiAdd": "Dodaj dostawcę AI",
        "ui.aiEdit": "Edytuj dostawcę AI",
        "ui.aiDelete": "Usuń dostawcę AI",
        "ui.aiToggle": "Włącz/Wyłącz dostawcę AI",
        "ui.aiActive": "🟢 Aktywny",
        "ui.aiInactive": "🔴 Nieaktywny",
        "ui.aiActiveCount": "Aktywne AI: {count}/{total}",
        "ui.aiUsingDefault": "Korzystam ze standardowych API tłumaczeń (domyślne)",
        "ui.aiAdded": "✅ AI '{name}' dodane.",
        "ui.aiDeleted": "🗑️ AI '{name}' usunięte.",
        "ui.aiUpdated": "✅ AI '{name}' zaktualizowane.",
        "ui.aiEnabled": "🟢 AI '{name}' włączone.",
        "ui.aiDisabled": "🔴 AI '{name}' wyłączone.",
        "ui.aiSelectProvider": "Wybierz dostawcę AI",
        "ui.aiProviders": "Dostawcy AI:",
        "ui.aiEnterName": "Podaj nazwę dla tego AI",
        "ui.aiAuthType": "Metoda uwierzytelniania",
        "ui.aiAuthKey": "[1] Klucz API",
        "ui.aiAuthBrowser": "[2] Logowanie przez przeglądarkę",
        "ui.aiEnterKey": "Podaj klucz API",
        "ui.aiBrowserOpening": "🌐 Otwieranie przeglądarki do logowania...",
        "ui.aiBrowserNote": "Przeglądarka otwarta. Zaloguj się, następnie naciśnij Enter.",
        "ui.aiSelectToEdit": "Podaj numer AI do edycji",
        "ui.aiSelectToDelete": "Podaj numer AI do usunięcia",
        "ui.aiSelectToToggle": "Podaj numer AI do włączenia/wyłączenia",
        "ui.aiConfirmDelete": "Usunąć AI '{name}'? [y/N]",
        "ui.aiInvalidNumber": "Nieprawidłowy numer AI.",
        "ui.aiActiveLabel": "aktywne",
        "ui.aiTableName": "Nazwa",
        "ui.aiTableProvider": "Dostawca",
        "ui.aiTableStatus": "Status",
        "ui.aiTableAuth": "Auth",
        "ui.aiEditing": "Edytowanie: {name} ({provider})",
        "ui.aiNewName": "Nowa nazwa [{name}] (Enter=zachowaj, q=anuluj)",
        "ui.aiNewKey": "Nowy klucz API (Enter=zachowaj, q=anuluj)",
        "ui.aiCancelHint": "(puste = anuluj)",
        "ui.ai_provider_openai": "OpenAI ChatGPT (klucz API lub logowanie przeglądarką)",
        "ui.ai_provider_gemini": "Google Gemini (klucz API lub logowanie przeglądarką)",
        "ui.ai_provider_claude": "Anthropic Claude (klucz API lub logowanie przeglądarką)",
        "ui.ai_provider_copilot": "Microsoft Copilot (logowanie przeglądarką)",
        "ui.ai_provider_mistral": "Mistral AI (klucz API lub logowanie przeglądarką)",
        "ui.ai_provider_perplexity": "Perplexity AI (klucz API lub logowanie przeglądarką)",
        "ui.ai_provider_custom": "Niestandardowe AI (endpoint API + klucz)",
        "ui.tableLimit": "Limit",
        "ui.enterLimit": "Limit użycia (Enter dla domyślnego, np. 500k/mies.)",
        "ui.limitDefault": "Domyślny: {value}",
        "ui.apiLimit": "Limit (Doładuj)",
        "ui.aiLimit": "Limit (Doładuj)",
        "ui.tableAccount": "Konto",
        "ui.enterAccount": "Nazwa konta (opcjonalnie, np: fatonyahmadfauzi)",
    },
    "pt": {
        "ui.codeLanguage": "Código/Idioma",
        "ui.changelogTitle": "REGISTRO DE ALTERAÇÕES",
        "ui.warningDifferentProject": "⚠️ AVISO: O Output Directory está em um projeto diferente!",
        "ui.pathOutsideProject": "(O caminho está fora da pasta do projeto atual)",
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
        "changelog.affectsSelected": "Afeta apenas idiomas selecionados: {count} idiomas",
        "changelog.generateWith": "📋 Gerar com CHANGELOG",
        "changelog.checkedDescription": "Quando marcado: Traduz arquivos README e CHANGELOG",
        "changelog.uncheckedDescription": "Quando desmarcado: Traduz apenas arquivos README",
        
        "progress.translatingWithChangelog": "Traduzindo README + CHANGELOG",
        "progress.translatingReadmeOnly": "Traduzindo apenas README",
        "success.filesSavedWithChangelog": "READMES e CHANGELOGs",
        "success.filesSavedReadmeOnly": "Apenas READMEs",
        "success.translationCompletedWithChangelog": "✅ {count} READMEs e CHANGELOGs traduzidos com sucesso!",
        "success.translationCompletedReadmeOnly": "✅ {count} READMEs traduzidos com sucesso!",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.md não encontrado - ignorando tradução CHANGELOG",
        
        "errors.changelogGenerateFailed": "❌ Falha na geração CHANGELOG",
        "errors.changelogRemoveSelectedFailed": "❌ Falha ao remover arquivos CHANGELOG selecionados",
        "success.changelogGenerated": "✅ CHANGELOG gerado com sucesso para {count} idiomas",
        "success.changelogRemovedSelected": "✅ {count} arquivos CHANGELOG removidos com sucesso",
        "confirmation.removeChangelogSelected": "Tem certeza de que deseja remover arquivos CHANGELOG para {count} idiomas selecionados? Arquivos README não serão afetados.",
        
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
        "debug_current": "Atual",
        "ui.changeLanguage": "Alterar idioma de exibição",
        "ui.currentLanguage": "Idioma atual",
        "ui.languageChanged": "✅ Idioma de exibição alterado para {name}",
        "ui.languageSelector": "Selecionar idioma de exibição para notificações CLI",
        "ui.translate": "Traduzir",
        "ui.removeTranslated": "Remover idiomas traduzidos",
        "ui.protectionSettings": "Configurações de proteção (Frases)",
        "ui.autoSetupChangelog": "Configuração automática de Changelog",
        "ui.detectGithub": "Detectar URL do GitHub",
        "ui.repairTranslations": "Reparar traduções (Corrigir duplicatas e falhas)",
        "ui.setupPaths": "Configurar caminhos",
        "ui.exit": "Sair",
        "ui.selectOption": "Selecione uma opção:",
        "ui.currentProjectPath": "Caminho atual do projeto",
        "ui.outputDirectory": "Diretório de saída",
        "ui.folderProject": "Pasta do projeto",
        "ui.available": "DISPONÍVEL",
        "ui.notFound": "NÃO ENCONTRADO",
        "ui.notSet": "Não definido",
        "ui.developer": "Desenvolvedor",
        "ui.exiting": "Saindo...",
        "ui.chooseLanguageCode": "Escolha o código do idioma (vazio para cancelar):",
        "ui.translationStatus": "Status de Tradução:",
        "ui.translateBoth": "Traduzir README & CHANGELOG",
        "ui.translateReadme": "Traduzir apenas README",
        "ui.translateChangelog": "Traduzir apenas CHANGELOG",
        "ui.removeBoth": "Remover README & CHANGELOG",
        "ui.removeReadme": "Remover apenas README",
        "ui.removeChangelog": "Remover apenas CHANGELOG",
        "ui.back": "Voltar",
        "ui.missing": "FALTANDO",
        "ui.enterLangCodes": "Insira os códigos de idioma (separados por vírgula, ou 'all'):",
        "ui.invalidOption": "Opção inválida.",
        "ui.invalidLanguages": "Idiomas inválidos.",
        "ui.pressEnter": "Pressione Enter para continuar...",
        "ui.status": "Status: ",
        "ui.active": "ATIVO",
        "ui.inactive": "INATIVO",
        "ui.protectedPhrases": "Frases Protegidas:",
        "ui.noProtectedDir": "- Nenhuma frase protegida configurada.",
        "ui.toggleProtection": "Alternar Status de Proteção",
        "ui.addProtection": "Adicionar Frase Protegida",
        "ui.removeProtection": "Remover Frase Protegida",
        "ui.resetDefault": "Restaurar Padrões",
        "ui.enterPhraseAdd": "Insira uma frase a proteger (vazio para cancelar): ",
        "ui.addedPhrase": "Adicionado: {phrase}",
        "ui.enterPhraseRemove": "Insira uma frase a remover (vazio para cancelar): ",
        "ui.removedPhrase": "Removido: {phrase}",
        "ui.phraseNotFound": "Frase não encontrada.",
        "ui.resetSuccess": "Redefinido para os padrões.",
        "ui.changelogComplete": "Configuração do Changelog concluída.",
        "ui.changelogFailed": "Falha na configuração do Changelog.",
        "ui.setupPathsMenu": "Setup Paths",
        "ui.setTargetDir": "Set Target Directory",
        "ui.currentDir": "Current: {path}",
        "ui.setOutputBaseDir": "Set Output Base Directory",
        "ui.enterTargetDir": "Enter target directory path:",
        "ui.enterOutputDir": "Enter output base directory path:",
        "ui.typeRoot": "  • Type 'root' to use project root",
        "ui.typeAuto": "  • Type 'auto' to find/use docs/lang in current project",
        "ui.leaveEmpty": "  • Leave empty to cancel",
        "ui.path": "Path: ",
        "ui.cancelled": "⏭️ Cancelled. No changes made.",
        "ui.replaceCurrentDir": "⚠️ This will replace the current directory:",
        "ui.oldPath": "   Old: {path}",
        "ui.newPath": "   New: {path}",
        "ui.continueYN": "Do you want to continue? (y/n): ",
        "ui.targetSet": "✅ Target directory set to: {path}",
        "ui.outputSet": "✅ Output directory set to: {path}",
        "ui.targetAlreadySet": "⚠️ Target directory already set to current working directory.",
        "ui.fileDetected": "📄 File path detected. Using parent directory: {path}",
        "ui.pathNotFound": "❌ Path not found: {path} \nPlease check if directory or file exists.",
        "ui.setOutputAuto": "Set output base directory to docs/lang in this project? (y/n): ",
        "ui.autoSetSuccess": "✅ Output directory automatically set to: {path}",
        "ui.autoSetFailed": "❌ Could not find docs/lang directory in the current project.",
        "ui.repairStarting": "Starting Translation Repair Tool...",
        "ui.repairStep1": "1. Cleaning up duplicate switchers and fixing their positions in all READMEs...",
        "ui.repairStep2": "2. Scanning translated documents for failures (API errors / unchanged English)...",
        "ui.repairLanguages": "Languages: {langs}",
        "ui.looksTranslated": "looks properly translated.",
        "ui.repairSuccess": "No failed translations detected. All files are clean and fully repaired!",
        "ui.highEnglishOverlap": "High English overlap ({percent}%)",
        "ui.repairErrorScan": "Could not scan ({error})",
        "ui.retranslatingFailed": "Re-translating {count} failed files: {langs}",
        "ui.repairFixed": "Repair completed! Missing translations have been fixed.",
        "ui.enterLangCodesRemove": "Enter language codes to remove (comma-separated, or 'all'): ",
        "ui.actionCancelled": "Action cancelled. Returning to remove menu...",
        "ui.allRemoved": "All translated languages removed.",
        "ui.removedList": "Removed: {langs}",
        "ui.enterLangCodesRemoveReadme": "Enter README language codes to remove (comma-separated, or 'all'): ",
        "ui.removedReadmeList": "Removed README: {langs}",
        "ui.enterLangCodesRemoveChangelog": "Enter CHANGELOG language codes to remove (comma-separated, or 'all'): ",
        "ui.removedChangelogFiles": "Selected CHANGELOG files removed.",
        "ui.statusLabel": "Status: ",
        "ui.protectedPhrasesList": "Protected Phrases:",
        "ui.pkgRepoField": "• package.json (repository field)",
        "ui.gitConfig": "• .git/config",
        "ui.readmeGitPattern": "• README.md (GitHub URL patterns)",
        "ui.pleaseCheck": "\nPlease check:",
        "ui.checkPkgRepo": "• package.json has 'repository' field",
        "ui.checkGitRemote": "• .git/config has remote URL",
        "ui.checkReadmeUrl": "• Or add GitHub URL manually to README",
        "ui.noTranslatedFilesRemove": "⚠️  Nenhum arquivo traduzido encontrado para remover.",
        "ui.noFilesInOutputDir": "Não há arquivos CHANGELOG (Registro de Alterações) no diretório de saída.",
        "progress.translatingChangelogOnly": "Traduzindo apenas CHANGELOG (Registro de Alterações)",
        "success.translationCompletedChangelogOnly": "✅ {count} CHANGELOG (Registros de Alterações) traduzidos com sucesso!",
        "ui.cannotTranslateBoth": "⚠️  Não é possível traduzir README & CHANGELOG.",
        "ui.missingReadmeForBoth": "README.md está ausente. Use a opção [2] para traduzir apenas o README.",
        "ui.missingChangelogForBoth": "CHANGELOG.md está ausente. Use a opção [3] para traduzir apenas o CHANGELOG.",
        "ui.missingBothFiles": "Tanto README.md quanto CHANGELOG.md estão ausentes.",
        "ui.cannotTranslateReadmeOnly": "⚠️  Não é possível traduzir apenas o README.",
        "ui.missingReadme": "README.md está ausente.",
        "ui.cannotTranslateChangelogOnly": "⚠️  Não é possível traduzir apenas o CHANGELOG.",
        "ui.missingChangelog": "CHANGELOG.md está ausente.",

        # API Settings
        "ui.apiSettings": "Configurações de API (Opcional)",
        "ui.apiList": "Lista de APIs",
        "ui.apiAdd": "Adicionar API",
        "ui.apiEdit": "Editar API",
        "ui.apiDelete": "Excluir API",
        "ui.apiToggle": "Ativar/Desativar API",
        "ui.apiName": "Nome da API",
        "ui.apiProvider": "Provedor",
        "ui.apiToken": "Token de API",
        "ui.apiStatus": "Status",
        "ui.apiActive": "🟢 Ativo",
        "ui.apiInactive": "🔴 Inativo",
        "ui.apiNoEntries": "Nenhuma API configurada. Usando Google Tradutor (gratuito) por padrão.",
        "ui.apiAdded": "✅ API '{name}' adicionada com sucesso.",
        "ui.apiDeleted": "🗑️ API '{name}' excluída.",
        "ui.apiUpdated": "✅ API '{name}' atualizada.",
        "ui.apiEnabled": "🟢 API '{name}' ativada.",
        "ui.apiDisabled": "🔴 API '{name}' desativada.",
        "ui.apiUsing": "🔌 Usando API: {name} ({provider})",
        "ui.apiFallback": "⚠️  Usando Google Tradutor (gratuito) como alternativa.",
        "ui.apiSelectProvider": "Selecionar provedor",
        "ui.apiEnterToken": "Digite o token da API (deixe em branco para provedores gratuitos)",
        "ui.apiEnterName": "Digite um nome para esta API",
        "ui.apiSelectToEdit": "Digite o número da API para editar",
        "ui.apiSelectToDelete": "Digite o número da API para excluir",
        "ui.apiSelectToToggle": "Digite o número da API para ativar/desativar",
        "ui.apiConfirmDelete": "Excluir API '{name}'? [y/N]",
        "ui.apiTestSuccess": "✅ Teste de API bem-sucedido: {result}",
        "ui.apiTestFailed": "❌ Falha no teste de API: {error}",
        "ui.apiTesting": "🔍 Testando conexão de API...",
        "ui.apiInvalidNumber": "Número de API inválido.",
        "ui.apiSavedNote": "💡 Tokens salvos em api_config.json (mantenha privado!)",
        "ui.apiMenuTitle": "🔌 Configurações de API — APIs de tradução opcionais",
        "ui.apiActiveCount": "APIs ativas: {count}/{total}",
        "ui.apiUsingFree": "Usando Google Tradutor (padrão, sem API necessária)",
        "ui.apiCancelHint": "(vazio para cancelar)",
        "ui.apiTableName": "Nome",
        "ui.apiTableProvider": "Provedor",
        "ui.apiTableStatus": "Status",
        "ui.apiProviders": "Provedores:",
        "ui.apiCancel": "Cancelar",
        "ui.apiEditing": "Editando: {name} ({provider})",
        "ui.apiNewName": "Novo nome [{name}] (Enter = manter, q=cancelar)",
        "ui.apiNewToken": "Novo token (Enter = manter, q=cancelar)",
        "ui.apiActiveLabel": "ativo",
        "ui.provider_google": "Google Tradutor (Gratuito, sem token necessário)",
        "ui.provider_deepl": "DeepL (Gratuito/Pro — token necessário)",
        "ui.provider_mymemory": "MyMemory (Gratuito com token opcional para maior cota)",
        "ui.provider_libretranslate": "LibreTranslate (Self-hosted gratuito / servidores públicos)",
        "ui.provider_yandex": "Yandex Tradutor (token necessário — nível gratuito disponível)",
        "ui.provider_microsoft": "Microsoft Azure Tradutor (token necessário — nível gratuito 2M car/mês)",
        "ui.provider_papago": "Papago / Naver (melhor para coreano — formato client_id:secret_key)",
        "ui.provider_custom": "API REST personalizada (qualquer endpoint HTTP com token Bearer)",
        "ui.aiSettings": "Configurações de IA (Opcional)",
        "ui.aiMenuTitle": "🤖 Configurações de IA — Provedores de IA opcionais",
        "ui.aiSavedNote": "💡 Configuração de IA salva em ai_config.json (manter privado!)",
        "ui.aiNoEntries": "Nenhum provedor de IA configurado.",
        "ui.aiAdd": "Adicionar provedor de IA",
        "ui.aiEdit": "Editar provedor de IA",
        "ui.aiDelete": "Excluir provedor de IA",
        "ui.aiToggle": "Ativar/Desativar provedor de IA",
        "ui.aiActive": "🟢 Ativo",
        "ui.aiInactive": "🔴 Inativo",
        "ui.aiActiveCount": "IA ativas: {count}/{total}",
        "ui.aiUsingDefault": "Usando APIs de tradução padrão (padrão)",
        "ui.aiAdded": "✅ IA '{name}' adicionada.",
        "ui.aiDeleted": "🗑️ IA '{name}' excluída.",
        "ui.aiUpdated": "✅ IA '{name}' atualizada.",
        "ui.aiEnabled": "🟢 IA '{name}' ativada.",
        "ui.aiDisabled": "🔴 IA '{name}' desativada.",
        "ui.aiSelectProvider": "Selecionar provedor de IA",
        "ui.aiProviders": "Provedores de IA:",
        "ui.aiEnterName": "Digite um nome para esta IA",
        "ui.aiAuthType": "Método de autenticação",
        "ui.aiAuthKey": "[1] Chave API",
        "ui.aiAuthBrowser": "[2] Login pelo navegador",
        "ui.aiEnterKey": "Digite a chave API",
        "ui.aiBrowserOpening": "🌐 Abrindo o navegador para login...",
        "ui.aiBrowserNote": "Navegador aberto. Faça login e pressione Enter.",
        "ui.aiSelectToEdit": "Digite o número da IA para editar",
        "ui.aiSelectToDelete": "Digite o número da IA para excluir",
        "ui.aiSelectToToggle": "Digite o número da IA para ativar/desativar",
        "ui.aiConfirmDelete": "Excluir IA '{name}'? [y/N]",
        "ui.aiInvalidNumber": "Número de IA inválido.",
        "ui.aiActiveLabel": "ativo",
        "ui.aiTableName": "Nome",
        "ui.aiTableProvider": "Provedor",
        "ui.aiTableStatus": "Status",
        "ui.aiTableAuth": "Auth",
        "ui.aiEditing": "Editando: {name} ({provider})",
        "ui.aiNewName": "Novo nome [{name}] (Enter=manter, q=cancelar)",
        "ui.aiNewKey": "Nova chave API (Enter=manter, q=cancelar)",
        "ui.aiCancelHint": "(vazio para cancelar)",
        "ui.ai_provider_openai": "OpenAI ChatGPT (chave API ou login pelo navegador)",
        "ui.ai_provider_gemini": "Google Gemini (chave API ou login pelo navegador)",
        "ui.ai_provider_claude": "Anthropic Claude (chave API ou login pelo navegador)",
        "ui.ai_provider_copilot": "Microsoft Copilot (login pelo navegador)",
        "ui.ai_provider_mistral": "Mistral AI (chave API ou login pelo navegador)",
        "ui.ai_provider_perplexity": "Perplexity AI (chave API ou login pelo navegador)",
        "ui.ai_provider_custom": "IA personalizada (endpoint API + chave)",
        "ui.tableLimit": "Limite",
        "ui.enterLimit": "Limite de uso (Enter para padrão, ex. 500k/mês)",
        "ui.limitDefault": "Padrão: {value}",
        "ui.apiLimit": "Limite (Recarregar)",
        "ui.aiLimit": "Limite (Recarregar)",
        "ui.tableAccount": "Conta",
        "ui.enterAccount": "Nome de usuário (opcional, ex: fatonyahmadfauzi)",
    },
    "ru": {
        "ui.codeLanguage": "Код/Язык",
        "ui.changelogTitle": "ИЗМЕНЕНИЯ",
        "ui.warningDifferentProject": "⚠️ ВНИМАНИЕ: каталог вывода находится в другом проекте!",
        "ui.pathOutsideProject": "(Путь находится за пределами текущей папки проекта)",
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
        "changelog.affectsSelected": "Затрагивает только выбранные языки: {count} языков",
        "changelog.generateWith": "📋 Генерировать с CHANGELOG",
        "changelog.checkedDescription": "Когда отмечено: Переводит файлы README и CHANGELOG",
        "changelog.uncheckedDescription": "Когда не отмечено: Переводит только файлы README",
        
        "progress.translatingWithChangelog": "Перевод README + CHANGELOG",
        "progress.translatingReadmeOnly": "Перевод только README",
        "success.filesSavedWithChangelog": "READMES и CHANGELOGs",
        "success.filesSavedReadmeOnly": "Только READMEs",
        "success.translationCompletedWithChangelog": "✅ {count} READMEs и CHANGELOGs успешно переведены!",
        "success.translationCompletedReadmeOnly": "✅ {count} READMEs успешно переведены!",
        "info.noChangelogFileSkipping": "⚠️ CHANGELOG.md не найден - пропускаю перевод CHANGELOG",
        
        "errors.changelogGenerateFailed": "❌ Ошибка генерации CHANGELOG",
        "errors.changelogRemoveSelectedFailed": "❌ Ошибка удаления выбранных файлов CHANGELOG",
        "success.changelogGenerated": "✅ CHANGELOG успешно сгенерирован для {count} языков",
        "success.changelogRemovedSelected": "✅ {count} файлов CHANGELOG успешно удалено",
        "confirmation.removeChangelogSelected": "Вы уверены, что хотите удалить файлы CHANGELOG для {count} выбранных языков? Файлы README не будут затронуты.",
        
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
        "debug_current": "Текущий",
        "ui.changeLanguage": "Изменить язык отображения",
        "ui.currentLanguage": "Текущий язык",
        "ui.languageChanged": "✅ Язык отображения изменен на {name}",
        "ui.languageSelector": "Выбрать язык отображения для уведомлений CLI",
        "ui.translate": "Перевести",
        "ui.removeTranslated": "Удалить переведенные языки",
        "ui.protectionSettings": "Настройки защиты (Фразы)",
        "ui.autoSetupChangelog": "Автоматическая настройка Changelog",
        "ui.detectGithub": "Определить URL GitHub",
        "ui.repairTranslations": "Восстановить переводы (Исправить дубликаты и ошибки)",
        "ui.setupPaths": "Настроить пути",
        "ui.exit": "Выход",
        "ui.selectOption": "Выберите опцию:",
        "ui.currentProjectPath": "Текущий путь к проекту",
        "ui.outputDirectory": "Выходной каталог",
        "ui.folderProject": "Папка проекта",
        "ui.available": "ДОСТУПНО",
        "ui.notFound": "НЕ НАЙДЕНО",
        "ui.notSet": "Не задано",
        "ui.developer": "Разработчик",
        "ui.exiting": "Выход...",
        "ui.chooseLanguageCode": "Выберите код языка (пусто для отмены):",
        "ui.translationStatus": "Статус перевода:",
        "ui.translateBoth": "Перевести README и CHANGELOG",
        "ui.translateReadme": "Перевести только README",
        "ui.translateChangelog": "Перевести только CHANGELOG",
        "ui.removeBoth": "Удалить README и CHANGELOG",
        "ui.removeReadme": "Удалить только README",
        "ui.removeChangelog": "Удалить только CHANGELOG",
        "ui.back": "Назад",
        "ui.missing": "ОТСУТСТВУЕТ",
        "ui.enterLangCodes": "Введите коды языков (через запятую, или 'all'):",
        "ui.invalidOption": "Недопустимый параметр.",
        "ui.invalidLanguages": "Недопустимые языки.",
        "ui.pressEnter": "Нажмите Enter для продолжения...",
        "ui.status": "Статус: ",
        "ui.active": "АКТИВЕН",
        "ui.inactive": "НЕ АКТИВЕН",
        "ui.protectedPhrases": "Защищенные фразы:",
        "ui.noProtectedDir": "- Защищенные фразы не настроены.",
        "ui.toggleProtection": "Переключить статус защиты",
        "ui.addProtection": "Добавить защищенную фразу",
        "ui.removeProtection": "Удалить защищенную фразу",
        "ui.resetDefault": "Сброс к настройкам по умолчанию",
        "ui.enterPhraseAdd": "Введите фразу для защиты (пусто для отмены): ",
        "ui.addedPhrase": "Добавлено: {phrase}",
        "ui.enterPhraseRemove": "Введите фразу для удаления (пусто для отмены): ",
        "ui.removedPhrase": "Удалено: {phrase}",
        "ui.phraseNotFound": "Фраза не найдена.",
        "ui.resetSuccess": "Сброшено до значений по умолчанию.",
        "ui.changelogComplete": "Настройка списка изменений завершена.",
        "ui.changelogFailed": "Ошибка настройки списка изменений.",
        "ui.setupPathsMenu": "Setup Paths",
        "ui.setTargetDir": "Set Target Directory",
        "ui.currentDir": "Current: {path}",
        "ui.setOutputBaseDir": "Set Output Base Directory",
        "ui.enterTargetDir": "Enter target directory path:",
        "ui.enterOutputDir": "Enter output base directory path:",
        "ui.typeRoot": "  • Type 'root' to use project root",
        "ui.typeAuto": "  • Type 'auto' to find/use docs/lang in current project",
        "ui.leaveEmpty": "  • Leave empty to cancel",
        "ui.path": "Path: ",
        "ui.cancelled": "⏭️ Cancelled. No changes made.",
        "ui.replaceCurrentDir": "⚠️ This will replace the current directory:",
        "ui.oldPath": "   Old: {path}",
        "ui.newPath": "   New: {path}",
        "ui.continueYN": "Do you want to continue? (y/n): ",
        "ui.targetSet": "✅ Target directory set to: {path}",
        "ui.outputSet": "✅ Output directory set to: {path}",
        "ui.targetAlreadySet": "⚠️ Target directory already set to current working directory.",
        "ui.fileDetected": "📄 File path detected. Using parent directory: {path}",
        "ui.pathNotFound": "❌ Path not found: {path} \nPlease check if directory or file exists.",
        "ui.setOutputAuto": "Set output base directory to docs/lang in this project? (y/n): ",
        "ui.autoSetSuccess": "✅ Output directory automatically set to: {path}",
        "ui.autoSetFailed": "❌ Could not find docs/lang directory in the current project.",
        "ui.repairStarting": "Starting Translation Repair Tool...",
        "ui.repairStep1": "1. Cleaning up duplicate switchers and fixing their positions in all READMEs...",
        "ui.repairStep2": "2. Scanning translated documents for failures (API errors / unchanged English)...",
        "ui.repairLanguages": "Languages: {langs}",
        "ui.looksTranslated": "looks properly translated.",
        "ui.repairSuccess": "No failed translations detected. All files are clean and fully repaired!",
        "ui.highEnglishOverlap": "High English overlap ({percent}%)",
        "ui.repairErrorScan": "Could not scan ({error})",
        "ui.retranslatingFailed": "Re-translating {count} failed files: {langs}",
        "ui.repairFixed": "Repair completed! Missing translations have been fixed.",
        "ui.enterLangCodesRemove": "Enter language codes to remove (comma-separated, or 'all'): ",
        "ui.actionCancelled": "Action cancelled. Returning to remove menu...",
        "ui.allRemoved": "All translated languages removed.",
        "ui.removedList": "Removed: {langs}",
        "ui.enterLangCodesRemoveReadme": "Enter README language codes to remove (comma-separated, or 'all'): ",
        "ui.removedReadmeList": "Removed README: {langs}",
        "ui.enterLangCodesRemoveChangelog": "Enter CHANGELOG language codes to remove (comma-separated, or 'all'): ",
        "ui.removedChangelogFiles": "Selected CHANGELOG files removed.",
        "ui.statusLabel": "Status: ",
        "ui.protectedPhrasesList": "Protected Phrases:",
        "ui.pkgRepoField": "• package.json (repository field)",
        "ui.gitConfig": "• .git/config",
        "ui.readmeGitPattern": "• README.md (GitHub URL patterns)",
        "ui.pleaseCheck": "\nPlease check:",
        "ui.checkPkgRepo": "• package.json has 'repository' field",
        "ui.checkGitRemote": "• .git/config has remote URL",
        "ui.checkReadmeUrl": "• Or add GitHub URL manually to README",
        "ui.noTranslatedFilesRemove": "⚠️  Не найдено переведённых файлов для удаления.",
        "ui.noFilesInOutputDir": "В выходном каталоге нет файлов ИЗМЕНЕНИЙ (CHANGELOG).",
        "progress.translatingChangelogOnly": "Перевод только ИЗМЕНЕНИЙ (CHANGELOG)",
        "success.translationCompletedChangelogOnly": "✅ {count} файлов ИЗМЕНЕНИЙ (CHANGELOG) успешно переведено!",
        "ui.cannotTranslateBoth": "⚠️  Невозможно перевести README и CHANGELOG.",
        "ui.missingReadmeForBoth": "README.md отсутствует. Используйте опцию [2] для перевода только README.",
        "ui.missingChangelogForBoth": "CHANGELOG.md отсутствует. Используйте опцию [3] для перевода только CHANGELOG.",
        "ui.missingBothFiles": "Отсутствуют как README.md, так и CHANGELOG.md.",
        "ui.cannotTranslateReadmeOnly": "⚠️  Невозможно перевести только README.",
        "ui.missingReadme": "README.md отсутствует.",
        "ui.cannotTranslateChangelogOnly": "⚠️  Невозможно перевести только CHANGELOG.",
        "ui.missingChangelog": "CHANGELOG.md отсутствует.",

        # API Settings
        "ui.apiSettings": "Настройки API (Опционально)",
        "ui.apiList": "Список API",
        "ui.apiAdd": "Добавить API",
        "ui.apiEdit": "Изменить API",
        "ui.apiDelete": "Удалить API",
        "ui.apiToggle": "Включить/Выключить API",
        "ui.apiName": "Название API",
        "ui.apiProvider": "Провайдер",
        "ui.apiToken": "Токен API",
        "ui.apiStatus": "Статус",
        "ui.apiActive": "🟢 Активен",
        "ui.apiInactive": "🔴 Неактивен",
        "ui.apiNoEntries": "API не настроены. По умолчанию используется Google Переводчик (бесплатно).",
        "ui.apiAdded": "✅ API '{name}' успешно добавлен.",
        "ui.apiDeleted": "🗑️ API '{name}' удалён.",
        "ui.apiUpdated": "✅ API '{name}' обновлён.",
        "ui.apiEnabled": "🟢 API '{name}' включён.",
        "ui.apiDisabled": "🔴 API '{name}' выключен.",
        "ui.apiUsing": "🔌 Используется API: {name} ({provider})",
        "ui.apiFallback": "⚠️  Переход на Google Переводчик (бесплатно).",
        "ui.apiSelectProvider": "Выберите провайдера",
        "ui.apiEnterToken": "Введите токен API (оставьте пустым для бесплатных провайдеров)",
        "ui.apiEnterName": "Введите имя для этого API",
        "ui.apiSelectToEdit": "Введите номер API для редактирования",
        "ui.apiSelectToDelete": "Введите номер API для удаления",
        "ui.apiSelectToToggle": "Введите номер API для включения/выключения",
        "ui.apiConfirmDelete": "Удалить API '{name}'? [y/N]",
        "ui.apiTestSuccess": "✅ Тест API успешен: {result}",
        "ui.apiTestFailed": "❌ Тест API завершился ошибкой: {error}",
        "ui.apiTesting": "🔍 Проверка подключения к API...",
        "ui.apiInvalidNumber": "Неверный номер API.",
        "ui.apiSavedNote": "💡 Токены сохранены в api_config.json (держите файл в тайне!)",
        "ui.apiMenuTitle": "🔌 Настройки API — Опциональные переводческие API",
        "ui.apiActiveCount": "Активных API: {count}/{total}",
        "ui.apiUsingFree": "Используется Google Переводчик (по умолчанию, API не нужен)",
        "ui.apiCancelHint": "(пусто = отмена)",
        "ui.apiTableName": "Название",
        "ui.apiTableProvider": "Провайдер",
        "ui.apiTableStatus": "Статус",
        "ui.apiProviders": "Провайдеры:",
        "ui.apiCancel": "Отмена",
        "ui.apiEditing": "Редактирование: {name} ({provider})",
        "ui.apiNewName": "Новое название [{name}] (Enter = оставить, q=отмена)",
        "ui.apiNewToken": "Новый токен (Enter = оставить, q=отмена)",
        "ui.apiActiveLabel": "активных",
        "ui.provider_google": "Google Переводчик (Бесплатно, токен не нужен)",
        "ui.provider_deepl": "DeepL (Бесплатно/Pro — требуется токен)",
        "ui.provider_mymemory": "MyMemory (Бесплатно, опциональный токен для большей квоты)",
        "ui.provider_libretranslate": "LibreTranslate (Бесплатный self-hosted / публичные серверы)",
        "ui.provider_yandex": "Яндекс.Переводчик (требуется токен — доступен бесплатный уровень)",
        "ui.provider_microsoft": "Microsoft Azure Переводчик (требуется токен — бесплатный уровень 2М сим/мес)",
        "ui.provider_papago": "Papago / Naver (лучший для корейского — формат client_id:secret_key)",
        "ui.provider_custom": "Пользовательский REST API (любой HTTP-эндпоинт с Bearer-токеном)",
        "ui.aiSettings": "Настройки ИИ (Опционально)",
        "ui.aiMenuTitle": "🤖 Настройки ИИ — Опциональные провайдеры ИИ",
        "ui.aiSavedNote": "💡 Конфиг ИИ сохранён в ai_config.json (храните в тайне!)",
        "ui.aiNoEntries": "Провайдеры ИИ не настроены.",
        "ui.aiAdd": "Добавить провайдер ИИ",
        "ui.aiEdit": "Редактировать провайдер ИИ",
        "ui.aiDelete": "Удалить провайдер ИИ",
        "ui.aiToggle": "Включить/выключить провайдер ИИ",
        "ui.aiActive": "🟢 Активен",
        "ui.aiInactive": "🔴 Неактивен",
        "ui.aiActiveCount": "Активных ИИ: {count}/{total}",
        "ui.aiUsingDefault": "Используются стандартные API (по умолчанию)",
        "ui.aiAdded": "✅ ИИ '{name}' добавлена.",
        "ui.aiDeleted": "🗑️ ИИ '{name}' удалена.",
        "ui.aiUpdated": "✅ ИИ '{name}' обновлена.",
        "ui.aiEnabled": "🟢 ИИ '{name}' включена.",
        "ui.aiDisabled": "🔴 ИИ '{name}' выключена.",
        "ui.aiSelectProvider": "Выберите провайдер ИИ",
        "ui.aiProviders": "Провайдеры ИИ:",
        "ui.aiEnterName": "Введите название для этой ИИ",
        "ui.aiAuthType": "Метод авторизации",
        "ui.aiAuthKey": "[1] API-токен",
        "ui.aiAuthBrowser": "[2] Вход через браузер",
        "ui.aiEnterKey": "Введите API-токен",
        "ui.aiBrowserOpening": "🌐 Открываем браузер...",
        "ui.aiBrowserNote": "Браузер открыт. Войдите, затем нажмите Enter.",
        "ui.aiSelectToEdit": "Введите номер ИИ для редактирования",
        "ui.aiSelectToDelete": "Введите номер ИИ для удаления",
        "ui.aiSelectToToggle": "Введите номер ИИ для вкл/выкл",
        "ui.aiConfirmDelete": "Удалить ИИ '{name}'? [y/N]",
        "ui.aiInvalidNumber": "Неверный номер ИИ.",
        "ui.aiActiveLabel": "активных",
        "ui.aiTableName": "Название",
        "ui.aiTableProvider": "Провайдер",
        "ui.aiTableStatus": "Статус",
        "ui.aiTableAuth": "Аутент",
        "ui.aiEditing": "Редактирование: {name} ({provider})",
        "ui.aiNewName": "Новое название [{name}] (Enter=оставить, q=отмена)",
        "ui.aiNewKey": "Новый API-токен (Enter=оставить, q=отмена)",
        "ui.aiCancelHint": "(пусто = отмена)",
        "ui.ai_provider_openai": "OpenAI ChatGPT (API-токен или вход через браузер)",
        "ui.ai_provider_gemini": "Google Gemini (API-токен или вход через браузер)",
        "ui.ai_provider_claude": "Anthropic Claude (API-токен или вход через браузер)",
        "ui.ai_provider_copilot": "Microsoft Copilot (API ключ)",
        "ui.ai_provider_mistral": "Mistral AI (API-токен или вход через браузер)",
        "ui.ai_provider_perplexity": "Perplexity AI (API-токен или вход через браузер)",
        "ui.ai_provider_custom": "Пользовательский ИИ (HTTP-эндпоинт + токен)",
        "ui.tableLimit": "Лимит",
        "ui.enterLimit": "Лимит использования (Enter для умолчания, напр. 500k/мес)",
        "ui.limitDefault": "По умолчанию: {value}",
        "ui.apiLimit": "Лимит (Пополнить)",
        "ui.aiLimit": "Лимит (Пополнить)",
        "ui.tableAccount": "Аккаунт",
        "ui.enterAccount": "Имя аккаунта (необязательно, напр: fatonyahmadfauzi)",
    },
    "zh": {
        "ui.codeLanguage": "Code/Language",
        "ui.changelogTitle": "CHANGELOG",
        "ui.warningDifferentProject": "⚠️  WARNING: Output Directory is in a different project!",
        "ui.pathOutsideProject": "(Path is outside the current project folder)",
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
        "changelog.affectsSelected": "仅影响选中的语言：{count} 种语言",
        "changelog.generateWith": "📋 生成包含 CHANGELOG",
        "changelog.checkedDescription": "勾选时：翻译 README 和 CHANGELOG 文件",
        "changelog.uncheckedDescription": "未勾选时：仅翻译 README 文件",
        
        "progress.translatingWithChangelog": "正在翻译 README + CHANGELOG",
        "progress.translatingReadmeOnly": "仅翻译 README",
        "success.filesSavedWithChangelog": "README 和 CHANGELOG",
        "success.filesSavedReadmeOnly": "仅 README",
        "success.translationCompletedWithChangelog": "✅ {count} 个 README 和 CHANGELOG 成功翻译！",
        "success.translationCompletedReadmeOnly": "✅ {count} 个 README 成功翻译！",
        "info.noChangelogFileSkipping": "⚠️ 未找到 CHANGELOG.md - 跳过 CHANGELOG 翻译",
        
        "errors.changelogGenerateFailed": "❌ CHANGELOG 生成失败",
        "errors.changelogRemoveSelectedFailed": "❌ 删除选中的 CHANGELOG 文件失败",
        "success.changelogGenerated": "✅ 成功为 {count} 种语言生成 CHANGELOG",
        "success.changelogRemovedSelected": "✅ {count} 个 CHANGELOG 文件成功删除",
        "confirmation.removeChangelogSelected": "您确定要删除 {count} 种选中语言的 CHANGELOG 文件吗？README 文件将不受影响。",
        
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
        "debug_current": "当前",
        "ui.changeLanguage": "更改显示语言",
        "ui.currentLanguage": "当前语言",
        "ui.languageChanged": "✅ 显示语言已更改为 {name}",
        "ui.languageSelector": "选择 CLI 通知的显示语言",
        "ui.translate": "翻译",
        "ui.removeTranslated": "删除已翻译语言",
        "ui.protectionSettings": "保护设置 (短语)",
        "ui.autoSetupChangelog": "自动设置更新日志部分",
        "ui.detectGithub": "检测 GitHub URL",
        "ui.repairTranslations": "修复翻译 (修复重复和失败)",
        "ui.setupPaths": "设置路径",
        "ui.exit": "退出",
        "ui.selectOption": "选择选项:",
        "ui.currentProjectPath": "当前项目路径",
        "ui.outputDirectory": "输出目录",
        "ui.folderProject": "项目文件夹",
        "ui.available": "可用",
        "ui.notFound": "未找到",
        "ui.notSet": "未设置",
        "ui.developer": "开发者",
        "ui.exiting": "正在退出...",
        "ui.chooseLanguageCode": "选择语言代码（留空以取消）:",
        "ui.translationStatus": "翻译状态:",
        "ui.translateBoth": "翻译 README 和 CHANGELOG",
        "ui.translateReadme": "仅翻译 README",
        "ui.translateChangelog": "仅翻译 CHANGELOG",
        "ui.removeBoth": "删除 README 和 CHANGELOG",
        "ui.removeReadme": "仅删除 README",
        "ui.removeChangelog": "仅删除 CHANGELOG",
        "ui.back": "返回",
        "ui.missing": "缺失",
        "ui.enterLangCodes": "输入语言代码（逗号分隔，或 'all'）:",
        "ui.invalidOption": "无效选项。",
        "ui.invalidLanguages": "无效语言。",
        "ui.pressEnter": "按 Enter 键继续...",
        "ui.status": "状态: ",
        "ui.active": "开启",
        "ui.inactive": "关闭",
        "ui.protectedPhrases": "受保护的短语:",
        "ui.noProtectedDir": "- 未配置受保护的短语。",
        "ui.toggleProtection": "切换保护状态",
        "ui.addProtection": "添加保护短语",
        "ui.removeProtection": "删除保护短语",
        "ui.resetDefault": "恢复默认",
        "ui.enterPhraseAdd": "输入要保护的短语（留空以取消）: ",
        "ui.addedPhrase": "已添加: {phrase}",
        "ui.enterPhraseRemove": "输入要删除的短语（留空以取消）: ",
        "ui.removedPhrase": "已删除: {phrase}",
        "ui.phraseNotFound": "未找到短语。",
        "ui.resetSuccess": "已恢复默认。",
        "ui.changelogComplete": "Changelog 设置已完成。",
        "ui.changelogFailed": "Changelog 设置失败。",
        "ui.setupPathsMenu": "设置路径",
        "ui.setTargetDir": "设置目标目录",
        "ui.currentDir": "当前: {path}",
        "ui.setOutputBaseDir": "设置输出基础目录",
        "ui.enterTargetDir": "输入目标目录路径:",
        "ui.enterOutputDir": "输入输出基础目录路径:",
        "ui.typeRoot": "  • 输入 'root' 使用项目根目录",
        "ui.typeAuto": "  • 输入 'auto' 在当前项目中查找 docs/lang",
        "ui.leaveEmpty": "  • 留空以取消",
        "ui.path": "路径: ",
        "ui.cancelled": "⏭️ 已取消。未作任何更改。",
        "ui.replaceCurrentDir": "⚠️ 这将替换当前目录:",
        "ui.oldPath": "   旧: {path}",
        "ui.newPath": "   新: {path}",
        "ui.continueYN": "您要继续吗？(y/n): ",
        "ui.targetSet": "✅ 目标目录已设置为: {path}",
        "ui.outputSet": "✅ 输出目录已设置为: {path}",
        "ui.targetAlreadySet": "⚠️ 目标目录已是当前工作目录。",
        "ui.fileDetected": "📄 检测到文件路径。使用父目录: {path}",
        "ui.pathNotFound": "❌ 找不到路径: {path} \n请检查目录或文件是否存在。",
        "ui.setOutputAuto": "将输出目录设置为当前项目的 docs/lang 吗？(y/n): ",
        "ui.autoSetSuccess": "✅ 输出目录已自动设置为: {path}",
        "ui.autoSetFailed": "❌ 未能在当前项目中找到 docs/lang 目录。",
        "ui.repairStarting": "正在启动翻译修复工具...",
        "ui.repairStep1": "1. 清理所有 README 中的重复语言切换器并修正位置...",
        "ui.repairStep2": "2. 扫描翻译文档的错误（API错误 / 未翻译的英文）...",
        "ui.repairLanguages": "语言: {langs}",
        "ui.looksTranslated": "看起来翻译正常。",
        "ui.repairSuccess": "未检测到失败的翻译。所有文件均干干净净、已完全修复！",
        "ui.highEnglishOverlap": "英语重叠率高 ({percent}%)",
        "ui.repairErrorScan": "无法扫描 ({error})",
        "ui.retranslatingFailed": "正在重新翻译 {count} 个失败的文件: {langs}",
        "ui.repairFixed": "修复完成！缺失的翻译已修正。",
        "ui.enterLangCodesRemove": "输入要删除的语言代码（逗号分隔，或 'all'）: ",
        "ui.actionCancelled": "操作已取消。返回删除菜单...",
        "ui.allRemoved": "所有翻译语言均已删除。",
        "ui.removedList": "已删除: {langs}",
        "ui.enterLangCodesRemoveReadme": "输入要删除的 README 语言代码（逗号分隔，或 'all'）: ",
        "ui.removedReadmeList": "已删除 README: {langs}",
        "ui.enterLangCodesRemoveChangelog": "输入要删除的 CHANGELOG 语言代码（逗号分隔，或 'all'）: ",
        "ui.removedChangelogFiles": "所选 CHANGELOG 文件已删除。",
        "ui.statusLabel": "状态: ",
        "ui.protectedPhrasesList": "受保护的短语:",
        "ui.pkgRepoField": "• package.json (repository 字段)",
        "ui.gitConfig": "• .git/config",
        "ui.readmeGitPattern": "• README.md (GitHub URL 模式)",
        "ui.pleaseCheck": "\n请检查:",
        "ui.checkPkgRepo": "• package.json 包含 'repository' 字段",
        "ui.checkGitRemote": "• .git/config 包含远程网址 (remote URL)",
        "ui.checkReadmeUrl": "• 或将 GitHub URL 手动添加到 README 中",
        "ui.noTranslatedFilesRemove": "⚠️  未找到要删除的翻译文件。",
        "ui.noFilesInOutputDir": "输出目录中没有更改日志 (CHANGELOG) 文件。",
        "progress.translatingChangelogOnly": "仅翻译更改日志 (CHANGELOG)",
        "success.translationCompletedChangelogOnly": "✅ {count} 个更改日志 (CHANGELOG) 翻译成功！",
        "ui.cannotTranslateBoth": "⚠️  无法翻译 README 和 CHANGELOG。",
        "ui.missingReadmeForBoth": "README.md 不存在。请使用选项 [2] 仅翻译 README。",
        "ui.missingChangelogForBoth": "CHANGELOG.md 不存在。请使用选项 [3] 仅翻译 CHANGELOG。",
        "ui.missingBothFiles": "README.md 和 CHANGELOG.md 都不存在。",
        "ui.cannotTranslateReadmeOnly": "⚠️  无法仅翻译 README。",
        "ui.missingReadme": "README.md 不存在。",
        "ui.cannotTranslateChangelogOnly": "⚠️  无法仅翻译 CHANGELOG。",
        "ui.missingChangelog": "CHANGELOG.md 不存在。",

        # API Settings
        "ui.apiSettings": "API 设置（可选）",
        "ui.apiList": "API 列表",
        "ui.apiAdd": "添加 API",
        "ui.apiEdit": "编辑 API",
        "ui.apiDelete": "删除 API",
        "ui.apiToggle": "启用/禁用 API",
        "ui.apiName": "API 名称",
        "ui.apiProvider": "服务商",
        "ui.apiToken": "API 令牌",
        "ui.apiStatus": "状态",
        "ui.apiActive": "🟢 已启用",
        "ui.apiInactive": "🔴 已禁用",
        "ui.apiNoEntries": "未配置 API。默认使用 Google 翻译（免费）。",
        "ui.apiAdded": "✅ API '{name}' 添加成功。",
        "ui.apiDeleted": "🗑️ API '{name}' 已删除。",
        "ui.apiUpdated": "✅ API '{name}' 已更新。",
        "ui.apiEnabled": "🟢 API '{name}' 已启用。",
        "ui.apiDisabled": "🔴 API '{name}' 已禁用。",
        "ui.apiUsing": "🔌 正在使用 API: {name} ({provider})",
        "ui.apiFallback": "⚠️  回退到 Google 翻译（免费）。",
        "ui.apiSelectProvider": "选择服务商",
        "ui.apiEnterToken": "输入 API 令牌（免费服务商可留空）",
        "ui.apiEnterName": "输入此 API 的名称",
        "ui.apiSelectToEdit": "输入要编辑的 API 编号",
        "ui.apiSelectToDelete": "输入要删除的 API 编号",
        "ui.apiSelectToToggle": "输入要启用/禁用的 API 编号",
        "ui.apiConfirmDelete": "确定删除 API '{name}'？[y/N]",
        "ui.apiTestSuccess": "✅ API 测试成功: {result}",
        "ui.apiTestFailed": "❌ API 测试失败: {error}",
        "ui.apiTesting": "🔍 正在测试 API 连接...",
        "ui.apiInvalidNumber": "无效的 API 编号。",
        "ui.apiSavedNote": "💡 API 令牌保存在 api_config.json 中（请妥善保管！）",
        "ui.apiMenuTitle": "🔌 API 设置 — 可选翻译 API",
        "ui.apiActiveCount": "已启用 API: {count}/{total}",
        "ui.apiUsingFree": "正在使用 Google 翻译（默认，无需 API）",
        "ui.apiCancelHint": "（留空取消）",
        "ui.apiTableName": "名称",
        "ui.apiTableProvider": "服务商",
        "ui.apiTableStatus": "状态",
        "ui.apiProviders": "服务商列表：",
        "ui.apiCancel": "取消",
        "ui.apiEditing": "编辑: {name} ({provider})",
        "ui.apiNewName": "新名称 [{name}] (Enter = 保留，q=取消)",
        "ui.apiNewToken": "新令牌 (Enter = 保留，q=取消)",
        "ui.apiActiveLabel": "已激活",
        "ui.provider_google": "Google 翻译（免费，无需令牌）",
        "ui.provider_deepl": "DeepL（免费/专业版 — 需要令牌）",
        "ui.provider_mymemory": "MyMemory（免费，可选令牌以获得更高配额）",
        "ui.provider_libretranslate": "LibreTranslate（免费自托管 / 公共服务器）",
        "ui.provider_yandex": "Yandex 翻译（需要令牌 — 提供免费套餐）",
        "ui.provider_microsoft": "Microsoft Azure 翻译（需要令牌 — 免费套餐每月200万字符）",
        "ui.provider_papago": "Papago / Naver（最适合韩语 — client_id:secret_key 格式）",
        "ui.provider_custom": "自定义 REST API（支持 Bearer 令牌的任意 HTTP 端点）",
        "ui.aiSettings": "AI 设置（可选）",
        "ui.aiMenuTitle": "🤖 AI 设置 — 可选 AI 服务商",
        "ui.aiSavedNote": "💡 AI 配置已保存到 ai_config.json（请保密！）",
        "ui.aiNoEntries": "未配置任何 AI 服务商。",
        "ui.aiAdd": "添加 AI 服务商",
        "ui.aiEdit": "编辑 AI 服务商",
        "ui.aiDelete": "删除 AI 服务商",
        "ui.aiToggle": "启用/禁用 AI 服务商",
        "ui.aiActive": "🟢 已启用",
        "ui.aiInactive": "🔴 已禁用",
        "ui.aiActiveCount": "已启用 AI: {count}/{total}",
        "ui.aiUsingDefault": "正在使用标准翻译 API（默认）",
        "ui.aiAdded": "✅ AI '{name}' 已添加。",
        "ui.aiDeleted": "🗑️ AI '{name}' 已删除。",
        "ui.aiUpdated": "✅ AI '{name}' 已更新。",
        "ui.aiEnabled": "🟢 AI '{name}' 已启用。",
        "ui.aiDisabled": "🔴 AI '{name}' 已禁用。",
        "ui.aiSelectProvider": "选择 AI 服务商",
        "ui.aiProviders": "AI 服务商列表：",
        "ui.aiEnterName": "输入此 AI 的名称",
        "ui.aiAuthType": "认证方式",
        "ui.aiAuthKey": "[1] API 密钥",
        "ui.aiAuthBrowser": "[2] 通过浏览器登录",
        "ui.aiEnterKey": "输入 API 密钥",
        "ui.aiBrowserOpening": "🌐 正在打开浏览器...",
        "ui.aiBrowserNote": "浏览器已打开。登录后请按 Enter 继续。",
        "ui.aiSelectToEdit": "输入要编辑的 AI 编号",
        "ui.aiSelectToDelete": "输入要删除的 AI 编号",
        "ui.aiSelectToToggle": "输入要启用/禁用的 AI 编号",
        "ui.aiConfirmDelete": "删除 AI '{name}'？ [y/N]",
        "ui.aiInvalidNumber": "无效的 AI 编号。",
        "ui.aiActiveLabel": "已激活",
        "ui.aiTableName": "名称",
        "ui.aiTableProvider": "服务商",
        "ui.aiTableStatus": "状态",
        "ui.aiTableAuth": "认证",
        "ui.aiEditing": "编辑: {name} ({provider})",
        "ui.aiNewName": "新名称 [{name}] (Enter=保留，q=取消)",
        "ui.aiNewKey": "新 API 密钥 (Enter=保留，q=取消)",
        "ui.aiCancelHint": "（留空取消）",
        "ui.ai_provider_openai": "OpenAI ChatGPT（API 密钥或浏览器登录）",
        "ui.ai_provider_gemini": "Google Gemini（API 密钥或浏览器登录）",
        "ui.ai_provider_claude": "Anthropic Claude（API 密钥或浏览器登录）",
        "ui.ai_provider_copilot": "Microsoft Copilot（浏览器登录）",
        "ui.ai_provider_mistral": "Mistral AI（API 密钥或浏览器登录）",
        "ui.ai_provider_perplexity": "Perplexity AI（API 密钥或浏览器登录）",
        "ui.ai_provider_custom": "自定义 AI（API 端点 + 密钥）",
        "ui.tableLimit": "限额",
        "ui.enterLimit": "使用限额（Enter使用默认，如 50万/月）",
        "ui.limitDefault": "默认：{value}",
        "ui.apiLimit": "额度受限 (充值)",
        "ui.aiLimit": "额度受限 (充值)",
        "ui.tableAccount": "账号",
        "ui.enterAccount": "账号用户名 (可选, 例: fatonyahmadfauzi)",
    }
}

# Global variable for display language
DISPLAY_LANG = "en"

def init_display_language():
    import locale
    import json
    import os
    global DISPLAY_LANG
    lang = "en"
    if os.path.exists(LANG_CONFIG_FILE):
        try:
            with open(LANG_CONFIG_FILE, 'r', encoding='utf-8') as f:
                lang = json.load(f).get("display_language", "en")
        except Exception:
            pass
    else:
        try:
            loc, _ = locale.getdefaultlocale()
            if loc:
                sys_lang = loc.split('_')[0].lower()
                if sys_lang in DISPLAY_LANGUAGES:
                    lang = sys_lang
                elif sys_lang == "ja":
                    lang = "jp"
                elif sys_lang == "ko":
                    lang = "kr"
        except Exception:
            pass
            
    if lang in DISPLAY_LANGUAGES:
        DISPLAY_LANG = lang
    return lang

def set_display_language(lang_code):
    """Set display language for notifications"""
    import json
    import os
    global DISPLAY_LANG
    if lang_code in DISPLAY_LANGUAGES:
        DISPLAY_LANG = lang_code
        try:
            with open(LANG_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump({"display_language": lang_code}, f)
        except Exception:
            pass
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
        print(t('ui.pkgRepoField'))
        print(t('ui.gitConfig'))
        print(t('ui.readmeGitPattern'))
        return True
    else:
        print(t("no_github_url"))
        print(t('ui.pleaseCheck'))
        print(t('ui.checkPkgRepo'))
        print(t('ui.checkGitRemote')) 
        print(t('ui.checkReadmeUrl'))
        return False

def create_square_panel(content, title=None, align_center=False, expand=True):
    """Create a simple text box using print statements"""
    # For now, just return the content as is for compatibility
    # The text will be printed separately using print_box or print_header
    if isinstance(content, str):
        return content
    else:
        # Handle Text objects by converting to string
        return str(content)


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
    """Resolve possible output directories for translation files"""
    candidate_dirs = []

    if base_output_dir:
        candidate_dirs.append(base_output_dir)
        nested_output_dir = os.path.join(base_output_dir, 'docs', 'lang')
        if nested_output_dir not in candidate_dirs:
            candidate_dirs.append(nested_output_dir)
    elif target_dir:
        candidate_dirs.append(os.path.join(target_dir, 'docs', 'lang'))
    else:
        candidate_dirs.append(OUTPUT_DIR)

    return candidate_dirs


def get_runtime_output_dir(target_dir, output_base_dir=None):
    """Get the runtime output directory path"""
    if output_base_dir:
        # Check if output_base_dir already ends with docs/lang
        if output_base_dir.endswith(os.path.join('docs', 'lang')) or output_base_dir.endswith(os.path.join('docs', 'lang').replace('\\', '/')):
            return output_base_dir
        else:
            return os.path.join(output_base_dir, 'docs', 'lang')
    else:
        return os.path.join(target_dir, 'docs', 'lang')


def configure_runtime_paths(target_dir, output_base_dir=None):
    global OUTPUT_DIR

    if not target_dir or not os.path.isdir(target_dir):
        print(Fore.RED + "Configured project path is invalid. Please update it in Setup Paths.")
        return False

    try:
        os.chdir(target_dir)
    except Exception as e:
        print(Fore.RED + f"Failed to change directory: {e}")
        return False

    runtime_output_dir = get_runtime_output_dir(target_dir, output_base_dir)
    os.makedirs(runtime_output_dir, exist_ok=True)
    OUTPUT_DIR = runtime_output_dir
    return True


def wcswidth(text):
    """Compute terminal display width for text with East Asian characters."""
    import unicodedata

    width = 0
    for ch in text:
        ea = unicodedata.east_asian_width(ch)
        if ea in ('F', 'W'):
            width += 2
        else:
            width += 1
    return width


def cjk_ljust(text, width):
    """Left justify text taking East Asian character widths into account."""
    text_str = str(text)
    pad_len = max(0, width - wcswidth(text_str))
    return text_str + (' ' * pad_len)


def create_translation_status_table(base_output_dir=None, target_dir=None, include_readme=True, include_changelog=True):
    """Create a simple text-based table showing translation status"""
    output_dirs = resolve_translation_output_dirs(base_output_dir, target_dir)
    
    # Compute max widths for alignment with East Asian width support
    max_lang_code = max(len(lang_code.upper()) for lang_code in LANGUAGES.keys())
    max_lang_name = max(wcswidth(lang_name) for lang_name, _, _ in LANGUAGES.values())

    # Build table data
    rows = []
    
    # Max width of the status column depends on translated words
    avail_width = wcswidth(t('ui.available'))
    missing_width = wcswidth(t('ui.missing'))
    # Make sure status column width accommodates the string "README" + 2 padding
    status_column_width = max(len("AVAILABLE"), len("MISSING"), avail_width, missing_width, len("README"), len(t('ui.changelogTitle'))) + 2

    base_width = max_lang_code + 1 + max_lang_name
    header_code_lang = t('ui.codeLanguage')
    pad_h = max(0, base_width - wcswidth(header_code_lang))
    header = f"{Fore.CYAN}{header_code_lang}{' ' * pad_h}"
    
    if include_readme:
        pad_r = max(0, status_column_width - len("README"))
        header += f"  README{' ' * pad_r}"
        
    if include_changelog:
        header_changelog = t('ui.changelogTitle')
        header += f"  {header_changelog}"

    header += Style.RESET_ALL
    
    rows.append("")
    rows.append(header)
    rows.append("")

    for lang_code, (lang_name, _, _) in LANGUAGES.items():
        readme_name, changelog_name = get_translation_file_names(lang_code)
        readme_available = any(os.path.exists(os.path.join(output_dir, readme_name)) for output_dir in output_dirs)
        changelog_available = any(os.path.exists(os.path.join(output_dir, changelog_name)) for output_dir in output_dirs)

        lang_code_field = f"{lang_code.upper():<{max_lang_code}}"
        pad_spaces = max_lang_name - wcswidth(lang_name)
        lang_name_field = f"{lang_name}{' ' * pad_spaces}"

        row = f"{lang_code_field} {lang_name_field}"

        if include_readme:
            status_word = t('ui.available') if readme_available else t('ui.missing')
            pad = max(0, status_column_width - wcswidth(status_word))
            status_display = status_word + (" " * pad)
            readme_status = f"{Fore.GREEN}{status_display}{Style.RESET_ALL}" if readme_available else f"{Fore.RED}{status_display}{Style.RESET_ALL}"
            row += f"  {readme_status}"

        if include_changelog:
            status_word = t('ui.available') if changelog_available else t('ui.missing')
            pad = max(0, status_column_width - wcswidth(status_word))
            status_display = status_word + (" " * pad)
            changelog_status = f"{Fore.GREEN}{status_display}{Style.RESET_ALL}" if changelog_available else f"{Fore.RED}{status_display}{Style.RESET_ALL}"
            row += f"  {changelog_status}"

        rows.append(row)

    return rows


def has_translation_output_files(base_output_dir=None, target_dir=None):
    for output_dir in resolve_translation_output_dirs(base_output_dir, target_dir):
        if not os.path.isdir(output_dir):
            continue

        for filename in os.listdir(output_dir):
            if (
                (filename.startswith("README-") or filename.startswith("CHANGELOG-"))
                and filename.endswith(".md")
            ):
                return True

    return False


def cleanup_output_dirs_if_empty():
    """Recursively remove empty directories starting from OUTPUT_DIR up to docs if empty"""
    try:
        # First, recursively remove any empty subdirectories
        for root, dirs, files in os.walk(OUTPUT_DIR, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):
                        shutil.rmtree(dir_path)
                        print(t("folder_deleted", folder=dir_path))
                except Exception as e:
                    print(t("failed_delete_folder", error=e))
        
        # Then check if OUTPUT_DIR itself is empty
        if os.path.exists(OUTPUT_DIR) and not os.listdir(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
            print(t("folder_deleted", folder=OUTPUT_DIR))
            
            # Check if docs folder is also empty
            docs_dir = os.path.dirname(OUTPUT_DIR)
            if os.path.exists(docs_dir) and not os.listdir(docs_dir):
                shutil.rmtree(docs_dir)
                print(t("folder_deleted", folder=docs_dir))
            return True
    except Exception as e:
        print(t("failed_delete_folder", error=e))
    
    return False


def set_output_to_docs_lang(project_dir, config, config_file):
    """Set output_base_dir to docs/lang within the specified project directory."""
    project_dir = os.path.abspath(project_dir)
    lang_dir = None

    # Find existing docs/lang inside project directory
    for root, dirs, files in os.walk(project_dir):
        if os.path.basename(root).lower() == 'lang' and os.path.basename(os.path.dirname(root)).lower() == 'docs':
            lang_dir = root
            break

    if not lang_dir:
        lang_dir = os.path.join(project_dir, 'docs', 'lang')

    if not os.path.exists(lang_dir):
        os.makedirs(lang_dir, exist_ok=True)
        print(Fore.GREEN + f"✅ Created directory: {lang_dir}")
    else:
        print(Fore.GREEN + f"✅ Using existing directory: {lang_dir}")

    config['output_base_dir'] = lang_dir
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(Fore.GREEN + t('ui.outputSet', path=config['output_base_dir']))
    time.sleep(1)


def setup_paths_menu():
    """Setup paths for input and output directories using .path_config"""
    config_file = PATH_CONFIG_FILE
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Load current config from .path_config
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {'target_dir': os.getcwd(), 'output_base_dir': None}
        
        target_dir = config.get('target_dir') or os.getcwd()
        output_base_dir = config.get('output_base_dir') or None
        
        # Header
        print(f"\n{Fore.CYAN}{t('ui.setupPathsMenu')}{Style.RESET_ALL}")
        print()  # Add spacing between title and content
        
        # Check project status
        readme_exists = os.path.isfile(os.path.join(target_dir, SOURCE_FILE))
        changelog_exists = os.path.isfile(os.path.join(target_dir, CHANGELOG_FILE))
        
        # Detect project folder name
        project_folder = os.path.basename(target_dir)
        print(f"{Fore.CYAN}📂 {t('ui.folderProject')}: {project_folder}{Style.RESET_ALL}")
        print()
        
        # Source Files Status
        readme_color = Fore.GREEN if readme_exists else Fore.RED
        readme_status = t('ui.available') if readme_exists else t('ui.missing')
        print(f"{readme_color}{'✅' if readme_exists else '❌'} README.md: {readme_status}{Style.RESET_ALL}")
        
        changelog_color = Fore.GREEN if changelog_exists else Fore.RED
        changelog_status = t('ui.available') if changelog_exists else t('ui.missing')
        print(f"{changelog_color}{'✅' if changelog_exists else '❌'} CHANGELOG.md: {changelog_status}{Style.RESET_ALL}\n")
        
        # Menu
        print(f"{Fore.GREEN}[1] {t('ui.setTargetDir')}{Style.RESET_ALL}")
        print(f"    {t('ui.currentDir', path=target_dir)}")
        print()
        print(f"{Fore.GREEN}[2] {t('ui.setOutputBaseDir')}{Style.RESET_ALL}")
        print(f"    {t('ui.currentDir', path=output_base_dir if output_base_dir else t('ui.notSet'))}")

        # Warning if output_base_dir is outside current target project directory
        if output_base_dir:
            try:
                project_root = os.path.abspath(target_dir)
                output_abs = os.path.abspath(output_base_dir)
                if not os.path.commonpath([project_root, output_abs]) == project_root:
                    print(Fore.YELLOW + "\n" + t('ui.warningDifferentProject'))
                    print(Fore.LIGHTBLACK_EX + t('ui.pathOutsideProject'))
            except Exception:
                pass

        print()
        print(f"{Fore.LIGHTBLACK_EX}[0] {t('ui.back')}{Style.RESET_ALL}")

        choice = input(f"\n{Fore.YELLOW}[+] {t('ui.selectOption')} {Fore.WHITE}").strip()


        if choice == '1':
            print(Fore.CYAN + t('ui.enterTargetDir'))
            print(Fore.LIGHTBLACK_EX + t('ui.typeRoot'))
            print(Fore.LIGHTBLACK_EX + t('ui.leaveEmpty'))
            new_target = input(Fore.CYAN + t('ui.path') + Fore.WHITE).strip()
            
            if not new_target:
                print(Fore.YELLOW + t('ui.cancelled'))
                time.sleep(1)
            elif new_target.lower() == 'root':
                # Get project root (two levels up from scripts/python)
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                # Show confirmation if changing existing directory
                if target_dir != project_root:
                    print(Fore.YELLOW + t('ui.replaceCurrentDir'))
                    print(Fore.LIGHTBLACK_EX + t('ui.oldPath', path=target_dir))
                    print(Fore.LIGHTBLACK_EX + t('ui.newPath', path=project_root))
                    confirm = input(Fore.YELLOW + t('ui.continueYN') + Fore.WHITE).strip().lower()
                    if confirm != 'y':
                        print(Fore.YELLOW + t('ui.cancelled'))
                        time.sleep(1)
                        continue
                config['target_dir'] = project_root
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print(Fore.GREEN + t('ui.targetSet', path=config['target_dir']))
                if input(Fore.CYAN + t('ui.setOutputAuto') + Fore.WHITE).strip().lower() == 'y':
                    set_output_to_docs_lang(project_root, config, config_file)
                time.sleep(1)
            elif new_target == '.':
                current_path = os.getcwd()
                if target_dir == current_path:
                    print(Fore.YELLOW + t('ui.targetAlreadySet'))
                    time.sleep(1)
                else:
                    print(Fore.YELLOW + t('ui.replaceCurrentDir'))
                    print(Fore.LIGHTBLACK_EX + t('ui.oldPath', path=target_dir))
                    print(Fore.LIGHTBLACK_EX + t('ui.newPath', path=current_path))
                    confirm = input(Fore.YELLOW + t('ui.continueYN') + Fore.WHITE).strip().lower()
                    if confirm != 'y':
                        print(Fore.YELLOW + t('ui.cancelled'))
                        time.sleep(1)
                        continue
                    config['target_dir'] = current_path
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=2)
                    print(Fore.GREEN + t('ui.targetSet', path=config['target_dir']))
                    if input(Fore.CYAN + t('ui.setOutputAuto') + Fore.WHITE).strip().lower() == 'y':
                        set_output_to_docs_lang(current_path, config, config_file)
                    time.sleep(1)
            else:
                # Validate path exists - check if it's a file or directory
                if os.path.isfile(new_target):
                    # If it's a file, extract the directory
                    abs_path = os.path.dirname(os.path.abspath(new_target))
                    print(Fore.CYAN + t('ui.fileDetected', path=abs_path))
                    # Show confirmation if changing existing directory
                    if target_dir != abs_path:
                        print(Fore.YELLOW + t('ui.replaceCurrentDir'))
                        print(Fore.LIGHTBLACK_EX + t('ui.oldPath', path=target_dir))
                        print(Fore.LIGHTBLACK_EX + t('ui.newPath', path=abs_path))
                        confirm = input(Fore.YELLOW + t('ui.continueYN') + Fore.WHITE).strip().lower()
                        if confirm != 'y':
                            print(Fore.YELLOW + t('ui.cancelled'))
                            time.sleep(1)
                            continue
                    config['target_dir'] = abs_path
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=2)
                    print(Fore.GREEN + t('ui.targetSet', path=config['target_dir']))
                    if input(Fore.CYAN + t('ui.setOutputAuto') + Fore.WHITE).strip().lower() == 'y':
                        set_output_to_docs_lang(abs_path, config, config_file)
                    time.sleep(1)
                elif os.path.isdir(new_target):
                    abs_path = os.path.abspath(new_target)
                    # Show confirmation if changing existing directory
                    if target_dir != abs_path:
                        print(Fore.YELLOW + t('ui.replaceCurrentDir'))
                        print(Fore.LIGHTBLACK_EX + t('ui.oldPath', path=target_dir))
                        print(Fore.LIGHTBLACK_EX + t('ui.newPath', path=abs_path))
                        confirm = input(Fore.YELLOW + t('ui.continueYN') + Fore.WHITE).strip().lower()
                        if confirm != 'y':
                            print(Fore.YELLOW + t('ui.cancelled'))
                            time.sleep(1)
                            continue
                    config['target_dir'] = abs_path
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=2)
                    print(Fore.GREEN + t('ui.targetSet', path=config['target_dir']))
                    if input(Fore.CYAN + t('ui.setOutputAuto') + Fore.WHITE).strip().lower() == 'y':
                        set_output_to_docs_lang(abs_path, config, config_file)
                    time.sleep(1)
                else:
                    print(Fore.RED + t('ui.pathNotFound', path=new_target))
                    time.sleep(2)
        
        elif choice == '2':
            print(Fore.CYAN + t('ui.enterOutputDir'))
            print(Fore.LIGHTBLACK_EX + t('ui.typeRoot'))
            print(Fore.LIGHTBLACK_EX + t('ui.typeAuto'))
            print(Fore.LIGHTBLACK_EX + t('ui.leaveEmpty'))
            new_output = input(Fore.CYAN + t('ui.path') + Fore.WHITE).strip()
            
            if not new_output:
                print(Fore.YELLOW + t('ui.cancelled'))
                time.sleep(1)
            elif new_output.lower() == 'root':
                # Get project root (two levels up from scripts/python)
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                # Show confirmation if changing existing directory
                if output_base_dir and output_base_dir != project_root:
                    print(Fore.YELLOW + f"⚠️  This will replace the current output directory:")
                    print(Fore.LIGHTBLACK_EX + f"   Old: {output_base_dir}")
                    print(Fore.LIGHTBLACK_EX + t('ui.newPath', path=project_root))
                    confirm = input(Fore.YELLOW + t('ui.continueYN') + Fore.WHITE).strip().lower()
                    if confirm != 'y':
                        print(Fore.YELLOW + t('ui.cancelled'))
                        time.sleep(1)
                        continue
                config['output_base_dir'] = project_root
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print(Fore.GREEN + t('ui.outputSet', path=config['output_base_dir']))
                time.sleep(1)
            elif new_output.lower() == 'auto':
                project_root = target_dir
                found_path = None
                for root, dirs, files in os.walk(project_root):
                    if os.path.basename(root).lower() == 'lang' and os.path.basename(os.path.dirname(root)).lower() == 'docs':
                        found_path = root
                        break

                if found_path:
                    config['output_base_dir'] = found_path
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=2)
                    print(Fore.GREEN + f"✅ Found docs/lang in project, output directory set to: {found_path}")
                    time.sleep(1)
                else:
                    print(Fore.YELLOW + "⚠️  docs/lang tidak ditemukan di project saat ini.")
                    print(Fore.CYAN + "Lokasi project saat ini: " + Fore.WHITE + f"{project_root}")
                    print(Fore.GREEN + "Pilih opsi:")
                    script_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    print(Fore.GREEN + "  [1] Buat docs/lang di root (script root): " + os.path.join(script_root, 'docs', 'lang'))
                    print(Fore.GREEN + "  [2] Buat docs/lang di path project saat ini: " + os.path.join(project_root, 'docs', 'lang'))
                    print(Fore.GREEN + "  [0] Batal")
                    choice_new = input(Fore.CYAN + "Pilihan: " + Fore.WHITE).strip()
                    if choice_new == '1':
                        make_path = os.path.join(script_root, 'docs', 'lang')
                    elif choice_new == '2':
                        make_path = os.path.join(project_root, 'docs', 'lang')
                    else:
                        print(Fore.YELLOW + "⏭️  Tidak ada perubahan.")
                        time.sleep(1)
                        continue

                    os.makedirs(make_path, exist_ok=True)
                    config['output_base_dir'] = make_path
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=2)
                    print(Fore.GREEN + f"✅ Folder dibuat dan output directory diset ke: {make_path}")
                    time.sleep(1)

            elif new_output == '.':
                current_path = os.getcwd()
                if output_base_dir == current_path:
                    print(Fore.YELLOW + "⚠️  Output directory already set to current working directory.")
                    time.sleep(1)
                else:
                    if output_base_dir:
                        print(Fore.YELLOW + f"⚠️  This will replace the current output directory:")
                        print(Fore.LIGHTBLACK_EX + f"   Old: {output_base_dir}")
                        print(Fore.LIGHTBLACK_EX + t('ui.newPath', path=current_path))
                        confirm = input(Fore.YELLOW + t('ui.continueYN') + Fore.WHITE).strip().lower()
                        if confirm != 'y':
                            print(Fore.YELLOW + t('ui.cancelled'))
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
                    print(Fore.CYAN + t('ui.fileDetected', path=abs_path))
                    # Show confirmation if changing existing directory
                    if output_base_dir and output_base_dir != abs_path:
                        print(Fore.YELLOW + f"⚠️  This will replace the current output directory:")
                        print(Fore.LIGHTBLACK_EX + f"   Old: {output_base_dir}")
                        print(Fore.LIGHTBLACK_EX + t('ui.newPath', path=abs_path))
                        confirm = input(Fore.YELLOW + t('ui.continueYN') + Fore.WHITE).strip().lower()
                        if confirm != 'y':
                            print(Fore.YELLOW + t('ui.cancelled'))
                            time.sleep(1)
                            continue
                    config['output_base_dir'] = abs_path
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=2)
                    print(Fore.GREEN + t('ui.outputSet', path=config['output_base_dir']))
                    time.sleep(1)
                elif os.path.isdir(new_output):
                    abs_path = os.path.abspath(new_output)
                    # Show confirmation if changing existing directory
                    if output_base_dir and output_base_dir != abs_path:
                        print(Fore.YELLOW + f"⚠️  This will replace the current output directory:")
                        print(Fore.LIGHTBLACK_EX + f"   Old: {output_base_dir}")
                        print(Fore.LIGHTBLACK_EX + t('ui.newPath', path=abs_path))
                        confirm = input(Fore.YELLOW + t('ui.continueYN') + Fore.WHITE).strip().lower()
                        if confirm != 'y':
                            print(Fore.YELLOW + t('ui.cancelled'))
                            time.sleep(1)
                            continue
                    config['output_base_dir'] = abs_path
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=2)
                    print(Fore.GREEN + t('ui.outputSet', path=config['output_base_dir']))
                    time.sleep(1)
                else:
                    print(Fore.RED + t('ui.pathNotFound', path=new_output))
                    time.sleep(2)
        
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

# ---------------------- API MANAGEMENT SYSTEM ----------------------
import uuid

# API config file path (at project root, not committed to git)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
API_CONFIG_FILE = os.path.join(_SCRIPT_DIR, '..', '..', 'api_config.json')

# Supported provider keys
SUPPORTED_PROVIDERS = {
    "google":         "Google Translate (Free, no token needed)",
    "deepl":          "DeepL (Free/Pro — token required)",
    "mymemory":       "MyMemory (Free with optional token for higher quota)",
    "libretranslate": "LibreTranslate (Free self-hosted / public servers)",
    "yandex":         "Yandex Translate (token required — free tier available)",
    "microsoft":      "Microsoft Azure Translator (token required — free tier 2M chars/month)",
    "papago":         "Papago / Naver (best for Korean — client_id:secret_key format)",
}

# Providers where API token is optional (can still work without token)
OPTIONAL_TOKEN_PROVIDERS = {"mymemory", "libretranslate"}

# Default quota/limits per translation provider
PROVIDER_DEFAULT_LIMITS = {
    "google":         "Unlimited",
    "deepl":          "500k chars/month",
    "mymemory":       "1k req/day",
    "libretranslate": "Varies",
    "yandex":         "1M chars/month",
    "microsoft":      "2M chars/month",
    "papago":         "10k chars/day",
}


def load_api_config() -> dict:
    """Load API configuration from api_config.json."""
    if os.path.exists(API_CONFIG_FILE):
        try:
            with open(API_CONFIG_FILE, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"apis": []}


def save_api_config(config: dict):
    """Save API configuration to api_config.json."""
    try:
        with open(API_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(Fore.RED + f"❌ Failed to save API config: {e}" + Style.RESET_ALL)


def add_api(name: str, provider: str, token: str, limit: str = "", status: str = "active", test_status: str = "") -> str:
    """Add a new API entry. Returns the new entry's id."""
    config = load_api_config()
    entry = {
        "id": str(uuid.uuid4()),
        "name": name,
        "provider": provider.lower(),
        "token": token,
        "limit": limit or PROVIDER_DEFAULT_LIMITS.get(provider.lower(), ""),
        "status": status,
        "active": status == "active",
        "test_status": test_status,
    }
    config["apis"].append(entry)
    save_api_config(config)
    return entry["id"]


def edit_api(api_id: str, **kwargs):
    """Edit an existing API entry by id."""
    config = load_api_config()
    for entry in config["apis"]:
        if entry["id"] == api_id:
            for k, v in kwargs.items():
                entry[k] = v
            break
    save_api_config(config)


def delete_api(api_id: str):
    """Delete an API entry by id."""
    config = load_api_config()
    config["apis"] = [e for e in config["apis"] if e["id"] != api_id]
    save_api_config(config)


def toggle_api(api_id: str) -> str:
    """Toggle API status (active -> limit -> inactive). Returns new status."""
    config = load_api_config()
    new_status = "active"
    for entry in config["apis"]:
        if entry["id"] == api_id:
            curr_status = entry.get("status")
            if not curr_status:
                curr_status = "active" if entry.get("active", False) else "inactive"
            
            if curr_status == "active":
                new_status = "limit"
            elif curr_status == "limit":
                new_status = "inactive"
            else:
                new_status = "active"
                
            entry["status"] = new_status
            entry["active"] = (new_status == "active")
            break
    save_api_config(config)
    return new_status


def get_active_apis() -> list:
    """Return list of active API entries (excluding default google)."""
    config = load_api_config()
    return [
        e for e in config["apis"] 
        if e.get("status", "active" if e.get("active", False) else "inactive") == "active" 
        and e["provider"] != "google"
    ]

API_ERROR_PATTERNS = (
    "authorization failed",
    "quota exceeded",
    "invalid email provided",
)


def is_successful_translation_result(result: str | None) -> bool:
    """Return True only for valid translation output, not provider error payloads."""
    if not result:
        return False
    lowered = str(result).strip().lower()
    if not lowered:
        return False
    return not any(pattern in lowered for pattern in API_ERROR_PATTERNS)


def refresh_api_health_status():
    """
    Realtime-ish health refresh for saved APIs:
    - test active providers with a lightweight translation probe
    - set test_status to '200' on success, 'false' on failure
    - auto-disable provider when health check fails
    """
    config = load_api_config()
    changed = False
    for entry in config.get("apis", []):
        curr_status = entry.get("status", "active" if entry.get("active", False) else "inactive")
        if curr_status != "active":
            continue
        provider = entry.get("provider", "")
        token = entry.get("token", "")
        probe = _translate_with_provider("hello", "fr", provider, token)
        if is_successful_translation_result(probe):
            if entry.get("test_status") != "200":
                entry["test_status"] = "200"
                changed = True
        else:
            if entry.get("test_status") != "false":
                entry["test_status"] = "false"
                changed = True
            if entry.get("status") != "inactive" or entry.get("active", True):
                entry["status"] = "inactive"
                entry["active"] = False
                changed = True
    if changed:
        save_api_config(config)


def refresh_api_health_status():
    """
    Realtime-ish health refresh for saved APIs:
    - test active providers with a lightweight translation probe
    - set test_status to '200' on success, 'false' on failure
    - auto-disable provider when health check fails
    """
    config = load_api_config()
    changed = False
    for entry in config.get("apis", []):
        curr_status = entry.get("status", "active" if entry.get("active", False) else "inactive")
        if curr_status != "active":
            continue
        provider = entry.get("provider", "")
        token = entry.get("token", "")
        probe = _translate_with_provider("hello", "fr", provider, token)
        if probe:
            if entry.get("test_status") != "200":
                entry["test_status"] = "200"
                changed = True
        else:
            if entry.get("test_status") != "false":
                entry["test_status"] = "false"
                changed = True
            if entry.get("status") != "inactive" or entry.get("active", True):
                entry["status"] = "inactive"
                entry["active"] = False
                changed = True
    if changed:
        save_api_config(config)


# ---------------------- AI MANAGEMENT SYSTEM ----------------------

# AI config file path
AI_CONFIG_FILE = os.path.join(_SCRIPT_DIR, '..', '..', 'ai_config.json')

# Supported AI providers
SUPPORTED_AI_PROVIDERS = {
}

# Default quota/limits per AI provider
AI_PROVIDER_DEFAULT_LIMITS = {
}

# Browser login URLs for each AI provider
AI_PROVIDER_URLS = {
}


def load_ai_config() -> dict:
    """Load AI configuration from ai_config.json."""
    if os.path.exists(AI_CONFIG_FILE):
        try:
            with open(AI_CONFIG_FILE, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"ais": []}


def save_ai_config(config: dict):
    """Save AI configuration to ai_config.json."""
    try:
        with open(AI_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(Fore.RED + f"❌ Failed to save AI config: {e}" + Style.RESET_ALL)


def add_ai(name: str, provider: str, token: str = "", auth_type: str = "key", limit: str = "", account: str = "", status: str = "active") -> str:
    """Add a new AI provider entry. Returns the new entry id."""
    config = load_ai_config()
    entry = {
        "id": str(uuid.uuid4()),
        "name": name,
        "provider": provider.lower(),
        "auth_type": auth_type,
        "token": token,
        "limit": limit or AI_PROVIDER_DEFAULT_LIMITS.get(provider.lower(), ""),
        "account": account,
        "status": status,
        "active": status == "active",
    }
    config["ais"].append(entry)
    save_ai_config(config)
    return entry["id"]


def edit_ai(ai_id: str, **kwargs):
    """Edit an existing AI entry by id."""
    config = load_ai_config()
    for entry in config["ais"]:
        if entry["id"] == ai_id:
            for k, v in kwargs.items():
                entry[k] = v
            break
    save_ai_config(config)


def delete_ai(ai_id: str):
    """Delete an AI entry by id."""
    config = load_ai_config()
    config["ais"] = [e for e in config["ais"] if e["id"] != ai_id]
    save_ai_config(config)


def toggle_ai(ai_id: str) -> str:
    """Toggle AI status (active -> limit -> inactive). Returns new status."""
    config = load_ai_config()
    new_status = "active"
    for entry in config["ais"]:
        if entry["id"] == ai_id:
            curr_status = entry.get("status")
            if not curr_status:
                curr_status = "active" if entry.get("active", False) else "inactive"
            
            if curr_status == "active":
                new_status = "limit"
            elif curr_status == "limit":
                new_status = "inactive"
            else:
                new_status = "active"
                
            entry["status"] = new_status
            entry["active"] = (new_status == "active")
            break
    save_api_config(config)
    return new_status


def get_active_ais() -> list:
    """Return list of active AI entries."""
    config = load_ai_config()
    return [
        e for e in config["ais"] 
        if e.get("status", "active" if e.get("active", False) else "inactive") == "active"
    ]


# ---------------------- TRANSLATION FUNCTIONS ----------------------
def _translate_with_provider(text: str, dest: str, provider: str, token: str) -> str | None:
    """
    Attempt translation using a specific provider.
    Returns translated string, or None on failure.
    """
    try:
        provider = provider.lower()
        if provider == "google":
            return GoogleTranslator(source="auto", target=dest).translate(text)
        elif provider == "deepl":
            from deep_translator import DeeplTranslator
            return DeeplTranslator(api_key=token, source="auto", target=dest).translate(text)
        elif provider == "mymemory":
            # MyMemory direct API:
            # - free: .../get?q=...&langpair=en|id
            # - email mode: add &de=email@example.com
            # - key mode: add &key=API_KEY
            base_url = "https://api.mymemory.translated.net/get"
            params = {
                "q": text,
                "langpair": f"en|{dest}",
            }
            if token.startswith("email:"):
                params["de"] = token.split(":", 1)[1].strip()
            elif token.startswith("key:"):
                params["key"] = token.split(":", 1)[1].strip()
            elif token:
                # Backward-compatibility for older saved entries
                params["key"] = token

            url = f"{base_url}?{urllib.parse.urlencode(params)}"
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            response_status = str(data.get("responseStatus", "")).strip()
            translated = (data.get("responseData", {}) or {}).get("translatedText", "")
            response_details = str(data.get("responseDetails", "")).strip().lower()

            # MyMemory can return text like "INVALID EMAIL PROVIDED" with responseStatus=403
            # Treat non-200 and known invalid responses as failure.
            if response_status != "200":
                return None
            if not translated:
                return None
            if "invalid" in translated.lower() or "invalid" in response_details:
                return None
            return translated
        elif provider == "libretranslate":
            from deep_translator import LibreTranslateTranslator
            return LibreTranslateTranslator(
                api_key=token or "",
                source="auto",
                target=dest
            ).translate(text)
        elif provider == "yandex":
            from deep_translator import YandexTranslator
            return YandexTranslator(api_key=token, source="auto", target=dest).translate(text)
        elif provider == "microsoft":
            from deep_translator import MicrosoftTranslator
            return MicrosoftTranslator(api_key=token, source="auto", target=dest).translate(text)
        elif provider == "papago":
            # token format = "client_id:secret_key"
            from deep_translator import PapagoTranslator
            parts = token.split(":", 1)
            client_id = parts[0].strip() if len(parts) >= 1 else ""
            secret = parts[1].strip() if len(parts) >= 2 else ""
            return PapagoTranslator(
                client_id=client_id, secret_key=secret,
                source="auto", target=dest
            ).translate(text)
        else:
            # Unknown provider — skip
            return None
    except Exception:
        return None


def translate_text(text: str, dest: str) -> str:
    """
    Translate text to the target language.
    Strategy:
    1. Try each active API (non-google) in order.
    2. If all fail or none configured → fallback to GoogleTranslator (free).
    """
    if not text.strip():
        return text

    active_apis = get_active_apis()

    for api_entry in active_apis:
        provider = api_entry.get("provider", "")
        token = api_entry.get("token", "")
        name = api_entry.get("name", provider)
        try:
            result = _translate_with_provider(text, dest, provider, token)
            if is_successful_translation_result(result):
                return result
        except Exception:
            pass  # Fall through to next API

    # Fallback: free Google Translate
    try:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return GoogleTranslator(source="auto", target=dest).translate(text)
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                raise e
    except Exception as e:
        print(t("translation_failed", error=e))
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

def has_translated_files(output_dir=None):
    """Check if there are any translated README or CHANGELOG files"""
    check_dir = output_dir or OUTPUT_DIR
    if not os.path.exists(check_dir):
        return False
    
    translation_files = [
        filename for filename in os.listdir(check_dir)
        if (
            (filename.startswith("README-") or filename.startswith("CHANGELOG-"))
            and filename.endswith(".md")
        )
    ]
    
    return len(translation_files) > 0

def update_language_switcher(new_languages=None, removed_languages=None, target_dir=None, output_base_dir=None):
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
    
    # Determine runtime output directory first (can be in config or default)
    runtime_output_dir = get_runtime_output_dir(target_dir or os.getcwd(), output_base_dir)

    # Calculate path from main README (target_dir) to translated language files
    try:
        main_relative_path = os.path.relpath(runtime_output_dir, target_dir or os.getcwd()).replace('\\', '/')
    except Exception:
        main_relative_path = 'docs/lang'

    def build_english_link(from_dir):
        try:
            link = os.path.relpath(os.path.join(target_dir or os.getcwd(), SOURCE_FILE), from_dir).replace('\\', '/')
            return f"[English]({link})"
        except Exception:
            return f"[English](../../README.md)"
    
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
                    lang_links.append(f"[{name}]({main_relative_path}/README-JP.md)")
                elif code == "zh":
                    lang_links.append(f"[{name}]({main_relative_path}/README-ZH.md)")
                elif code == "kr":
                    lang_links.append(f"[{name}]({main_relative_path}/README-KR.md)")
                else:
                    lang_links.append(f"[{name}]({main_relative_path}/README-{code.upper()}.md)")
        
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
            print(f"   {t('ui.repairLanguages', langs=', '.join(ordered_existing))}")
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
                    
                    # Calculate relative path from translation folder to target README for English link
                    english_link = build_english_link(runtime_output_dir)
                    
                    # Create link list for this language (all languages except itself)
                    links = [english_link]
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
        cleanup_output_dirs_if_empty()
    
    return removed_langs


def remove_readme_files(lang_codes):
    """Remove README files only for specific languages and update language switcher"""
    removed_langs = []

    for lang_code in lang_codes:
        if lang_code in LANGUAGES:
            readme_name, _ = get_translation_file_names(lang_code)
            readme_path = os.path.join(OUTPUT_DIR, readme_name)

            if os.path.exists(readme_path):
                try:
                    os.remove(readme_path)
                    removed_langs.append(lang_code)
                    print(t("file_deleted", filename=os.path.basename(readme_path)))
                except Exception as e:
                    print(t("failed_delete_file", filename=os.path.basename(readme_path), error=e))
            else:
                print(t("file_not_found", filename=os.path.basename(readme_path)))
        else:
            print(t("language_not_recognized", code=lang_code))

    if removed_langs:
        update_language_switcher(removed_languages=removed_langs)
        cleanup_output_dirs_if_empty()

    return removed_langs

def remove_all_language_files():
    """Remove all translated README files and docs/lang folder and docs if empty"""
    if not os.path.exists(OUTPUT_DIR):
        print(t("no_translation_files"))
        return

    translation_files = [
        filename for filename in os.listdir(OUTPUT_DIR)
        if (
            (filename.startswith("README-") or filename.startswith("CHANGELOG-"))
            and filename.endswith(".md")
        )
    ]

    if not translation_files:
        print(t("no_translation_files"))
        return

    removed_readme_langs = []

    for filename in translation_files:
        file_path = os.path.join(OUTPUT_DIR, filename)
        try:
            os.remove(file_path)
            print(t("file_deleted", filename=filename))

            if filename.startswith("README-"):
                lang_code = filename.replace("README-", "").replace(".md", "").lower()
                lang_code = {"jp": "jp", "zh": "zh", "kr": "kr"}.get(lang_code, lang_code)
                if lang_code in LANGUAGES:
                    removed_readme_langs.append(lang_code)
        except Exception as e:
            print(t("failed_delete_file", filename=filename, error=e))
    
    # Remove docs/lang folder if empty, then docs if also empty
    cleanup_output_dirs_if_empty()
    
    if removed_readme_langs:
        update_language_switcher(removed_languages=removed_readme_langs)

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
    
    # Protection for version (generic pattern)
    text = re.sub(r'(\*\*)?v?\d+\.\d+\.\d+(\*\*)?', lambda m: m.group(0), text)
    
    # Protection for dates (YYYY-MM-DD format)
    text = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', lambda m: m.group(0), text)
    
    # Protection for product names and technical terms
    text = re.sub(r'\bPixiv OAuth Token\b', 'Pixiv OAuth Token', text, flags=re.IGNORECASE)
    text = re.sub(r'\bOAuth\b', 'OAuth', text)
    text = re.sub(r'\bCLI\b', 'CLI', text)
    text = re.sub(r'\bGUI\b', 'GUI', text)
    text = re.sub(r'\bAPI\b', 'API', text)
    text = re.sub(r'\bGitHub\b', 'GitHub', text)
    text = re.sub(r'\bVercel\b', 'Vercel', text)
    text = re.sub(r'\bPython\b', 'Python', text)
    text = re.sub(r'\bWindows\b', 'Windows', text, flags=re.IGNORECASE)
    text = re.sub(r'\bmacOS\b', 'macOS', text, flags=re.IGNORECASE)
    text = re.sub(r'\bLinux\b', 'Linux', text, flags=re.IGNORECASE)
    
    # Protection for file extensions and paths
    text = re.sub(r'\b\w+\.\w+\b(?!\s*\))', lambda m: m.group(0) if '.' in m.group(0) else m.group(0), text)
    
    # Protection for emoji
    text = re.sub(r'[🌐🧾🐞✨🔜📦⚙]', lambda m: m.group(0), text)
    
    # Protection for version ranges and build codes
    text = re.sub(r'\bREL-U\d+\b', lambda m: m.group(0), text)
    text = re.sub(r'\bBUILD-UNKNOWN\b', lambda m: m.group(0), text)
    
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
            
            # Additional protection for file paths, versions, dates, and technical terms
            temp_line = protect(r'\b\w+/\w+(/\w+)*\.\w+\b', temp_line)     # File paths
            temp_line = protect(r'\b\w+\.\w+\b', temp_line)                # File extensions
            temp_line = protect(r'\bv\d+\.\d+\.\d+\b', temp_line)          # Versions
            temp_line = protect(r'\b\d{4}-\d{2}-\d{2}\b', temp_line)       # Dates
            temp_line = protect(r'\bPixiv OAuth Token\b', temp_line, re.IGNORECASE)
            temp_line = protect(r'\bOAuth\b', temp_line)
            temp_line = protect(r'\bCLI\b', temp_line)
            temp_line = protect(r'\bGUI\b', temp_line)
            temp_line = protect(r'\bAPI\b', temp_line)
            temp_line = protect(r'\bGitHub\b', temp_line)
            temp_line = protect(r'\bVercel\b', temp_line)
            temp_line = protect(r'\bPython\b', temp_line)
            temp_line = protect(r'[🌐🧾🐞✨🔜📦⚙]', temp_line)             # Emoji
            temp_line = protect(r'\bREL-U\d+\b', temp_line)                # Build codes
            temp_line = protect(r'\bBUILD-UNKNOWN\b', temp_line)
            
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

    # Internet connection check
    if not check_internet_connection():
        print(t("no_internet"))
        return False

    protected = load_protected_phrases()

    # Filter valid language codes
    if not lang_codes:
        lang_codes = list(LANGUAGES.keys())
    valid_langs = [code for code in lang_codes if code in LANGUAGES and code != 'en']

    if not valid_langs:
        print(t("errors.noLanguagesSelected"))
        return False

    # Show progress mode header
    mode_text = t("progress.translatingChangelogOnly")
    print(t("progress.startingTranslation", count=len(valid_langs), mode_text=mode_text))

    success_count = 0
    for i, lang_code in enumerate(valid_langs):
        lang_name = LANGUAGES[lang_code][0]
        progress_msg = t("progress.translatingLanguage",
                        lang_name=lang_name,
                        current=i + 1,
                        total=len(valid_langs))
        print(progress_msg, flush=True)

        # Show inline visual progress bar
        print_translation_progress(i + 1, len(valid_langs))

        try:
            if translate_changelog(lang_code, LANGUAGES[lang_code], protected):
                success_count += 1
                # Update links in translated README if it exists
                update_changelog_links_in_readme(lang_code, LANGUAGES[lang_code])

            # Delay to avoid rate limiting
            print(t("progress.waiting", seconds=2), flush=True)
            time.sleep(2)

        except Exception as e:
            error_msg = t("errors.translationFailed", lang_code=lang_code, error=str(e))
            print(f"\n❌ {error_msg}", flush=True)

    # Complete progress line
    print("", flush=True)

    print(t("progress.completed"), flush=True)
    print(t("progress.filesSaved", path=OUTPUT_DIR), flush=True)

    if success_count > 0:
        print(t("success.translationCompletedChangelogOnly", count=success_count))
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
        print(Fore.YELLOW + t("ui.actionCancelled") + Style.RESET_ALL)
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
        cleanup_output_dirs_if_empty()
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
        print(Fore.YELLOW + t("ui.actionCancelled") + Style.RESET_ALL)
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
            cleanup_output_dirs_if_empty()
                
        except Exception as e:
            print(f"❌ Error reading directory: {e}")
    
    if removed_count > 0:
        print(t("success.changelogRemoved", count=removed_count))
        return True
    else:
        print(t("info.noChangelogFiles"))
        return False

def print_translation_progress(current, total, width=40):
    """Print inline progress bar with percentage and count."""
    if total <= 0:
        return
    filled = int(width * current / total)
    bar = "█" * filled + "─" * (width - filled)
    percent = int(100 * current / total)
    progress_label = t("progress.barLabel")
    print(f"  {progress_label} [{bar}] {current}/{total} ({percent}%)", end='\r', flush=True)


def translate_with_changelog(lang_codes, with_changelog=True, target_dir=None, output_base_dir=None):
    """
    Translate README with option to include CHANGELOG
    """
    if not lang_codes:
        print(t("errors.noLanguagesSelected"), flush=True)
        return False
    
    valid_langs = [code for code in lang_codes if code in LANGUAGES and code != 'en']
    
    if not valid_langs:
        print(t("errors.noLanguagesSelected"))
        return False
    
    # Internet connection check
    if not check_internet_connection():
        print(t("no_internet"))
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
        print(progress_msg, flush=True)

        # Show inline visual progress bar per language
        print_translation_progress(i+1, len(valid_langs))

        try:
            # Translate README first
            translate_readme(lang_code, LANGUAGES[lang_code], protected, include_changelog=with_changelog)

            if with_changelog and not has_changelog_file():
                print(t("info.noChangelogFileSkipping"))
            
            success_count += 1
            
            # Delay to avoid rate limiting
            print(t("progress.waiting", seconds=3), flush=True)
            time.sleep(3)
            
        except Exception as e:
            error_msg = t("errors.translationFailed", lang_code=lang_code, error=str(e))
            print(f"❌ {error_msg}", flush=True)
    
    # Complete progress line (remove carriage return overlay)
    print("", flush=True)

    # Update language switcher for ALL existing languages (including English)
    all_langs_for_switcher = ['en'] + valid_langs
    update_language_switcher(all_langs_for_switcher, target_dir=target_dir, output_base_dir=output_base_dir)
    
    # Show summary
    print(t("progress.completed"), flush=True)
    
    mode_summary = t("success.filesSavedWithChangelog") if with_changelog else t("success.filesSavedReadmeOnly")
    print(t("progress.filesSaved", path=os.path.join(OUTPUT_DIR)), flush=True)
    
    success_message = (t("success.translationCompletedWithChangelog", count=success_count) 
                      if with_changelog else 
                      t("success.translationCompletedReadmeOnly", count=success_count))
    print(success_message)
    
    return success_count > 0

# ---------------------- MAIN README TRANSLATION FUNCTION ----------------------
def translate_readme(lang_code, lang_info, protected, include_changelog=True):
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
    # Calculate correct relative path to root README from the translated file location
    current_file_dir = os.path.dirname(dest_path)
    english_link = ''
    try:
        english_link = os.path.relpath(os.path.join(os.getcwd(), SOURCE_FILE), current_file_dir).replace('\\', '/')
    except Exception:
        english_link = '../../README.md'

    links = [f"[English]({english_link})"]
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
        
        # Protection for file paths and names
        temp_line = protect(r'\b\w+/\w+(/\w+)*\.\w+\b', temp_line)       # File paths like app/pixiv_login.py
        temp_line = protect(r'\b\w+\.\w+\b', temp_line)                  # File extensions like README.md
        
        # Protection for version numbers and dates
        temp_line = protect(r'\bv\d+\.\d+\.\d+\b', temp_line)            # Versions like v1.0.4
        temp_line = protect(r'\b\d{4}-\d{2}-\d{2}\b', temp_line)         # Dates like 2026-03-29
        
        # Protection for technical terms and product names
        temp_line = protect(r'\bPixiv OAuth Token\b', temp_line, re.IGNORECASE)
        temp_line = protect(r'\bOAuth\b', temp_line)
        temp_line = protect(r'\bCLI\b', temp_line)
        temp_line = protect(r'\bGUI\b', temp_line)
        temp_line = protect(r'\bAPI\b', temp_line)
        temp_line = protect(r'\bGitHub\b', temp_line)
        temp_line = protect(r'\bVercel\b', temp_line)
        temp_line = protect(r'\bPython\b', temp_line)
        
        # Protection for emoji
        temp_line = protect(r'[🌐🧾🐞✨🔜📦⚙]', temp_line)
        
        # Protection for build codes
        temp_line = protect(r'\bREL-U\d+\b', temp_line)
        temp_line = protect(r'\bBUILD-UNKNOWN\b', temp_line)
        
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

    # After successfully translating README, handle CHANGELOG only when requested
    if include_changelog and has_changelog_file() and has_changelog_section_in_readme():
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
def repair_translations(target_dir=None, output_base_dir=None):
    """Repair language switchers positioning, remove duplicates, and detect translation failures."""
    _msg_repair_starting = t("ui.repairStarting")
    print(Fore.CYAN + f"\n[+] {_msg_repair_starting}")
    
    # Internet connection check
    if not check_internet_connection():
        print(Fore.RED + t("no_internet"))
        return False

    # 1. Update/fix all switchers globally
    print(Fore.YELLOW + t("ui.repairStep1"))
    update_language_switcher(target_dir=target_dir, output_base_dir=output_base_dir)
    
    # 2. Detect translation failures
    _msg_repair_step2 = t("ui.repairStep2")
    print(Fore.YELLOW + f"\n{_msg_repair_step2}")
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
                        print(Fore.RED + f"   - [FAIL] {LANGUAGES[lang_code][0]} ({lang_code}): {t('ui.highEnglishOverlap', percent=int(overlap_ratio*100))}")
                        failed_langs.append(lang_code)
                    else:
                        print(Fore.GREEN + f"   - [OK] {LANGUAGES[lang_code][0]} ({lang_code}) {t('ui.looksTranslated')}")
            except Exception as e:
                print(Fore.RED + f"   - [ERROR] {lang_code}: {t('ui.repairErrorScan', error=e)}")
                
    if failed_langs:
        print(Fore.CYAN + f"\n3. {t('ui.retranslatingFailed', count=len(failed_langs), langs=', '.join(failed_langs))}")
        translate_with_changelog(failed_langs, with_changelog=has_changelog_file(), target_dir=target_dir, output_base_dir=output_base_dir)
        print(Fore.GREEN + f"\n{t('ui.repairFixed')}")
    else:
        print(Fore.GREEN + f"\n{t('ui.repairSuccess')}")
        
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
    # Require internet connection before showing menu (blocking spinner as in pixiv_login CLI)
    _check_internet_blocking(color_on=True)

    while True:
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')

        # Load configuration from .path_config
        config_file = PATH_CONFIG_FILE
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            target_dir = config.get('target_dir') or os.getcwd()
            output_base_dir = config.get('output_base_dir') or None
        else:
            target_dir = os.getcwd()
            output_base_dir = None

        # Set OUTPUT_DIR based on configuration
        if output_base_dir:
            # Check if output_base_dir already ends with docs/lang
            if output_base_dir.endswith(os.path.join('docs', 'lang')) or output_base_dir.endswith(os.path.join('docs', 'lang').replace('\\', '/')):
                runtime_output_dir = output_base_dir
            else:
                runtime_output_dir = os.path.join(output_base_dir, 'docs', 'lang')
        else:
            runtime_output_dir = os.path.join(target_dir, 'docs', 'lang')
        
        # Set OUTPUT_DIR to the resolved path
        OUTPUT_DIR = runtime_output_dir

        # Check project status
        readme_exists = os.path.isfile(os.path.join(target_dir, SOURCE_FILE))
        changelog_exists = os.path.isfile(os.path.join(target_dir, CHANGELOG_FILE))

        # Header
        print(f"\n{Fore.WHITE}🌍 MultiDoc Translator{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}{t('ui.developer')}: Fatony Ahmad Fauzi{Style.RESET_ALL}\n")

        # Current Status
        print(f"{Fore.GREEN}✅ {t('ui.currentProjectPath')}: {target_dir}{Style.RESET_ALL}")
        output_display = output_base_dir if output_base_dir else t('ui.notSet')
        print(f"{Fore.YELLOW}📁 {t('ui.outputDirectory')}: {output_display}{Style.RESET_ALL}")
        
        # Validate output directory path
        if output_base_dir:
            normalized_output = os.path.abspath(output_base_dir)
            normalized_target = os.path.abspath(target_dir)
            if not normalized_output.startswith(normalized_target):
                print(f"{Fore.RED}{t('ui.warningDifferentProject')}{Style.RESET_ALL}")
                print(f"{Fore.RED}{t('ui.pathOutsideProject')}{Style.RESET_ALL}")
        
        # Detect project folder name
        project_folder = os.path.basename(target_dir)
        print(f"{Fore.CYAN}📂 {t('ui.folderProject')}: {project_folder}{Style.RESET_ALL}\n")

        # Source Files
        readme_color = Fore.GREEN if readme_exists else Fore.RED
        readme_status = t('ui.available') if readme_exists else t('ui.missing')
        print(f"{readme_color}{'✅' if readme_exists else '❌'} README.md: {readme_status}{Style.RESET_ALL}")
        
        changelog_color = Fore.GREEN if changelog_exists else Fore.RED
        changelog_status = t('ui.available') if changelog_exists else t('ui.missing')
        print(f"{changelog_color}{'✅' if changelog_exists else '❌'} CHANGELOG.md: {changelog_status}{Style.RESET_ALL}\n")

        # Warning message if output directory not set
        if not output_base_dir:
            print(f"{Fore.YELLOW}⚠️  Output directory not set!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please use option [8] Setup Paths first.{Style.RESET_ALL}\n")

        actions_locked = not output_base_dir
        remove_disabled = not has_translated_files(OUTPUT_DIR)

        # Main Menu
        menu_color = Fore.LIGHTBLACK_EX if actions_locked else Fore.GREEN
        remove_color = Fore.LIGHTBLACK_EX if remove_disabled or actions_locked else Fore.GREEN
        print(f"{menu_color}[1] {t('ui.changeLanguage')}{Style.RESET_ALL}")
        print(f"{menu_color}[2] {t('ui.translate')}{Style.RESET_ALL}")
        print(f"{remove_color}[3] {t('ui.removeTranslated')}{Style.RESET_ALL}")
        print(f"{menu_color}[4] {t('ui.protectionSettings')}{Style.RESET_ALL}")
        print(f"{menu_color}[5] {t('ui.autoSetupChangelog')}{Style.RESET_ALL}")
        print(f"{menu_color}[6] {t('ui.detectGithub')}{Style.RESET_ALL}")
        print(f"{Fore.RED}[7] {t('ui.repairTranslations')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[8] {t('ui.setupPaths')}{Style.RESET_ALL}")
        # [9] API Settings — always accessible
        try:
            api_cfg = load_api_config()
            active_count = sum(1 for e in api_cfg.get('apis', []) if e.get('active', False))
            total_count = len(api_cfg.get('apis', []))
            api_label = t('ui.apiSettings')
            if total_count > 0:
                api_label += f" ({active_count}/{total_count} {t('ui.apiActiveLabel')})"
        except Exception:
            api_label = t('ui.apiSettings')
        print(f"{Fore.CYAN}[9] {api_label}{Style.RESET_ALL}")
        # [10] AI Settings—always accessible
        try:
            ai_cfg = load_ai_config()
            ai_active = sum(1 for e in ai_cfg.get('ais', []) if e.get('active', False))
            ai_total  = len(ai_cfg.get('ais', []))
            ai_label  = t('ui.aiSettings')
            if ai_total > 0:
                ai_label += f" ({ai_active}/{ai_total} {t('ui.aiActiveLabel')})"
        except Exception:
            ai_label = t('ui.aiSettings')
        print(f"{Fore.MAGENTA}[10] {ai_label}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}[11] Debug{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}[0] {t('ui.exit')}{Style.RESET_ALL}")

        # Get user input
        choice = input(f"\n{Fore.YELLOW}[+] {t('ui.selectOption')} {Fore.WHITE}").strip()
        debug_print(f"User selected main menu option: {choice}", color_on=False)
        
        # Check if remove option is disabled
        if choice == '3' and remove_disabled:
            print(f"\n{Fore.YELLOW}{t('ui.noTranslatedFilesRemove')}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{t('ui.noFilesInOutputDir')}{Style.RESET_ALL}")
            input(f"\n{t('ui.pressEnter')}")
            continue
        
        if actions_locked and choice in {'2', '3', '4', '5', '6', '7'}:
            print(f"\n{Fore.YELLOW}⚠️  This action is locked because Output Directory is not set.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please use [8] Setup Paths first, then return to the main menu.{Style.RESET_ALL}")
            input(f"\n{t('ui.pressEnter')}")
            continue

        if choice == '1':
            # Change Display Language
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"\n{Fore.CYAN}{t('ui.changeLanguage')}{Style.RESET_ALL}\n")
            
            lang_options = ['en', 'pl', 'zh', 'jp', 'de', 'fr', 'es', 'ru', 'pt', 'id', 'kr']
            for lc in lang_options:
                lang_display_name = LANGUAGES.get(lc, (lc.upper(),))[0] if lc in LANGUAGES else lc.upper()
                if lc == 'id':
                    lang_display_name = 'Indonesia'
                elif lc == 'en':
                    lang_display_name = 'English'
                
                print(f"[{lc}] {lang_display_name}")
                
            print(f"\n{Fore.YELLOW}[+] {t('ui.chooseLanguageCode')} {Fore.WHITE}", end="")
            lang_choice = input().strip().lower()
            
            if not lang_choice:
                continue
                
            if lang_choice in lang_options:
                set_display_language(lang_choice)
                if lang_choice == 'id':
                    lang_display_name = 'Indonesia'
                elif lang_choice == 'en':
                    lang_display_name = 'English'
                else:
                    lang_display_name = LANGUAGES.get(lang_choice, (lang_choice.upper(),))[0]
                
                pass
            else:
                print(f"\n{Fore.RED}Invalid language code.{Style.RESET_ALL}")
                time.sleep(0.8)

        elif choice == '2':
            # Show translate submenu
            os.system('cls' if os.name == 'nt' else 'clear')
            translation_status_rows = create_translation_status_table(
                output_base_dir,
                target_dir,
                include_readme=readme_exists,
                include_changelog=changelog_exists
            )
            
            # Print translation status table
            print(f"\n{Fore.CYAN}{t('ui.translationStatus')}{Style.RESET_ALL}\n")
            for row in translation_status_rows:
                print(row)
            print()  # Add empty line below translation status

            # Translation menu options
            print()
            # Determine colors based on file availability
            readme_changelog_color = Fore.GREEN if readme_exists and changelog_exists else Fore.LIGHTBLACK_EX
            readme_only_color = Fore.GREEN if readme_exists else Fore.LIGHTBLACK_EX
            changelog_only_color = Fore.GREEN if changelog_exists else Fore.LIGHTBLACK_EX
            
            print(f"{readme_changelog_color}[1] {t('ui.translateBoth')}{Style.RESET_ALL}")
            print(f"{readme_only_color}[2] {t('ui.translateReadme')}{Style.RESET_ALL}")
            print(f"{changelog_only_color}[3] {t('ui.translateChangelog')}{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}[0] {t('ui.back')}{Style.RESET_ALL}")

            trans_choice = input(f"\n{Fore.YELLOW}[+] {t('ui.selectOption')} {Fore.WHITE}").strip()
            
            # Handle disabled options
            if trans_choice == '1' and not (readme_exists and changelog_exists):
                if not readme_exists and changelog_exists:
                    print(f"\n{Fore.YELLOW}{t('ui.cannotTranslateBoth')}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}{t('ui.missingReadmeForBoth')}{Style.RESET_ALL}")
                elif readme_exists and not changelog_exists:
                    print(f"\n{Fore.YELLOW}{t('ui.cannotTranslateBoth')}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}{t('ui.missingChangelogForBoth')}{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.YELLOW}{t('ui.cannotTranslateBoth')}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}{t('ui.missingBothFiles')}{Style.RESET_ALL}")
                input(f"\n{t('ui.pressEnter')}")
                continue

            if trans_choice == '2' and not readme_exists:
                print(f"\n{Fore.YELLOW}{t('ui.cannotTranslateReadmeOnly')}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{t('ui.missingReadme')}{Style.RESET_ALL}")
                input(f"\n{t('ui.pressEnter')}")
                continue

            if trans_choice == '3' and not changelog_exists:
                print(f"\n{Fore.YELLOW}{t('ui.cannotTranslateChangelogOnly')}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{t('ui.missingChangelog')}{Style.RESET_ALL}")
                input(f"\n{t('ui.pressEnter')}")
                continue
            
            if trans_choice == '1' and readme_exists and changelog_exists:
                # Translate README & CHANGELOG
                if not configure_runtime_paths(target_dir, output_base_dir):
                    input(f"\n{t('ui.pressEnter')}")
                    continue
                langs = input(Fore.CYAN + t('ui.enterLangCodes') + " " + Fore.WHITE).strip()
                if langs.lower() == 'all':
                    langs_list = list(LANGUAGES.keys())
                else:
                    langs_list = [l.strip() for l in langs.split(',') if l.strip() in LANGUAGES]
                if langs_list:
                    translate_with_changelog(langs_list, with_changelog=True, target_dir=target_dir, output_base_dir=output_base_dir)
                else:
                    print(Fore.RED + t('ui.invalidLanguages'))
                input(f"\n{t('ui.pressEnter')}")
                
            elif trans_choice == '2' and readme_exists:
                # Translate README Only
                if not configure_runtime_paths(target_dir, output_base_dir):
                    input(f"\n{t('ui.pressEnter')}")
                    continue
                langs = input(Fore.CYAN + t('ui.enterLangCodes') + " " + Fore.WHITE).strip()
                if langs.lower() == 'all':
                    langs_list = list(LANGUAGES.keys())
                else:
                    langs_list = [l.strip() for l in langs.split(',') if l.strip() in LANGUAGES]
                if langs_list:
                    translate_with_changelog(langs_list, with_changelog=False, target_dir=target_dir, output_base_dir=output_base_dir)
                else:
                    print(Fore.RED + t('ui.invalidLanguages'))
                input(f"\n{t('ui.pressEnter')}")
                
            elif trans_choice == '3' and changelog_exists:
                # Translate CHANGELOG Only
                if not configure_runtime_paths(target_dir, output_base_dir):
                    input(f"\n{t('ui.pressEnter')}")
                    continue
                langs = input(Fore.CYAN + t('ui.enterLangCodes') + " " + Fore.WHITE).strip()
                if langs.lower() == 'all':
                    langs_list = list(LANGUAGES.keys())
                else:
                    langs_list = [l.strip() for l in langs.split(',') if l.strip() in LANGUAGES]
                if langs_list:
                    translate_changelog_only(langs_list)
                else:
                    print(Fore.RED + t('ui.invalidLanguages'))
                input(f"\n{t('ui.pressEnter')}")
            elif trans_choice != '0':
                print(Fore.RED + t('ui.invalidOption'))
                input(f"\n{t('ui.pressEnter')}")
            
        elif choice == '3':
            # Remove Translated Languages (was option 4)
            if not has_translation_output_files(output_base_dir, target_dir):
                print(f"\n{Fore.YELLOW}⚠️  No translated files found.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}The docs/lang folder is empty or no translation results exist yet.{Style.RESET_ALL}")
                input(f"\n{t('ui.pressEnter')}")
                continue

            os.system('cls' if os.name == 'nt' else 'clear')
            while True:
                remove_status_rows = create_translation_status_table(
                    output_base_dir,
                    target_dir,
                    include_readme=readme_exists,
                    include_changelog=changelog_exists
                )
                
                # Print translation status table
                print(f"\n{Fore.CYAN}{t('ui.translationStatus')}{Style.RESET_ALL}\n")
                for row in remove_status_rows:
                    print(row)
                print()  # Add empty line below translation status

                # Remove menu options
                print()
                print(f"{Fore.GREEN}[1] {t('ui.removeBoth')}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}[2] {t('ui.removeReadme')}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}[3] {t('ui.removeChangelog')}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}[0] {t('ui.back')}{Style.RESET_ALL}")

                sub_choice = input(f"\n{Fore.YELLOW}[+] {t('ui.selectOption')} {Fore.WHITE}").strip()
                
                if sub_choice == '0':
                    break  # Exit remove submenu
                
                elif sub_choice == '1':
                    if not configure_runtime_paths(target_dir, output_base_dir):
                        input(f"\n{t('ui.pressEnter')}")
                        continue
                    langs = input(Fore.CYAN + t('ui.enterLangCodesRemove') + Fore.WHITE).strip()
                    if not langs:
                        print(Fore.YELLOW + t('ui.actionCancelled') + "\n")
                        continue
                    if langs.lower() == 'all':
                        remove_all_language_files()
                        print(Fore.GREEN + t('ui.allRemoved'))
                        input(f"\n{t('ui.pressEnter')}")
                        continue
                    else:
                        lang_codes = [l.strip() for l in langs.split(',')]
                        removed = remove_language_files(lang_codes)
                        if removed:
                            print(Fore.GREEN + t('ui.removedList', langs=', '.join(removed)))
                        input(f"\n{t('ui.pressEnter')}")
                        continue
                elif sub_choice == '2':
                    if not configure_runtime_paths(target_dir, output_base_dir):
                        input(f"\n{t('ui.pressEnter')}")
                        continue
                    langs = input(Fore.CYAN + t('ui.enterLangCodesRemoveReadme') + Fore.WHITE).strip()
                    if not langs:
                        print(Fore.YELLOW + t('ui.actionCancelled') + "\n")
                        continue
                    lang_codes = list(LANGUAGES.keys()) if langs.lower() == 'all' else [l.strip() for l in langs.split(',')]
                    removed = remove_readme_files(lang_codes)
                    if removed:
                        print(Fore.GREEN + t('ui.removedReadmeList', langs=', '.join(removed)))
                    input(f"\n{t('ui.pressEnter')}")
                    continue
                elif sub_choice == '3':
                    if not configure_runtime_paths(target_dir, output_base_dir):
                        input(f"\n{t('ui.pressEnter')}")
                        continue
                    langs = input(Fore.CYAN + t('ui.enterLangCodesRemoveChangelog') + Fore.WHITE).strip()
                    if not langs:
                        print(Fore.YELLOW + t('ui.actionCancelled') + "\n")
                        continue
                    lang_codes = list(LANGUAGES.keys()) if langs.lower() == 'all' else [l.strip() for l in langs.split(',')]
                    removed = remove_changelog_selected(lang_codes)
                    if removed:
                        print(Fore.GREEN + t('ui.removedChangelogFiles'))
                    input(f"\n{t('ui.pressEnter')}")
                    continue
                
                else:
                    print(Fore.RED + t('ui.invalidOption'))
                    input(f"\n{t('ui.pressEnter')}")
                    continue
            # End of remove submenu loop
        elif choice == '4':
            if not configure_runtime_paths(target_dir, output_base_dir):
                input(f"\n{t('ui.pressEnter')}")
                continue
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                protected = load_protected_phrases()
                status = t('ui.active') if is_protect_enabled() else t('ui.inactive')
                print("\n" + f"{Fore.WHITE}{t('ui.statusLabel')}{Style.RESET_ALL}", end="")
                if is_protect_enabled():
                    print(f"{Fore.GREEN}{status}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}{status}{Style.RESET_ALL}")
                
                print(f"\n{Fore.CYAN}{t('ui.protectedPhrasesList')}{Style.RESET_ALL}")
                if protected['protected_phrases']:
                    for phrase in protected['protected_phrases']:
                        print(f"- {phrase}")
                else:
                    print(t('ui.noProtectedDir'))
                
                print()
                print(f"{Fore.GREEN}[1] {t('ui.toggleProtection')}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}[2] {t('ui.addProtection')}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}[3] {t('ui.removeProtection')}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[4] {t('ui.resetDefault')}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}[0] {t('ui.back')}{Style.RESET_ALL}")
                
                p_choice = input(f"\n{Fore.YELLOW}[+] {t('ui.selectOption')} {Fore.WHITE}").strip()
                
                if p_choice == '1':
                    set_protect_status(not is_protect_enabled())
                elif p_choice == '2':
                    phrase = input(Fore.CYAN + t('ui.enterPhraseAdd') + Fore.WHITE).strip()
                    if phrase:
                        protected['protected_phrases'].append(phrase)
                        save_protected_phrases(protected)
                        print(Fore.GREEN + t('ui.addedPhrase', phrase=phrase))
                        time.sleep(1)
                elif p_choice == '3':
                    phrase = input(Fore.CYAN + t('ui.enterPhraseRemove') + Fore.WHITE).strip()
                    if phrase:
                        if phrase in protected['protected_phrases']:
                            protected['protected_phrases'].remove(phrase)
                            save_protected_phrases(protected)
                            print(Fore.GREEN + t('ui.removedPhrase', phrase=phrase))
                        else:
                            print(Fore.RED + t('ui.phraseNotFound'))
                        time.sleep(1)
                elif p_choice == '4':
                    save_protected_phrases(DEFAULT_PROTECTED)
                    print(Fore.GREEN + t('ui.resetSuccess'))
                    time.sleep(1)
                elif p_choice == '0':
                    break

        elif choice == '5':
            # Auto Setup Changelog Section (was option 6)
            if not configure_runtime_paths(target_dir, output_base_dir):
                input(f"\n{t('ui.pressEnter')}")
                continue
            if add_changelog_section_to_readme():
                print(Fore.GREEN + t('ui.changelogComplete'))
            else:
                print(Fore.RED + t('ui.changelogFailed'))
            input(f"\n{t('ui.pressEnter')}")
            
        elif choice == '6':
            # Detect GitHub URL (was option 7)
            if not configure_runtime_paths(target_dir, output_base_dir):
                input(f"\n{t('ui.pressEnter')}")
                continue
            detect_github_url()
            input(f"\n{t('ui.pressEnter')}")
            
        elif choice == '7':
            # Repair Translations (was option 8)
            if not configure_runtime_paths(target_dir, output_base_dir):
                input(f"\n{t('ui.pressEnter')}")
                continue
            repair_translations(target_dir=target_dir, output_base_dir=output_base_dir)
            input(f"\n{t('ui.pressEnter')}")
            
        elif choice == '8':
            # Setup Paths (NEW)
            setup_paths_menu()

        elif choice == '9':
            # API Settings
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                refresh_api_health_status()
                api_cfg = load_api_config()
                apis = api_cfg.get('apis', [])
                active_n = sum(1 for e in apis if e.get('active', False))

                print(f"\n{Fore.CYAN}{t('ui.apiMenuTitle')}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{t('ui.apiSavedNote')}{Style.RESET_ALL}\n")

                if not apis:
                    print(f"{Fore.LIGHTBLACK_EX}{t('ui.apiNoEntries')}{Style.RESET_ALL}")
                else:
                    h_idx = cjk_ljust('#', 4)
                    h_name = cjk_ljust(t('ui.apiTableName'), 20)
                    h_prov = cjk_ljust(t('ui.apiTableProvider'), 24)
                    h_stat = t('ui.apiTableStatus')
                    print(f"{Fore.WHITE}{h_idx} {h_name} {h_prov} {h_stat}{Style.RESET_ALL}")
                    print("─" * 56)
                    for idx, entry in enumerate(apis, 1):
                        status = entry.get('status')
                        if not status:
                            status = 'active' if entry.get('active', False) else 'inactive'

                        if status == 'limit':
                            st = t('ui.apiLimit')
                            st_color = Fore.YELLOW
                        elif status == 'active':
                            st = t('ui.apiActive')
                            st_color = Fore.GREEN
                        else:
                            st = t('ui.apiInactive')
                            st_color = Fore.RED

                        v_idx = cjk_ljust(idx, 4)
                        v_name = cjk_ljust(entry['name'], 20)
                        test_status = (entry.get('test_status') or "").strip()
                        prov_with_status = entry['provider'] if not test_status else f"{entry['provider']} ({test_status})"
                        v_prov = cjk_ljust(prov_with_status, 24)
                        print(f"{Fore.WHITE}{v_idx}{Style.RESET_ALL} "
                              f"{v_name} {v_prov} "
                              f"{st_color}{st}{Style.RESET_ALL}")
                    print()
                    print(f"{Fore.CYAN}{t('ui.apiActiveCount', count=active_n, total=len(apis))}{Style.RESET_ALL}")
                    if active_n == 0:
                        print(f"{Fore.YELLOW}  → {t('ui.apiUsingFree')}{Style.RESET_ALL}")

                print()
                has_apis = len(apis) > 0
                mgmt_color = Fore.GREEN if has_apis else Fore.LIGHTBLACK_EX
                del_color   = Fore.RED   if has_apis else Fore.LIGHTBLACK_EX
                tog_color   = Fore.YELLOW if has_apis else Fore.LIGHTBLACK_EX
                print(f"{Fore.GREEN}[1] {t('ui.apiAdd')}{Style.RESET_ALL}")
                print(f"{mgmt_color}[2] {t('ui.apiEdit')}{Style.RESET_ALL}")
                print(f"{del_color}[3] {t('ui.apiDelete')}{Style.RESET_ALL}")
                print(f"{tog_color}[4] {t('ui.apiToggle')}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}[0] {t('ui.back')}{Style.RESET_ALL}")

                # Print status message from previous action (shown below menu)
                if '_api_msg' in dir():
                    if _api_msg:
                        print(f"\n{_api_msg}")
                    _api_msg = ""
                else:
                    _api_msg = ""

                api_choice = input(f"\n{Fore.YELLOW}[+] {t('ui.selectOption')} {Fore.WHITE}").strip()

                if api_choice not in ('0', '1', '2', '3', '4'):
                    _api_msg = Fore.RED + t('ui.apiInvalidNumber') + Style.RESET_ALL
                    continue

                if api_choice == '0':
                    break

                elif api_choice == '1':
                    # Add API
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(f"\n{Fore.CYAN}[+] {t('ui.apiAdd')}{Style.RESET_ALL}\n")
                    print(f"{Fore.WHITE}{t('ui.apiProviders')}{Style.RESET_ALL}")
                    used_google_free = any((e.get("provider") == "google") for e in apis)
                    used_mymemory_free = any((e.get("provider") == "mymemory" and not (e.get("token") or "").strip()) for e in apis)
                    used_mymemory_emails = {
                        (e.get("token") or "").strip().lower()
                        for e in apis
                        if e.get("provider") == "mymemory" and (e.get("token") or "").lower().startswith("email:")
                    }
                    used_mymemory_keys = {
                        (e.get("token") or "").strip()
                        for e in apis
                        if e.get("provider") == "mymemory" and (e.get("token") or "").lower().startswith("key:")
                    }
                    prov_list = list(SUPPORTED_PROVIDERS.keys())
                    for pi, (pk, pdesc) in enumerate(SUPPORTED_PROVIDERS.items(), 1):
                        desc = t(f'ui.provider_{pk}')
                        is_disabled = (pk == "google" and used_google_free)
                        row_color = Fore.LIGHTBLACK_EX if is_disabled else Fore.WHITE
                        suffix = " (already used)" if is_disabled else ""
                        print(f"{row_color}  [{pi}] {pk:<16} — {desc}{suffix}{Style.RESET_ALL}")
                    print(f"  {Fore.LIGHTBLACK_EX}[0] {t('ui.apiCancel')}{Style.RESET_ALL}")
                    prov_input = input(f"\n{Fore.CYAN}{t('ui.apiSelectProvider')} (1-{len(prov_list)}, 0=cancel): {Fore.WHITE}").strip()
                    if prov_input == '0' or prov_input == '':
                        _api_msg = ""
                        continue  # back to API menu
                    if not prov_input.isdigit() or not (1 <= int(prov_input) <= len(prov_list)):
                        _api_msg = Fore.RED + t('ui.apiInvalidNumber') + Style.RESET_ALL
                        continue
                    provider = prov_list[int(prov_input) - 1]
                    if provider == "google" and used_google_free:
                        _api_msg = Fore.YELLOW + "Google free is already used. Choose another provider." + Style.RESET_ALL
                        continue

                    # Default name follows selected provider (no manual prompt)
                    name_in = provider

                    token_in = ""
                    _cancelled = False
                    test_status = "n/a"

                    if provider == "google":
                        pass  # No token needed
                    elif provider == "papago":
                        print(f"{Fore.LIGHTBLACK_EX}  ℹ️  Papago token format: client_id:secret_key{Style.RESET_ALL}")
                        token_in = input(f"{Fore.CYAN}{t('ui.apiEnterToken')} (client_id:secret_key) {Fore.LIGHTBLACK_EX}{t('ui.apiCancelHint')}{Fore.CYAN}: {Fore.WHITE}").strip()
                        if not token_in:
                            _api_msg = ""
                            _cancelled = True
                    elif provider == "mymemory":
                        print(f"{Fore.WHITE}  MyMemory auth mode:{Style.RESET_ALL}")
                        free_mode_color = Fore.LIGHTBLACK_EX if used_mymemory_free else Fore.WHITE
                        print(f"{free_mode_color}    [1] Free (no token, no email){' (already used)' if used_mymemory_free else ''}{Style.RESET_ALL}")
                        print(f"{Fore.WHITE}    [2] Email mode (de=email@domain.com){Style.RESET_ALL}")
                        print(f"{Fore.WHITE}    [3] API key mode (key=API_KEY){Style.RESET_ALL}")
                        print(f"    {Fore.LIGHTBLACK_EX}[0] {t('ui.apiCancel')}{Style.RESET_ALL}")
                        mm_choice = input(f"{Fore.CYAN}  Select mode (1-3, 0=cancel): {Fore.WHITE}").strip()
                        if mm_choice in ("0", ""):
                            _api_msg = ""
                            _cancelled = True
                        elif mm_choice == "1":
                            if used_mymemory_free:
                                _api_msg = Fore.YELLOW + "MyMemory free mode is already used." + Style.RESET_ALL
                                _cancelled = True
                            else:
                                token_in = ""
                        elif mm_choice == "2":
                            email_in = input(f"{Fore.CYAN}  Enter email (required): {Fore.WHITE}").strip()
                            if not email_in:
                                _api_msg = ""
                                _cancelled = True
                            else:
                                candidate = f"email:{email_in}".lower()
                                if candidate in used_mymemory_emails:
                                    _api_msg = Fore.YELLOW + "MyMemory email already used." + Style.RESET_ALL
                                    _cancelled = True
                                else:
                                    token_in = f"email:{email_in}"
                        elif mm_choice == "3":
                            key_in = input(f"{Fore.CYAN}  Enter API key (required): {Fore.WHITE}").strip()
                            if not key_in:
                                _api_msg = ""
                                _cancelled = True
                            else:
                                candidate = f"key:{key_in}"
                                if candidate in used_mymemory_keys:
                                    _api_msg = Fore.YELLOW + "MyMemory API key already used." + Style.RESET_ALL
                                    _cancelled = True
                                else:
                                    token_in = f"key:{key_in}"
                        else:
                            _api_msg = Fore.RED + t('ui.apiInvalidNumber') + Style.RESET_ALL
                            _cancelled = True
                    else:
                        token_in = input(f"{Fore.CYAN}{t('ui.apiEnterToken')} {Fore.LIGHTBLACK_EX}{t('ui.apiCancelHint')}{Fore.CYAN}: {Fore.WHITE}").strip()
                        if not token_in and provider not in OPTIONAL_TOKEN_PROVIDERS:
                            _api_msg = ""
                            _cancelled = True

                    if _cancelled:
                        continue

                    # Test the API connection
                    print(Fore.YELLOW + t('ui.apiTesting'))
                    test_result = _translate_with_provider("hello", "fr", provider, token_in)
                    if is_successful_translation_result(test_result):
                        print(Fore.GREEN + t('ui.apiTestSuccess', result=test_result))
                        print(Fore.GREEN + "✅ API test status: TRUE (response received)" + Style.RESET_ALL)
                        test_status = "200"
                    else:
                        print(Fore.RED + "❌ API test status: FALSE (no response/invalid token)" + Style.RESET_ALL)
                        print(Fore.RED + t('ui.apiTestFailed', error='No response or invalid token'))
                        _api_msg = Fore.RED + "API test failed. Entry was not saved." + Style.RESET_ALL
                        continue

                    default_lim = PROVIDER_DEFAULT_LIMITS.get(provider, "")
                    add_api(name_in, provider, token_in, limit=default_lim, status="active", test_status=test_status)
                    _api_msg = Fore.GREEN + t('ui.apiAdded', name=name_in) + Style.RESET_ALL


                elif api_choice == '2':
                    # Edit API
                    if not apis:
                        _api_msg = Fore.YELLOW + t('ui.apiNoEntries') + Style.RESET_ALL
                        continue
                    h_idx = cjk_ljust('#', 4)
                    h_name = cjk_ljust(t('ui.apiTableName'), 20)
                    h_prov = t('ui.apiTableProvider')
                    print(f"\n{Fore.WHITE}{h_idx} {h_name} {h_prov}{Style.RESET_ALL}")
                    for idx2, e2 in enumerate(apis, 1):
                        v_name = cjk_ljust(e2['name'], 20)
                        print(f"  {idx2}. {v_name} ({e2['provider']})")
                    print(f"  {Fore.LIGHTBLACK_EX}0. {t('ui.apiCancel')}{Style.RESET_ALL}")
                    num_in = input(f"{Fore.CYAN}{t('ui.apiSelectToEdit')} (1-{len(apis)}, 0=cancel): {Fore.WHITE}").strip()
                    if num_in == '0' or num_in == '':
                        _api_msg = ""
                        continue
                    if not num_in.isdigit() or not (1 <= int(num_in) <= len(apis)):
                        _api_msg = Fore.RED + t('ui.apiInvalidNumber') + Style.RESET_ALL
                        continue
                    entry = apis[int(num_in) - 1]
                    print(f"\n{Fore.WHITE}{t('ui.apiEditing', name=entry['name'], provider=entry['provider'])}{Style.RESET_ALL}")
                    new_name = input(f"{Fore.CYAN}{t('ui.apiNewName', name=entry['name'])}: {Fore.WHITE}").strip()
                    if new_name.lower() == 'q':
                        _api_msg = ""
                        continue
                    new_token = input(f"{Fore.CYAN}{t('ui.apiNewToken')}: {Fore.WHITE}").strip()
                    if new_token.lower() == 'q':
                        _api_msg = ""
                        continue
                    updates = {}
                    if new_name:
                        updates['name'] = new_name
                    if new_token:
                        updates['token'] = new_token
                    if updates:
                        edit_api(entry['id'], **updates)
                        _api_msg = Fore.GREEN + t('ui.apiUpdated', name=new_name or entry['name']) + Style.RESET_ALL
                    else:
                        _api_msg = ""

                elif api_choice == '3':
                    # Delete API
                    if not apis:
                        _api_msg = Fore.YELLOW + t('ui.apiNoEntries') + Style.RESET_ALL
                        continue
                    h_idx = cjk_ljust('#', 4)
                    h_name = cjk_ljust(t('ui.apiTableName'), 20)
                    h_prov = t('ui.apiTableProvider')
                    print(f"\n{Fore.WHITE}{h_idx} {h_name} {h_prov}{Style.RESET_ALL}")
                    for idx2, e2 in enumerate(apis, 1):
                        v_name = cjk_ljust(e2['name'], 20)
                        print(f"  {idx2}. {v_name} ({e2['provider']})")
                    print(f"  {Fore.LIGHTBLACK_EX}0. {t('ui.apiCancel')}{Style.RESET_ALL}")
                    num_in = input(f"{Fore.CYAN}{t('ui.apiSelectToDelete')} (1-{len(apis)}, 0=cancel): {Fore.WHITE}").strip()
                    if num_in == '0' or num_in == '':
                        _api_msg = ""
                        continue
                    if not num_in.isdigit() or not (1 <= int(num_in) <= len(apis)):
                        _api_msg = Fore.RED + t('ui.apiInvalidNumber') + Style.RESET_ALL
                        continue
                    entry = apis[int(num_in) - 1]
                    confirm = input(Fore.RED + t('ui.apiConfirmDelete', name=entry['name']) + " " + Fore.WHITE).strip().lower()
                    if confirm == 'y':
                        delete_api(entry['id'])
                        _api_msg = Fore.GREEN + t('ui.apiDeleted', name=entry['name']) + Style.RESET_ALL
                    else:
                        _api_msg = ""

                elif api_choice == '4':
                    # Toggle API active/inactive
                    if not apis:
                        _api_msg = Fore.YELLOW + t('ui.apiNoEntries') + Style.RESET_ALL
                        continue
                    h_idx = cjk_ljust('#', 4)
                    h_name = cjk_ljust(t('ui.apiTableName'), 20)
                    h_stat = t('ui.apiTableStatus')
                    print(f"\n{Fore.WHITE}{h_idx} {h_name} {h_stat}{Style.RESET_ALL}")
                    for idx2, e2 in enumerate(apis, 1):
                        status = e2.get('status')
                        if not status:
                            status = 'active' if e2.get('active', False) else 'inactive'
                        
                        if status == 'limit':
                            st2 = t('ui.apiLimit')
                        elif status == 'active':
                            st2 = t('ui.apiActive')
                        else:
                            st2 = t('ui.apiInactive')

                        v_name = cjk_ljust(e2['name'], 20)
                        print(f"  {idx2}. {v_name} {st2}")
                    print(f"  {Fore.LIGHTBLACK_EX}0. {t('ui.back')}{Style.RESET_ALL}")
                    num_in = input(f"{Fore.CYAN}{t('ui.apiSelectToToggle')} (1-{len(apis)}, 0=back): {Fore.WHITE}").strip()
                    if num_in == '0' or num_in == '':
                        _api_msg = ""
                        continue
                    if not num_in.isdigit() or not (1 <= int(num_in) <= len(apis)):
                        _api_msg = Fore.RED + t('ui.apiInvalidNumber') + Style.RESET_ALL
                        continue
                    entry = apis[int(num_in) - 1]
                    new_status = toggle_api(entry['id'])
                    if new_status == "active":
                        _api_msg = Fore.GREEN + t('ui.apiEnabled', name=entry['name']) + Style.RESET_ALL
                    elif new_status == "limit":
                        _api_msg = Fore.YELLOW + entry['name'] + ": " + t('ui.apiLimit') + Style.RESET_ALL
                    else:
                        _api_msg = Fore.RED + t('ui.apiDisabled', name=entry['name']) + Style.RESET_ALL
            
        elif choice == '10':
            # AI Settings
            _ai_msg = ""
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                ai_cfg  = load_ai_config()
                ais     = ai_cfg.get('ais', [])
                ai_act  = sum(1 for e in ais if e.get('active', False))

                print(f"\n{Fore.MAGENTA}{t('ui.aiMenuTitle')}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{t('ui.aiSavedNote')}{Style.RESET_ALL}\n")

                if not ais:
                    print(f"{Fore.LIGHTBLACK_EX}{t('ui.aiNoEntries')}{Style.RESET_ALL}")
                else:
                    h_idx = cjk_ljust('#', 4)
                    h_name = cjk_ljust(t('ui.aiTableName'), 20)
                    h_prov = cjk_ljust(t('ui.aiTableProvider'), 14)
                    h_stat = t('ui.aiTableStatus')
                    print(f"{Fore.WHITE}{h_idx} {h_name} {h_prov} {h_stat}{Style.RESET_ALL}")
                    print("─" * 50)
                    for idx, entry in enumerate(ais, 1):
                        status = entry.get('status')
                        if not status:
                            status = 'active' if entry.get('active', False) else 'inactive'

                        if status == 'limit':
                            st = t('ui.aiLimit')
                            st_col = Fore.YELLOW
                        elif status == 'active':
                            st = t('ui.aiActive')
                            st_col = Fore.GREEN
                        else:
                            st = t('ui.aiInactive')
                            st_col = Fore.RED

                        v_idx   = cjk_ljust(idx, 4)
                        v_name  = cjk_ljust(entry['name'], 20)
                        v_prov  = cjk_ljust(entry['provider'], 14)
                        
                        print(f"{Fore.WHITE}{v_idx}{Style.RESET_ALL} "
                              f"{v_name} {v_prov} "
                              f"{st_col}{st}{Style.RESET_ALL}")
                    print()
                    print(f"{Fore.MAGENTA}{t('ui.aiActiveCount', count=ai_act, total=len(ais))}{Style.RESET_ALL}")
                    if ai_act == 0:
                        print(f"{Fore.YELLOW}  → {t('ui.aiUsingDefault')}{Style.RESET_ALL}")

                print()
                has_ais  = len(ais) > 0
                mgmt_col = Fore.GREEN if has_ais else Fore.LIGHTBLACK_EX
                del_col  = Fore.RED   if has_ais else Fore.LIGHTBLACK_EX
                tog_col  = Fore.YELLOW if has_ais else Fore.LIGHTBLACK_EX
                print(f"{Fore.GREEN}[1] {t('ui.aiAdd')}{Style.RESET_ALL}")
                print(f"{mgmt_col}[2] {t('ui.aiEdit')}{Style.RESET_ALL}")
                print(f"{del_col}[3] {t('ui.aiDelete')}{Style.RESET_ALL}")
                print(f"{tog_col}[4] {t('ui.aiToggle')}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}[0] {t('ui.back')}{Style.RESET_ALL}")

                if _ai_msg:
                    print(f"\n{_ai_msg}")
                _ai_msg = ""

                ai_choice = input(f"\n{Fore.YELLOW}[+] {t('ui.selectOption')} {Fore.WHITE}").strip()

                if ai_choice not in ('0', '1', '2', '3', '4'):
                    _ai_msg = Fore.RED + t('ui.aiInvalidNumber') + Style.RESET_ALL
                    continue

                if ai_choice == '0':
                    break

                elif ai_choice == '1':
                    # ── Add AI ──
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(f"\n{Fore.MAGENTA}[+] {t('ui.aiAdd')}{Style.RESET_ALL}\n")
                    print(f"{Fore.WHITE}{t('ui.aiProviders')}{Style.RESET_ALL}")
                    ai_prov_list = list(SUPPORTED_AI_PROVIDERS.keys())
                    if not ai_prov_list:
                        _ai_msg = Fore.YELLOW + "No supported AI providers available in this build." + Style.RESET_ALL
                        continue
                    for pi, pk in enumerate(ai_prov_list, 1):
                        desc = t(f'ui.ai_provider_{pk}')
                        print(f"  [{pi}] {pk:<12} — {desc}")
                    print(f"  {Fore.LIGHTBLACK_EX}[0] {t('ui.apiCancel')}{Style.RESET_ALL}")
                    prov_in = input(f"\n{Fore.CYAN}{t('ui.aiSelectProvider')} (1-{len(ai_prov_list)}, 0=cancel): {Fore.WHITE}").strip()
                    if prov_in == '0' or prov_in == '':
                        _ai_msg = ""
                        continue
                    if not prov_in.isdigit() or not (1 <= int(prov_in) <= len(ai_prov_list)):
                        _ai_msg = Fore.RED + t('ui.aiInvalidNumber') + Style.RESET_ALL
                        continue
                    ai_provider = ai_prov_list[int(prov_in) - 1]

                    name_in = input(f"{Fore.CYAN}{t('ui.aiEnterName')} {Fore.LIGHTBLACK_EX}{t('ui.aiCancelHint')}{Fore.CYAN}: {Fore.WHITE}").strip()
                    if not name_in:
                        _ai_msg = ""
                        continue

                    auth_type = 'key'
                    if ai_provider == "custom":
                        endpoint_in = input(f"{Fore.CYAN}Endpoint URL {Fore.LIGHTBLACK_EX}{t('ui.aiCancelHint')}{Fore.CYAN}: {Fore.WHITE}").strip()
                        if not endpoint_in:
                            _ai_msg = ""
                            continue
                        token_in = input(f"{Fore.CYAN}{t('ui.aiEnterKey')} (optional Bearer token) {Fore.LIGHTBLACK_EX}{t('ui.aiCancelHint')}{Fore.CYAN}: {Fore.WHITE}").strip()
                        token_in = f"{token_in}|{endpoint_in}"
                    else:
                        token_in = input(f"{Fore.CYAN}{t('ui.aiEnterKey')} {Fore.LIGHTBLACK_EX}{t('ui.aiCancelHint')}{Fore.CYAN}: {Fore.WHITE}").strip()
                        if not token_in:
                            _ai_msg = ""
                            continue

                    default_lim = AI_PROVIDER_DEFAULT_LIMITS.get(ai_provider, "")
                    add_ai(name_in, ai_provider, token_in, auth_type, limit=default_lim, account="", status="active")
                    _ai_msg = Fore.GREEN + t('ui.aiAdded', name=name_in) + Style.RESET_ALL

                elif ai_choice == '2':
                    # ── Edit AI ──
                    if not ais:
                        _ai_msg = Fore.YELLOW + t('ui.aiNoEntries') + Style.RESET_ALL
                        continue
                    h_idx = cjk_ljust('#', 4)
                    h_name = cjk_ljust(t('ui.aiTableName'), 20)
                    h_prov = t('ui.aiTableProvider')
                    print(f"\n{Fore.WHITE}{h_idx} {h_name} {h_prov}{Style.RESET_ALL}")
                    for idx2, e2 in enumerate(ais, 1):
                        v_name = cjk_ljust(e2['name'], 20)
                        print(f"  {idx2}. {v_name} ({e2['provider']})")
                    print(f"  {Fore.LIGHTBLACK_EX}0. {t('ui.apiCancel')}{Style.RESET_ALL}")
                    num_in = input(f"{Fore.CYAN}{t('ui.aiSelectToEdit')} (1-{len(ais)}, 0=cancel): {Fore.WHITE}").strip()
                    if num_in == '0' or num_in == '':
                        _ai_msg = ""
                        continue
                    if not num_in.isdigit() or not (1 <= int(num_in) <= len(ais)):
                        _ai_msg = Fore.RED + t('ui.aiInvalidNumber') + Style.RESET_ALL
                        continue
                    entry = ais[int(num_in) - 1]
                    print(f"\n{Fore.WHITE}{t('ui.aiEditing', name=entry['name'], provider=entry['provider'])}{Style.RESET_ALL}")
                    new_name = input(f"{Fore.CYAN}{t('ui.aiNewName', name=entry['name'])}: {Fore.WHITE}").strip()
                    if new_name.lower() == 'q':
                        _ai_msg = ""
                        continue
                    new_key = input(f"{Fore.CYAN}{t('ui.aiNewKey')}: {Fore.WHITE}").strip()
                    if new_key.lower() == 'q':
                        _ai_msg = ""
                        continue
                    updates = {}
                    if new_name:
                        updates['name'] = new_name
                    if new_key:
                        updates['token'] = new_key
                    if updates:
                        edit_ai(entry['id'], **updates)
                        _ai_msg = Fore.GREEN + t('ui.aiUpdated', name=new_name or entry['name']) + Style.RESET_ALL
                    else:
                        _ai_msg = ""

                elif ai_choice == '3':
                    # ── Delete AI ──
                    if not ais:
                        _ai_msg = Fore.YELLOW + t('ui.aiNoEntries') + Style.RESET_ALL
                        continue
                    h_idx = cjk_ljust('#', 4)
                    h_name = cjk_ljust(t('ui.aiTableName'), 20)
                    h_prov = t('ui.aiTableProvider')
                    print(f"\n{Fore.WHITE}{h_idx} {h_name} {h_prov}{Style.RESET_ALL}")
                    for idx2, e2 in enumerate(ais, 1):
                        v_name = cjk_ljust(e2['name'], 20)
                        print(f"  {idx2}. {v_name} ({e2['provider']})")
                    print(f"  {Fore.LIGHTBLACK_EX}0. {t('ui.apiCancel')}{Style.RESET_ALL}")
                    num_in = input(f"{Fore.CYAN}{t('ui.aiSelectToDelete')} (1-{len(ais)}, 0=cancel): {Fore.WHITE}").strip()
                    if num_in == '0' or num_in == '':
                        _ai_msg = ""
                        continue
                    if not num_in.isdigit() or not (1 <= int(num_in) <= len(ais)):
                        _ai_msg = Fore.RED + t('ui.aiInvalidNumber') + Style.RESET_ALL
                        continue
                    entry = ais[int(num_in) - 1]
                    confirm = input(Fore.RED + t('ui.aiConfirmDelete', name=entry['name']) + " " + Fore.WHITE).strip().lower()
                    if confirm == 'y':
                        delete_ai(entry['id'])
                        _ai_msg = Fore.GREEN + t('ui.aiDeleted', name=entry['name']) + Style.RESET_ALL
                    else:
                        _ai_msg = ""

                elif ai_choice == '4':
                    # ── Toggle AI ──
                    if not ais:
                        _ai_msg = Fore.YELLOW + t('ui.aiNoEntries') + Style.RESET_ALL
                        continue
                    h_idx = cjk_ljust('#', 4)
                    h_name = cjk_ljust(t('ui.aiTableName'), 20)
                    h_stat = t('ui.aiTableStatus')
                    print(f"\n{Fore.WHITE}{h_idx} {h_name} {h_stat}{Style.RESET_ALL}")
                    for idx2, e2 in enumerate(ais, 1):
                        status = e2.get('status')
                        if not status:
                            status = 'active' if e2.get('active', False) else 'inactive'

                        if status == 'limit':
                            st2 = t('ui.aiLimit')
                        elif status == 'active':
                            st2 = t('ui.aiActive')
                        else:
                            st2 = t('ui.aiInactive')

                        v_name = cjk_ljust(e2['name'], 20)
                        print(f"  {idx2}. {v_name} {st2}")
                    print(f"  {Fore.LIGHTBLACK_EX}0. {t('ui.back')}{Style.RESET_ALL}")
                    num_in = input(f"{Fore.CYAN}{t('ui.aiSelectToToggle')} (1-{len(ais)}, 0=back): {Fore.WHITE}").strip()
                    if num_in == '0' or num_in == '':
                        _ai_msg = ""
                        continue
                    if not num_in.isdigit() or not (1 <= int(num_in) <= len(ais)):
                        _ai_msg = Fore.RED + t('ui.aiInvalidNumber') + Style.RESET_ALL
                        continue
                    entry = ais[int(num_in) - 1]
                    new_status = toggle_ai(entry['id'])
                    if new_status == "active":
                        _ai_msg = Fore.GREEN + t('ui.aiEnabled', name=entry['name']) + Style.RESET_ALL
                    elif new_status == "limit":
                        _ai_msg = Fore.YELLOW + entry['name'] + ": " + t('ui.aiLimit') + Style.RESET_ALL
                    else:
                        _ai_msg = Fore.RED + t('ui.aiDisabled', name=entry['name']) + Style.RESET_ALL

        elif choice == '11':
            open_debug_menu()

        elif choice == '0':
            print(Fore.GREEN + t('ui.exiting'))
            break


# ---------------------- MAIN PROGRAM ----------------------
def main():
    if len(sys.argv) == 1:
        init_display_language()
        interactive_menu()
        return

    display_lang = init_display_language()
    
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
        # Check internet connection before translation
        if not check_internet_connection():
            print(t("no_internet"))
            return
        
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
        
        # Check internet connection before translation
        if not check_internet_connection():
            print(t("no_internet"))
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
        # Check internet connection before translation
        if not check_internet_connection():
            print(t("no_internet"))
            return
        
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
            translate_with_changelog(valid_langs, with_changelog, target_dir=os.getcwd(), output_base_dir=OUTPUT_DIR)
        else:
            print(t("no_valid_language"))
    else:
        # Check internet connection before translation
        if not check_internet_connection():
            print(t("no_internet"))
            return
        
        # Translate all languages with CHANGELOG option
        all_langs = list(LANGUAGES.keys())
        translate_with_changelog(all_langs, with_changelog, target_dir=os.getcwd(), output_base_dir=OUTPUT_DIR)
    
    print("\n" + t("all_translated") + "\n")


DEBUG_WRAP_EXCLUDED = {
    "debug_print",
    "_instrument_all_functions_for_debug",
}
DEBUG_WRAP_INSTALLED = False


def _instrument_all_functions_for_debug():
    global DEBUG_WRAP_INSTALLED
    if DEBUG_WRAP_INSTALLED:
        return

    for func_name, func_obj in list(globals().items()):
        if not isinstance(func_obj, types.FunctionType):
            continue
        if func_obj.__module__ != __name__:
            continue
        if func_name in DEBUG_WRAP_EXCLUDED:
            continue

        @functools.wraps(func_obj)
        def wrapped(*args, __fn=func_obj, __name=func_name, **kwargs):
            debug_print(f"[FUNC] {__name}() called", color_on=False)
            return __fn(*args, **kwargs)

        globals()[func_name] = wrapped

    DEBUG_WRAP_INSTALLED = True


if __name__ == "__main__":
    _instrument_all_functions_for_debug()
    main()
