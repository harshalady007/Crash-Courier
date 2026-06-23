export type UpgradeId = 'engine'|'tires'|'armor'|'cooler'|'cargoPadding'|'bonusTips';
export type ParcelTypeId = 'standard'|'glass'|'hotFood';
export type UpgradeDef = { id: UpgradeId; name: string; description: string; maxLevel: number; cost: number; effectPerLevel: number };
export const UPGRADES: UpgradeDef[] = [
  { id:'engine', name:'Turbo Engine', description:'+ top speed', maxLevel:5, cost:120, effectPerLevel:0.08 },
  { id:'tires', name:'Sticky Tires', description:'+ steering grip', maxLevel:5, cost:100, effectPerLevel:0.07 },
  { id:'armor', name:'Van Armor', description:'+ van health', maxLevel:5, cost:110, effectPerLevel:10 },
  { id:'cooler', name:'Food Warmer', description:'+ hot food grace', maxLevel:4, cost:90, effectPerLevel:0.08 },
  { id:'cargoPadding', name:'Cargo Padding', description:'- parcel damage', maxLevel:5, cost:105, effectPerLevel:0.08 },
  { id:'bonusTips', name:'Tip Magnet', description:'+ delivery cash', maxLevel:5, cost:130, effectPerLevel:0.08 },
];
export const PARCEL_TYPES = {
  standard: { id:'standard', label:'Standard Box', damageMultiplier:1, rewardMultiplier:1, speedReward:0 },
  glass: { id:'glass', label:'Glass Crate', damageMultiplier:1.65, rewardMultiplier:1.25, speedReward:0 },
  hotFood: { id:'hotFood', label:'Hot Food', damageMultiplier:0.9, rewardMultiplier:1.05, speedReward:0.55 },
} as const;
