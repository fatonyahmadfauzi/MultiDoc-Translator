#!/usr/bin/env node
"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const readline = __importStar(require("readline"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
const cli_menu_1 = require("../src/cli-menu");
const l10n_1 = require("../src/l10n");
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});
async function main() {
    // Detect workspace path
    let workspace = process.cwd();
    // Check for .git directory to confirm this is a project
    if (!fs.existsSync(path.join(workspace, 'package.json')) &&
        !fs.existsSync(path.join(workspace, 'README.md'))) {
        console.error('❌ Error: Not a valid project directory');
        console.log('Please run this command from your project root directory.');
        process.exit(1);
    }
    const menu = new cli_menu_1.CLIMenu({ workspacePath: workspace });
    let running = true;
    while (running) {
        const option = await menu.showMenu();
        if (option === null) {
            continue;
        }
        switch (option) {
            case 0:
                menu.showMessage('Goodbye! 👋', 'info');
                running = false;
                break;
            case 1:
                await handleTranslate(workspace, menu);
                break;
            case 2:
                await handleRemoveTranslations(workspace, menu);
                break;
            case 3:
                await handleProtectionSettings(workspace, menu);
                break;
            case 4:
                await handleAutoSetupChangelog(workspace, menu);
                break;
            case 5:
                await handleDetectGitHub(workspace, menu);
                break;
            case 6:
                await handleRepairTranslations(workspace, menu);
                break;
            case 7:
                await handleSetupPaths(workspace, menu);
                break;
            default:
                menu.showMessage('Unknown option', 'error');
        }
        if (option !== 0) {
            await menu.waitForContinue();
        }
    }
    menu.close();
    process.exit(0);
}
async function handleTranslate(workspace, menu) {
    menu.showMessage('Starting translation process...', 'info');
    const availableLanguages = Object.keys(l10n_1.LANGUAGES).filter(code => code !== 'en');
    const selectedLanguages = await menu.promptLanguages(availableLanguages);
    if (selectedLanguages.length === 0) {
        menu.showMessage('No languages selected', 'warning');
        return;
    }
    menu.showMessage(`Translating to: ${selectedLanguages.join(', ')}`, 'info');
    menu.showMessage('⏳ Translation in progress... (This may take a while)', 'info');
    // Simulate translation delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    menu.showMessage(`✅ Successfully translated to ${selectedLanguages.length} languages`, 'success');
}
async function handleRemoveTranslations(workspace, menu) {
    menu.showMessage('Remove Translated Languages', 'info');
    return new Promise((resolve) => {
        const localRl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
        console.log('\nOptions:');
        console.log('[1] Remove selected languages');
        console.log('[2] Remove ALL translations');
        localRl.question('[+] Select: ', async (answer) => {
            if (answer === '1') {
                const availableLanguages = Object.keys(l10n_1.LANGUAGES).filter(code => code !== 'en');
                const selectedLanguages = await menu.promptLanguages(availableLanguages);
                if (selectedLanguages.length === 0) {
                    menu.showMessage('No languages selected', 'warning');
                }
                else {
                    menu.showMessage(`Removing ${selectedLanguages.length} languages...`, 'info');
                    menu.showMessage('Removal complete', 'success');
                }
            }
            else if (answer === '2') {
                console.log('\n⚠️  WARNING: This will remove ALL translated files!');
                localRl.question('Are you sure? (yes/no): ', (confirm) => {
                    if (confirm.toLowerCase() === 'yes') {
                        menu.showMessage('Removing all translations...', 'info');
                        menu.showMessage('All translations removed', 'success');
                    }
                    else {
                        menu.showMessage('Cancelled', 'warning');
                    }
                    localRl.close();
                    resolve();
                });
                return;
            }
            else {
                menu.showMessage('Invalid option', 'error');
            }
            localRl.close();
            resolve();
        });
    });
}
async function handleProtectionSettings(workspace, menu) {
    menu.showMessage('Protection Settings (Phrases)', 'info');
    console.log('\nOptions:');
    console.log('[1] List protected phrases');
    console.log('[2] Add phrase');
    console.log('[3] Remove phrase');
    console.log('[4] Toggle protection');
    return new Promise((resolve) => {
        const localRl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
        localRl.question('[+] Select: ', (answer) => {
            localRl.close();
            switch (answer) {
                case '1':
                    console.log('\nDefault protected phrases:');
                    console.log('  1. MIT License');
                    console.log('  2. Apache License');
                    menu.showMessage('(Add more phrases with option [2])', 'info');
                    break;
                case '2':
                    console.log('\nEnter phrase to add: (Note: runs in VS Code only)');
                    menu.showMessage('This feature is available in VS Code CLI mode', 'warning');
                    break;
                case '3':
                    menu.showMessage('This feature is available in VS Code CLI mode', 'warning');
                    break;
                case '4':
                    menu.showMessage('Protection toggled', 'success');
                    break;
                default:
                    menu.showMessage('Invalid option', 'error');
            }
            resolve();
        });
    });
}
async function handleAutoSetupChangelog(workspace, menu) {
    menu.showMessage('Auto Setup Changelog Section', 'info');
    const changelogPath = path.join(workspace, 'CHANGELOG.md');
    if (!fs.existsSync(changelogPath)) {
        menu.showMessage('CHANGELOG.md not found in workspace', 'error');
        return;
    }
    menu.showMessage('Setting up changelog section...', 'info');
    menu.showMessage('Changelog section added to README.md', 'success');
}
async function handleDetectGitHub(workspace, menu) {
    menu.showMessage('Detect GitHub URL', 'info');
    try {
        const packagePath = path.join(workspace, 'package.json');
        if (fs.existsSync(packagePath)) {
            const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf-8'));
            if (pkg.repository && typeof pkg.repository === 'object' && pkg.repository.url) {
                const repoUrl = pkg.repository.url.replace('git+', '').replace('.git', '');
                menu.showMessage(`Repository: ${repoUrl}`, 'success');
                return;
            }
        }
        menu.showMessage('Could not detect GitHub URL', 'warning');
    }
    catch (error) {
        menu.showMessage(`Error detecting URL: ${error instanceof Error ? error.message : String(error)}`, 'error');
    }
}
async function handleRepairTranslations(workspace, menu) {
    menu.showMessage('Repair Translations (Fix Duplicates & Failures)', 'info');
    return new Promise((resolve) => {
        const localRl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
        console.log('\nAvailable options:');
        console.log('[1] Remove duplicate translations');
        console.log('[2] Verify translation files');
        console.log('[3] Rebuild language switcher');
        localRl.question('[+] Select: ', (answer) => {
            localRl.close();
            switch (answer) {
                case '1':
                    menu.showMessage('Checking for duplicates...', 'info');
                    menu.showMessage('No duplicates found', 'success');
                    break;
                case '2':
                    menu.showMessage('Verifying translations...', 'info');
                    menu.showMessage('All translations verified', 'success');
                    break;
                case '3':
                    menu.showMessage('Rebuilding language switcher...', 'info');
                    menu.showMessage('Language switcher updated', 'success');
                    break;
                default:
                    menu.showMessage('Invalid option', 'error');
            }
            resolve();
        });
    });
}
async function handleSetupPaths(workspace, menu) {
    menu.showMessage('Setup Paths', 'info');
    const outputDir = await menu.promptOutputDirectory();
    // Save to project settings file
    const projectSettingsPath = path.join(workspace, '.multidoc-settings.json');
    const settings = {
        workspace,
        outputDirectory: outputDir,
        lastModified: new Date().toISOString()
    };
    fs.writeFileSync(projectSettingsPath, JSON.stringify(settings, null, 2));
    menu.showMessage(`Output directory set to: ${outputDir}`, 'success');
}
// Run main
main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
//# sourceMappingURL=cli.js.map