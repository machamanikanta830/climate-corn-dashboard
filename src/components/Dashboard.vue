<script setup>
import { ref, onMounted, watch, computed, nextTick } from "vue";
import * as d3 from "d3";
import UsChoroplethMap from "./UsChoroplethMap.vue";
import TemperatureTrend from "./TemperatureTrend.vue";
import YieldTrend from "./YieldTrend.vue";
import ThemeRiver from "./ThemeRiver.vue";
import StateTemperatureTrend from "./StateTemperatureTrend.vue";
import StateYieldTrend from "./StateYieldTrend.vue";
import ScatterPlots from "./ScatterPlots.vue";
import TreemapVisualization from "./TreemapVisualization.vue";
import ParallelCoordinates from "./ParallelCoordinates.vue";
import RankingChart from "./RankingChart.vue";
import StatisticalInsights from "./StatisticalInsights.vue";
import PrecipitationTrend from "./PrecipitationTrend.vue";
import StatePrecipitationTrend from "./StatePrecipitationTrend.vue";

const emit = defineEmits(["goToLanding"]);

const allData = ref([]);
const states = ref([]);
const selectedState = ref("ALL");
const tempMetric = ref("F");
const brushedIds = ref([]);
const hoveredYear = ref(null);
const hoveredState = ref(null);
const hoveredNationalYear = ref(null);
const nationalData = computed(() => yearFilteredAllData.value);
const scatterResetKey = ref(0);

const minYear = ref(null);
const maxYear = ref(null);
const yearStart = ref(null);
const yearEnd = ref(null);

const yearOptions = computed(() => {
  if (!allData.value.length) return [];
  const years = Array.from(new Set(allData.value.map((d) => d.Year)));
  years.sort((a, b) => a - b);
  return years;
});

const yearFilteredAllData = computed(() => {
  if (
    !allData.value.length ||
    yearStart.value == null ||
    yearEnd.value == null
  ) {
    return allData.value;
  }
  return allData.value.filter(
    (d) => d.Year >= yearStart.value && d.Year <= yearEnd.value
  );
});

const filteredData = computed(() => {
  const base = yearFilteredAllData.value;
  if (selectedState.value === "ALL") return base;
  return base.filter((d) => d.State === selectedState.value);
});

function handleBrushSelection(ids) {
  brushedIds.value = ids;
}

