import { describe, expect, it } from "vitest";
import { filterRecords, normalizeYearRange, toCelsius } from "./data";

const records = [
  { State: "IOWA", Year: 2000 },
  { State: "IOWA", Year: 2001 },
  { State: "OHIO", Year: 2001 },
  { State: "OHIO", Year: 2002 },
];

describe("data utilities", () => {
  it("converts Fahrenheit to Celsius", () => {
    expect(toCelsius(32)).toBe(0);
    expect(toCelsius(68)).toBe(20);
  });

  it("filters records by year and state", () => {
    expect(
      filterRecords(records, { startYear: 2001, endYear: 2002, state: "OHIO" })
    ).toEqual([
      { State: "OHIO", Year: 2001 },
      { State: "OHIO", Year: 2002 },
    ]);
  });

  it("enforces a three-year selection", () => {
    expect(normalizeYearRange(2000, 2001, 2000, 2024)).toEqual([2000, 2002]);
    expect(normalizeYearRange(2024, 2000, 2000, 2024)).toEqual([2022, 2024]);
  });
});
