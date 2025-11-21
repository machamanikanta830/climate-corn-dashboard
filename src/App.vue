<script setup>
import { ref, onMounted, watch } from 'vue';
import * as d3 from 'd3';

import OverviewTempYield from './components/OverviewTempYield.vue';
import ScatterTempYield from './components/ScatterTempYield.vue';
import StateTrendChart from './components/StateTrendChart.vue';
import UsChoroplethMap from './components/UsChoroplethMap.vue';
import ParallelCoordinates from './components/ParallelCoordinates.vue';

const allData = ref([]);
const states = ref([]);
const selectedState = ref('ALL');
const tempMetric = ref('C');  // 'C' or 'F'
const brushedIds = ref([]);   // from scatter brush

onMounted(async () => {
  const data = await d3.csv('/data/final_climate_yield_dataset.csv', d3.autoType);

  // Add unique id per row for linking scatter ↔ parallel coords
  data.forEach((d, i) => {
    d._id = i;
  });

  allData.value = data;
  states.value = Array.from(new Set(data.map(d => d.State))).sort();
});

function handleBrushSelection(ids) {
  brushedIds.value = ids;
}

function resetAll() {
  selectedState.value = 'ALL';
  tempMetric.value = 'C';
  brushedIds.value = [];
}

// When user changes selected state (dropdown or map/scatter click),
// clear brushed selection so purple subset doesn’t conflict with red state.
watch(selectedState, () => {
  brushedIds.value = [];
});
</script>

<template>
  <div class="page">
    <!-- Header -->
    <header class="page-header">
      <h1>Impact of Climate Trends on Corn Yields (2000–2024)</h1>
      <p>Data: NOAA (GSOY) + USDA NASS – 41 states × 25 years</p>
    </header>

    <!-- Controls bar (replaces sidebar) -->
    <div class="controls-bar">
      <div class="controls-group">
        <span class="control-label">State:</span>
        <select v-model="selectedState">
          <option value="ALL">All States (national view)</option>
          <option v-for="s in states" :key="s" :value="s">
            {{ s }}
          </option>
        </select>
      </div>

      <div class="controls-group">
        <span class="control-label">Temperature:</span>
        <div class="radio-group-inline">
          <label>
            <input type="radio" value="C" v-model="tempMetric" />
            °C
          </label>
          <label>
            <input type="radio" value="F" v-model="tempMetric" />
            °F
          </label>
        </div>
      </div>

      <button class="reset-button" @click="resetAll">
        Reset all views
      </button>
    </div>

    <!-- Main content -->
    <main class="layout">
      <section class="content">
        <!-- Row 1: National trends + Scatter side by side -->
        <section class="panel">
          <div class="panel-row">
            <OverviewTempYield
              class="half"
              :data="allData"
              :tempMetric="tempMetric"
            />
            <ScatterTempYield
              :data="allData"
              :tempMetric="tempMetric"
              :selectedState="selectedState"
              @brushSelection="handleBrushSelection"
              @selectState="selectedState = $event"
            />
          </div>
        </section>

        <!-- Row 2: Map + State trends side by side -->
        <section class="panel">
          <div class="panel-row">
            <UsChoroplethMap
              class="half"
              :data="allData"
              :tempMetric="tempMetric"
              :selectedState="selectedState"
              @selectState="selectedState = $event"
            />
            <StateTrendChart
              :data="allData"
              :tempMetric="tempMetric"
              :selectedState="selectedState"
            />
          </div>
        </section>

        <!-- Row 3: Parallel coordinates -->
        <section class="panel">
          <h2>Multi-variable Patterns</h2>
          <ParallelCoordinates
            :data="allData"
            :tempMetric="tempMetric"
            :selectedState="selectedState"
            :brushedIds="brushedIds"
          />
        </section>
      </section>
    </main>
  </div>
</template>
