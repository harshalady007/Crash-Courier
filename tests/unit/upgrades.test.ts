import { describe, expect, it } from "vitest";
import { DEFAULT_PROFILE } from "../../src/game/data/defaultProfile";
import {
  applyUpgrade,
  getUpgradeCost,
  modifiersFor,
} from "../../src/game/systems/UpgradeSystem";

describe("upgrades", () => {
  it("spends cash and changes modifiers when affordable", () => {
    const profile = { ...structuredClone(DEFAULT_PROFILE), cash: 500 };
    const upgraded = applyUpgrade(profile, "engine");
    expect(upgraded.cash).toBe(500 - getUpgradeCost("engine", 0));
    expect(upgraded.upgrades.engine).toBe(1);
    expect(modifiersFor(upgraded).maxSpeedMultiplier).toBeGreaterThan(1);
  });
});
