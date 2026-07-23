<script setup>
import { computed } from "vue";
import {
  linearRegression,
  mean,
  pearsonCorrelation,
} from "../utils/statistics";

const props = defineProps({
  data: { type: Array, required: true },
  tempMetric: { type: String, default: "C" },
});

const statistics = computed(() => {
  if (!props.data || props.data.length === 0) return null;

  const temps = props.data.map((d) =>
    props.tempMetric === "C" ? d.TAVG_C : d.TAVG
  );
  const precips = props.data.map((d) => d.PRCP);
  const yields = props.data.map((d) => d.Yield_bu_acre);
  const years = props.data.map((d) => d.Year);

  const tempYieldCorr = pearsonCorrelation(temps, yields);
  const precipYieldCorr = pearsonCorrelation(precips, yields);
  const tempPrecipCorr = pearsonCorrelation(temps, precips);

  const tempTrend = linearRegression(years, temps);
  const yieldTrend = linearRegression(years, yields);
  const precipTrend = linearRegression(years, precips);

  const firstYear = Math.min(...years);
  const lastYear = Math.max(...years);
  const yearSpan = lastYear - firstYear;

  const tempChange = tempTrend.slope * yearSpan;
  const yieldChange = yieldTrend.slope * yearSpan;
  const precipChange = precipTrend.slope * yearSpan;

  const avgTemp = mean(temps);
  const avgPrecip = mean(precips);
  const avgYield = mean(yields);

  const minYear = Math.min(...years);
  const maxYear = Math.max(...years);

  return {
    tempYieldCorr,
    precipYieldCorr,
    tempPrecipCorr,
    tempChange,
    yieldChange,
    precipChange,
    avgTemp,
    avgPrecip,
    avgYield,
    yearRange: `${minYear}–${maxYear}`,
    dataPoints: props.data.length,
  };
});

function getCorrelationStrength(r) {
  const absR = Math.abs(r);
  if (absR > 0.7) return "Strong";
  if (absR > 0.4) return "Moderate";
  if (absR > 0.2) return "Weak";
  return "Very weak";
}

function getCorrelationDirection(r) {
  if (Math.abs(r) < 0.01) return "neutral";
  return r > 0 ? "positive" : "negative";
}

function getTrendDirection(slope) {
  if (Math.abs(slope) < 0.01) return "stable";
  return slope > 0 ? "increasing" : "decreasing";
}
</script>

