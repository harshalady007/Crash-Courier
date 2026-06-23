import { describe, expect, it } from "vitest";
import { calculateDeliveryReward } from "../../src/game/systems/DeliverySystem";

describe("calculateDeliveryReward", () => {
  it("rewards faster hot-food deliveries and combo chains", () => {
    const slow = calculateDeliveryReward({
      baseCash: 80,
      elapsedSeconds: 32,
      targetSeconds: 34,
      nearMisses: 0,
      combo: 1,
      parcelType: "hotFood",
      cashMultiplier: 1,
    });
    const fast = calculateDeliveryReward({
      baseCash: 80,
      elapsedSeconds: 8,
      targetSeconds: 34,
      nearMisses: 2,
      combo: 3,
      parcelType: "hotFood",
      cashMultiplier: 1.1,
    });
    expect(fast.cash).toBeGreaterThan(slow.cash);
    expect(fast.nearMissBonus).toBe(20);
    expect(fast.comboMultiplier).toBeGreaterThan(1);
  });
});
