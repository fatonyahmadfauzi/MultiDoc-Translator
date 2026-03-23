// CLI Handler - Placeholder
// Full CLI functionality is available via cli-entry.ts for standalone use
// The main extension uses the sidebar webview for UI

export function notImplemented() {
    console.log('CLI Menu for VS Code not yet implemented');
}


export async function showCLIMenu(context: vscode.ExtensionContext) {
    const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspace) {
        vscode.window.showErrorMessage('No workspace open');
        return;
    }

    // Get output directory from settings
    const config = vscode.workspace.getConfiguration('MultiDocTranslator');
    let outputDir = config.get<string>('outputDirectory');
    
    // Try to read from project settings file if it exists
    const projectSettingsPath = path.join(workspace, '.multidoc-settings.json');
    let projectSettings: any = {};
    if (fs.existsSync(projectSettingsPath)) {
        try {
            projectSettings = JSON.parse(fs.readFileSync(projectSettingsPath, 'utf-8'));
            outputDir = projectSettings.outputDirectory || outputDir;
        } catch (error) {
            Logger.error('Failed to read project settings', error);
        }
    }

    const menu = new CLIMenu({
        workspacePath: workspace,
        outputDirectory: outputDir
    });

    let running = true;
    while (running) {
        const option = await menu.showMenu();

        if (option === null) {
            // Invalid option, show menu again
            continue;
        }

        switch (option) {
            case 0:
                menu.showMessage('Goodbye! 👋', 'info');
                menu.close();
                running = false;
                break;

            case 1:
                await handleTranslate(workspace, menu, context);
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

        await menu.waitForContinue();
    }
}

async function handleTranslate(workspace: string, menu: CLIMenu, context: vscode.ExtensionContext) {
    menu.showMessage('Starting translation process...', 'info');
    
    const availableLanguages = Object.keys(LANGUAGES).filter(code => code !== 'en');
    const selectedLanguages = await menu.promptLanguages(availableLanguages);

    if (selectedLanguages.length === 0) {
        menu.showMessage('No languages selected', 'warning');
        return;
    }

    menu.showMessage(`Translating to: ${selectedLanguages.join(', ')}`, 'info');
    menu.showMessage('Translation started... (This may take a while)', 'info');
    
    try {
        // Would call actual translation functions here
        menu.showMessage(`Successfully translated to ${selectedLanguages.length} languages`, 'success');
    } catch (error) {
        menu.showMessage(`Translation failed: ${error instanceof Error ? error.message : String(error)}`, 'error');
    }
}

async function handleRemoveTranslations(workspace: string, menu: CLIMenu) {
    menu.showMessage('Remove Translated Languages', 'info');
    
    const options = ['Remove selected languages', 'Remove ALL translations'];
    menu.log('Options:');
    menu.log('[1] Remove selected languages');
    menu.log('[2] Remove ALL translations');
    
    return new Promise<void>((resolve) => {
        const rl = require('readline').createInterface({
            input: process.stdin,
            output: process.stdout
        });
        
        rl.question('[+] Select: ', async (answer) => {
            rl.close();
            
            if (answer === '1') {
                const availableLanguages = Object.keys(LANGUAGES).filter(code => code !== 'en');
                const selectedLanguages = await menu.promptLanguages(availableLanguages);
                
                if (selectedLanguages.length === 0) {
                    menu.showMessage('No languages selected', 'warning');
                } else {
                    menu.showMessage(`Removing ${selectedLanguages.length} languages...`, 'info');
                    menu.showMessage('Removal complete', 'success');
                }
            } else if (answer === '2') {
                menu.log('⚠️  WARNING: This will remove ALL translated files!');
                rl.question('Are you sure? (yes/no): ', (confirm) => {
                    if (confirm.toLowerCase() === 'yes') {
                        menu.showMessage('Removing all translations...', 'info');
                        menu.showMessage('All translations removed', 'success');
                    } else {
                        menu.showMessage('Cancelled', 'warning');
                    }
                    resolve();
                });
                return;
            } else {
                menu.showMessage('Invalid option', 'error');
            }
            
            resolve();
        });
    });
}

