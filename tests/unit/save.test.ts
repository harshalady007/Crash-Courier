import { describe, expect, it } from 'vitest';
import { DEFAULT_PROFILE } from '../../src/game/data/defaultProfile';
import { deserializeProfile, serializeProfile } from '../../src/game/systems/SaveSystem';

describe('save serialization', () => {
  it('round-trips profile data and tolerates invalid saves', () => {
    const profile = { ...structuredClone(DEFAULT_PROFILE), cash: 123, bestScore: 456 };
    expect(deserializeProfile(serializeProfile(profile))).toMatchObject({ cash: 123, bestScore: 456 });
    expect(deserializeProfile('{bad')).toEqual(DEFAULT_PROFILE);
  });
});
