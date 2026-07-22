import { describe, expect, it } from "vitest";
import {
  linearRegression,
  mean,
  pearsonCorrelation,
  regressionFromPairs,
} from "./statistics";

describe("statistics utilities", () => {
  it("calculates means and ignores non-finite values", () => {
    expect(mean([1, 2, 3, null])).toBe(2);
  });

  it("calculates perfect positive and negative correlations", () => {
    expect(pearsonCorrelation([1, 2, 3], [2, 4, 6])).toBeCloseTo(1);
    expect(pearsonCorrelation([1, 2, 3], [6, 4, 2])).toBeCloseTo(-1);
  });

  it("returns zero when a variable has no variance", () => {
    expect(pearsonCorrelation([1, 1, 1], [2, 3, 4])).toBe(0);
  });

  it("calculates a linear regression", () => {
    expect(linearRegression([1, 2, 3], [3, 5, 7])).toEqual({
      slope: 2,
      intercept: 1,
      r: 1,
    });
  });

  it("supports the pair format used by the scatterplots", () => {
    const result = regressionFromPairs([
      [1, 3],
      [2, 5],
      [3, 7],
    ]);
    expect(result.slope).toBe(2);
    expect(result.r).toBe(1);
  });
});
