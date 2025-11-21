<script setup>
import { ref, watch, onMounted } from 'vue';
import * as d3 from 'd3';

const props = defineProps({
  data: { type: Array, required: true },
  tempMetric: { type: String, default: 'C' },
  selectedState: { type: String, default: 'ALL' },
  brushedIds: { type: Array, default: () => [] } // ids from scatter brush
});

const containerRef = ref(null);
const margin = { top: 30, right: 20, bottom: 10, left: 40 };

function tempAccessor(d) {
  return props.tempMetric === 'C' ? d.TAVG_C : d.TAVG;
}

function render() {
  if (!containerRef.value || !props.data.length) return;

  const container = d3.select(containerRef.value);
  container.select('svg').remove();

  const svg = container.append('svg').attr('width', '100%').attr('height', 300);

  const width =
    container.node().clientWidth - margin.left - margin.right;
  const height = 300 - margin.top - margin.bottom;

  const g = svg
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  // Dimensions for parallel coordinates
  const dimensions = [
    {
      key: 'Year',
      label: 'Year',
      scale: d3
        .scaleLinear()
        .domain(d3.extent(props.data, d => d.Year))
        .range([height, 0])
    },
    {
      key: 'temp',
      label: `Temp (${props.tempMetric === 'C' ? '°C' : '°F'})`,
      scale: d3
        .scaleLinear()
        .domain(d3.extent(props.data, d => tempAccessor(d)))
        .range([height, 0])
    },
    {
      key: 'PRCP',
      label: 'Precip (in)',
      scale: d3
        .scaleLinear()
        .domain(d3.extent(props.data, d => d.PRCP))
        .range([height, 0])
    },
    {
      key: 'Yield_bu_acre',
      label: 'Yield (bu/acre)',
      scale: d3
        .scaleLinear()
        .domain(d3.extent(props.data, d => d.Yield_bu_acre))
        .range([height, 0])
    }
  ];

  const x = d3
    .scalePoint()
    .domain(dimensions.map(d => d.key))
    .range([0, width])
    .padding(0.5);

  const brushedSet = new Set(props.brushedIds);

  const line = d3
    .line()
    .defined(d => d[1] != null)
    .x(([key]) => x(key))
    .y(([key, value]) => {
      const dim = dimensions.find(d => d.key === key);
      return dim ? dim.scale(value) : height / 2;
    });

  function path(d) {
    const values = [
      ['Year', d.Year],
      ['temp', tempAccessor(d)],
      ['PRCP', d.PRCP],
      ['Yield_bu_acre', d.Yield_bu_acre]
    ];
    return line(values);
  }

  // Color logic
  const color = d => {
    if (props.selectedState !== 'ALL' && d.State === props.selectedState) {
      return '#ef3b2c';
    }
    if (brushedSet.size && brushedSet.has(d._id)) {
      return '#756bb1';
    }
    return 'rgba(150,150,150,0.3)';
  };

  const strokeWidth = d => {
    if (props.selectedState !== 'ALL' && d.State === props.selectedState) {
      return 2.2;
    }
    if (brushedSet.size && brushedSet.has(d._id)) {
      return 1.8;
    }
    return 0.7;
  };

  g.selectAll('path.line')
    .data(props.data)
    .enter()
    .append('path')
    .attr('class', 'line')
    .attr('d', path)
    .attr('fill', 'none')
    .attr('stroke', color)
    .attr('stroke-width', strokeWidth);

  // Axes
  const axisGroup = g
    .selectAll('.dimension')
    .data(dimensions)
    .enter()
    .append('g')
    .attr('class', 'dimension')
    .attr('transform', d => `translate(${x(d.key)},0)`);

  axisGroup
    .append('g')
    .each(function (d) {
      d3.select(this).call(d3.axisLeft(d.scale).ticks(4));
    });

  axisGroup
    .append('text')
    .attr('y', -10)
    .attr('text-anchor', 'middle')
    .attr('font-size', 11)
    .text(d => d.label);
}

onMounted(render);
watch(
  () => [props.data, props.tempMetric, props.selectedState, props.brushedIds],
  render,
  { deep: true }
);
</script>

<template>
  <div class="chart-box">
    <h3>Parallel Coordinates: Year, Temp, Precip, Yield</h3>
    <div ref="containerRef"></div>
  </div>
</template>
