#!/usr/bin/env python3
"""Download and aggregate NOAA GSOY climate observations by state and year.

The NOAA Climate Data Online API returns station observations. This script
reproduces the course-project method by taking an unweighted mean of available
station values for each state, year, and variable.
"""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

import pandas as pd
import requests

API_BASE = "https://www.ncei.noaa.gov/cdo-web/api/v2"
DATASET_ID = "GSOY"
VARIABLES = ("TAVG", "PRCP")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-year", type=int, default=2000)
    parser.add_argument("--end-year", type=int, default=2024)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/interim/noaa_state_climate_2000_2024.csv"),
    )
    parser.add_argument(
        "--request-delay",
        type=float,
        default=0.25,
        help="Seconds between API requests (default: 0.25).",
    )
    return parser.parse_args()


def request_json(
    session: requests.Session,
    endpoint: str,
    params: dict[str, object],
    retries: int = 4,
) -> dict:
    """Request one API page with bounded exponential backoff."""

    for attempt in range(retries):
        try:
            response = session.get(
                f"{API_BASE}/{endpoint}", params=params, timeout=45
            )
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError):
            if attempt == retries - 1:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("NOAA request failed unexpectedly")


def fetch_all(
    session: requests.Session,
    endpoint: str,
    params: dict[str, object],
    request_delay: float,
) -> list[dict]:
    """Fetch all pages for a CDO collection endpoint."""

    results: list[dict] = []
    offset = 1
    limit = 1000

    while True:
        page_params = {**params, "limit": limit, "offset": offset}
        payload = request_json(session, endpoint, page_params)
        page = payload.get("results", [])
        results.extend(page)

        total = (
            payload.get("metadata", {})
            .get("resultset", {})
            .get("count", len(results))
        )
        if not page or len(results) >= total or len(page) < limit:
            break

        offset += limit
        time.sleep(request_delay)

    return results


def year_chunks(start_year: int, end_year: int, size: int = 5):
    year = start_year
    while year <= end_year:
        chunk_end = min(year + size - 1, end_year)
        yield year, chunk_end
        year = chunk_end + 1


def main() -> None:
    args = parse_args()
    if args.start_year > args.end_year:
        raise SystemExit("--start-year must be less than or equal to --end-year")

    token = os.environ.get("NOAA_CDO_TOKEN")
    if not token:
        raise SystemExit(
            "NOAA_CDO_TOKEN is not set. Copy .env.example and export your token."
        )

    session = requests.Session()
    session.headers.update({"token": token, "User-Agent": "climate-corn-dashboard"})

    states = fetch_all(
        session,
        "locations",
        {"datasetid": DATASET_ID, "locationcategoryid": "ST"},
        args.request_delay,
    )
    if not states:
        raise SystemExit("NOAA returned no state locations for the GSOY dataset")

    observations: list[dict[str, object]] = []
    for state in states:
        state_id = state["id"]
        state_name = str(state["name"]).upper().strip()

        for variable in VARIABLES:
            for chunk_start, chunk_end in year_chunks(
                args.start_year, args.end_year
            ):
                rows = fetch_all(
                    session,
                    "data",
                    {
                        "datasetid": DATASET_ID,
                        "locationid": state_id,
                        "datatypeid": variable,
                        "startdate": f"{chunk_start}-01-01",
                        "enddate": f"{chunk_end}-12-31",
                        "units": "standard",
                    },
                    args.request_delay,
                )
                observations.extend(
                    {
                        "State": state_name,
                        "Year": int(row["date"][:4]),
                        "Datatype": variable,
                        "Value": row["value"],
                    }
                    for row in rows
                    if row.get("value") is not None and row.get("date")
                )
                time.sleep(args.request_delay)

    if not observations:
        raise SystemExit("NOAA returned no climate observations")

    frame = pd.DataFrame(observations)
    aggregated = (
        frame.groupby(["State", "Year", "Datatype"], as_index=False)["Value"]
        .mean()
        .pivot(index=["State", "Year"], columns="Datatype", values="Value")
        .reset_index()
        .rename_axis(columns=None)
        .sort_values(["State", "Year"])
    )

    missing_variables = set(VARIABLES) - set(aggregated.columns)
    if missing_variables:
        raise SystemExit(f"Missing NOAA variables: {sorted(missing_variables)}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    aggregated[["State", "Year", "PRCP", "TAVG"]].to_csv(
        args.output, index=False
    )
    print(
        f"Saved {len(aggregated):,} state-year rows across "
        f"{aggregated['State'].nunique()} locations to {args.output}"
    )


if __name__ == "__main__":
    main()
