export function toCelsius(fahrenheit) {
  return ((Number(fahrenheit) - 32) * 5) / 9;
}

export function filterRecords(
  records,
  { startYear = null, endYear = null, state = "ALL" } = {}
) {
  return records.filter((record) => {
    const inYearRange =
      (startYear == null || record.Year >= startYear) &&
      (endYear == null || record.Year <= endYear);
    const inState = state === "ALL" || record.State === state;
    return inYearRange && inState;
  });
}

export function normalizeYearRange(
  startYear,
  endYear,
  minimumYear,
  maximumYear,
  minimumLength = 3
) {
  if ([startYear, endYear, minimumYear, maximumYear].some((value) => value == null)) {
    return [startYear, endYear];
  }

  const minimumGap = minimumLength - 1;
  let start = Math.max(minimumYear, Math.min(startYear, maximumYear));
  let end = Math.max(minimumYear, Math.min(endYear, maximumYear));

  if (start > end) {
    if (start + minimumGap <= maximumYear) {
      end = start + minimumGap;
    } else {
      end = maximumYear;
      start = maximumYear - minimumGap;
    }
  } else if (end - start < minimumGap) {
    if (start + minimumGap <= maximumYear) {
      end = start + minimumGap;
    } else {
      start = maximumYear - minimumGap;
      end = maximumYear;
    }
  }

  return [start, end];
}
