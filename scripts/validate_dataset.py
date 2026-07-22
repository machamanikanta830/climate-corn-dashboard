#!/usr/bin/env python3
"""Validate the portfolio dataset and generate its deterministic summary JSON."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

EXPECTED_COLUMNS = ["Year", "State", "TAVG", "TAVG_C", "PRCP", "Yield_bu_acre"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("public/data/final_climate_yield_dataset.csv"),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("public/data/dataset-summary.json"),
    )
    parser.add_argument("--expected-rows", type=int, default=1025)
    parser.add_argument("--expected-states", type=int, default=41)
    parser.add_argument("--expected-start-year", type=int, default=2000)
    parser.add_argument("--expected-end-year", type=int, default=2024)
    return parser.parse_args()


def rounded(value: float, digits: int = 3) -> float:
    return round(float(value), digits)


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def correlation(x_values: list[float], y_values: list[float]) -> float:
    n = len(x_values)
    sum_x = sum(x_values)
    sum_y = sum(y_values)
    numerator = n * sum(x * y for x, y in zip(x_values, y_values)) - sum_x * sum_y
    denominator = math.sqrt(
        (n * sum(x * x for x in x_values) - sum_x**2)
        * (n * sum(y * y for y in y_values) - sum_y**2)
    )
    return 0 if denominator == 0 else numerator / denominator


def main() -> None:
    args = parse_args()
    with args.input.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != EXPECTED_COLUMNS:
            raise SystemExit(
                f"Expected columns {EXPECTED_COLUMNS}, found {reader.fieldnames}"
            )

        rows = []
        for line_number, raw in enumerate(reader, start=2):
            if any(raw[column].strip() == "" for column in EXPECTED_COLUMNS):
                raise SystemExit(f"Missing value on CSV line {line_number}")
            try:
                rows.append(
                    {
                        "Year": int(raw["Year"]),
                        "State": raw["State"].strip(),
                        "TAVG": float(raw["TAVG"]),
                        "TAVG_C": float(raw["TAVG_C"]),
                        "PRCP": float(raw["PRCP"]),
                        "Yield_bu_acre": float(raw["Yield_bu_acre"]),
                    }
                )
            except ValueError as error:
                raise SystemExit(f"Invalid numeric value on CSV line {line_number}") from error

    if len(rows) != args.expected_rows:
        raise SystemExit(f"Expected {args.expected_rows} rows, found {len(rows)}")

    states = {row["State"] for row in rows}
    years = {row["Year"] for row in rows}
    if len(states) != args.expected_states:
        raise SystemExit(f"Expected {args.expected_states} states, found {len(states)}")
    if min(years) != args.expected_start_year or max(years) != args.expected_end_year:
        raise SystemExit("Unexpected year coverage")

    state_year_pairs = {(row["State"], row["Year"]) for row in rows}
    if len(state_year_pairs) != len(rows):
        raise SystemExit("Dataset contains duplicate state-year rows")

    expected_year_count = args.expected_end_year - args.expected_start_year + 1
    coverage: dict[str, set[int]] = defaultdict(set)
    for row in rows:
        coverage[row["State"]].add(row["Year"])
        expected_celsius = (row["TAVG"] - 32) * 5 / 9
        if not math.isclose(expected_celsius, row["TAVG_C"], abs_tol=1e-8):
            raise SystemExit("TAVG_C is inconsistent with TAVG")
    if any(len(state_years) != expected_year_count for state_years in coverage.values()):
        raise SystemExit("At least one state does not have complete year coverage")

    yearly: dict[int, dict[str, list[float]]] = defaultdict(
        lambda: {"TAVG": [], "PRCP": [], "Yield_bu_acre": []}
    )
    for row in rows:
        for key in yearly[row["Year"]]:
            yearly[row["Year"]][key].append(row[key])

    start = {
        key: mean(values)
        for key, values in yearly[args.expected_start_year].items()
    }
    end = {
        key: mean(values)
        for key, values in yearly[args.expected_end_year].items()
    }
    temperatures = [row["TAVG"] for row in rows]
    precipitation = [row["PRCP"] for row in rows]
    yields = [row["Yield_bu_acre"] for row in rows]

    summary = {
        "coverage": {
            "observations": len(rows),
            "states": len(states),
            "startYear": min(years),
            "endYear": max(years),
        },
        "pooledCorrelations": {
            "temperatureYield": rounded(correlation(temperatures, yields)),
            "precipitationYield": rounded(correlation(precipitation, yields)),
            "temperaturePrecipitation": rounded(
                correlation(temperatures, precipitation)
            ),
        },
        "nationalStateAverageChange": {
            "temperatureF": rounded(end["TAVG"] - start["TAVG"], 2),
            "precipitationInches": rounded(end["PRCP"] - start["PRCP"], 2),
            "yieldBuPerAcre": rounded(
                end["Yield_bu_acre"] - start["Yield_bu_acre"], 1
            ),
        },
        "methodNote": (
            "Correlations pool state-year observations and are descriptive associations, "
            "not causal estimates. Changes compare state averages in the first and last years."
        ),
    }

    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(
        f"Validated {len(rows):,} rows with complete {expected_year_count}-year "
        f"coverage; wrote {args.summary}"
    )


if __name__ == "__main__":
    main()