<template>
  <div v-if="statistics" class="insights-container">
    <!-- Summary Cards -->
    <div class="summary-cards">
      <div class="stat-card">
        <div class="stat-icon">Temp</div>
        <div class="stat-value">
          {{ statistics.avgTemp.toFixed(1) }}°{{ tempMetric }}
        </div>
        <div class="stat-label">Average Temperature</div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">Rain</div>
        <div class="stat-value">{{ statistics.avgPrecip.toFixed(1) }}"</div>
        <div class="stat-label">Average Precipitation</div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">Yield</div>
        <div class="stat-value">{{ statistics.avgYield.toFixed(0) }}</div>
        <div class="stat-label">Average Yield (bu/acre)</div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">Span</div>
        <div class="stat-value">{{ statistics.yearRange }}</div>
        <div class="stat-label">{{ statistics.dataPoints }} observations</div>
      </div>
    </div>

    <!-- Correlations -->
    <div class="insights-section">
      <h3 class="section-title">Climate-Yield Correlations</h3>
      <div class="correlations-grid">
        <div
          class="correlation-item"
          :class="getCorrelationDirection(statistics.tempYieldCorr)"
        >
          <div class="corr-header">
            <span class="corr-title">Temperature ↔ Yield</span>
            <span class="corr-value"
              >r = {{ statistics.tempYieldCorr.toFixed(3) }}</span
            >
          </div>
          <div class="corr-bar-container">
            <div
              class="corr-bar"
              :style="{ width: Math.abs(statistics.tempYieldCorr) * 100 + '%' }"
            ></div>
          </div>
          <div class="corr-interpretation">
            {{ getCorrelationStrength(statistics.tempYieldCorr) }}
            {{ getCorrelationDirection(statistics.tempYieldCorr) }} relationship
          </div>
          <div class="corr-insight">
            Temperature and corn yield move
            {{ statistics.tempYieldCorr > 0 ? "together" : "in opposite directions" }}
            in this filtered sample.
          </div>
        </div>

        <div
          class="correlation-item"
          :class="getCorrelationDirection(statistics.precipYieldCorr)"
        >
          <div class="corr-header">
            <span class="corr-title">Precipitation ↔ Yield</span>
            <span class="corr-value"
              >r = {{ statistics.precipYieldCorr.toFixed(3) }}</span
            >
          </div>
          <div class="corr-bar-container">
            <div
              class="corr-bar"
              :style="{
                width: Math.abs(statistics.precipYieldCorr) * 100 + '%',
              }"
            ></div>
          </div>
          <div class="corr-interpretation">
            {{ getCorrelationStrength(statistics.precipYieldCorr) }}
            {{ getCorrelationDirection(statistics.precipYieldCorr) }}
            relationship
          </div>
          <div class="corr-insight">
            Precipitation and corn yield move
            {{ statistics.precipYieldCorr > 0 ? "together" : "in opposite directions" }}
            in this filtered sample.
          </div>
        </div>

        <div
          class="correlation-item"
          :class="getCorrelationDirection(statistics.tempPrecipCorr)"
        >
          <div class="corr-header">
            <span class="corr-title">Temperature ↔ Precipitation</span>
            <span class="corr-value"
              >r = {{ statistics.tempPrecipCorr.toFixed(3) }}</span
            >
          </div>
          <div class="corr-bar-container">
            <div
              class="corr-bar"
              :style="{
                width: Math.abs(statistics.tempPrecipCorr) * 100 + '%',
              }"
            ></div>
          </div>
          <div class="corr-interpretation">
            {{ getCorrelationStrength(statistics.tempPrecipCorr) }}
            {{ getCorrelationDirection(statistics.tempPrecipCorr) }}
            relationship
          </div>
          <div class="corr-insight">
            Temperature and precipitation show
            {{
              getCorrelationStrength(statistics.tempPrecipCorr).toLowerCase()
            }}
            correlation.
          </div>
        </div>
      </div>
    </div>

    <!-- Trends -->
    <div class="insights-section">
      <h3 class="section-title">
        Long-term Trends ({{ statistics.yearRange }})
      </h3>
      <div class="trends-grid">
        <div class="trend-item">
          <div class="trend-icon">Temp</div>
          <div class="trend-content">
            <div class="trend-title">Temperature Trend</div>
            <div
              class="trend-value"
              :class="getTrendDirection(statistics.tempChange)"
            >
              {{ statistics.tempChange > 0 ? "+" : ""
              }}{{ statistics.tempChange.toFixed(2) }}°{{ tempMetric }}
            </div>
            <div class="trend-description">
              {{
                getTrendDirection(statistics.tempChange) === "increasing"
                  ? "Rising"
                  : getTrendDirection(statistics.tempChange) === "decreasing"
                  ? "Falling"
                  : "Stable"
              }}
              over
              {{
                statistics.yearRange.split("–")[1] -
                statistics.yearRange.split("–")[0]
              }}
              years
            </div>
          </div>
        </div>

        <div class="trend-item">
          <div class="trend-icon">Rain</div>
          <div class="trend-content">
            <div class="trend-title">Precipitation Trend</div>
            <div
              class="trend-value"
              :class="getTrendDirection(statistics.precipChange)"
            >
              {{ statistics.precipChange > 0 ? "+" : ""
              }}{{ statistics.precipChange.toFixed(2) }} inches
            </div>
            <div class="trend-description">
              {{
                getTrendDirection(statistics.precipChange) === "increasing"
                  ? "Rising"
                  : getTrendDirection(statistics.precipChange) === "decreasing"
                  ? "Falling"
                  : "Stable"
              }}
              over
              {{
                statistics.yearRange.split("–")[1] -
                statistics.yearRange.split("–")[0]
              }}
              years
            </div>
          </div>
        </div>

        <div class="trend-item">
          <div class="trend-icon">Yield</div>
          <div class="trend-content">
            <div class="trend-title">Yield Trend</div>
            <div
              class="trend-value"
              :class="getTrendDirection(statistics.yieldChange)"
            >
              {{ statistics.yieldChange > 0 ? "+" : ""
              }}{{ statistics.yieldChange.toFixed(0) }} bu/acre
            </div>
            <div class="trend-description">
              {{
                getTrendDirection(statistics.yieldChange) === "increasing"
                  ? "Rising"
                  : getTrendDirection(statistics.yieldChange) === "decreasing"
                  ? "Falling"
                  : "Stable"
              }}
              over
              {{
                statistics.yearRange.split("–")[1] -
                statistics.yearRange.split("–")[0]
              }}
              years
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Key Insights -->
    <div class="insights-section">
      <h3 class="section-title">Key Findings</h3>
      <div class="findings-list">
        <div
          class="finding-item"
          v-if="Math.abs(statistics.tempYieldCorr) > 0.2"
        >
          <span class="finding-bullet">•</span>
          <span class="finding-text">
            <strong
              >{{ getCorrelationStrength(statistics.tempYieldCorr) }}
              {{ getCorrelationDirection(statistics.tempYieldCorr) }}
              correlation</strong
            >
            between temperature and yield (r={{
              statistics.tempYieldCorr.toFixed(2)
            }}) in the selected observations. This is an association, not a
            causal estimate.
          </span>
        </div>

        <div
          class="finding-item"
          v-if="Math.abs(statistics.precipYieldCorr) > 0.2"
        >
          <span class="finding-bullet">•</span>
          <span class="finding-text">
            <strong
              >{{ getCorrelationStrength(statistics.precipYieldCorr) }}
              {{ getCorrelationDirection(statistics.precipYieldCorr) }}
              correlation</strong
            >
            between precipitation and yield (r={{
              statistics.precipYieldCorr.toFixed(2)
            }}) in the selected observations. Other agricultural and regional
            factors are not controlled here.
          </span>
        </div>

        <div class="finding-item" v-if="Math.abs(statistics.tempChange) > 0.5">
          <span class="finding-bullet">•</span>
          <span class="finding-text">
            Temperature has
            <strong
              >{{ statistics.tempChange > 0 ? "increased" : "decreased" }} by
              {{ Math.abs(statistics.tempChange).toFixed(1) }}°{{
                tempMetric
              }}</strong
            >
            across the fitted study-period trend. This describes the selected
            observations and is not a significance test.
          </span>
        </div>

        <div class="finding-item" v-if="Math.abs(statistics.yieldChange) > 10">
          <span class="finding-bullet">•</span>
          <span class="finding-text">
            Corn yields have
            <strong
              >{{ statistics.yieldChange > 0 ? "improved" : "declined" }} by
              {{ Math.abs(statistics.yieldChange).toFixed(0) }} bu/acre</strong
            > across the fitted trend. The dashboard does not identify the
            causes of that change.
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.insights-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: #f5f2e9;
  border-radius: 3px;
  padding: 1.25rem;
  text-align: left;
  border: 1px solid #c9c4b6;
  border-top: 3px solid #e3aa35;
}

