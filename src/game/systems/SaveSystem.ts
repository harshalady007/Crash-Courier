import { DEFAULT_PROFILE, type Profile } from '../data/defaultProfile';
import { safeStorage, type KeyValueStorage } from '../utils/storage';
const KEY = 'crash-courier-profile-v1';
export function serializeProfile(profile: Profile): string { return JSON.stringify(profile); }
export function deserializeProfile(raw: string | null): Profile { if (!raw) return structuredClone(DEFAULT_PROFILE); try { const parsed = JSON.parse(raw) as Partial<Profile>; return { ...structuredClone(DEFAULT_PROFILE), ...parsed, upgrades:{...DEFAULT_PROFILE.upgrades, ...parsed.upgrades} }; } catch { return structuredClone(DEFAULT_PROFILE); } }
export class SaveSystem { constructor(private storage: KeyValueStorage | undefined = safeStorage()) {} load(): Profile { return deserializeProfile(this.storage?.getItem(KEY) ?? null); } save(profile: Profile): void { this.storage?.setItem(KEY, serializeProfile(profile)); } clear(): void { this.storage?.removeItem(KEY); } }
