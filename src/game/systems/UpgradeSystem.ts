import { UPGRADES, type UpgradeId } from "../data/balanceConfig";
import type { Profile } from "../data/defaultProfile";
export type UpgradeModifiers = {
  maxSpeedMultiplier: number;
  turnMultiplier: number;
  maxHealthBonus: number;
  parcelDamageMultiplier: number;
  cashMultiplier: number;
  hotFoodGraceMultiplier: number;
};
export function getUpgradeCost(id: UpgradeId, level: number): number {
  const def = UPGRADES.find((u) => u.id === id);
  if (!def) throw new Error(`Unknown upgrade ${id}`);
  return Math.round(def.cost * (1 + level * 0.55));
}
export function applyUpgrade(profile: Profile, id: UpgradeId): Profile {
  const def = UPGRADES.find((u) => u.id === id);
  if (!def) throw new Error(`Unknown upgrade ${id}`);
  const level = profile.upgrades[id];
  const cost = getUpgradeCost(id, level);
  if (level >= def.maxLevel || profile.cash < cost) return profile;
  return {
    ...profile,
    cash: profile.cash - cost,
    upgrades: { ...profile.upgrades, [id]: level + 1 },
  };
}
export function modifiersFor(profile: Profile): UpgradeModifiers {
  const u = profile.upgrades;
  return {
    maxSpeedMultiplier: 1 + u.engine * 0.08,
    turnMultiplier: 1 + u.tires * 0.07,
    maxHealthBonus: u.armor * 10,
    parcelDamageMultiplier: 1 - u.cargoPadding * 0.08,
    cashMultiplier: 1 + u.bonusTips * 0.08,
    hotFoodGraceMultiplier: 1 + u.cooler * 0.08,
  };
}
