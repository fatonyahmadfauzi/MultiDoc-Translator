import * as fs from 'fs';
import * as path from 'path';
import { Logger } from './translation-core';

// ──────────────────────────────────────────────
// AI Config Schema — identified by provider+model
// No "name" field, ever.
// ──────────────────────────────────────────────
export interface AIEntry {
    id: string;
    provider: string;   // e.g. "openai", "anthropic", "groq", "deepseek", "openrouter", "google", "mistral", "custom"
    model: string;      // e.g. "gpt-4o"
    token: string;      // API key / token
    base_url?: string | null;  // only used for "custom" provider
    enabled: boolean;
}

export interface AIConfig {
    ais: AIEntry[];
}

// ──────────────────────────────────────────────
// Provider / model reference data
// ──────────────────────────────────────────────
export const AI_PROVIDERS: string[] = [
    'groq',
    'deepseek',
    'openrouter',
    'openai',
    'anthropic',
    'google',
    'mistral',
    'custom'
];

export const AI_MODELS_BY_PROVIDER: Record<string, string[]> = {
    groq:      ['llama3-70b-8192', 'llama3-8b-8192', 'mixtral-8x7b-32768'],
    deepseek:  ['deepseek-chat'],
    openrouter:['deepseek/deepseek-chat', 'openai/gpt-4o-mini', 'anthropic/claude-3.5-sonnet'],
    openai:    ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    anthropic: ['claude-3-5-sonnet-20241022', 'claude-3-haiku-20240307', 'claude-3-opus-20240229'],
    google:    ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro'],
    mistral:  ['mistral-chat'],
    custom:    [] // user-defined
};

export const AI_CONFIG_FILE = 'ai_config.json';

// ──────────────────────────────────────────────
// I/O helpers
// ──────────────────────────────────────────────

export function loadAIConfig(extensionPath: string): AIConfig {
    const configPath = path.join(extensionPath, AI_CONFIG_FILE);
    try {
        if (!fs.existsSync(configPath)) {
            const defaults: AIConfig = { ais: [] };
            saveAIConfig(extensionPath, defaults);
            return defaults;
        }
        const raw = fs.readFileSync(configPath, 'utf-8');
        const parsed = JSON.parse(raw);
        // Validate: must have ais array
        if (!parsed || !Array.isArray(parsed.ais)) {
            return { ais: [] };
        }
        return parsed as AIConfig;
    } catch (error) {
        Logger.error('Failed to load ai_config.json', error);
        return { ais: [] };
    }
}

export function saveAIConfig(extensionPath: string, config: AIConfig): void {
    const configPath = path.join(extensionPath, AI_CONFIG_FILE);
    try {
        fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf-8');
    } catch (error) {
        Logger.error('Failed to save ai_config.json', error);
        throw error;
    }
}

// ──────────────────────────────────────────────
// CRUD operations
// ──────────────────────────────────────────────

/** Add a new AI entry. Returns the new entry's id. */
export function addAIEntry(
    extensionPath: string,
    provider: string,
    model: string,
    token: string,
    base_url: string | null,
    enabled: boolean
): AIEntry {
    const config = loadAIConfig(extensionPath);

    // Check duplicate (same provider+model)
    const existing = config.ais.find(a => a.provider === provider && a.model === model);
    if (existing) {
        // Update token instead of adding duplicate
        existing.token = token;
        if (base_url !== undefined) {
            existing.base_url = base_url;
        }
        existing.enabled = enabled;
        saveAIConfig(extensionPath, config);
        return existing;
    }

    const entry: AIEntry = {
        id: generateId(),
        provider,
        model,
        token,
        base_url: base_url || null,
        enabled
    };

    config.ais.push(entry);
    saveAIConfig(extensionPath, config);
    return entry;
}

/** Toggle enabled flag for an AI entry by id. */
export function toggleAIEntry(extensionPath: string, id: string): boolean {
    const config = loadAIConfig(extensionPath);
    const entry = config.ais.find(a => a.id === id);
    if (!entry) {
        return false;
    }
    entry.enabled = !entry.enabled;
    saveAIConfig(extensionPath, config);
    return true;
}

/** Update token (and optionally base_url) for an AI entry by id. */
export function updateAIEntryToken(
    extensionPath: string,
    id: string,
    token: string,
    base_url?: string | null
): boolean {
    const config = loadAIConfig(extensionPath);
    const entry = config.ais.find(a => a.id === id);
    if (!entry) {
        return false;
    }
    entry.token = token;
    if (base_url !== undefined) {
        entry.base_url = base_url;
    }
    saveAIConfig(extensionPath, config);
    return true;
}

/** Delete an AI entry by id. */
export function deleteAIEntry(extensionPath: string, id: string): boolean {
    const config = loadAIConfig(extensionPath);
    const before = config.ais.length;
    config.ais = config.ais.filter(a => a.id !== id);
    if (config.ais.length === before) {
        return false;
    }
    saveAIConfig(extensionPath, config);
    return true;
}

/** Get all enabled AI entries. */
export function getActiveAIs(extensionPath: string): AIEntry[] {
    const config = loadAIConfig(extensionPath);
    return config.ais.filter(a => a.enabled && a.token && a.token.trim() !== '');
}

/** Check if any AI is enabled and configured. */
export function isAIAvailable(extensionPath: string): boolean {
    return getActiveAIs(extensionPath).length > 0;
}

/** Return display label for an entry: "provider / model" */
export function getAILabel(entry: AIEntry): string {
    return `${entry.provider} / ${entry.model}`;
}

/** Mask a token for display: show first 6 chars + '...' */
export function maskToken(token: string): string {
    if (!token || token.length <= 6) {
        return token ? '••••••' : '(none)';
    }
    return token.substring(0, 6) + '••••••';
}

// ──────────────────────────────────────────────
// Utilities
// ──────────────────────────────────────────────

function generateId(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}
