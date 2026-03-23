import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';
import { Logger } from './translation-core';

export interface CLIMenuConfig {
    workspacePath: string;
    outputDirectory?: string;
}

export class CLIMenu {
    private rl: readline.Interface;
    private config: CLIMenuConfig;
    private output: string[] = [];

    constructor(config: CLIMenuConfig) {
        this.config = config;
        this.rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
    }

    public log(message: string) {
        this.output.push(message);
        console.log(message);
    }

    private checkProjectStatus(): { readme: boolean; changelog: boolean; outputDir: string | null } {
        const readmePath = path.join(this.config.workspacePath, 'README.md');
        const changelogPath = path.join(this.config.workspacePath, 'CHANGELOG.md');
        
        return {
            readme: fs.existsSync(readmePath),
            changelog: fs.existsSync(changelogPath),
            outputDir: this.config.outputDirectory || null
        };
    }

    private displayHeader() {
        console.clear();
        this.log('╔═══════════════════════════════════════════════════════════╗');
        this.log('║          🌍 MultiDoc Translator - CLI Menu               ║');
        this.log('╚═══════════════════════════════════════════════════════════╝\n');
    }

    private displayStatus() {
        const status = this.checkProjectStatus();
        
        this.log('┌─ Current Status ─────────────────────────────────────────┐');
        this.log(`║ ✅ Current project path: ${this.config.workspacePath}`);
        this.log(`║ 📁 Output Directory: ${status.outputDir || 'Not set'}`);
        this.log('└──────────────────────────────────────────────────────────┘\n');
        
        this.log('┌─ Source Files ───────────────────────────────────────────┐');
        this.log(`║ ${status.readme ? '✅' : '❌'} README.md: ${status.readme ? 'AVAILABLE' : 'NOT FOUND'}`);
        this.log(`║ ${status.changelog ? '✅' : '❌'} CHANGELOG.md: ${status.changelog ? 'AVAILABLE' : 'NOT FOUND'}`);
        this.log('└──────────────────────────────────────────────────────────┘\n');

        if (!status.outputDir) {
            this.log('⚠️  Output directory not set!');
            this.log('Please use option [7] Setup Paths first.\n');
        }
    }

    private displayMenu() {
        this.log('┌─ Main Menu ──────────────────────────────────────────────┐');
        this.log('║  [1] Translate                                           ║');
        this.log('║  [2] Remove Translated Languages                        ║');
        this.log('║  [3] Protection Settings (Phrases)                      ║');
        this.log('║  [4] Auto Setup Changelog Section                       ║');
        this.log('║  [5] Detect GitHub URL                                  ║');
        this.log('║  [6] Repair Translations (Fix Duplicates & Failures)   ║');
        this.log('║  [7] Setup Paths                                        ║');
        this.log('║  [0] Exit                                               ║');
        this.log('└──────────────────────────────────────────────────────────┘\n');
    }

    public async showMenu(): Promise<number | null> {
        this.displayHeader();
        this.displayStatus();
        this.displayMenu();

        return new Promise((resolve) => {
            this.prompt('[+] Select option: ', (answer) => {
                const option = parseInt(answer, 10);
                if (isNaN(option) || option < 0 || option > 7) {
                    this.log('❌ Invalid option. Please enter a number between 0 and 7.\n');
                    resolve(null);
                } else {
                    resolve(option);
                }
            });
        });
    }

    private prompt(question: string, callback: (answer: string) => void) {
        this.rl.question(question, (answer) => {
            callback(answer.trim());
        });
    }

    public promptLanguages(available: string[]): Promise<string[]> {
        return new Promise((resolve) => {
            this.log(`\nAvailable languages: ${available.join(', ')}`);
            this.log('Enter language codes separated by commas (or "all" for all languages):');
            
            this.prompt('[+] Languages: ', (answer) => {
                if (answer.toLowerCase() === 'all') {
                    resolve(available);
                } else {
                    const selected = answer.split(',').map(l => l.trim()).filter(l => l.length > 0);
                    resolve(selected);
                }
            });
        });
    }

    public promptOutputDirectory(): Promise<string> {
        return new Promise((resolve) => {
            this.log('\nEnter output directory path (or press Enter for default "./docs"):');
            
            this.prompt('[+] Output Directory: ', (answer) => {
                resolve(answer || './docs');
            });
        });
    }

    public showMessage(message: string, type: 'info' | 'success' | 'warning' | 'error' = 'info') {
        const icons = {
            info: 'ℹ️ ',
            success: '✅ ',
            warning: '⚠️  ',
            error: '❌ '
        };
        this.log(`\n${icons[type]} ${message}\n`);
    }

    public async waitForContinue() {
        this.prompt('Press Enter to continue...', () => {
            // Continue
        });
    }

    public close() {
        this.rl.close();
    }

    public getOutput(): string {
        return this.output.join('\n');
    }
}
