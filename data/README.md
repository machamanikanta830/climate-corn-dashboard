# Data workflow

The dashboard uses one observation per U.S. state and year. The committed file,
`public/data/final_climate_yield_dataset.csv`, contains 1,025 observations for
41 corn-reporting states from 2000 through 2024.

## Sources

- Climate: NOAA/NCEI Climate Data Online, Global Summary of the Year (GSOY),
  variables `TAVG` and `PRCP`, requested in standard units.
- Corn yield: USDA NASS Quick Stats, Survey program, state geographic level,
  data item `CORN, GRAIN - YIELD, MEASURED IN BU / ACRE`.

The NOAA API requires a personal token. Request one from the
[Climate Data Online token page](https://www.ncei.noaa.gov/cdo-web/token), copy
`.env.example` to a private local environment file, and export
`NOAA_CDO_TOKEN`. Never put the real token in a notebook, report, screenshot,
or Git commit.

The USDA source file is a manual Quick Stats CSV export and is intentionally
not committed. Save it under `data/raw/` using the filters documented in
`docs/METHODOLOGY.md`.

## Rebuild

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python scripts/fetch_noaa.py
python scripts/clean_usda.py --input data/raw/usda_quick_stats_corn_yield.csv
python scripts/build_dataset.py \
  --climate data/interim/noaa_state_climate_2000_2024.csv \
  --yield-data data/interim/usda_corn_yield_2000_2024.csv
python scripts/validate_dataset.py
```

The final validation command must report 1,025 rows, 41 states, complete
25-year coverage, no missing values, and no duplicate state-year records.

## Schema

| Column | Meaning | Unit |
| --- | --- | --- |
| `Year` | Observation year | year |
| `State` | Uppercase U.S. state name | - |
| `TAVG` | Mean of available station-level annual average temperatures | degrees Fahrenheit |
| `TAVG_C` | `TAVG` converted to Celsius | degrees Celsius |
| `PRCP` | Mean of available station-level annual precipitation totals | inches |
| `Yield_bu_acre` | Corn grain yield | bushels per acre |

`TAVG` and `PRCP` are state-level aggregates created from available GSOY
stations. They are not area-weighted climate estimates.
