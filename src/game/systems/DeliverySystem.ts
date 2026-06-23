import { PARCEL_TYPES, type ParcelTypeId } from "../data/balanceConfig";
import { clamp } from "../utils/math";
export type DeliveryRewardInput = {
  baseCash: number;
  elapsedSeconds: number;
  targetSeconds: number;
  nearMisses: number;
  combo: number;
  parcelType: ParcelTypeId;
  cashMultiplier: number;
};
export type DeliveryReward = {
  cash: number;
  score: number;
  speedBonus: number;
  nearMissBonus: number;
  comboMultiplier: number;
};
export function calculateDeliveryReward(
  input: DeliveryRewardInput,
): DeliveryReward {
  const parcel = PARCEL_TYPES[input.parcelType];
  const speedRatio = clamp(
    (input.targetSeconds - input.elapsedSeconds) / input.targetSeconds,
    0,
    1,
  );
  const speedBonus = Math.round(
    input.baseCash * (0.15 + parcel.speedReward) * speedRatio,
  );
  const nearMissBonus = input.nearMisses * 10;
  const comboMultiplier = 1 + Math.max(0, input.combo - 1) * 0.18;
  const cash = Math.round(
    (input.baseCash * parcel.rewardMultiplier + speedBonus + nearMissBonus) *
      comboMultiplier *
      input.cashMultiplier,
  );
  return { cash, score: cash * 10, speedBonus, nearMissBonus, comboMultiplier };
}
