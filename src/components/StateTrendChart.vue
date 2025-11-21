<script setup>
import { ref, watch, onMounted } from 'vue';
import * as d3 from 'd3';

const props = defineProps({
  data: { type: Array, required: true },
  tempMetric: { type: String, default: 'C' },
  selectedState: { type: String, default: 'ALL' }
});

const containerRef = ref(null);
const margin = { top: 25, right: 20, bottom: 35, left: 45 };

function tempAccessor(d) {
  return props.tempMetric === 'C' ? d.TAVG_C : d.TAVG;
}

function render() {
  if (!containerRef.value) return;

  const container = d3.select(containerRef.value);
  container.select('svg').remove();

  if (!props.data.length || props.selectedState === 'ALL') {
    return;
  }

  const stateData = props.data
    .filter(d => d.State === props.selectedState)
    .sort((a, b) => d3.ascending(a.Year, b.Year));

  if (!stateData.length) return;

  const svg = container.append('svg').attr('width', '100%').attr('height', 280);

  const width =
    container.node().clientWidth - margin.left - margin.right;
  const height = 280 - margin.top - margin.bottom;

  const g = svg
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3
    .scaleLinear()
    .domain(d3.extent(stateData, d => d.Year))
    .range([0, width]);

  const yTemp = d3
    .scaleLinear()
    .domain(d3.extent(stateData, d => tempAccessor(d)))
    .nice()
    .range([height, 0]);

  const yYield = d3
    .scaleLinear()
    .domain(d3.extent(stateData, d => d.Yield_bu_acre))
    .nice()
    .range([height, 0]);

  const xAxis = d3.axisBottom(x).ticks(6).tickFormat(d3.format('d'));
  const yAxisLeft = d3.axisLeft(yTemp).ticks(5);
  const yAxisRight = d3.axisRight(yYield).ticks(5);

  g.append('g')
    .attr('transform', `translate(0,${height})`)
    .attr('class', 'axis')
    .call(xAxis);

  g.append('g').attr('class', 'axis').call(yAxisLeft);

  g.append('g')
    .attr('class', 'axis')
    .attr('transform', `translate(${width},0)`)
    .call(yAxisRight);

  const lineTemp = d3
    .line()
    .x(d => x(d.Year))
    .y(d => yTemp(tempAccessor(d)));

  const lineYield = d3
    .line()
    .x(d => x(d.Year))
    .y(d => yYield(d.Yield_bu_acre));

  g.append('path')
    .datum(stateData)
    .attr('fill', 'none')
    .attr('stroke', '#e6550d')
    .attr('stroke-width', 2)
    .attr('d', lineTemp);

  g.append('path')
    .datum(stateData)
    .attr('fill', 'none')
    .attr('stroke', '#31a354')
    .attr('stroke-width', 2)
    .attr('d', lineYield);

  const legend = g.append('g').attr('transform', 'translate(0,0)');

  legend
    .append('rect')
    .attr('x', 0)
    .attr('y', -18)
    .attr('width', 230)
    .attr('height', 16)
    .attr('fill', 'white')
    .attr('opacity', 0.8);

  legend
    .append('line')
    .attr('x1', 6)
    .attr('y1', -10)
    .attr('x2', 22)
    .attr('y2', -10)
    .attr('stroke', '#e6550d')
    .attr('stroke-width', 2);

  legend
    .append('text')
    .attr('x', 26)
    .attr('y', -8)
    .attr('font-size', 10)
    .text(`Avg Temp (${props.tempMetric === 'C' ? '°C' : '°F'})`);

  legend
    .append('line')
    .attr('x1', 130)
    .attr('y1', -10)
    .attr('x2', 146)
    .attr('y2', -10)
    .attr('stroke', '#31a354')
    .attr('stroke-width', 2);

  legend
    .append('text')
    .attr('x', 150)
    .attr('y', -8)
    .attr('font-size', 10)
    .text('Yield (bu/acre)');
}

onMounted(render);
watch(
  () => [props.data, props.tempMetric, props.selectedState],
  render,
  { deep: true }
);
</script>

<template>
  <div class="chart-box half" ref="containerRef">
    <h3>State Trends</h3>
    <p
      v-if="selectedState === 'ALL'"
      style="font-size:0.85rem; color:#666; padding:0.25rem 0.5rem;"
    >
      Select a state from the dropdown or click a state on the map to see its
      temperature and yield trends over time.
    </p>
  </div>
</template>
