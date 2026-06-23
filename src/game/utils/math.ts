export function clamp(value: number, min: number, max: number): number { return Math.min(max, Math.max(min, value)); }
export function distance(a: { x: number; y: number }, b: { x: number; y: number }): number { return Math.hypot(a.x - b.x, a.y - b.y); }
export function randomItem<T>(items: readonly T[], random = Math.random): T { return items[Math.floor(random() * items.length)]!; }
