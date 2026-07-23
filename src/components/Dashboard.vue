<script setup>
import { ref, onMounted, watch, computed, nextTick } from "vue";
import * as d3 from "d3";
import UsChoroplethMap from "./UsChoroplethMap.vue";
import TemperatureTrend from "./TemperatureTrend.vue";
import YieldTrend from "./YieldTrend.vue";
import ThemeRiver from "./ThemeRiver.vue";
import StateMetricTrend from "./StateMetricTrend.vue";
import ScatterPlots from "./ScatterPlots.vue";
import ParallelCoordinates from "./ParallelCoordinates.vue";
import RankingChart from "./RankingChart.vue";
import StatisticalInsights from "./StatisticalInsights.vue";
import PrecipitationTrend from "./PrecipitationTrend.vue";
import { filterRecords, normalizeYearRange } from "../utils/data";

const emit = defineEmits(["goToLanding"]);

const allData = ref([]);
const states = ref([]);
const selectedState = ref("ALL");
const tempMetric = ref("F");
const brushedIds = ref([]);
const hoveredState = ref(null);
const hoveredNationalYear = ref(null);
const nationalData = computed(() => yearFilteredAllData.value);
const scatterResetKey = ref(0);
const isLoading = ref(true);
const loadError = ref("");

const minYear = ref(null);
const maxYear = ref(null);
const yearStart = ref(null);
const yearEnd = ref(null);

const displayYearRange = computed(() => {
  if (yearStart.value == null || yearEnd.value == null) return "";
  return `${yearStart.value}–${yearEnd.value}`;
});

const displayYearCount = computed(() => {
  if (yearStart.value == null || yearEnd.value == null) return 0;
  return yearEnd.value - yearStart.value + 1;
});

const yearOptions = computed(() => {
  if (!allData.value.length) return [];
  const years = Array.from(new Set(allData.value.map((d) => d.Year)));
  years.sort((a, b) => a - b);
  return years;
});

const yearFilteredAllData = computed(() => {
  return filterRecords(allData.value, {
    startYear: yearStart.value,
    endYear: yearEnd.value,
  });
});

const filteredData = computed(() => {
  return filterRecords(yearFilteredAllData.value, { state: selectedState.value });
});

function handleBrushSelection(ids) {
  brushedIds.value = ids;
}

function handleSelectState(state) {
  selectedState.value = state;
  brushedIds.value = [];
}

watch([yearStart, yearEnd], ([start, end]) => {
  if (
    start == null ||
    end == null ||
    minYear.value == null ||
    maxYear.value == null
  )
    return;

  const [normalizedStart, normalizedEnd] = normalizeYearRange(
    start,
    end,
    minYear.value,
    maxYear.value
  );
  if (normalizedStart !== start) yearStart.value = normalizedStart;
  if (normalizedEnd !== end) yearEnd.value = normalizedEnd;
});