function handleSelectState(state) {
  selectedState.value = state;

  brushedIds.value = [];

  d3.selectAll(".tooltip").remove();
  d3.selectAll(".scatter-tooltip").remove();

  if (state !== "ALL") {
    nextTick(() => {
      setTimeout(() => {
        const element = document.getElementById("state-detail-section");
        if (element) {
          element.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      }, 150);
    });
  }
}

watch([yearStart, yearEnd], ([start, end]) => {
  if (
    start == null ||
    end == null ||
    minYear.value == null ||
    maxYear.value == null
  )
    return;

  if (start > end) {
    const desiredEnd = Math.min(start + 2, maxYear.value);
    if (desiredEnd - start >= 2) {
      yearEnd.value = desiredEnd;
      return;
    } else {
      yearStart.value = Math.max(minYear.value, end - 2);
      return;
    }
  }

  if (end - start < 2) {
    if (start === minYear.value) {
      yearEnd.value = Math.min(start + 2, maxYear.value);
    } else if (end === maxYear.value) {
      yearStart.value = Math.max(minYear.value, end - 2);
    } else {
      yearEnd.value = Math.min(start + 2, maxYear.value);
    }
  }
});

watch(selectedState, (newVal, oldVal) => {
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

function handleHoverYear(year) {
  hoveredYear.value = year;
}

function handleHoverState(state) {
  hoveredState.value = state;
}

function resetAll() {
  selectedState.value = "ALL";
  brushedIds.value = [];
  hoveredYear.value = null;
  hoveredState.value = null;
  tempMetric.value = "F";

  if (typeof hoveredNationalYear !== "undefined") {
    hoveredNationalYear.value = null;
  }
  if (typeof stateDetailHoveredYear !== "undefined") {
    stateDetailHoveredYear.value = null;
  }
  if (typeof scatterResetKey !== "undefined") {
    scatterResetKey.value++;
  }
  if (typeof mapResetKey !== "undefined") {
    mapResetKey.value++;
  }

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

onMounted(async () => {
  const data = await d3.csv(
    "/data/final_climate_yield_dataset.csv",
    d3.autoType
  );
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
    <nav class="sticky-navbar">
      <div class="navbar-content">
        <div class="navbar-left">
          <button @click="goBack" class="back-button">
            <span class="back-icon">←</span>
            Back to Home
          </button>
          <h1 class="navbar-title">Climate Impact Dashboard</h1>
          <!-- <span class="live-badge">LIVE DATA</span> -->
        </div>

        <div class="navbar-controls">
          <div class="control-group">
            <label>State:</label>
            <select v-model="selectedState" class="state-selector">
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
              <select v-model.number="yearStart" class="year-select">
                <option v-for="y in yearOptions" :key="'start-' + y" :value="y">
                  {{ y }}
                </option>
              </select>
              <span class="year-separator">–</span>
              <select v-model.number="yearEnd" class="year-select">
                <option v-for="y in yearOptions" :key="'end-' + y" :value="y">
                  {{ y }}
                </option>
              </select>
            </div>
          </div>

          <div class="control-group">
            <label>Temperature:</label>
            <div class="temp-toggle">
              <button
                @click="tempMetric = 'F'"
                :class="['toggle-btn', { active: tempMetric === 'F' }]"
              >
                °F
              </button>
              <button
                @click="tempMetric = 'C'"
                :class="['toggle-btn', { active: tempMetric === 'C' }]"
              >
                °C
              </button>
            </div>
          </div>

          <button @click="resetAll" class="reset-button">Reset All</button>
        </div>
      </div>
    </nav>

    <!-- Main Dashboard Content -->
    <div class="dashboard-container">
      <!-- Map Section - LARGER -->
      <section class="section">
        <div class="section-header">
          <h2>Geographic Overview</h2>
          <p class="section-subtitle">
            Click a state to explore detailed trends
          </p>
        </div>
        <div class="map-container-large">
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
          <h2>National Trends (2000-2024)</h2>
          <p class="section-subtitle">25-year climate and yield patterns</p>
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
          <h2>Regional Patterns</h2>
          <p class="section-subtitle">Compare trends across U.S. regions</p>
        </div>
        <div class="chart-card">
          <h3>Regional Yield Evolution (ThemeRiver)</h3>
          <ThemeRiver :data="yearFilteredAllData" />
        </div>
      </section>

      <!-- Correlation Analysis -->
      <section class="section">
        <div class="section-header">
          <h2>Correlation Analysis</h2>
          <p class="section-subtitle">
            Relationship between climate factors and corn yield
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
          <h3>Parallel Coordinates View</h3>
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

      <!-- Distribution -->
      <section class="section">
        <div class="section-header">
          <h2>Yield Distribution</h2>
          <p class="section-subtitle">Production breakdown by state</p>
        </div>
        <div class="chart-card">
          <TreemapVisualization
            :data="yearFilteredAllData"
            :selectedState="selectedState"
            @select-state="handleSelectState"
          />
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
              <StateYieldTrend
                :data="filteredData"
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
              <StateTemperatureTrend
                :data="filteredData"
                :tempMetric="tempMetric"
                :hoveredYear="stateDetailHoveredYear"
                @hover-year="stateDetailHoveredYear = $event"
              />
            </div>
          </div>
          <div class="col-md-6">
            <div class="chart-card">
              <h3>{{ selectedState }} Precipitation Trend</h3>
              <StatePrecipitationTrend
                :data="filteredData"
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
            <p>NOAA Climate Data (2000-2024)</p>
            <p>USDA Agricultural Statistics</p>
          </div>
          <div class="footer-section">
            <h4>Coverage</h4>
            <p>41 U.S. States</p>
            <p>25 Years of Data</p>
          </div>
          <div class="footer-section">
            <h4>Project Info</h4>
            <p>CS:4980 - Interactive Data Visualization</p>
            <p>University of Iowa, Fall 2025</p>
          </div>
        </div>
      </footer>
    </div>
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
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%);
  color: #1e293b;
}

/* Sticky Navbar */
.sticky-navbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
  border-bottom: 2px solid #3b82f6;
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
  gap: 1.5rem;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.control-group label {
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

/* Sections */
.section {
  margin-bottom: 4rem;
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

/* Responsive */
@media (max-width: 768px) {
  .navbar-content {
    flex-direction: column;
    gap: 1rem;
  }

  .row {
    grid-template-columns: 1fr;
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
