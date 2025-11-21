<script setup>
import { ref, watch, onMounted } from 'vue';
import * as d3 from 'd3';

const props = defineProps({
  data: { type: Array, required: true },
  tempMetric: { type: String, default: 'C' },
  selectedState: { type: String, default: 'ALL' }
});

// brushSelection → parallel coords, selectState → global state selection
const emit = defineEmits(['brushSelection', 'selectState']);

const containerRef = ref(null);
const margin = { top: 25, right: 20, bottom: 35, left: 45 };

// toggle between hover-only and brushing mode
const brushEnabled = ref(false);

function tempAccessor(d) {
  return props.tempMetric === 'C' ? d.TAVG_C : d.TAVG;
}

function render() {
  if (!containerRef.value || !props.data.length) return;

  const container = d3.select(containerRef.value);
  container.select('svg').remove();
  container.select('.tooltip').remove();

  const svg = container.append('svg').attr('width', '100%').attr('height', 280);

  const width =
    container.node().clientWidth - margin.left - margin.right;
  const height = 280 - margin.top - margin.bottom;

  const g = svg
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3
    .scaleLinear()
    .domain(d3.extent(props.data, d => tempAccessor(d)))
    .nice()
    .range([0, width]);

  const y = d3
    .scaleLinear()
    .domain(d3.extent(props.data, d => d.Yield_bu_acre))
    .nice()
    .range([height, 0]);

  const xAxis = d3.axisBottom(x).ticks(6);
  const yAxis = d3.axisLeft(y).ticks(6);

  g.append('g')
    .attr('transform', `translate(0,${height})`)
    .attr('class', 'axis')
    .call(xAxis);

  g.append('g').attr('class', 'axis').call(yAxis);

  g.append('text')
    .attr('x', width / 2)
    .attr('y', height + 30)
    .attr('text-anchor', 'middle')
    .attr('font-size', 11)
    .text(`Average Temperature (${props.tempMetric === 'C' ? '°C' : '°F'})`);

  g.append('text')
    .attr('transform', 'rotate(-90)')
    .attr('x', -height / 2)
    .attr('y', -32)
    .attr('text-anchor', 'middle')
    .attr('font-size', 11)
    .text('Yield (bushels/acre)');

  // Tooltip – explains what a point is on hover
  const tooltip = container
    .append('div')
    .attr('class', 'tooltip');

  const dots = g
    .selectAll('.dot')
    .data(props.data)
    .enter()
    .append('circle')
    .attr('class', 'dot')
    .attr('cx', d => x(tempAccessor(d)))
    .attr('cy', d => y(d.Yield_bu_acre))
    .attr('r', d =>
      props.selectedState !== 'ALL' && d.State === props.selectedState
        ? 4.8
        : 3
    )
    .attr('fill', d =>
      props.selectedState !== 'ALL' && d.State === props.selectedState
        ? '#ef3b2c'
        : '#4292c6'
    )
    .attr('fill-opacity', d =>
      props.selectedState !== 'ALL' && d.State === props.selectedState
        ? 0.9
        : 0.4
    )
    .on('mouseover', function (event, d) {
      // In brush mode, we still show tooltip IF event reaches the circle
      d3.select(this).attr('stroke', '#000').attr('stroke-width', 1.2);

      const [mx, my] = d3.pointer(event, container.node());

      tooltip
        .style('opacity', 1)
        .style('left', `${mx + 15}px`)
        .style('top', `${my + 15}px`)
        .html(
          `<strong>${d.State}</strong> (${d.Year})<br/>
           Temp: ${d3.format('.2f')(tempAccessor(d))} ${
             props.tempMetric === 'C' ? '°C' : '°F'
           }<br/>
           Yield: ${d3.format('.2f')(d.Yield_bu_acre)} bu/acre`
        );
    })
    .on('mousemove', function (event) {
      const [mx, my] = d3.pointer(event, container.node());
      tooltip
        .style('left', `${mx + 15}px`)
      .style('top', `${my + 15}px`);
    })
    .on('mouseout', function () {
      d3.select(this).attr('stroke', null);
      tooltip.style('opacity', 0);
    })
    .on('click', (event, d) => {
      // clicking a point selects that state globally
      emit('selectState', d.State.toUpperCase());
    });

  // If brush mode is OFF, do not create a brush overlay
  if (!brushEnabled.value) {
    emit('brushSelection', []); // clear any previous selection
    return;
  }

  // Brush mode ON – allow rectangular selection for parallel coords
  const brush = d3
    .brush()
    .extent([
      [0, 0],
      [width, height]
    ])
    .on('end', brushEnded);

  g.append('g').attr('class', 'brush').call(brush);

  function brushEnded(event) {
    const s = event.selection;
    if (!s) {
      dots.attr('stroke', null);
      emit('brushSelection', []);
      return;
    }

    const [[x0, y0], [x1, y1]] = s;

    const selected = [];
    dots.each(function (d) {
      const cx = x(tempAccessor(d));
      const cy = y(d.Yield_bu_acre);
      const inside = x0 <= cx && cx <= x1 && y0 <= cy && cy <= y1;
      d3.select(this).attr('stroke', inside ? '#000' : null);
      if (inside && d._id != null) {
        selected.push(d._id);
      }
    });

    emit('brushSelection', selected);
  }
}

onMounted(render);
watch(
  () => [props.data, props.tempMetric, props.selectedState, brushEnabled.value],
  render,
  { deep: true }
);
</script>

<template>
  <div class="chart-box half">
    <div
      style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.25rem;"
    >
      <h3>Yield vs Temperature (All States, All Years)</h3>
      <label style="font-size:0.8rem; display:flex; align-items:center; gap:0.25rem;">
        <input type="checkbox" v-model="brushEnabled" />
        Enable brushing
      </label>
    </div>
    <div ref="containerRef"></div>
  </div>
</template>