watch(selectedState, (newVal) => {
  brushedIds.value = [];
  d3.selectAll(".tooltip").remove();
  d3.selectAll(".scatter-tooltip").remove();
  d3.selectAll(".chart-tooltip").remove();

  if (newVal !== "ALL") {
    nextTick(() => {
      const element = document.getElementById("state-detail-section");
      if (element) {
        element.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  }
});

function handleHoverState(state) {
  hoveredState.value = state;
}

function resetAll() {
  selectedState.value = "ALL";
  brushedIds.value = [];
  hoveredState.value = null;
  tempMetric.value = "F";
  hoveredNationalYear.value = null;
  stateDetailHoveredYear.value = null;
  scatterResetKey.value++;

  if (minYear.value != null && maxYear.value != null) {
    yearStart.value = minYear.value;
    yearEnd.value = maxYear.value;
  }

  d3.selectAll(".tooltip").remove();
  d3.selectAll(".scatter-tooltip").remove();
  d3.selectAll(".scatter-tooltip-shared").remove();
  d3.selectAll(".chart-tooltip").remove();
  d3.selectAll(".map-tooltip").remove();

  scrollToTop();
}

function goBack() {
  emit("goToLanding");
}

function reloadPage() {
  window.location.reload();
}

onMounted(async () => {
  try {
    const data = await d3.csv(
      "/data/final_climate_yield_dataset.csv",
      d3.autoType
    );
    if (!data.length) throw new Error("The dataset is empty");

    data.forEach((d, i) => {
      d._id = i;
    });
    allData.value = data;
    states.value = Array.from(new Set(data.map((d) => d.State))).sort();

    const years = data.map((d) => d.Year);
    const min = d3.min(years);
    const max = d3.max(years);
    minYear.value = min;
    maxYear.value = max;
    yearStart.value = min;
    yearEnd.value = max;
  } catch {
    loadError.value =
      "The dashboard data could not be loaded. Please refresh the page or try again later.";
  } finally {
    isLoading.value = false;
  }
});

function scrollToTop() {
  const targets = [
    window,
    document.scrollingElement,
    document.documentElement,
    document.body,
    document.getElementById("app"),
    document.querySelector(".dashboard-wrapper"),
    document.querySelector(".dashboard-container"),
  ].filter(Boolean);

  targets.forEach((el) => {
    try {
      if (el === window) {
        window.scrollTo({ top: 0, behavior: "smooth" });
      } else if ("scrollTo" in el) {
        el.scrollTo({ top: 0, behavior: "smooth" });
      } else {
        el.scrollTop = 0;
      }
    } catch {
      if (el === window) {
        window.scrollTo(0, 0);
      } else {
        el.scrollTop = 0;
      }
    }
  });
}

const stateDetailHoveredYear = ref(null);
</script>

<template>
  <div class="dashboard-wrapper">
    <!-- Sticky Navigation Bar -->
    <nav class="sticky-navbar" aria-label="Dashboard controls">
      <div class="navbar-content">
        <div class="navbar-left">
          <button @click="goBack" class="back-button">
            <span class="back-icon">←</span>
            Back to Home
          </button>
          <h1 class="navbar-title">Climate + Corn Explorer</h1>
        </div>

        <div class="navbar-controls">
          <div class="control-group">
            <label for="state-selector">State</label>
            <select id="state-selector" v-model="selectedState" class="state-selector">
              <option value="ALL">All States</option>
              <option v-for="state in states" :key="state" :value="state">
                {{ state }}
              </option>
            </select>
          </div>

          <div class="control-group year-group">
            <div class="year-label-row">
              <span>Year Range</span>
              <span class="year-mini-hint">(min 3 years)</span>
            </div>
            <div class="year-range">
              <select
                v-model.number="yearStart"
                class="year-select"
                aria-label="Start year"
              >
                <option v-for="y in yearOptions" :key="'start-' + y" :value="y">
                  {{ y }}
                </option>
              </select>
              <span class="year-separator">–</span>
              <select
                v-model.number="yearEnd"
                class="year-select"
                aria-label="End year"
              >
                <option v-for="y in yearOptions" :key="'end-' + y" :value="y">
                  {{ y }}
                </option>
              </select>
            </div>
          </div>

          <div class="control-group">
            <span class="control-label">Temperature</span>
            <div class="temp-toggle" role="group" aria-label="Temperature unit">
              <button
                @click="tempMetric = 'F'"
                :class="['toggle-btn', { active: tempMetric === 'F' }]"
                :aria-pressed="tempMetric === 'F'"
              >
                °F
              </button>
              <button
                @click="tempMetric = 'C'"
                :class="['toggle-btn', { active: tempMetric === 'C' }]"
                :aria-pressed="tempMetric === 'C'"
              >
                °C
              </button>
            </div>
          </div>

          <button @click="resetAll" class="reset-button">Reset All</button>
        </div>
      </div>
    </nav>

    <div v-if="isLoading" class="dashboard-status" role="status">
      <strong>Preparing the dashboard…</strong>
      <span>Loading 25 years of state-level climate and yield observations.</span>
    </div>

    <div v-else-if="loadError" class="dashboard-status error-status" role="alert">
      <strong>Dashboard unavailable</strong>
      <span>{{ loadError }}</span>
      <button class="retry-button" @click="reloadPage">Reload page</button>
    </div>

    <!-- Main Dashboard Content -->
    <main v-else class="dashboard-container">
      <section class="analysis-intro" aria-labelledby="analysis-title">
        <div>
          <p class="analysis-eyebrow">Descriptive exploration</p>
          <h2 id="analysis-title">Compare place, time, and climate relationships.</h2>
        </div>
        <div class="analysis-copy">
          <p>
            The dashboard combines NOAA station-based annual climate observations
            with USDA state corn-yield estimates. Use the controls to focus every
            coordinated view on the same years and state.
          </p>
          <p class="analysis-caution">
            Correlations are descriptive. They do not isolate causal climate effects
            or control for technology, irrigation, soil, or farm practices.
          </p>
        </div>
      </section>

      <!-- Map Section - LARGER -->
      <section class="section">
        <div class="section-header">
          <p class="section-kicker">01 · Landscape</p>
          <div>
            <h2>Geographic Overview</h2>
            <p class="section-subtitle">
              Click a state to explore detailed trends
            </p>
          </div>
        </div>
        <div
          class="map-container-large"
          role="group"
          :aria-label="`State map for ${displayYearRange}`"
        >
          <UsChoroplethMap
            :data="yearFilteredAllData"
            :selectedState="selectedState"
            :hoveredState="hoveredState"
            :tempMetric="tempMetric"
            @select-state="handleSelectState"
            @hover-state="handleHoverState"
          />
        </div>
      </section>

      <!-- National Trends -->
      <section class="section">
        <div class="section-header">
          <p class="section-kicker">02 · Time</p>
          <div>
            <h2>State-Average Trends ({{ displayYearRange }})</h2>
            <p class="section-subtitle">
              Annual averages across 41 reporting states · {{ displayYearCount }} years selected
            </p>
          </div>
        </div>

        <!-- Row 1: Yield (full width) -->
        <div class="row">
          <div class="col-md-12">
            <div class="chart-card">
              <h3>National Yield Trend</h3>
              <YieldTrend
                :data="nationalData"
                :tempMetric="tempMetric"
                :hoveredYear="hoveredNationalYear"
                @hover-year="(year) => (hoveredNationalYear = year)"
              />
            </div>
          </div>
        </div>

        <!-- Row 2: Temp + Precip side-by-side -->
        <div class="row" style="margin-top: 1.5rem">
          <div class="col-md-6">
            <div class="chart-card">
              <h3>Average Temperature</h3>
              <TemperatureTrend
                :data="nationalData"
                :tempMetric="tempMetric"
                :hoveredYear="hoveredNationalYear"
                @hover-year="(year) => (hoveredNationalYear = year)"
              />
            </div>
          </div>
          <div class="col-md-6">
            <div class="chart-card">
              <h3>Total Precipitation</h3>
              <PrecipitationTrend
                :data="nationalData"
                :tempMetric="tempMetric"
                :hoveredYear="hoveredNationalYear"
                @hover-year="(year) => (hoveredNationalYear = year)"
              />
            </div>
          </div>
        </div>
      </section>

      <!-- Regional Patterns -->
      <section class="section">
        <div class="section-header">
          <p class="section-kicker">03 · Regions</p>
          <div>
            <h2>Regional Patterns</h2>
            <p class="section-subtitle">Compare descriptive yield patterns across U.S. regions</p>
          </div>
        </div>
        <div class="chart-card">
          <h3>Regional Yield Evolution</h3>
          <ThemeRiver :data="yearFilteredAllData" />
        </div>
      </section>

      <!-- Correlation Analysis -->
      <section class="section">
        <div class="section-header">
          <p class="section-kicker">04 · Relationships</p>
          <div>
            <h2>Correlation Analysis</h2>
            <p class="section-subtitle">
              Pooled state-year relationships; correlation does not imply causation
            </p>
          </div>
        </div>

        <!-- Scatter Plots with Brush -->
        <div class="scatter-container">
          <ScatterPlots
            :data="yearFilteredAllData"
            :tempMetric="tempMetric"
            :selectedState="selectedState"
            :resetKey="scatterResetKey"
            @select-state="handleSelectState"
            @brush-selection="handleBrushSelection"
          />
        </div>

        <!-- Parallel Coordinates below Scatter -->
        <div class="chart-card" style="margin-top: 2rem">
          <h3>Advanced Multivariable View</h3>
          <ParallelCoordinates
            :data="yearFilteredAllData"
            :tempMetric="tempMetric"
            :selectedState="selectedState"
            :brushedIds="brushedIds"
          />
        </div>
      </section>

      <!-- Rankings -->
      <section class="section">
        <div class="section-header">
          <p class="section-kicker">05 · Comparison</p>
          <div>
            <h2>State Rankings</h2>
            <p class="section-subtitle">Top and bottom performers</p>
          </div>
        </div>
        <div class="chart-card">
          <RankingChart
            :data="yearFilteredAllData"
            :selectedState="selectedState"
            :tempMetric="tempMetric"
            @select-state="handleSelectState"
          />
        </div>
      </section>

      <!-- Statistical summary -->
      <section class="section">
        <div class="section-header">
          <p class="section-kicker">06 · Summary</p>
          <div>
            <h2>Statistical Summary</h2>
            <p class="section-subtitle">
              Descriptive statistics for {{ displayYearRange }} across all reporting states
            </p>
          </div>
        </div>
        <div class="chart-card">
          <StatisticalInsights :data="yearFilteredAllData" :tempMetric="tempMetric" />
        </div>
      </section>

      <!-- State Detail Section - ONLY shows when state selected -->
      <section
        v-if="selectedState !== 'ALL'"
        id="state-detail-section"
        class="state-detail-section"
      >
        <div class="section-header">
          <p class="section-kicker">Selected state</p>
          <div>
            <h2>{{ selectedState }} Deep Dive</h2>
            <p class="section-subtitle">Detailed trends and statistics</p>
          </div>
        </div>

        <!-- Row 1: Yield (full width) -->
        <div class="row">
          <div class="col-md-12">
            <div class="chart-card">
              <h3>{{ selectedState }} Yield Trend</h3>
              <StateMetricTrend
                :data="filteredData"
                metric="yield"
                :tempMetric="tempMetric"
                :hoveredYear="stateDetailHoveredYear"
                @hover-year="stateDetailHoveredYear = $event"
              />
            </div>
          </div>
        </div>

        <!-- Row 2: Temp + Precip side-by-side -->
        <div class="row" style="margin-top: 1.5rem">
          <div class="col-md-6">
            <div class="chart-card">
              <h3>{{ selectedState }} Temperature Trend</h3>
              <StateMetricTrend
                :data="filteredData"
                metric="temperature"
                :tempMetric="tempMetric"
                :hoveredYear="stateDetailHoveredYear"
                @hover-year="stateDetailHoveredYear = $event"
              />
            </div>
          </div>
          <div class="col-md-6">
            <div class="chart-card">
              <h3>{{ selectedState }} Precipitation Trend</h3>
              <StateMetricTrend
                :data="filteredData"
                metric="precipitation"
                :tempMetric="tempMetric"
                :hoveredYear="stateDetailHoveredYear"
                @hover-year="stateDetailHoveredYear = $event"
              />
            </div>
          </div>
        </div>

        <div class="chart-card" style="margin-top: 2rem">
          <h3>Statistical Insights</h3>
          <StatisticalInsights :data="filteredData" :tempMetric="tempMetric" />
        </div>
      </section>

      <!-- Footer -->
      <footer class="dashboard-footer">
        <div class="footer-content">
          <div class="footer-section">
            <h4>Data Sources</h4>
            <p>
              <a href="https://www.ncei.noaa.gov/cdo-web/webservices/v2" target="_blank" rel="noreferrer">
                NOAA GSOY climate data
              </a>
            </p>
            <p>
              <a href="https://www.nass.usda.gov/Quick_Stats/" target="_blank" rel="noreferrer">
                USDA NASS Quick Stats
              </a>
            </p>
          </div>
          <div class="footer-section">
            <h4>Coverage</h4>
            <p>41 corn-reporting states</p>
            <p>1,025 observations · 2000–2024</p>
          </div>
          <div class="footer-section">
            <h4>Project Info</h4>
            <p>Created by Manikanta Macha and Yashwanth Kumar Mogili</p>
            <p>Interactive Data Visualization · University of Iowa</p>
          </div>
        </div>
      </footer>
    </main>
  </div>
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.dashboard-wrapper {
  --ink: #18332b;
  --muted: #5f6f68;
  --paper: #f5f2e9;
  --paper-deep: #e9e3d3;
  --card: #fffdf7;
  --corn: #e3aa35;
  --leaf: #2f6b4f;
  --line: #c9c4b6;
  min-height: 100vh;
  background: var(--paper);
  color: var(--ink);
}

/* Sticky Navbar */
.sticky-navbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: rgba(24, 51, 43, 0.98);
  border-bottom: 3px solid var(--corn);
  box-shadow: 0 8px 24px rgba(24, 51, 43, 0.16);
  backdrop-filter: blur(14px);
}

.navbar-content {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0.85rem 2rem;
  display: grid;
  grid-template-columns: minmax(250px, 0.72fr) minmax(0, 1.65fr);
  align-items: center;
  gap: 2.5rem;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 0.8rem;
  background: transparent;
  border: 1px solid rgba(245, 242, 233, 0.35);
  border-radius: 3px;
  color: var(--paper);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-button:hover {
  background: rgba(245, 242, 233, 0.1);
  border-color: var(--corn);
  color: #f0c661;
}

.year-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.year-label-row {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--paper-deep);
}

.year-mini-hint {
  font-size: 0.75rem;
  font-weight: 500;
  color: #b8c7c1;
}

.year-range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.year-select {
  min-width: 90px;
  padding: 0.45rem 0.75rem;
  background: var(--paper);
  color: var(--ink);
  border: 1px solid transparent;
  border-radius: 3px;
  font-size: 0.9rem;
  cursor: pointer;
}

.year-select:hover {
  border-color: var(--corn);
}

.year-separator {
  color: var(--paper-deep);
  font-weight: 600;
}

.back-icon {
  font-size: 1.2rem;
}

.navbar-title {
  color: var(--paper);
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.45rem;
  font-weight: 500;
  line-height: 1.05;
  margin: 0;
}

/* .live-badge {
  padding: 0.4rem 0.8rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
  border-radius: 4px;
  letter-spacing: 0.5px;
} */

.navbar-controls {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 1rem;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.control-group label,
.control-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--paper-deep);
}

.state-selector {
  min-width: 178px;
  padding: 0.58rem 0.8rem;
  background: var(--paper);
  color: var(--ink);
  border: 1px solid transparent;
  border-radius: 3px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.state-selector:hover {
  border-color: var(--corn);
}

.state-selector:focus {
  outline: none;
  border-color: var(--corn);
  box-shadow: 0 0 0 3px rgba(227, 170, 53, 0.22);
}

.temp-toggle {
  display: flex;
  background: var(--paper-deep);
  border-radius: 3px;
  overflow: hidden;
  border: 1px solid transparent;
}

.toggle-btn {
  padding: 0.6rem 1rem;
  background: transparent;
  color: var(--ink);
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.toggle-btn.active {
  background: var(--corn);
  color: var(--ink);
}

.toggle-btn:hover:not(.active) {
  background: #d9d2bf;
}

.reset-button {
  padding: 0.6rem 1.2rem;
  background: transparent;
  color: #f0c661;
  border: 1px solid rgba(227, 170, 53, 0.7);
  border-radius: 3px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.reset-button:hover {
  background: var(--corn);
  color: var(--ink);
  box-shadow: none;
}

/* Dashboard Container */
.dashboard-container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 2.5rem 2rem 0;
}

.dashboard-status {
  min-height: 70vh;
  display: grid;
  place-content: center;
  gap: 0.5rem;
  padding: 2rem;
  text-align: center;
  color: var(--muted);
}

.dashboard-status strong {
  color: var(--ink);
  font-size: 1.4rem;
}

.error-status {
  color: #991b1b;
}

.retry-button {
  justify-self: center;
  margin-top: 1rem;
  padding: 0.65rem 1rem;
  background: var(--ink);
  color: white;
  border-radius: 3px;
}

.analysis-intro {
  display: grid;
  grid-template-columns: minmax(0, 0.85fr) minmax(0, 1.15fr);
  gap: 4rem;
  padding: clamp(2rem, 5vw, 4rem);
  margin-bottom: 5rem;
  background: var(--ink);
  color: var(--paper);
  border-top: 5px solid var(--corn);
}

.analysis-intro h2 {
  margin: 0;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(2rem, 4vw, 3.25rem);
  font-weight: 500;
  line-height: 1.05;
}

.analysis-eyebrow,
.section-kicker {
  margin: 0 0 0.75rem;
  color: #e9c779;
  font-size: 0.75rem;
  font-weight: 750;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.analysis-copy {
  color: #d7e0dc;
  line-height: 1.65;
}

.analysis-caution {
  padding-top: 1rem;
  margin-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  color: #bac8c2;
  font-size: 0.9rem;
}

.section-kicker {
  color: var(--leaf);
  padding-top: 0.4rem;
}

/* Sections */
.section {
  margin-bottom: 5.5rem;
  scroll-margin-top: 9rem;
}

.section-header {
  display: grid;
  grid-template-columns: minmax(150px, 0.32fr) minmax(0, 1fr);
  gap: 2rem;
  text-align: left;
  margin-bottom: 2.25rem;
  padding-top: 1.4rem;
  border-top: 1px solid var(--line);
}

.section-header h2 {
  color: var(--ink);
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 500;
  line-height: 1.05;
  margin-bottom: 0.5rem;
}

.section-subtitle {
  font-size: 1rem;
  color: var(--muted);
  line-height: 1.55;
}

/* Grid */
.row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 1.5rem;
}

/* Cards */
.chart-card {
  background: var(--card);
  border-radius: 4px;
  padding: 1.5rem;
  box-shadow: 0 12px 30px rgba(24, 51, 43, 0.06);
  border: 1px solid var(--line);
  border-top: 3px solid var(--leaf);
}

.chart-card:hover {
  box-shadow: 0 16px 36px rgba(24, 51, 43, 0.09);
}

.chart-card h3 {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.35rem;
  font-weight: 500;
  margin-bottom: 1rem;
  color: var(--ink);
}

/* Map Container - LARGER */
.map-container-large {
  background: var(--card);
  border-radius: 4px;
  padding: 1.5rem;
  box-shadow: 0 12px 30px rgba(24, 51, 43, 0.06);
  border: 1px solid var(--line);
  border-top: 3px solid var(--corn);
  min-height: 520px;
  overflow: visible;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Scatter Container */
.scatter-container {
  background: var(--card);
  border-radius: 4px;
  padding: 2rem;
  box-shadow: 0 12px 30px rgba(24, 51, 43, 0.06);
  border: 1px solid var(--line);
  border-top: 3px solid var(--leaf);
}

/* State Detail Section */
.state-detail-section {
  background: var(--paper-deep);
  border-radius: 4px;
  padding: 2rem;
  margin-bottom: 4rem;
  border: 1px solid var(--line);
  border-top: 5px solid var(--corn);
  animation: slideIn 0.5s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Footer */
.dashboard-footer {
  margin-top: 4rem;
  padding: 2.5rem;
  background: var(--ink);
  border-top: 4px solid var(--corn);
  border-radius: 0;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
}

.footer-section h4 {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  color: #e9c779;
}

.footer-section p {
  font-size: 0.9rem;
  color: #c7d2ce;
  margin-bottom: 0.5rem;
}

.footer-section a {
  color: var(--paper);
  text-underline-offset: 0.2rem;
}

button:focus-visible,
select:focus-visible,
a:focus-visible {
  outline: 3px solid var(--corn);
  outline-offset: 3px;
}

/* Responsive */
@media (max-width: 1050px) {
  .sticky-navbar {
    position: relative;
  }

  .navbar-content {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }

  .navbar-controls {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {

  .row {
    grid-template-columns: 1fr;
  }

  .navbar-left,
  .navbar-controls,
  .control-group {
    width: 100%;
  }

  .navbar-left {
    align-items: flex-start;
    flex-direction: column;
  }

  .navbar-controls {
    align-items: stretch;
    flex-direction: column;
  }

  .control-group {
    justify-content: space-between;
  }

  .state-selector {
    min-width: 0;
    width: 58%;
  }

  .analysis-intro {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    padding: 1.5rem;
  }

  .section-header {
    grid-template-columns: 1fr;
    gap: 0.25rem;
  }

  .dashboard-container {
    padding: 1rem;
  }

  .map-container-large,
  .scatter-container,
  .chart-card {
    padding: 1rem;
  }
}

.year-range {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.year-hint {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: var(--muted);
}

.year-select {
  padding: 0.4rem 0.75rem;
  border-radius: 3px;
  border: 1px solid transparent;
  background: var(--paper);
  font-size: 0.9rem;
  min-width: 80px;
  cursor: pointer;
}

.year-select:focus {
  outline: none;
  border-color: var(--corn);
  box-shadow: 0 0 0 3px rgba(227, 170, 53, 0.2);
}

.year-separator {
  font-size: 0.9rem;
  color: var(--paper-deep);
  font-weight: 600;
}
</style>
