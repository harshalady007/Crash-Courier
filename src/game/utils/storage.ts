export interface KeyValueStorage { getItem(key: string): string | null; setItem(key: string, value: string): void; removeItem(key: string): void; }
export function safeStorage(): KeyValueStorage | undefined { try { return globalThis.localStorage; } catch { return undefined; } }
