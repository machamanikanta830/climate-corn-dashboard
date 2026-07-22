#!/usr/bin/env python3
"""Clean a USDA NASS Quick Stats CSV export for state-level corn yield."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

YIELD_ITEM = "CORN, GRAIN - YIELD, MEASURED IN BU / ACRE"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/interim/usda_corn_yield_2000_2024.csv"),
    )
    parser.add_argument("--start-year", type=int, default=2000)
    parser.add_argument("--end-year", type=int, default=2024)
    return parser.parse_args()


def require_columns(frame: pd.DataFrame, columns: set[str]) -> None:
    missing = columns - set(frame.columns)
    if missing:
        raise SystemExit(f"USDA export is missing columns: {sorted(missing)}")


def main() -> None:
    args = parse_args()
    frame = pd.read_csv(args.input, low_memory=False)
    require_columns(frame, {"Year", "State", "Geo Level", "Data Item", "Value"})

    cleaned = frame.copy()
    cleaned = cleaned[
        cleaned["Geo Level"].astype(str).str.upper().str.strip().eq("STATE")
    ]
    cleaned = cleaned[
        cleaned["Data Item"].astype(str).str.contains(YIELD_ITEM, case=False, na=False)
    ]

    if "Domain" in cleaned.columns:
        total_domain = cleaned["Domain"].astype(str).str.upper().str.strip().eq("TOTAL")
        if total_domain.any():
            cleaned = cleaned[total_domain]

    cleaned["Year"] = pd.to_numeric(cleaned["Year"], errors="coerce")
    cleaned["State"] = cleaned["State"].astype(str).str.upper().str.strip()
    cleaned["Yield_bu_acre"] = pd.to_numeric(
        cleaned["Value"].astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    )

    cleaned = cleaned[
        cleaned["Year"].between(args.start_year, args.end_year)
        & cleaned["State"].ne("OTHER STATES")
    ][["Year", "State", "Yield_bu_acre"]].dropna()
    cleaned["Year"] = cleaned["Year"].astype(int)
    cleaned = cleaned.sort_values(["State", "Year"]).reset_index(drop=True)

    duplicates = cleaned.duplicated(["State", "Year"], keep=False)
    if duplicates.any():
        sample = cleaned.loc[duplicates, ["State", "Year"]].head().to_dict("records")
        raise SystemExit(f"Duplicate USDA state-year rows remain after filtering: {sample}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(args.output, index=False)
    print(
        f"Saved {len(cleaned):,} rows for {cleaned['State'].nunique()} states "
        f"to {args.output}"
    )


if __name__ == "__main__":
    main()
