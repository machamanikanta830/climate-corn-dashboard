<script setup>
import { ref, watch, onMounted } from 'vue';
import * as d3 from 'd3';
import * as topojson from 'topojson-client';

const props = defineProps({
  data: { type: Array, required: true },
  tempMetric: { type: String, default: 'C' }, // for temp option
  selectedState: { type: String, default: 'ALL' }
});

const emit = defineEmits(['selectState']);

const containerRef = ref(null);
const usTopo = ref(null);
const mapMetric = ref('yield'); // 'yield' | 'temp' | 'prcp'

const margin = { top: 10, right: 10, bottom: 10, left: 10 };

async function loadTopo() {
  if (usTopo.value) return;
  const json = await d3.json('/data/us-states-10m.json');
  usTopo.value = json;
}

function render() {
  if (!containerRef.value || !props.data.length || !usTopo.value) return;

  const container = d3.select(containerRef.value);
  container.select('svg').remove();
  container.select('.tooltip').remove();

  const svg = container.append('svg').attr('width', '100%').attr('height', 260);

  const width =
    container.node().clientWidth - margin.left - margin.right;
  const height = 260 - margin.top - margin.bottom;

  const g = svg
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  const geo = topojson.feature(usTopo.value, usTopo.value.objects.states);

  const projection = d3
    .geoAlbersUsa()
    .fitSize([width, height], geo);

  const path = d3.geoPath(projection);

  // Aggregate data by state
  const agg = d3.rollup(
    props.data,
    v => ({
      avgYield: d3.mean(v, d => d.Yield_bu_acre),
      avgTempC: d3.mean(v, d => d.TAVG_C),
      avgTempF: d3.mean(v, d => d.TAVG),
      avgPrcp: d3.mean(v, d => d.PRCP)
    }),
    d => d.State
  );

  let metricKey;
  let legendLabel;
  let valueLabel;

  if (mapMetric.value === 'yield') {
    metricKey = 'avgYield';
    legendLabel = 'Average Yield (bu/acre)';
    valueLabel = 'Yield';
  } else if (mapMetric.value === 'temp') {
    metricKey = props.tempMetric === 'C' ? 'avgTempC' : 'avgTempF';
    legendLabel = `Average Temperature (${props.tempMetric === 'C' ? '°C' : '°F'})`;
    valueLabel = 'Temperature';
  } else {
    metricKey = 'avgPrcp';
    legendLabel = 'Average Precipitation';
    valueLabel = 'Precipitation';
  }

  const values = geo.features
    .map(f => {
      const key = f.properties.name.toUpperCase();
      const entry = agg.get(key);
      return entry ? entry[metricKey] : undefined;
    })
    .filter(v => v != null);

  const color = d3
    .scaleSequential(d3.extent(values), d3.interpolateYlGnBu)
    .unknown('#eee');

  const tooltip = container
    .append('div')
    .attr('class', 'tooltip');

  g.selectAll('path.state')
    .data(geo.features)
    .enter()
    .append('path')
    .attr('class', 'state')
    .attr('d', path)
    .attr('stroke', d => {
      const name = d.properties.name.toUpperCase();
      return props.selectedState !== 'ALL' &&
        name === props.selectedState.toUpperCase()
        ? '#000'
        : '#fff';
    })
    .attr('stroke-width', d => {
      const name = d.properties.name.toUpperCase();
      return props.selectedState !== 'ALL' &&
        name === props.selectedState.toUpperCase()
        ? 1.5
        : 0.6;
    })
    .attr('fill', d => {
      const key = d.properties.name.toUpperCase();
      const entry = agg.get(key);
      return entry ? color(entry[metricKey]) : '#eee';
    })
    .on('mouseover', function (event, d) {
      const key = d.properties.name.toUpperCase();
      const entry = agg.get(key);
      const val = entry ? entry[metricKey] : null;

      d3.select(this).attr('stroke-width', 2);

      const [mx, my] = d3.pointer(event, container.node());

      tooltip
        .style('opacity', 1)
        .style('left', `${mx + 15}px`)
        .style('top', `${my + 15}px`)
      tooltip
      .html(
        `<strong>${d.properties.name}</strong><br/>
        Avg ${valueLabel} (2000–2024): ${
          val != null ? d3.format('.2f')(val) : 'N/A'
        }`
      )

    })
    .on('mousemove', function (event) {
      const [mx, my] = d3.pointer(event, container.node());
      tooltip
        .style('left', `${mx + 15}px`)
        .style('top', `${my + 15}px`);
    })
    .on('mouseout', function () {
      d3.select(this).attr('stroke-width', d => {
        const name = d.properties.name.toUpperCase();
        return props.selectedState !== 'ALL' &&
          name === props.selectedState.toUpperCase()
          ? 1.5
          : 0.6;
      });
      tooltip.style('opacity', 0);
    })
    .on('click', (event, d) => {
      const stateName = d.properties.name.toUpperCase();
      emit('selectState', stateName);
    });

  // Legend
  const legendWidth = 180;
  const legendHeight = 8;

  const legendScale = d3
    .scaleLinear()
    .domain(color.domain())
    .range([0, legendWidth]);

  const legendAxis = d3
    .axisBottom(legendScale)
    .ticks(4)
    .tickSize(legendHeight)
    .tickFormat(d3.format('.1f'));

  const legendGradientId = 'mapLegendGrad';

  const defs = svg.append('defs');
  const gradient = defs
    .append('linearGradient')
    .attr('id', legendGradientId)
    .attr('x1', '0%')
    .attr('x2', '100%');

  const [minVal, maxVal] = color.domain();
  const steps = d3.range(0, 1.01, 0.25);
  steps.forEach(t => {
    gradient
      .append('stop')
      .attr('offset', `${t * 100}%`)
      .attr('stop-color', color(minVal + t * (maxVal - minVal)));
  });

  const legend = g
    .append('g')
    .attr(
      'transform',
      `translate(10, ${height})`
    );

  legend
    .append('rect')
    .attr('width', legendWidth)
    .attr('height', legendHeight)
    .attr('fill', `url(#${legendGradientId})`);

  legend
    .append('g')
    .attr('transform', `translate(0, ${legendHeight})`)
    .attr('class', 'axis')
    .call(legendAxis)
    .call(g => g.select('.domain').remove())
    .selectAll('text')
    .attr('font-size', 8);

  legend
    .append('text')
    .attr('x', legendWidth / 2)
    .attr('y', -4)
    .attr('text-anchor', 'middle')
    .attr('font-size', 9)
    .text(legendLabel);

  legend
    .append('text')
    .attr('x', 0)
    .attr('y', legendHeight + 20)
    .attr('text-anchor', 'start')
    .attr('font-size', 8)

  legend
    .append('text')
    .attr('x', legendWidth)
    .attr('y', legendHeight + 20)
    .attr('text-anchor', 'end')
    .attr('font-size', 8)
}

onMounted(async () => {
  await loadTopo();
  render();
});

watch(
  () => [props.data, props.tempMetric, props.selectedState, mapMetric.value],
  render,
  { deep: true }
);
</script>

<template>
  <div class="chart-box half">
    <div
      style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.25rem;"
    >
      <h3>U.S. Choropleth Map</h3>
      <div style="font-size:0.8rem;">
        <label style="margin-right:0.5rem;">
          <input type="radio" value="yield" v-model="mapMetric" /> Yield
        </label>
        <label style="margin-right:0.5rem;">
          <input type="radio" value="temp" v-model="mapMetric" /> Temp
        </label>
        <label>
          <input type="radio" value="prcp" v-model="mapMetric" /> Precip
        </label>
      </div>
    </div>
    <div ref="containerRef"></div>
  </div>
</template>