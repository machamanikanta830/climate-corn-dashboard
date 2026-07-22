#!/usr/bin/env python3
"""Merge cleaned NOAA climate and USDA corn-yield data."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--climate", type=Path, required=True)
    parser.add_argument("--yield-data", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("public/data/final_climate_yield_dataset.csv"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    climate = pd.read_csv(args.climate)
    yields = pd.read_csv(args.yield_data)

    climate_required = {"State", "Year", "TAVG", "PRCP"}
    yield_required = {"State", "Year", "Yield_bu_acre"}
    if climate_required - set(climate.columns):
        raise SystemExit("Climate input is missing required columns")
    if yield_required - set(yields.columns):
        raise SystemExit("Yield input is missing required columns")

    for frame in (climate, yields):
        frame["State"] = frame["State"].astype(str).str.upper().str.strip()
        frame["Year"] = pd.to_numeric(frame["Year"], errors="raise").astype(int)

    combined = yields.merge(climate, on=["State", "Year"], how="inner", validate="one_to_one")
    combined["TAVG_C"] = (combined["TAVG"] - 32) * 5 / 9
    combined = combined[
        ["Year", "State", "TAVG", "TAVG_C", "PRCP", "Yield_bu_acre"]
    ].sort_values(["State", "Year"])

    if combined.empty:
        raise SystemExit("The NOAA and USDA inputs have no matching state-year rows")
    if combined.isna().any().any():
        raise SystemExit("The merged dataset contains missing values")
    if combined.duplicated(["State", "Year"]).any():
        raise SystemExit("The merged dataset contains duplicate state-year rows")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(args.output, index=False)
    print(
        f"Saved {len(combined):,} rows for {combined['State'].nunique()} states "
        f"({combined['Year'].min()}-{combined['Year'].max()}) to {args.output}"
    )


if __name__ == "__main__":
    main()
