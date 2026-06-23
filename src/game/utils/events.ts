export const EVENTS = {
  hud: "hud:update",
  runOver: "run:over",
  delivered: "delivery:success",
  parcel: "parcel:change",
  cash: "cash:change",
} as const;
export type HudSnapshot = {
  score: number;
  cash: number;
  combo: number;
  time: number;
  deliveryTime: number;
  health: number;
  parcel: number;
  objective: string;
};
