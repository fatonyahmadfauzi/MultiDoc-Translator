import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { 
    translateReadme, 
    translateChangelogOnly, 
    updateLanguageSwitcher, 
    removeLanguageFiles, 
    removeAllLanguageFiles,
    hasChangelogFile,
    hasChangelogSectionInReadme,
    addChangelogSectionToReadme,
    fixExistingChangelogSpacing,
    getGitHubRepoUrl,
    getGitHubReleasesUrl,
    loadProtectedPhrases,
    saveProtectedPhrases,
    isProtectEnabled,
    setProtectStatus,
    DEFAULT_PROTECTED_PHRASES,
    Logger,
    ProtectedData,
    OUTPUT_DIR,
    translateChangelog,
    updateChangelogLinksInReadme
} from './translation-core';
import { getL10n, initL10n, LANGUAGES } from './l10n';

export class TranslateSidebarProvider implements vscode.WebviewViewProvider {
    public readonly output: vscode.OutputChannel;
    public readonly progressOutput: vscode.OutputChannel;
    private _view?: vscode.WebviewView;
    
    // ✅ PERBAIKAN: Hanya bahasa target yang bisa dipilih (tidak termasuk English)
    private selectedLanguages: Set<string> = new Set();
    private protectEnabled: boolean = false;
    private protectedPhrases: string[] = [...DEFAULT_PROTECTED_PHRASES];
    private l10n: ReturnType<typeof getL10n> | undefined;
    private generateWithChangelog: boolean = true; // ✅ NEW: Default true

    // ✅ PERBAIKAN: Daftar bahasa yang benar-benar bisa dipilih (tanpa English)
    private readonly availableTargetLanguages = ['pl', 'zh', 'jp', 'de', 'fr', 'es', 'ru', 'pt', 'id', 'kr'];

    constructor(
        private readonly _uri: vscode.Uri,
        private readonly _context: vscode.ExtensionContext
    ) {
        this.output = vscode.window.createOutputChannel("MultiDoc Translator");
        this.progressOutput = vscode.window.createOutputChannel("Translation Progress");
        
        // Inisialisasi dengan semua bahasa target terpilih (kecuali English)
        this.selectedLanguages = new Set(this.availableTargetLanguages);
        
        this.loadProtectionStatus();
    }

    resolveWebviewView(view: vscode.WebviewView) {
        // Inisialisasi l10n di sini untuk memastikan sudah ready
        try {
            this.l10n = getL10n();
        } catch (error) {
            console.error('L10n not ready, reinitializing...');
            this.l10n = initL10n(this._context.extensionPath);
        }
        
        this._view = view;
        view.webview.options = { enableScripts: true };
        this.loadProtectionStatus();
        view.webview.html = this.getWebviewContent();
        
        // ✅ Kirim terjemahan setelah webview siap
        setTimeout(() => {
            this.sendTranslationsToWebview();
        }, 100);
        
        view.webview.onDidReceiveMessage(async (msg) => {
            try {
                switch (msg.command) {
                    case 'getTranslations':
                        this.sendTranslationsToWebview();
                        break;
                    case 'run':
                        await this.generateReadmes();
                        break;
                    case 'toggleAll':
                        this.toggleAllLanguages(msg.checked);
                        break;
                    case 'toggleLanguage':
                        this.toggleLanguage(msg.language, msg.checked);
                        break;
                    case 'toggleChangelog':
                        this.toggleChangelogOption(msg.checked); // ✅ NEW
                        break;
                    case 'removeSelected':
                        await this.removeSelectedLanguages();
                        break;
                    case 'removeAll':
                        await this.removeAllLanguages();
                        break;
                    case 'removeChangelogOnly':
                        await this.removeChangelogOnly();
                        break;
                    case 'addProtect':
                        await this.addProtectPhrase();
                        break;
                    case 'removeProtect':
                        await this.removeProtectPhrase();
                        break;
                    case 'listProtect':
                        await this.listProtectPhrases();
                        break;
                    case 'initProtect':
                        await this.initProtectPhrases();
                        break;
                    case 'enableProtect':
                        await this.setProtectStatus(true);
                        break;
                    case 'disableProtect':
                        await this.setProtectStatus(false);
                        break;
                    case 'statusProtect':
                        await this.showProtectStatus();
                        break;
                    case 'showProgress':
                        this.showProgressOutput();
                        break;
                    case 'autoSetupChangelog':
                        await this.autoSetupChangelog();
                        break;
                    case 'translateChangelog':
                        await this.translateChangelog();
                        break;
                    case 'detectGitHubUrl':
                        await this.detectGitHubUrl();
                        break;
                    // ✅ NEW: CHANGELOG Only commands
                    case 'generateChangelogOnly':
                        await this.generateChangelogOnly();
                        break;
                    case 'removeChangelogSelected':
                        await this.removeChangelogSelected();
                        break;
                }
            } catch (error) {
                Logger.error('Error handling webview message', error);
                vscode.window.showErrorMessage(this.l10n.t('errors.translationFailedCheckOutput'));
            }
        });
    }

    private sendTranslationsToWebview() {
        if (this._view && this.l10n) {
            const translations = {
                languagesSelectedCount: this.l10n.t('languages.selectedCount', '{0}', '{1}'),
                affectsSelected: this.l10n.t('changelog.affectsSelected', '{0}')
            };
            
            console.log('Sending translations to webview:', translations); // ✅ DEBUG
            
            this._view.webview.postMessage({
                command: 'updateTranslations',
                translations: translations
            });
        }
    }

    private loadProtectionStatus() {
        const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (workspace) {
            this.protectEnabled = isProtectEnabled(workspace);
            const protectedData = loadProtectedPhrases(workspace);
            this.protectedPhrases = protectedData.protected_phrases;
        }
    }

