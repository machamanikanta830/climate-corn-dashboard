<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as d3 from "d3";

const props = defineProps({
  data: { type: Array, required: true },
  metric: {
    type: String,
    required: true,
    validator: (value) => ["yield", "temperature", "precipitation"].includes(value),
  },
  tempMetric: { type: String, default: "F" },
  hoveredYear: { type: Number, default: null },
});

const emit = defineEmits(["hover-year"]);
const containerRef = ref(null);
const margin = { top: 25, right: 24, bottom: 50, left: 65 };
let resizeObserver;

const configuration = computed(() => {
  if (props.metric === "temperature") {
    return {
      label: `Temperature (°${props.tempMetric})`,
      shortLabel: "Temperature",
      unit: `°${props.tempMetric}`,
      color: "#dc2626",
      accessor: (row) => (props.tempMetric === "C" ? row.TAVG_C : row.TAVG),
    };
  }
  if (props.metric === "precipitation") {
    return {
      label: "Precipitation (inches)",
      shortLabel: "Precipitation",
      unit: " in",
      color: "#2563eb",
      accessor: (row) => row.PRCP,
    };
  }
  return {
    label: "Corn yield (bu/acre)",
    shortLabel: "Yield",
    unit: " bu/acre",
    color: "#16805d",
    accessor: (row) => row.Yield_bu_acre,
  };
});

const trendData = computed(() => {
  if (!props.data?.length) return [];
  const byYear = d3.rollups(
    props.data,
    (rows) => d3.mean(rows, configuration.value.accessor),
    (row) => row.Year
  );
  return byYear
    .map(([year, value]) => ({ year, value }))
    .sort((a, b) => a.year - b.year);
});

function render() {
  if (!containerRef.value || !trendData.value.length) return;

  const container = d3.select(containerRef.value);
  container.selectAll("*").remove();

  const fullWidth = Math.max(container.node().clientWidth, 320);
  const fullHeight = 310;
  const width = fullWidth - margin.left - margin.right;
  const height = fullHeight - margin.top - margin.bottom;
  const config = configuration.value;

  const svg = container
    .append("svg")
    .attr("width", "100%")
    .attr("height", fullHeight)
    .attr("viewBox", `0 0 ${fullWidth} ${fullHeight}`)
    .attr("role", "img")
    .attr("aria-label", `${config.shortLabel} trend for the selected state`);

  const g = svg
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  const x = d3
    .scaleLinear()
    .domain(d3.extent(trendData.value, (row) => row.year))
    .range([0, width]);
  const y = d3
    .scaleLinear()
    .domain(d3.extent(trendData.value, (row) => row.value))
    .nice()
    .range([height, 0]);

  g.append("g")
    .selectAll("line")
    .data(y.ticks(5))
    .join("line")
    .attr("x2", width)
    .attr("y1", (value) => y(value))
    .attr("y2", (value) => y(value))
    .attr("stroke", "#e2e8f0");

  const area = d3
    .area()
    .x((row) => x(row.year))
    .y0(height)
    .y1((row) => y(row.value))
    .curve(d3.curveMonotoneX);
  const line = d3
    .line()
    .x((row) => x(row.year))
    .y((row) => y(row.value))
    .curve(d3.curveMonotoneX);

  g.append("path")
    .datum(trendData.value)
    .attr("d", area)
    .attr("fill", config.color)
    .attr("opacity", 0.12);
  g.append("path")
    .datum(trendData.value)
    .attr("d", line)
    .attr("fill", "none")
    .attr("stroke", config.color)
    .attr("stroke-width", 2.5);

  const tooltip = container
    .append("div")
    .attr("class", "chart-tooltip")
    .style("position", "absolute")
    .style("pointer-events", "none")
    .style("opacity", 0);

  g.selectAll("circle")
    .data(trendData.value)
    .join("circle")
    .attr("cx", (row) => x(row.year))
    .attr("cy", (row) => y(row.value))
    .attr("r", (row) => (props.hoveredYear === row.year ? 7 : 4))
    .attr("fill", config.color)
    .attr("stroke", "white")
    .attr("stroke-width", 1.5)
    .on("mouseenter", (event, row) => {
      emit("hover-year", row.year);
      tooltip
        .style("opacity", 1)
        .html(
          `<strong>${row.year}</strong><br>${config.shortLabel}: ` +
            `<strong>${row.value.toFixed(1)}${config.unit}</strong>`
        );
      const rect = containerRef.value.getBoundingClientRect();
      tooltip
        .style("left", `${event.clientX - rect.left + 12}px`)
        .style("top", `${event.clientY - rect.top - 25}px`);
    })
    .on("mousemove", (event) => {
      const rect = containerRef.value.getBoundingClientRect();
      tooltip
        .style("left", `${event.clientX - rect.left + 12}px`)
        .style("top", `${event.clientY - rect.top - 25}px`);
    })
    .on("mouseleave", () => {
      emit("hover-year", null);
      tooltip.style("opacity", 0);
    });

  g.append("g")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x).ticks(Math.min(8, trendData.value.length)).tickFormat(d3.format("d")))
    .attr("color", "#64748b");
  g.append("g").call(d3.axisLeft(y).ticks(5)).attr("color", "#64748b");

  g.append("text")
    .attr("x", width / 2)
    .attr("y", height + 42)
    .attr("text-anchor", "middle")
    .attr("fill", "#475569")
    .text("Year");
  g.append("text")
    .attr("transform", "rotate(-90)")
    .attr("x", -height / 2)
    .attr("y", -47)
    .attr("text-anchor", "middle")
    .attr("fill", "#475569")
    .text(config.label);
}

onMounted(() => {
  render();
  resizeObserver = new ResizeObserver(render);
  resizeObserver.observe(containerRef.value);
});
watch(
  () => [props.data, props.metric, props.tempMetric, props.hoveredYear],
  render,
  { deep: true }
);
onBeforeUnmount(() => {
  resizeObserver?.disconnect();
  if (containerRef.value) d3.select(containerRef.value).selectAll("*").remove();
});
</script>

<template>
  <div ref="containerRef" class="state-metric-trend"></div>
</template>

<style scoped>
.state-metric-trend {
  position: relative;
  width: 100%;
  min-height: 310px;
}
</style>
