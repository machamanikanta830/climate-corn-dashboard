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
          <h2>Geographic Overview</h2>
          <p class="section-subtitle">
            Click a state to explore detailed trends
          </p>
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
          <h2>State-Average Trends ({{ displayYearRange }})</h2>
          <p class="section-subtitle">
            Annual averages across 41 reporting states · {{ displayYearCount }} years selected
          </p>
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
          <p class="section-kicker">Advanced exploration</p>
          <h2>Regional Patterns</h2>
          <p class="section-subtitle">Compare descriptive yield patterns across U.S. regions</p>
        </div>
        <div class="chart-card">
          <h3>Regional Yield Evolution</h3>
          <ThemeRiver :data="yearFilteredAllData" />
        </div>
      </section>

      <!-- Correlation Analysis -->
      <section class="section">
        <div class="section-header">
          <h2>Correlation Analysis</h2>
          <p class="section-subtitle">
            Pooled state-year relationships; correlation does not imply causation
          </p>
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
          <h2>State Rankings</h2>
          <p class="section-subtitle">Top and bottom performers</p>
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
          <h2>Statistical Summary</h2>
          <p class="section-subtitle">
            Descriptive statistics for {{ displayYearRange }} across all reporting states
          </p>
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
          <h2>{{ selectedState }} Deep Dive</h2>
          <p class="section-subtitle">Detailed trends and statistics</p>
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
  min-height: 100vh;
  background: #f4f2ec;
  color: #1e293b;
}

/* Sticky Navbar */
.sticky-navbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
  border-bottom: 2px solid #2f6b4f;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.navbar-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  background: transparent;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  color: #475569;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-button:hover {
  background: #f1f5f9;
  border-color: #3b82f6;
  color: #3b82f6;
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
  color: #475569;
}

.year-mini-hint {
  font-size: 0.75rem;
  font-weight: 500;
  color: #94a3b8;
}

.year-range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.year-select {
  min-width: 90px;
  padding: 0.45rem 0.75rem;
  background: #ffffff;
  color: #1e293b;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
}

.year-select:hover {
  border-color: #3b82f6;
}

.year-separator {
  color: #64748b;
  font-weight: 600;
}

.back-icon {
  font-size: 1.2rem;
}

.navbar-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
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
  gap: 1.5rem;
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
  color: #475569;
}

.state-selector {
  min-width: 200px;
  padding: 0.6rem 1rem;
  background: #ffffff;
  color: #1e293b;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.state-selector:hover {
  border-color: #3b82f6;
}

.state-selector:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.temp-toggle {
  display: flex;
  background: #f1f5f9;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #cbd5e1;
}

.toggle-btn {
  padding: 0.6rem 1rem;
  background: transparent;
  color: #475569;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.toggle-btn.active {
  background: #3b82f6;
  color: white;
}

.toggle-btn:hover:not(.active) {
  background: #e2e8f0;
}

.reset-button {
  padding: 0.6rem 1.2rem;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.reset-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

/* Dashboard Container */
.dashboard-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.dashboard-status {
  min-height: 70vh;
  display: grid;
  place-content: center;
  gap: 0.5rem;
  padding: 2rem;
  text-align: center;
  color: #475569;
}

.dashboard-status strong {
  color: #18332b;
  font-size: 1.4rem;
}

.error-status {
  color: #991b1b;
}

.retry-button {
  justify-self: center;
  margin-top: 1rem;
  padding: 0.65rem 1rem;
  background: #18332b;
  color: white;
  border-radius: 6px;
}

.analysis-intro {
  display: grid;
  grid-template-columns: minmax(0, 0.85fr) minmax(0, 1.15fr);
  gap: 4rem;
  padding: 2.5rem;
  margin-bottom: 4rem;
  background: #18332b;
  color: white;
  border-top: 5px solid #e3aa35;
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
  color: #2f6b4f;
}

/* Sections */
.section {
  margin-bottom: 4rem;
  scroll-margin-top: 9rem;
}

.section-header {
  text-align: center;
  margin-bottom: 2rem;
}

.section-header h2 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.section-subtitle {
  font-size: 1rem;
  color: #64748b;
}

/* Grid */
.row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 2rem;
}

/* Cards */
.chart-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  transition: all 0.3s ease;
}

.chart-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.chart-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #1e293b;
}

/* Map Container - LARGER */
.map-container-large {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  min-height: 450px;
  max-height: 500px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Scatter Container */
.scatter-container {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

/* State Detail Section */
.state-detail-section {
  background: linear-gradient(
    135deg,
    rgba(59, 130, 246, 0.05) 0%,
    rgba(167, 139, 250, 0.05) 100%
  );
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
  border: 2px solid rgba(59, 130, 246, 0.3);
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
  padding: 2rem;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  border-top: 2px solid #3b82f6;
  border-radius: 16px 16px 0 0;
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
  color: #2563eb;
}

.footer-section p {
  font-size: 0.9rem;
  color: #475569;
  margin-bottom: 0.5rem;
}

.footer-section a {
  color: #1d4f3c;
  text-underline-offset: 0.2rem;
}

button:focus-visible,
select:focus-visible,
a:focus-visible {
  outline: 3px solid #e3aa35;
  outline-offset: 3px;
}

/* Responsive */
@media (max-width: 768px) {
  .navbar-content {
    flex-direction: column;
    gap: 1rem;
  }

  .row {
    grid-template-columns: 1fr;
  }

  .navbar-left,
  .navbar-controls,
  .control-group {
    width: 100%;
  }

  .navbar-left {
    justify-content: space-between;
  }

  .navbar-controls {
    justify-content: center;
  }

  .analysis-intro {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    padding: 1.5rem;
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
  color: #64748b;
}

.year-select {
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  font-size: 0.9rem;
  min-width: 80px;
  cursor: pointer;
}

.year-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}

.year-separator {
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 600;
}
</style>