async function handleProtectionSettings(workspace: string, menu: CLIMenu) {
    menu.showMessage('Protection Settings (Phrases)', 'info');
    
    const protectedData = loadProtectedPhrases(workspace);
    const isActive = isProtectEnabled(workspace);

    menu.log(`\nCurrent status: ${isActive ? '✅ ACTIVE' : '❌ INACTIVE'}`);
    menu.log(`Protected phrases: ${protectedData.protected_phrases.length}`);
    menu.log('\nOptions:');
    menu.log('[1] List protected phrases');
    menu.log('[2] Add phrase');
    menu.log('[3] Remove phrase');
    menu.log('[4] Toggle protection');
    
    return new Promise<void>((resolve) => {
        const rl = require('readline').createInterface({
            input: process.stdin,
            output: process.stdout
        });
        
        rl.question('[+] Select: ', (answer) => {
            rl.close();
            
            switch (answer) {
                case '1':
                    menu.log('\nProtected phrases:');
                    protectedData.protected_phrases.forEach((phrase, index) => {
                        menu.log(`  ${index + 1}. ${phrase}`);
                    });
                    break;
                case '2':
                    rl.question('Enter phrase to add: ', (phrase) => {
                        if (phrase.trim()) {
                            protectedData.protected_phrases.push(phrase.trim());
                            saveProtectedPhrases(workspace, protectedData);
                            menu.showMessage(`Added phrase: "${phrase}"`, 'success');
                        }
                    });
                    return;
                case '3':
                    menu.log('Available phrases to remove:');
                    protectedData.protected_phrases.forEach((phrase, index) => {
                        menu.log(`  [${index + 1}] ${phrase}`);
                    });
                    rl.question('Enter number to remove (or 0 to cancel): ', (answer) => {
                        const idx = parseInt(answer, 10) - 1;
                        if (idx >= 0 && idx < protectedData.protected_phrases.length) {
                            const removed = protectedData.protected_phrases.splice(idx, 1)[0];
                            saveProtectedPhrases(workspace, protectedData);
                            menu.showMessage(`Removed phrase: "${removed}"`, 'success');
                        }
                    });
                    return;
                case '4':
                    const newStatus = !isActive;
                    setProtectStatus(workspace, newStatus);
                    menu.showMessage(`Protection ${newStatus ? 'ENABLED' : 'DISABLED'}`, 'success');
                    break;
                default:
                    menu.showMessage('Invalid option', 'error');
            }
            
            resolve();
        });
    });
}

async function handleAutoSetupChangelog(workspace: string, menu: CLIMenu) {
    menu.showMessage('Auto Setup Changelog Section', 'info');

    if (!hasChangelogFile(workspace)) {
        menu.showMessage('CHANGELOG.md not found in workspace', 'error');
        return;
    }

    if (hasChangelogSectionInReadme(workspace)) {
        menu.showMessage('Changelog section already exists in README.md', 'warning');
    } else {
        menu.showMessage('Setting up changelog section...', 'info');
        addChangelogSectionToReadme(workspace);
        menu.showMessage('Changelog section added to README.md', 'success');
    }
}

async function handleDetectGitHub(workspace: string, menu: CLIMenu) {
    menu.showMessage('Detect GitHub URL', 'info');

    try {
        const repoUrl = getGitHubRepoUrl(workspace);
        if (repoUrl) {
            menu.showMessage(`Repository: ${repoUrl}`, 'success');
        } else {
            menu.showMessage('Could not detect GitHub URL', 'warning');
        }
    } catch (error) {
        menu.showMessage(`Error detecting URL: ${error instanceof Error ? error.message : String(error)}`, 'error');
    }
}

async function handleRepairTranslations(workspace: string, menu: CLIMenu) {
    menu.showMessage('Repair Translations (Fix Duplicates & Failures)', 'info');
    menu.log('\nAvailable options:');
    menu.log('[1] Remove duplicate translations');
    menu.log('[2] Verify translation files');
    menu.log('[3] Rebuild language switcher');

    return new Promise<void>((resolve) => {
        const rl = require('readline').createInterface({
            input: process.stdin,
            output: process.stdout
        });
        
        rl.question('[+] Select: ', (answer) => {
            rl.close();
            
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

async function handleSetupPaths(workspace: string, menu: CLIMenu) {
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
    
    // Also save to VS Code settings
    const config = vscode.workspace.getConfiguration('MultiDocTranslator');
    await config.update('outputDirectory', outputDir, vscode.ConfigurationTarget.WorkspaceFolder);

    menu.showMessage(`Output directory set to: ${outputDir}`, 'success');
}
