# Methodology and limitations

## Research question

How are annual temperature and precipitation associated with reported corn
yield across U.S. states between 2000 and 2024?

This is an exploratory visualization project. It describes patterns in the
available data; it does not estimate the causal effect of climate on yield.

## Climate data

The climate source is NOAA/NCEI's Global Summary of the Year (GSOY), accessed
through the Climate Data Online v2 API. `scripts/fetch_noaa.py` requests annual
average temperature (`TAVG`) and annual precipitation (`PRCP`) in standard
units for each state and year. API requests use five-year windows and paginate
through all returned station observations.

For each state-year-variable combination, the pipeline calculates an
unweighted mean across available stations. This reproduces the submitted
course-project method, but it has an important limitation: stations are not
distributed uniformly, and the result is not area-weighted or weighted by corn
acreage.

Official references:

- [NOAA Climate Data Online API v2](https://www.ncei.noaa.gov/cdo-web/webservices/v2)
- [NOAA GSOY documentation](https://www.ncei.noaa.gov/pub/data/cdo/documentation/GSOY_documentation.pdf)

## Corn-yield data

Corn yield comes from a CSV export from USDA NASS Quick Stats with these
filters:

| Field | Selection |
| --- | --- |
| Program | Survey |
| Sector | Crops |
| Group | Field Crops |
| Commodity | Corn |
| Geographic level | State |
| Data item | Corn, grain - yield, measured in bu/acre |
| Years | 2000-2024 |

The cleaning script removes aggregate categories, restricts records to the
`TOTAL` domain when that field is present, converts the reported value to a
number, and requires one record per state and year.

Official references:

- [USDA NASS Quick Stats](https://www.nass.usda.gov/Quick_Stats/)
- [USDA NASS developer resources](https://www.nass.usda.gov/developer/)

## Integration and validation

The sources are inner-joined on uppercase state name and year. Therefore the
final dashboard includes the 41 states with complete USDA corn-yield records,
not all 50 states. The committed dataset contains:

- 1,025 observations
- 41 states
- 25 years, 2000-2024
- no missing values
- no duplicate state-year records

`scripts/validate_dataset.py` checks these invariants, verifies the Fahrenheit
to Celsius conversion, and generates the summary used for public-facing
claims.

## Statistical interpretation

The dashboard displays Pearson correlations and simple linear trend lines.
The headline correlations pool all 1,025 state-year observations. Pooling can
combine two different sources of variation: persistent differences between
states and changes within a state over time. A pooled coefficient should not be
interpreted as the effect of a warmer or wetter year on a particular state.

The analysis does not control for irrigation, soil, planted hybrids, fertilizer,
technology, farm practices, extreme-weather timing, harvested acreage, or
changes in where corn is grown. Annual state averages also conceal growing-
season timing and within-state variation. These factors can confound observed
relationships.

The dashboard therefore uses terms such as *association*, *relationship*, and
*descriptive trend*. It avoids causal claims and does not report statistical
significance tests that are not implemented.
