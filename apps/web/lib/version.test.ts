import { describe, expect, it } from 'vitest';

import { appName, appVersion } from '@/lib/version';

const SEMVER_PATTERN = /^\d+\.\d+\.\d+$/;

describe('version', () => {
  it('exports semver appVersion from package.json', () => {
    expect(appVersion).toMatch(SEMVER_PATTERN);
    expect(appVersion).toBe('0.1.0');
  });

  it('exports appName from package.json', () => {
    expect(appName).toBe('web');
  });
});