    private getWebviewContent(): string {
        const t = this.l10n.t.bind(this.l10n);
        
        // ✅ PERBAIKAN: Gunakan availableTargetLanguages yang sudah dikoreksi
        const languageCheckboxes = this.availableTargetLanguages
            .map(code => {
                if (code in LANGUAGES) {
                    const [name] = LANGUAGES[code];
                    // Untuk zh, tampilkan hanya "中文"
                    const displayName = code === 'zh' ? '中文' : name;
                    const checked = this.selectedLanguages.has(code) ? 'checked' : '';
                    return `
                    <div class="language-item">
                        <label>
                            <input type="checkbox" id="lang-${code}" value="${code}" ${checked} 
                                onchange="toggleLanguage('${code}', this.checked)"
                                class="language-checkbox">
                            ${displayName}
                        </label>
                    </div>
                    `;
                }
                return '';
            })
            .join('');
        
        // ✅ PERBAIKAN: Hitung available languages berdasarkan availableTargetLanguages
        const availableLanguages = this.availableTargetLanguages.length;
        const selectedCount = this.selectedLanguages.size;
        const allChecked = selectedCount === availableLanguages ? 'checked' : '';
        const someChecked = selectedCount > 0 && selectedCount < availableLanguages;

        const protectStatusText = this.protectEnabled ? t('protection.active') : t('protection.inactive');
        const protectButtonText = this.protectEnabled ? t('protection.disable') : t('protection.enable');
        const protectButtonCommand = this.protectEnabled ? 'disableProtect' : 'enableProtect';

        // ✅ NEW: Changelog option
        const changelogChecked = this.generateWithChangelog ? 'checked' : '';

        return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    font-size: var(--vscode-font-size);
                    color: var(--vscode-foreground);
                    background: var(--vscode-editor-background);
                    padding: 12px;
                    margin: 0;
                }
                .header {
                    margin-bottom: 20px;
                }
                .header h3 {
                    margin: 0 0 8px 0;
                    color: var(--vscode-titleBar-activeForeground);
                    font-size: 14px;
                }
                .header p {
                    margin: 0;
                    color: var(--vscode-descriptionForeground);
                    font-size: 12px;
                    line-height: 1.4;
                }
                .section {
                    margin-bottom: 20px;
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 6px;
                    padding: 16px;
                    background: var(--vscode-input-background);
                }
                .section-title {
                    font-weight: bold;
                    margin-bottom: 12px;
                    color: var(--vscode-foreground);
                    font-size: 13px;
                }
                .language-list {
                    max-height: 200px;
                    overflow-y: auto;
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 4px;
                    padding: 12px;
                    background: var(--vscode-input-background);
                    margin-bottom: 8px;
                }
                .language-item {
                    margin: 6px 0;
                    padding: 4px 0;
                }
                .language-item label {
                    display: flex;
                    align-items: center;
                    cursor: pointer;
                    font-size: 13px;
                    line-height: 1.4;
                }
                .language-item input[type="checkbox"] {
                    margin-right: 10px;
                    transform: scale(1.1);
                }
                .select-all {
                    margin-bottom: 12px;
                    padding: 6px 0;
                    border-bottom: 1px solid var(--vscode-panel-border);
                }
                .select-all label {
                    display: flex;
                    align-items: center;
                    cursor: pointer;
                    font-weight: bold;
                    font-size: 13px;
                    line-height: 1.4;
                }
                .select-all input[type="checkbox"] {
                    margin-right: 10px;
                    transform: scale(1.1);
                }
                .button {
                    width: 100%;
                    padding: 10px 12px;
                    background: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 13px;
                    margin-top: 8px;
                    font-weight: 500;
                    transition: background 0.2s;
                }
                .button:hover {
                    background: var(--vscode-button-hoverBackground);
                }
                .button:disabled {
                    background: var(--vscode-button-secondaryBackground);
                    color: var(--vscode-button-secondaryForeground);
                    cursor: not-allowed;
                    opacity: 0.6;
                }
                .button.remove {
                    background: var(--vscode-inputValidation-errorBackground);
                    color: var(--vscode-inputValidation-errorForeground);
                }
                .button.remove:hover {
                    background: var(--vscode-inputValidation-errorBorder);
                }
                .button.protect {
                    background: var(--vscode-inputOption-activeBackground);
                    color: var(--vscode-inputOption-activeForeground);
                    border: 1px solid var(--vscode-inputOption-activeBorder);
                }
                .button.protect:hover {
                    background: var(--vscode-inputOption-activeBorder);
                }
                .button.remove-changelog {
                    background: var(--vscode-inputValidation-warningBackground);
                    color: var(--vscode-inputValidation-warningForeground);
                    border: 1px solid var(--vscode-inputValidation-warningBorder);
                }
                .button.remove-changelog:hover {
                    background: var(--vscode-inputValidation-warningBorder);
                }
                .stats {
                    margin-top: 12px;
                    font-size: 11px;
                    color: var(--vscode-descriptionForeground);
                    text-align: center;
                    padding: 4px;
                    background: var(--vscode-badge-background);
                    border-radius: 3px;
                }
                .indeterminate {
                    opacity: 0.7;
                }
                .button-group {
                    display: flex;
                    gap: 10px;
                    margin-top: 16px;
                }
                .button-group .button {
                    flex: 1;
                    margin-top: 0;
                }
                .protect-status {
                    padding: 12px;
                    background: var(--vscode-input-background);
                    border-radius: 4px;
                    margin-bottom: 16px;
                    font-size: 12px;
                    text-align: center;
                    border: 1px solid var(--vscode-panel-border);
                    font-weight: 500;
                }
                .protect-status.active {
                    background: var(--vscode-testing-iconPassed);
                    color: var(--vscode-input-foreground);
                    border-color: var(--vscode-testing-iconPassed);
                }
                .protect-status.inactive {
                    background: var(--vscode-inputValidation-errorBackground);
                    color: var(--vscode-inputValidation-errorForeground);
                    border-color: var(--vscode-inputValidation-errorBorder);
                }
                .small-button {
                    padding: 8px 12px;
                    font-size: 12px;
                    margin: 4px 0;
                    font-weight: 500;
                }
                .protect-buttons-grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                    margin: 12px 0;
                }
                .protect-buttons-grid .button {
                    margin: 0;
                }
                .divider {
                    height: 1px;
                    background: var(--vscode-panel-border);
                    margin: 16px 0;
                    opacity: 0.5;
                }
                .compact-grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 8px;
                    margin: 8px 0;
                }
                .compact-grid .button {
                    margin: 0;
                }
                .changelog-section {
                    background: var(--vscode-textBlockQuote-background);
                    border-left: 4px solid var(--vscode-textBlockQuote-border);
                    padding: 12px;
                    margin: 12px 0;
                    border-radius: 4px;
                }
                .info-box {
                    background: var(--vscode-textCodeBlock-background);
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 4px;
                    padding: 10px;
                    margin: 8px 0;
                    font-size: 11px;
                    line-height: 1.4;
                }
                .changelog-option {
                    margin: 12px 0;
                    padding: 8px 0;
                    border-top: 1px solid var(--vscode-panel-border);
                }
                .changelog-option label {
                    display: flex;
                    align-items: center;
                    cursor: pointer;
                    font-size: 13px;
                    font-weight: 500;
                    line-height: 1.4;
                }
                .changelog-option input[type="checkbox"] {
                    margin-right: 10px;
                    transform: scale(1.1);
                }
                .changelog-description {
                    font-size: 11px;
                    color: var(--vscode-descriptionForeground);
                    margin-left: 24px;
                    margin-top: 4px;
                    line-height: 1.3;
                }
                .changelog-only-section {
                    background: var(--vscode-textBlockQuote-background);
                    border: 1px solid var(--vscode-inputOption-activeBorder);
                    border-radius: 4px;
                    padding: 12px;
                    margin: 12px 0;
                }
                .changelog-only-title {
                    font-weight: bold;
                    margin-bottom: 8px;
                    color: var(--vscode-inputOption-activeForeground);
                    font-size: 12px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h3>${t('extension.title')}</h3>
                <p>${t('extension.description')}</p>
            </div>

            <!-- PROGRESS SECTION -->
            <div class="section">
                <div class="section-title">${t('progress.title')}</div>
                <button class="button" onclick="vscodePostMessage('showProgress')">
                    ${t('progress.show')}
                </button>
                <div style="font-size: 11px; color: var(--vscode-descriptionForeground); margin-top: 8px;">
                    ${t('progress.description')}
                </div>
            </div>

            <!-- CHANGELOG SECTION -->
            <div class="section">
                <div class="section-title">${t('changelog.title')}</div>
                <div class="changelog-section">
                    <div style="font-size: 12px; margin-bottom: 8px;">
                        <strong>${t('changelog.features')}</strong>
                    </div>
                    <div style="font-size: 11px; color: var(--vscode-descriptionForeground); line-height: 1.4;">
                        ${t('changelog.featureList')}
                    </div>
                </div>
                
                <button class="button small-button" onclick="vscodePostMessage('autoSetupChangelog')">
                    ${t('changelog.autoSetup')}
                </button>
                <button class="button small-button" onclick="vscodePostMessage('translateChangelog')">
                    ${t('changelog.translateOnly')}
                </button>
                
                <!-- NEW: Remove Changelog Only Button -->
                <button class="button small-button remove-changelog" onclick="vscodePostMessage('removeChangelogOnly')">
                    ${t('changelog.removeOnly')}
                </button>
                
                <button class="button small-button" onclick="vscodePostMessage('detectGitHubUrl')">
                    ${t('changelog.detectGitHub')}
                </button>
                
                <div class="info-box">
                    <strong>${t('changelog.githubDetection')}</strong><br>
                    ${t('changelog.githubSources')}
                </div>
            </div>

            <!-- NEW: CHANGELOG ONLY ACTIONS SECTION -->
            <div class="section">
                <div class="section-title">${t('changelog.onlyActions')}</div>
                
                <div class="changelog-only-section">
                    <div class="changelog-only-title">${t('changelog.generateRemoveOnly')}</div>
                    <div style="font-size: 11px; color: var(--vscode-descriptionForeground); margin-bottom: 12px; line-height: 1.3;">
                        ${t('changelog.onlyDescription')}
                    </div>

                    <button class="button small-button" id="generateChangelogBtn" ${selectedCount === 0 ? 'disabled' : ''} 
                            onclick="vscodePostMessage('generateChangelogOnly')">
                        ${t('changelog.generateOnly')}
                    </button>
                    
                    <button class="button small-button remove-changelog" id="removeChangelogSelectedBtn" ${selectedCount === 0 ? 'disabled' : ''} 
                            onclick="vscodePostMessage('removeChangelogSelected')">
                        ${t('changelog.removeSelected')}
                    </button>

                    <div style="font-size: 11px; color: var(--vscode-descriptionForeground); margin-top: 8px; text-align: center;">
                        ${t('changelog.affectsSelected', selectedCount.toString())}
                    </div>
                </div>
            </div>

            <!-- PROTECTION SETTINGS BOX -->
            <div class="section">
                <div class="section-title">${t('protection.title')}</div>
                
                <div class="protect-status ${this.protectEnabled ? 'active' : 'inactive'}">
                    ${t('protection.status')}: <strong>${protectStatusText}</strong>
                </div>
                
                <div class="protect-buttons-grid">
                    <button class="button protect small-button" onclick="vscodePostMessage('${protectButtonCommand}')">
                        ${protectButtonText}
                    </button>
                    <button class="button protect small-button" onclick="vscodePostMessage('statusProtect')">
                        ${t('protection.statusDetails')}
                    </button>
                </div>

                <div class="divider"></div>

                <div class="section-title" style="font-size: 12px; margin-bottom: 8px;">${t('protection.managePhrases')}:</div>
                
                <div class="compact-grid">
                    <button class="button protect" onclick="vscodePostMessage('addProtect')">
                        ${t('protection.add')}
                    </button>
                    <button class="button protect" onclick="vscodePostMessage('removeProtect')">
                        ${t('protection.remove')}
                    </button>
                    <button class="button protect" onclick="vscodePostMessage('listProtect')">
                        ${t('protection.list')}
                    </button>
                    <button class="button protect" onclick="vscodePostMessage('initProtect')">
                        ${t('protection.reset')}
                    </button>
                </div>
            </div>

            <!-- LANGUAGES BOX -->
            <div class="section">
                <div class="section-title">${t('languages.title')}</div>
                <div class="select-all">
                    <label class="${someChecked ? 'indeterminate' : ''}">
                        <input type="checkbox" id="selectAll" ${allChecked} 
                               onchange="toggleAllLanguages(this.checked)">
                        ${t('languages.selectAll')}
                    </label>
                </div>
                <div class="language-list">
                    ${languageCheckboxes}
                </div>
                <div class="stats">
                    ${t('languages.selectedCount', selectedCount.toString(), availableLanguages.toString())}
                </div>

                <!-- ✅ NEW: Changelog Option -->
                <div class="changelog-option">
                    <label>
                        <input type="checkbox" id="changelogOption" ${changelogChecked} 
                            onchange="toggleChangelogOption(this.checked)">
                        ${t('changelog.generateWith')}
                    </label>
                    <div class="changelog-description">
                        ${t('changelog.checkedDescription')}<br>
                        ${t('changelog.uncheckedDescription')}
                    </div>
                </div>
            </div>

            <button class="button" id="runBtn" ${selectedCount === 0 ? 'disabled' : ''} onclick="vscodePostMessage('run')">
                ${t('actions.generate')}
            </button>

            <div class="button-group">
                <button class="button remove" id="removeSelectedBtn" ${selectedCount === 0 ? 'disabled' : ''} onclick="vscodePostMessage('removeSelected')">
                    ${t('actions.removeSelected')}
                </button>
                <button class="button remove" id="removeAllBtn" onclick="vscodePostMessage('removeAll')">
                    ${t('actions.removeAll')}
                </button>
            </div>

            <script>
                const vscode = acquireVsCodeApi();
                
                // Store untuk terjemahan
                let translations = {
                    languagesSelectedCount: '{0} of {1} languages selected',
                    affectsSelected: 'Affects only selected languages: {0} languages'
                };
                
                function vscodePostMessage(command) {
                    vscode.postMessage({ command: command });
                }
                
                function toggleLanguage(language, checked) {
                    vscode.postMessage({
                        command: 'toggleLanguage',
                        language: language,
                        checked: checked
                    });
                    
                    updateButtonStates();
                }
                
                function toggleAllLanguages(checked) {
                    document.querySelectorAll('.language-checkbox').forEach(checkbox => {
                        checkbox.checked = checked;
                    });

                    vscode.postMessage({
                        command: 'toggleAll',
                        checked: checked
                    });
                    
                    updateButtonStates();
                }

                function toggleChangelogOption(checked) {
                    vscode.postMessage({
                        command: 'toggleChangelog',
                        checked: checked
                    });
                }

                function updateButtonStates() {
                    const selectedCount = document.querySelectorAll('.language-checkbox:checked').length;
                    const totalLanguages = document.querySelectorAll('.language-checkbox').length;
                    
                    // Update stats - GUNAKAN TRANSLATIONS
                    const statsElement = document.querySelector('.stats');
                    if (statsElement) {
                        const text = translations.languagesSelectedCount
                            .replace('{0}', selectedCount)
                            .replace('{1}', totalLanguages);
                        statsElement.textContent = text;
                    }
                    
                    // Update buttons
                    const runBtn = document.getElementById('runBtn');
                    const removeSelectedBtn = document.getElementById('removeSelectedBtn');
                    const generateChangelogBtn = document.getElementById('generateChangelogBtn');
                    const removeChangelogSelectedBtn = document.getElementById('removeChangelogSelectedBtn');
                    
                    if (runBtn) {
                        runBtn.disabled = selectedCount === 0;
                    }
                    if (removeSelectedBtn) {
                        removeSelectedBtn.disabled = selectedCount === 0;
                    }
                    if (generateChangelogBtn) {
                        generateChangelogBtn.disabled = selectedCount === 0;
                    }
                    if (removeChangelogSelectedBtn) {
                        removeChangelogSelectedBtn.disabled = selectedCount === 0;
                    }
                    
                    // Update selected count in CHANGELOG Only section - GUNAKAN TRANSLATIONS
                    const selectedCountElement = document.querySelector('.changelog-only-section div:last-child');
                    if (selectedCountElement) {
                        const text = translations.affectsSelected.replace('{0}', selectedCount);
                        selectedCountElement.textContent = text;
                    }
                    
                    // Update select all checkbox
                    const selectAllCheckbox = document.getElementById('selectAll');
                    if (selectAllCheckbox) {
                        selectAllCheckbox.checked = selectedCount === totalLanguages;
                        selectAllCheckbox.indeterminate = selectedCount > 0 && selectedCount < totalLanguages;
                    }
                }

                // Terima message dari extension dengan terjemahan
                window.addEventListener('message', event => {
                    const message = event.data;
                    
                    if (message.command === 'updateTranslations') {
                        console.log('Received translations:', message.translations); // ✅ DEBUG
                        translations = { ...translations, ...message.translations };
                        updateButtonStates();
                    }
                    else if (message.command === 'updateSelection') {
                        // Update checkboxes
                        document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                            if (checkbox.id === 'selectAll') {
                                const totalLanguages = document.querySelectorAll('.language-checkbox').length;
                                checkbox.checked = message.selectedLanguages.length === totalLanguages;
                                checkbox.indeterminate = message.selectedLanguages.length > 0 && message.selectedLanguages.length < totalLanguages;
                            } else if (checkbox.id === 'changelogOption') {
                                // Skip changelog option - handled separately
                            } else {
                                checkbox.checked = message.selectedLanguages.includes(checkbox.value);
                            }
                        });

                        updateButtonStates();
                    }
                });

                // Minta terjemahan saat pertama kali load
                document.addEventListener('DOMContentLoaded', function() {
                    vscodePostMessage('getTranslations');
                    updateButtonStates();
                });
            </script>
        </body>
        </html>
        `;
    }

    private toggleLanguage(language: string, checked: boolean) {
        if (checked) {
            this.selectedLanguages.add(language);
        } else {
            this.selectedLanguages.delete(language);
        }
        
        // ✅ PERBAIKAN: Pastikan update webview dipanggil
        this.updateWebview();
        
        // Debug: log untuk memastikan method dipanggil
        console.log(`Language ${language} ${checked ? 'selected' : 'deselected'}`);
        console.log(`Selected languages: ${Array.from(this.selectedLanguages).join(', ')}`);
    }

    private toggleAllLanguages(checked: boolean) {
        // ✅ PERBAIKAN: Gunakan availableTargetLanguages yang sudah dikoreksi
        if (checked) {
            this.selectedLanguages = new Set(this.availableTargetLanguages);
        } else {
            this.selectedLanguages.clear();
        }
        
        this.updateWebview();
    }

    // ✅ NEW: Toggle changelog option
    private toggleChangelogOption(checked: boolean) {
        this.generateWithChangelog = checked;
        console.log(`Generate with CHANGELOG: ${checked}`);
    }

    private updateWebview() {
        if (this._view) {
            this._view.webview.postMessage({
                command: 'updateSelection',
                selectedLanguages: Array.from(this.selectedLanguages)
            });
            // ✅ Juga kirim terjemahan terbaru
            this.sendTranslationsToWebview();
        }
    }

    async generateChangelogOnly() {
        if (this.selectedLanguages.size === 0) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noLanguagesSelected'));
            return;
        }

        const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspace) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noWorkspace'));
            return;
        }

        if (!hasChangelogFile(workspace)) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noChangelogFile'));
            return;
        }

        const targetLanguages = Array.from(this.selectedLanguages).filter(code => code !== 'en');

        if (targetLanguages.length === 0) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noLanguagesSelected'));
            return;
        }

        // ✅ GUNAKAN l10n UNTUK SEMUA PESAN PROGRESS
        this.progressOutput.show();
        this.progressOutput.clear();
        
        this.progressOutput.appendLine(this.l10n.t('changelog.translatingChangelog', targetLanguages.length.toString()));
        this.progressOutput.appendLine("");

        try {
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: this.l10n.t('changelog.translatingChangelog', targetLanguages.length.toString()),
                cancellable: false
            }, async (progress) => {
                const total = targetLanguages.length;
                
                for (let i = 0; i < targetLanguages.length; i++) {
                    const code = targetLanguages[i];
                    if (code in LANGUAGES) {
                        const langName = LANGUAGES[code][0];
                        
                        progress.report({
                            message: this.l10n.t('changelog.translating', langName),
                            increment: (100 / total)
                        });

                        // ✅ GUNAKAN l10n UNTUK PROGRESS OUTPUT
                        this.progressOutput.appendLine(this.l10n.t('changelog.translating', langName));

                        try {
                            const protectedData = loadProtectedPhrases(workspace);
                            await translateChangelog(code, LANGUAGES[code], protectedData, workspace);
                            await updateChangelogLinksInReadme(code, LANGUAGES[code], workspace);
                            
                            // ✅ GUNAKAN l10n UNTUK SUKSES MESSAGE
                            this.progressOutput.appendLine(this.l10n.t('changelog.translationComplete', langName));
                            
                        } catch (error) {
                            const errorMsg = this.l10n.t('errors.translationFailed', code, error);
                            Logger.error(errorMsg);
                            this.progressOutput.appendLine(`❌ ${errorMsg}`);
                            vscode.window.showErrorMessage(this.l10n.t('errors.translationFailedShort', langName));
                        }

                        await new Promise(resolve => setTimeout(resolve, 2000));
                    }
                }
            });

            // ✅ GUNAKAN l10n UNTUK SUMMARY
            this.progressOutput.appendLine("");
            this.progressOutput.appendLine(this.l10n.t('success.changelogTranslationCompleted'));
            this.progressOutput.appendLine(this.l10n.t('progress.filesSaved', path.join(workspace, OUTPUT_DIR)));

            vscode.window.showInformationMessage(
                this.l10n.t('success.changelogTranslated', targetLanguages.length.toString())
            );

        } catch (error) {
            const errorMsg = this.l10n.t('errors.changelogTranslationFailed');
            this.progressOutput.appendLine(`❌ ${errorMsg}`);
            vscode.window.showErrorMessage(this.l10n.t('errors.changelogTranslationFailed'));
        }
    }

    async removeChangelogSelected() {
        if (this.selectedLanguages.size === 0) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noLanguagesSelectedRemove'));
            return;
        }

        const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspace) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noWorkspace'));
            return;
        }

        const targetLanguages = Array.from(this.selectedLanguages).filter(code => code !== 'en');

        if (targetLanguages.length === 0) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noLanguagesSelectedRemove'));
            return;
        }

        // ✅ GUNAKAN l10n UNTUK KONFIRMASI
        const result = await vscode.window.showWarningMessage(
            this.l10n.t('confirmation.removeChangelogSelected', targetLanguages.length.toString()),
            { modal: true },
            this.l10n.t('actions.yesRemoveChangelog'),
            this.l10n.t('actions.cancel')
        );

        if (result !== this.l10n.t('actions.yesRemoveChangelog')) {
            return;
        }

        // ✅ GUNAKAN l10n UNTUK PROGRESS
        this.progressOutput.show();
        this.progressOutput.clear();
        
        this.progressOutput.appendLine(this.l10n.t('progress.removingSelected', targetLanguages.length.toString()));
        this.progressOutput.appendLine("");

        try {
            const outputDir = path.join(workspace, OUTPUT_DIR);
            let removedCount = 0;

            if (fs.existsSync(outputDir)) {
                for (const langCode of targetLanguages) {
                    const changelogPath = path.join(outputDir, `CHANGELOG-${langCode.toUpperCase()}.md`);
                    
                    if (fs.existsSync(changelogPath)) {
                        try {
                            fs.unlinkSync(changelogPath);
                            removedCount++;
                            const langName = LANGUAGES[langCode]?.[0] || langCode;
                            // ✅ GUNAKAN l10n UNTUK PROGRESS DETAIL
                            this.progressOutput.appendLine(this.l10n.t('progress.fileCreated', langName));
                        } catch (error) {
                            this.progressOutput.appendLine(this.l10n.t('errors.changelogRemoveFailed'));
                            Logger.error(`Failed to remove CHANGELOG-${langCode.toUpperCase()}.md`, error);
                        }
                    } else {
                        this.progressOutput.appendLine(this.l10n.t('info.noChangelogFiles'));
                    }
                }
            }

            if (removedCount > 0) {
                this.progressOutput.appendLine("");
                this.progressOutput.appendLine(this.l10n.t('success.changelogRemovedSelected', removedCount.toString()));
                vscode.window.showInformationMessage(
                    this.l10n.t('success.changelogRemovedSelected', removedCount.toString())
                );
            } else {
                this.progressOutput.appendLine(this.l10n.t('info.noChangelogFiles'));
                vscode.window.showInformationMessage(this.l10n.t('info.noChangelogFiles'));
            }

        } catch (error) {
            const errorMsg = this.l10n.t('errors.changelogRemoveSelectedFailed');
            this.progressOutput.appendLine(`❌ ${errorMsg}`);
            vscode.window.showErrorMessage(errorMsg);
            Logger.error('Error in removeChangelogSelected', error);
        }
    }

    async generateReadmes() {
        if (this.selectedLanguages.size === 0) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noLanguagesSelected'));
            return;
        }

        const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspace) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noWorkspace'));
            return;
        }

        // ✅ PERBAIKAN: Filter bahasa yang dipilih untuk memastikan tidak termasuk English
        const targetLanguages = Array.from(this.selectedLanguages).filter(code => code !== 'en');

        if (targetLanguages.length === 0) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noLanguagesSelected'));
            return;
        }

        // ✅ NEW: Auto setup changelog hanya jika generateWithChangelog aktif DAN file CHANGELOG ada
        if (this.generateWithChangelog && hasChangelogFile(workspace) && !hasChangelogSectionInReadme(workspace)) {
            this.progressOutput.show();
            this.progressOutput.appendLine(this.l10n.t('changelog.autoSettingUp'));
            addChangelogSectionToReadme(workspace);
        } else if (this.generateWithChangelog && hasChangelogSectionInReadme(workspace)) {
            // Perbaiki spacing untuk section yang sudah ada
            this.progressOutput.appendLine(this.l10n.t('changelog.checkingSpacing'));
            fixExistingChangelogSpacing(workspace);
        }

        const protectedData = loadProtectedPhrases(workspace);

        // Show progress output channel
        this.progressOutput.show();
        this.progressOutput.clear();
        
        const timestamp = new Date().toLocaleTimeString();
        
        // ✅ PERBAIKAN BESAR: Gunakan l10n untuk semua pesan progress
        const modeText = this.generateWithChangelog 
            ? this.l10n.t('progress.translatingWithChangelog') 
            : this.l10n.t('progress.translatingReadmeOnly');
        
        this.progressOutput.appendLine(this.l10n.t('progress.startingTranslation', targetLanguages.length.toString(), modeText));
        this.progressOutput.appendLine("");

        try {
            // Show progress bar - GUNAKAN l10n UNTUK TITLE
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: this.generateWithChangelog 
                    ? this.l10n.t('progress.translatingWithChangelog')
                    : this.l10n.t('progress.translatingReadmeOnly'),
                cancellable: false
            }, async (progress) => {
                const total = targetLanguages.length;
                
                for (let i = 0; i < targetLanguages.length; i++) {
                    const code = targetLanguages[i];
                    if (code in LANGUAGES) {
                        const langName = LANGUAGES[code][0];
                        
                        // Update progress bar - GUNAKAN l10n
                        progress.report({
                            message: this.l10n.t('progress.translatingLanguage', langName, (i + 1).toString(), total.toString()),
                            increment: (100 / total)
                        });

                        // Tampilkan progress di output channel - GUNAKAN l10n
                        this.progressOutput.appendLine(this.l10n.t('progress.translatingLanguage', langName, (i + 1).toString(), total.toString()));

                        try {
                            // Translate README first
                            await translateReadme(code, LANGUAGES[code], protectedData, workspace, this.progressOutput);
                            
                            // ✅ NEW: Translate CHANGELOG hanya jika opsi aktif DAN file CHANGELOG ada
                            if (this.generateWithChangelog && hasChangelogFile(workspace)) {
                                this.progressOutput.appendLine("");
                                this.progressOutput.appendLine(this.l10n.t('changelog.translating', langName));
                                await translateChangelogOnly([code], workspace, this.progressOutput);
                                this.progressOutput.appendLine(this.l10n.t('progress.changelogTranslated', langName));
                            } else if (this.generateWithChangelog && !hasChangelogFile(workspace)) {
                                this.progressOutput.appendLine(this.l10n.t('info.noChangelogFileSkipping'));
                            }
                            
                            // Delay untuk menghindari rate limiting dengan progress
                            await new Promise(resolve => {
                                let countdown = 3;
                                const interval = setInterval(() => {
                                    if (countdown > 0) {
                                        this.progressOutput.appendLine(this.l10n.t('progress.waiting', countdown.toString()));
                                        countdown--;
                                    } else {
                                        clearInterval(interval);
                                        resolve(null);
                                    }
                                }, 1000);
                            });
                            
                        } catch (error) {
                            const errorMsg = this.l10n.t('errors.translationFailed', code, error instanceof Error ? error.message : String(error));
                            Logger.error(errorMsg);
                            this.progressOutput.appendLine(errorMsg);
                            vscode.window.showErrorMessage(this.l10n.t('errors.translationFailedShort', LANGUAGES[code][0]));
                        }
                    }
                }
            });

            // Update language switcher untuk SEMUA bahasa yang sudah ada (termasuk yang baru)
            // ✅ PERBAIKAN: Tambahkan English ke daftar bahasa untuk language switcher
            const allLanguagesForSwitcher = ['en', ...targetLanguages];
            updateLanguageSwitcher(workspace, allLanguagesForSwitcher);

            // ✅ PERBAIKAN BESAR: Tampilkan summary dengan l10n
            this.progressOutput.appendLine("");
            this.progressOutput.appendLine(this.l10n.t('progress.completed'));
            
            // Tampilkan mode yang digunakan - GUNAKAN l10n
            const modeSummary = this.generateWithChangelog 
                ? this.l10n.t('success.filesSavedWithChangelog')
                : this.l10n.t('success.filesSavedReadmeOnly');
                
            this.progressOutput.appendLine(this.l10n.t('progress.filesSaved', path.join(workspace, OUTPUT_DIR)));

            // ✅ PERBAIKAN BESAR: Notifikasi akhir dengan l10n
            const successMessage = this.generateWithChangelog
                ? this.l10n.t('success.translationCompletedWithChangelog', targetLanguages.length.toString())
                : this.l10n.t('success.translationCompletedReadmeOnly', targetLanguages.length.toString());
                
            vscode.window.showInformationMessage(successMessage);

        } catch (error) {
            const errorMsg = this.l10n.t('errors.translationFailedGeneral', error instanceof Error ? error.message : String(error));
            this.progressOutput.appendLine(errorMsg);
            vscode.window.showErrorMessage(this.l10n.t('errors.translationFailedCheckOutput'));
        }
    }

    async removeSelectedLanguages() {
        if (this.selectedLanguages.size === 0) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noLanguagesSelectedRemove'));
            return;
        }

        const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspace) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noWorkspace'));
            return;
        }

        // ✅ PERBAIKAN: Filter bahasa yang dipilih untuk memastikan tidak termasuk English
        const targetLanguages = Array.from(this.selectedLanguages).filter(code => code !== 'en');

        if (targetLanguages.length === 0) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noLanguagesSelectedRemove'));
            return;
        }

        const result = await vscode.window.showWarningMessage(
            this.l10n.t('confirmation.removeSelected', targetLanguages.length.toString()),
            { modal: true },
            this.l10n.t('actions.yesRemove'),
            this.l10n.t('actions.cancel')
        );

        if (result !== this.l10n.t('actions.yesRemove')) {
            return;
        }

        // Show progress output
        this.progressOutput.show();
        this.progressOutput.clear();
        
        const timestamp = new Date().toLocaleTimeString();
        this.progressOutput.appendLine(this.l10n.t('progress.removingSelected', targetLanguages.length.toString()));
        this.progressOutput.appendLine("");

        const removedLangs = removeLanguageFiles(targetLanguages, workspace);

        if (removedLangs.length > 0) {
            // Update language switcher di SEMUA file setelah menghapus
            updateLanguageSwitcher(workspace, undefined, removedLangs);
            
            // Show success message in output
            this.progressOutput.appendLine(this.l10n.t('success.removalCompleted'));
            this.progressOutput.appendLine(this.l10n.t('success.removedLanguages', removedLangs.map(code => LANGUAGES[code][0]).join(', ')));
            
            vscode.window.showInformationMessage(
                this.l10n.t('success.languagesRemoved', removedLangs.length.toString(), removedLangs.map(code => LANGUAGES[code][0]).join(', '))
            );
        } else {
            this.progressOutput.appendLine(this.l10n.t('info.noFilesDeleted'));
            vscode.window.showInformationMessage(this.l10n.t('info.noFilesDeleted'));
        }
    }

    async removeAllLanguages() {
        const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspace) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noWorkspace'));
            return;
        }

        const result = await vscode.window.showWarningMessage(
            this.l10n.t('confirmation.removeAll'),
            { modal: true },
            this.l10n.t('actions.yesRemoveAll'),
            this.l10n.t('actions.cancel')
        );

        if (result !== this.l10n.t('actions.yesRemoveAll')) {
            return;
        }

        // Show progress output
        this.progressOutput.show();
        this.progressOutput.clear();
        
        const timestamp = new Date().toLocaleTimeString();
        this.progressOutput.appendLine(this.l10n.t('progress.removingAll'));
        this.progressOutput.appendLine("");

        const removedLangs = removeAllLanguageFiles(workspace);

        if (removedLangs.length > 0) {
            this.progressOutput.appendLine(this.l10n.t('success.allRemoved'));
            this.progressOutput.appendLine(this.l10n.t('success.totalRemoved', removedLangs.length.toString()));
            
            vscode.window.showInformationMessage(
                this.l10n.t('success.allTranslationFilesRemoved', removedLangs.length.toString())
            );
        } else {
            this.progressOutput.appendLine(this.l10n.t('info.noTranslationFiles'));
            vscode.window.showInformationMessage(this.l10n.t('info.noTranslationFiles'));
        }
    }

    // 🔄 NEW: Remove Changelog Only Function
    async removeChangelogOnly() {
        const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspace) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noWorkspace'));
            return;
        }

        const result = await vscode.window.showWarningMessage(
            this.l10n.t('confirmation.removeChangelog'),
            { modal: true },
            this.l10n.t('actions.yesRemoveChangelog'),
            this.l10n.t('actions.cancel')
        );

        if (result !== this.l10n.t('actions.yesRemoveChangelog')) {
            return;
        }

        // Show progress output
        this.progressOutput.show();
        this.progressOutput.clear();
        
        const timestamp = new Date().toLocaleTimeString();
        this.progressOutput.appendLine(this.l10n.t('progress.removingChangelog'));
        this.progressOutput.appendLine("");

        try {
            const outputDir = path.join(workspace, OUTPUT_DIR);
            let removedCount = 0;

            if (fs.existsSync(outputDir)) {
                const files = fs.readdirSync(outputDir);
                const changelogFiles = files.filter(file => 
                    file.startsWith("CHANGELOG-") && file.endsWith(".md")
                );

                for (const file of changelogFiles) {
                    try {
                        const filePath = path.join(outputDir, file);
                        fs.unlinkSync(filePath);
                        removedCount++;
                        this.progressOutput.appendLine(`✅ Removed: ${file}`);
                    } catch (error) {
                        this.progressOutput.appendLine(`❌ Failed to remove: ${file}`);
                        Logger.error(`Failed to remove ${file}`, error);
                    }
                }

                // Hapus folder docs/lang jika kosong, lalu docs jika juga kosong
                try {
                    if (fs.existsSync(outputDir)) {
                        const remainingFiles = fs.readdirSync(outputDir);
                        if (remainingFiles.length === 0) {
                            fs.rmdirSync(outputDir);
                            this.progressOutput.appendLine(`📁 Folder ${outputDir} deleted (empty)`);
                            
                            // Cek apakah folder docs juga kosong, jika ya hapus
                            const docsDir = path.dirname(outputDir);
                            if (fs.existsSync(docsDir) && fs.readdirSync(docsDir).length === 0) {
                                fs.rmdirSync(docsDir);
                                this.progressOutput.appendLine(`📁 Folder ${docsDir} deleted (empty)`);
                            }
                        }
                    }
                } catch (error) {
                    Logger.error('Failed to delete folder', error);
                }
            }

            if (removedCount > 0) {
                this.progressOutput.appendLine("");
                this.progressOutput.appendLine(this.l10n.t('success.changelogRemoved', removedCount.toString()));
                vscode.window.showInformationMessage(
                    this.l10n.t('success.changelogRemoved', removedCount.toString())
                );
            } else {
                this.progressOutput.appendLine(this.l10n.t('info.noChangelogFiles'));
                vscode.window.showInformationMessage(this.l10n.t('info.noChangelogFiles'));
            }

        } catch (error) {
            const errorMsg = this.l10n.t('errors.changelogRemoveFailed');
            this.progressOutput.appendLine(`❌ ${errorMsg}`);
            vscode.window.showErrorMessage(errorMsg);
            Logger.error('Error in removeChangelogOnly', error);
        }
    }

    async addProtectPhrase() {
        const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspace) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noWorkspace'));
            return;
        }

        const phrase = await vscode.window.showInputBox({
            prompt: this.l10n.t('protection.enterPhrase'),
            placeHolder: this.l10n.t('protection.phraseExample')
        });

        if (phrase) {
            const protectedData = loadProtectedPhrases(workspace);
            
            if (!protectedData.protected_phrases.includes(phrase)) {
                protectedData.protected_phrases.push(phrase);
                saveProtectedPhrases(workspace, protectedData);
                this.protectedPhrases = protectedData.protected_phrases;
                vscode.window.showInformationMessage(this.l10n.t('success.phraseAdded', phrase));
            } else {
                vscode.window.showWarningMessage(this.l10n.t('info.phraseExists', phrase));
            }
        }
    }

    async removeProtectPhrase() {
        const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspace) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noWorkspace'));
            return;
        }

        const protectedData = loadProtectedPhrases(workspace);
        
        if (protectedData.protected_phrases.length === 0) {
            vscode.window.showInformationMessage(this.l10n.t('info.noPhrasesToRemove'));
            return;
        }

        const phrase = await vscode.window.showQuickPick(protectedData.protected_phrases, {
            placeHolder: this.l10n.t('protection.selectPhraseToRemove')
        });

        if (phrase) {
            protectedData.protected_phrases = protectedData.protected_phrases.filter(p => p !== phrase);
            saveProtectedPhrases(workspace, protectedData);
            this.protectedPhrases = protectedData.protected_phrases;
            vscode.window.showInformationMessage(this.l10n.t('success.phraseRemoved', phrase));
        }
    }

    async listProtectPhrases() {
        const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspace) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noWorkspace'));
            return;
        }

        const protectedData = loadProtectedPhrases(workspace);
        
        if (protectedData.protected_phrases.length === 0) {
            vscode.window.showInformationMessage(this.l10n.t('info.noPhrasesRegistered'));
            return;
        }

        const phrasesList = protectedData.protected_phrases.map((phrase, index) => 
            `${index + 1}. ${phrase}`
        ).join('\n');

        this.output.show();
        this.output.appendLine(this.l10n.t('protection.phraseList'));
        this.output.appendLine(phrasesList);
        this.output.appendLine("");

        vscode.window.showInformationMessage(this.l10n.t('info.phraseListShown'));
    }
    
    async initProtectPhrases() {
        const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspace) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noWorkspace'));
            return;
        }

        const result = await vscode.window.showWarningMessage(
            this.l10n.t('confirmation.resetPhrases'),
            { modal: true },
            this.l10n.t('actions.yesReset'),
            this.l10n.t('actions.cancel')
        );

        if (result === this.l10n.t('actions.yesReset')) {
            const defaultData: ProtectedData = { protected_phrases: DEFAULT_PROTECTED_PHRASES };
            saveProtectedPhrases(workspace, defaultData);
            this.protectedPhrases = DEFAULT_PROTECTED_PHRASES;
            vscode.window.showInformationMessage(this.l10n.t('success.phrasesReset'));
        }
    }

    async setProtectStatus(enabled: boolean) {
        const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspace) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noWorkspace'));
            return;
        }

        setProtectStatus(workspace, enabled);
        this.protectEnabled = enabled;
        
        // Reload webview to update status
        if (this._view) {
            this._view.webview.html = this.getWebviewContent();
        }

        vscode.window.showInformationMessage(
            enabled ? this.l10n.t('success.protectionEnabled') : this.l10n.t('success.protectionDisabled')
        );
    }

    async showProtectStatus() {
        const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspace) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noWorkspace'));
            return;
        }

        const protectedData = loadProtectedPhrases(workspace);
        const status = isProtectEnabled(workspace) ? this.l10n.t('protection.active') : this.l10n.t('protection.inactive');
        
        const message = this.l10n.t('protection.statusDetailsFull', status, protectedData.protected_phrases.length.toString());
        
        vscode.window.showInformationMessage(message);
    }

    showProgressOutput() {
        this.progressOutput.show();
    }

    // 🔄 Changelog Functions
    async autoSetupChangelog() {
        const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspace) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noWorkspace'));
            return;
        }

        this.progressOutput.show();
        this.progressOutput.clear();
        
        const timestamp = new Date().toLocaleTimeString();
        this.progressOutput.appendLine(this.l10n.t('changelog.autoSettingUp'));

        if (addChangelogSectionToReadme(workspace)) {
            this.progressOutput.appendLine(this.l10n.t('success.changelogSetupCompleted'));
            vscode.window.showInformationMessage(this.l10n.t('success.changelogSectionAdded'));
        } else {
            this.progressOutput.appendLine(this.l10n.t('errors.changelogSetupFailed'));
            vscode.window.showErrorMessage(this.l10n.t('errors.changelogSetupFailed'));
        }
    }

    async translateChangelog() {
        const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspace) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noWorkspace'));
            return;
        }

        if (!hasChangelogFile(workspace)) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noChangelogFile'));
            return;
        }

        const result = await vscode.window.showQuickPick(
            [
                {
                    label: this.l10n.t('languages.all'),
                    description: this.l10n.t('changelog.translateAll')
                },
                {
                    label: this.l10n.t('languages.selected'), 
                    description: this.l10n.t('changelog.translateSelected', this.selectedLanguages.size.toString())
                }
            ],
            {
                placeHolder: this.l10n.t('changelog.selectLanguages')
            }
        );

        if (!result) {
            return;
        }

        const langCodes = result.label === this.l10n.t('languages.all') 
            ? Array.from(Object.keys(LANGUAGES))
            : Array.from(this.selectedLanguages);

        if (langCodes.length === 0) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noLanguagesSelected'));
            return;
        }

        this.progressOutput.show();
        this.progressOutput.clear();
        
        const timestamp = new Date().toLocaleTimeString();
        this.progressOutput.appendLine(this.l10n.t('changelog.translatingChangelog', langCodes.length.toString()));

        const success = await translateChangelogOnly(langCodes, workspace, this.progressOutput);

        if (success) {
            this.progressOutput.appendLine(this.l10n.t('success.changelogTranslationCompleted'));
            vscode.window.showInformationMessage(this.l10n.t('success.changelogTranslated', langCodes.length.toString()));
        } else {
            this.progressOutput.appendLine(this.l10n.t('errors.changelogTranslationFailed'));
            vscode.window.showErrorMessage(this.l10n.t('errors.changelogTranslationFailed'));
        }
    }

    // 🔄 GitHub URL Detection Function
    async detectGitHubUrl() {
        const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        if (!workspace) {
            vscode.window.showErrorMessage(this.l10n.t('errors.noWorkspace'));
            return;
        }

        const repoUrl = getGitHubRepoUrl(workspace);
        const releasesUrl = getGitHubReleasesUrl(workspace);

        if (repoUrl) {
            this.output.show();
            this.output.appendLine(this.l10n.t('github.detectionResults'));
            this.output.appendLine(this.l10n.t('github.repositoryUrl', repoUrl));
            this.output.appendLine(this.l10n.t('github.releasesUrl', releasesUrl));
            this.output.appendLine("");
            this.output.appendLine(this.l10n.t('github.sourcesChecked'));
            this.output.appendLine(this.l10n.t('github.sourcePackageJson'));
            this.output.appendLine(this.l10n.t('github.sourceGitConfig'));
            this.output.appendLine(this.l10n.t('github.sourceReadme'));
            
            vscode.window.showInformationMessage(
                this.l10n.t('success.githubUrlDetected', repoUrl, releasesUrl),
                { modal: true }
            );
        } else {
            vscode.window.showWarningMessage(
                this.l10n.t('errors.githubUrlNotDetected'),
                { modal: true }
            );
        }
    }
}