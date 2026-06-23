import type { UpgradeId } from "./balanceConfig";
export type Profile = {
  version: 1;
  cash: number;
  bestScore: number;
  upgrades: Record<UpgradeId, number>;
  muted: boolean;
};
export const DEFAULT_PROFILE: Profile = {
  version: 1,
  cash: 0,
  bestScore: 0,
  muted: false,
  upgrades: {
    engine: 0,
    tires: 0,
    armor: 0,
    cooler: 0,
    cargoPadding: 0,
    bonusTips: 0,
  },
};
