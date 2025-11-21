<script setup>
import { ref, watch, onMounted } from 'vue';
import * as d3 from 'd3';

const props = defineProps({
  data: { type: Array, required: true },
  tempMetric: { type: String, default: 'C' } // 'C' or 'F'
});

const containerRef = ref(null);
const margin = { top: 30, right: 20, bottom: 40, left: 45, right2: 45 };

function tempAccessor(d) {
  return props.tempMetric === 'C' ? d.TAVG_C : d.TAVG;
}

function render() {
  if (!containerRef.value || !props.data.length) return;

  const container = d3.select(containerRef.value);
  container.select('svg').remove();

  const yearly = d3.rollups(
    props.data,
    v => ({
      avgTemp: d3.mean(v, d => tempAccessor(d)),
      avgYield: d3.mean(v, d => d.Yield_bu_acre)
    }),
    d => d.Year
  )
    .map(([Year, vals]) => ({ Year, ...vals }))
    .sort((a, b) => d3.ascending(a.Year, b.Year));

  const svg = container.append('svg').attr('width', '100%').attr('height', 260);
  const width =
    container.node().clientWidth - margin.left - margin.right - margin.right2;
  const height = 260 - margin.top - margin.bottom;

  const g = svg
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3
    .scaleLinear()
    .domain(d3.extent(yearly, d => d.Year))
    .range([0, width]);

  const yTemp = d3
    .scaleLinear()
    .domain(d3.extent(yearly, d => d.avgTemp))
    .nice()
    .range([height, 0]);

  const yYield = d3
    .scaleLinear()
    .domain(d3.extent(yearly, d => d.avgYield))
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

  // Axis labels
  g.append('text')
    .attr('x', width / 2)
    .attr('y', height + 30)
    .attr('text-anchor', 'middle')
    .attr('font-size', 11)
    .text('Year');

  g.append('text')
    .attr('transform', 'rotate(-90)')
    .attr('x', -height / 2)
    .attr('y', -32)
    .attr('text-anchor', 'middle')
    .attr('font-size', 11)
    .text(`Temperature (${props.tempMetric === 'C' ? '°C' : '°F'})`);

  g.append('text')
    .attr('transform', 'rotate(-90)')
    .attr('x', -height / 2)
    .attr('y', width + 36)
    .attr('text-anchor', 'middle')
    .attr('font-size', 11)
    .text('Yield (bu/acre)');

  // Temp line
  const lineTemp = d3
    .line()
    .x(d => x(d.Year))
    .y(d => yTemp(d.avgTemp));

  g.append('path')
    .datum(yearly)
    .attr('fill', 'none')
    .attr('stroke', '#e6550d')
    .attr('stroke-width', 2)
    .attr('d', lineTemp);

  // Yield line
  const lineYield = d3
    .line()
    .x(d => x(d.Year))
    .y(d => yYield(d.avgYield));

  g.append('path')
    .datum(yearly)
    .attr('fill', 'none')
    .attr('stroke', '#31a354')
    .attr('stroke-width', 2)
    .attr('d', lineYield);

  // Series legend
  const legend = g.append('g').attr('transform', 'translate(0,0)');

  legend
    .append('rect')
    .attr('x', 0)
    .attr('y', -22)
    .attr('width', 270)
    .attr('height', 18)
    .attr('fill', 'white')
    .attr('opacity', 0.8);

  legend
    .append('line')
    .attr('x1', 6)
    .attr('y1', -11)
    .attr('x2', 22)
    .attr('y2', -11)
    .attr('stroke', '#e6550d')
    .attr('stroke-width', 2);

  legend
    .append('text')
    .attr('x', 26)
    .attr('y', -9)
    .attr('font-size', 10)
    .text(`Avg Temp (${props.tempMetric === 'C' ? '°C' : '°F'})`);

  legend
    .append('line')
    .attr('x1', 140)
    .attr('y1', -11)
    .attr('x2', 156)
    .attr('y2', -11)
    .attr('stroke', '#31a354')
    .attr('stroke-width', 2);

  legend
    .append('text')
    .attr('x', 160)
    .attr('y', -9)
    .attr('font-size', 10)
    .text('Avg Yield (bu/acre)');
}

onMounted(render);
watch(
  () => [props.data, props.tempMetric],
  render,
  { deep: true }
);
</script>

<template>
  <div ref="containerRef" class="chart-box half">
    <h3>Temperature & Yield Over Time</h3>
  </div>
</template>