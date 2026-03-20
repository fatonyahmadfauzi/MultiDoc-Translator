import * as vscode from 'vscode';
import { TranslateSidebarProvider } from './sidebar-provider';
import { initL10n, getL10n } from './l10n';

// Global l10n instance
let l10n: ReturnType<typeof initL10n>;

export function activate(context: vscode.ExtensionContext) {
    console.log('Activating MultiDoc Translator extension...');
    
    // ✅ INISIALISASI L10N YANG DIPERBAIKI
    try {
        l10n = initL10n(context.extensionPath);
        
        // Set bahasa berdasarkan VS Code locale
        const vscodeLanguage = vscode.env.language;
        console.log(`VS Code detected language: ${vscodeLanguage}`);
        
        l10n.setLanguage(vscodeLanguage);
        
        console.log(`MultiDoc Translator initialized with language: ${l10n.getCurrentLanguage()}`);
    } catch (error) {
        console.error('Failed to initialize l10n', error);
        // Fallback initialization
        l10n = initL10n(context.extensionPath);
        l10n.setLanguage('en'); // Fallback ke English
    }
    
    const provider = new TranslateSidebarProvider(context.extensionUri, context);
    
    // Register semua commands dan resources
    const subscriptions = [
        vscode.window.registerWebviewViewProvider("multiDocTranslatorView", provider),
        vscode.commands.registerCommand("multi-doc-translator.run", () =>
            provider.generateReadmes()
        ),
        vscode.commands.registerCommand("multi-doc-translator.removeSelected", () =>
            provider.removeSelectedLanguages()
        ),
        vscode.commands.registerCommand("multi-doc-translator.removeAll", () =>
            provider.removeAllLanguages()
        ),
        // NEW: Remove Changelog Only command
        vscode.commands.registerCommand("multi-doc-translator.removeChangelogOnly", () =>
            provider.removeChangelogOnly()
        ),
        vscode.commands.registerCommand("multi-doc-translator.addProtect", () =>
            provider.addProtectPhrase()
        ),
        vscode.commands.registerCommand("multi-doc-translator.removeProtect", () =>
            provider.removeProtectPhrase()
        ),
        vscode.commands.registerCommand("multi-doc-translator.listProtect", () =>
            provider.listProtectPhrases()
        ),
        vscode.commands.registerCommand("multi-doc-translator.initProtect", () =>
            provider.initProtectPhrases()
        ),
        vscode.commands.registerCommand("multi-doc-translator.enableProtect", () =>
            provider.setProtectStatus(true)
        ),
        vscode.commands.registerCommand("multi-doc-translator.disableProtect", () =>
            provider.setProtectStatus(false)
        ),
        vscode.commands.registerCommand("multi-doc-translator.statusProtect", () =>
            provider.showProtectStatus()
        ),
        vscode.commands.registerCommand("multi-doc-translator.showProgress", () =>
            provider.showProgressOutput()
        ),
        // NEW: Changelog commands
        vscode.commands.registerCommand("multi-doc-translator.autoSetupChangelog", () =>
            provider.autoSetupChangelog()
        ),
        vscode.commands.registerCommand("multi-doc-translator.translateChangelog", () =>
            provider.translateChangelog()
        ),
        // NEW: GitHub URL detection command
        vscode.commands.registerCommand("multi-doc-translator.detectGitHubUrl", () =>
            provider.detectGitHubUrl()
        ),
        // ✅ NEW: CHANGELOG Only commands
        vscode.commands.registerCommand("multi-doc-translator.generateChangelogOnly", () =>
            provider.generateChangelogOnly()
        ),
        vscode.commands.registerCommand("multi-doc-translator.removeChangelogSelected", () =>
            provider.removeChangelogSelected()
        ),
        // Register output channels untuk proper disposal
        provider.output,
        provider.progressOutput
    ];

    subscriptions.forEach(subscription => context.subscriptions.push(subscription));
    
    console.log('MultiDoc Translator extension activated successfully');
}

export function deactivate() {
    console.log('Deactivating MultiDoc Translator extension...');
}