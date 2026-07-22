function finitePairs(xValues, yValues) {
  if (!Array.isArray(xValues) || !Array.isArray(yValues)) return [];

  const length = Math.min(xValues.length, yValues.length);
  const pairs = [];
  for (let index = 0; index < length; index += 1) {
    const x = Number(xValues[index]);
    const y = Number(yValues[index]);
    if (Number.isFinite(x) && Number.isFinite(y)) pairs.push([x, y]);
  }
  return pairs;
}

export function mean(values) {
  const finite = values
    .filter((value) => value !== null && value !== undefined && value !== "")
    .map(Number)
    .filter(Number.isFinite);
  if (!finite.length) return 0;
  return finite.reduce((total, value) => total + value, 0) / finite.length;
}

export function pearsonCorrelation(xValues, yValues) {
  const pairs = finitePairs(xValues, yValues);
  const n = pairs.length;
  if (n < 2) return 0;

  const sumX = pairs.reduce((total, [x]) => total + x, 0);
  const sumY = pairs.reduce((total, [, y]) => total + y, 0);
  const sumXY = pairs.reduce((total, [x, y]) => total + x * y, 0);
  const sumX2 = pairs.reduce((total, [x]) => total + x * x, 0);
  const sumY2 = pairs.reduce((total, [, y]) => total + y * y, 0);

  const numerator = n * sumXY - sumX * sumY;
  const denominator = Math.sqrt(
    (n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY)
  );

  return denominator === 0 ? 0 : numerator / denominator;
}

export function linearRegression(xValues, yValues) {
  const pairs = finitePairs(xValues, yValues);
  const n = pairs.length;
  if (n < 2) return { slope: 0, intercept: 0, r: 0 };

  const sumX = pairs.reduce((total, [x]) => total + x, 0);
  const sumY = pairs.reduce((total, [, y]) => total + y, 0);
  const sumXY = pairs.reduce((total, [x, y]) => total + x * y, 0);
  const sumX2 = pairs.reduce((total, [x]) => total + x * x, 0);
  const xDenominator = n * sumX2 - sumX * sumX;

  if (xDenominator === 0) {
    return { slope: 0, intercept: sumY / n, r: 0 };
  }

  const slope = (n * sumXY - sumX * sumY) / xDenominator;
  const intercept = (sumY - slope * sumX) / n;
  const r = pearsonCorrelation(
    pairs.map(([x]) => x),
    pairs.map(([, y]) => y)
  );

  return { slope, intercept, r };
}

export function regressionFromPairs(pairs) {
  return linearRegression(
    pairs.map(([x]) => x),
    pairs.map(([, y]) => y)
  );
}