.stat-card:hover {
  background: #efe9da;
}

.stat-icon {
  margin-bottom: 1.25rem;
  color: #2f6b4f;
  font-size: 0.7rem;
  font-weight: 750;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #18332b;
  margin: 0.25rem 0;
}

.stat-label {
  font-size: 0.85rem;
  color: #5f6f68;
  font-weight: 500;
}

.insights-section {
  background: #f5f2e9;
  border-radius: 3px;
  padding: 1.25rem;
  border: 1px solid #c9c4b6;
}

.section-title {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.35rem;
  font-weight: 500;
  color: #18332b;
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.correlations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.correlation-item {
  padding: 1rem;
  background: #fffdf7;
  border-radius: 2px;
  border: 1px solid #d5cfbf;
}

.correlation-item.positive {
  background: #edf2eb;
  border-color: #9db2a2;
}

.correlation-item.negative {
  background: #f4e7df;
  border-color: #c99e85;
}

.corr-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.corr-title {
  font-weight: 600;
  color: #18332b;
  font-size: 0.95rem;
}

.corr-value {
  font-family: "Courier New", monospace;
  font-weight: 700;
  color: #2f6b4f;
  font-size: 0.9rem;
}

.corr-bar-container {
  height: 8px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 0;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.corr-bar {
  height: 100%;
  background: #e3aa35;
  transition: width 0.3s ease;
}

.corr-interpretation {
  font-size: 0.85rem;
  font-weight: 600;
  color: #40594f;
  margin-bottom: 0.25rem;
}

.corr-insight {
  font-size: 0.8rem;
  color: #5f6f68;
  font-style: italic;
}

.trends-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.trend-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: #fffdf7;
  border-radius: 2px;
  border: 1px solid #d5cfbf;
}

.trend-icon {
  min-width: 3rem;
  padding-top: 0.2rem;
  color: #2f6b4f;
  font-size: 0.7rem;
  font-weight: 750;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.trend-content {
  flex: 1;
}

.trend-title {
  font-weight: 600;
  color: #18332b;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.trend-value {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0.25rem 0;
}

.trend-value.increasing {
  color: #b7653b;
}

.trend-value.decreasing {
  color: #4f7475;
}

.trend-value.stable {
  color: #5f6f68;
}

.trend-description {
  font-size: 0.8rem;
  color: #5f6f68;
}

.findings-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.finding-item {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  padding: 0.75rem;
  background: #fffdf7;
  border-radius: 2px;
  border-left: 3px solid #e3aa35;
}

.finding-bullet {
  color: #e3aa35;
  font-weight: 700;
  font-size: 1.25rem;
  line-height: 1.4;
}

.finding-text {
  flex: 1;
  font-size: 0.9rem;
  color: #18332b;
  line-height: 1.5;
}

.finding-text strong {
  color: #2f6b4f;
}

@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .correlations-grid,
  .trends-grid {
    grid-template-columns: 1fr;
  }
}
</style>
