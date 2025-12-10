<script setup>
import { ref, watch, onMounted, computed } from "vue";
import * as d3 from "d3";

const props = defineProps({
  data: { type: Array, required: true },
  hoveredYear: { type: Number, default: null },
});

const emit = defineEmits(["hover-year"]);
const containerRef = ref(null);
const margin = { top: 30, right: 30, bottom: 50, left: 60 };

const aggregatedData = computed(() => {
  if (!props.data || !props.data.length) return [];
  const byYear = d3.rollups(
    props.data,
    (v) => d3.mean(v, (d) => d.PRCP),
    (d) => d.Year
  );
  return byYear
    .map(([year, avgPrecip]) => ({ year, avgPrecip }))
    .sort((a, b) => a.year - b.year);
});

function render() {
  if (!containerRef.value || !aggregatedData.value.length) return;

  const container = d3.select(containerRef.value);
  container.selectAll("*").remove();

  const fullWidth = container.node().clientWidth;
  const fullHeight = 300;
  const width = fullWidth - margin.left - margin.right;
  const height = fullHeight - margin.top - margin.bottom;

  const svg = container
    .append("svg")
    .attr("width", "100%")
    .attr("height", fullHeight);

  const g = svg
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  const x = d3
    .scaleLinear()
    .domain(d3.extent(aggregatedData.value, (d) => d.year))
    .range([0, width]);

  const y = d3
    .scaleLinear()
    .domain(d3.extent(aggregatedData.value, (d) => d.avgPrecip))
    .nice()
    .range([height, 0]);

  const defs = svg.append("defs");
  defs
    .append("linearGradient")
    .attr("id", "state-precip-gradient")
    .attr("x1", "0%")
    .attr("x2", "0%")
    .attr("y1", "0%")
    .attr("y2", "100%")
    .selectAll("stop")
    .data([
      { o: "0%", c: "#3b82f6", a: 0.6 },
      { o: "100%", c: "#3b82f6", a: 0.1 },
    ])
    .join("stop")
    .attr("offset", (d) => d.o)
    .attr("stop-color", (d) => d.c)
    .attr("stop-opacity", (d) => d.a);

  const area = d3
    .area()
    .x((d) => x(d.year))
    .y0(height)
    .y1((d) => y(d.avgPrecip))
    .curve(d3.curveMonotoneX);

  g.append("path")
    .datum(aggregatedData.value)
    .attr("fill", "url(#state-precip-gradient)")
    .attr("d", area);

  const line = d3
    .line()
    .x((d) => x(d.year))
    .y((d) => y(d.avgPrecip))
    .curve(d3.curveMonotoneX);

  g.append("path")
    .datum(aggregatedData.value)
    .attr("fill", "none")
    .attr("stroke", "#2563eb")
    .attr("stroke-width", 3)
    .attr("d", line);

  d3.select("body").selectAll(".state-precip-tooltip").remove();
  const tooltip = d3
    .select("body")
    .append("div")
    .attr("class", "chart-tooltip state-precip-tooltip")
    .style("opacity", 0)
    .style("position", "fixed")
    .style("pointer-events", "none");

  const points = g
    .selectAll(".point")
    .data(aggregatedData.value)
    .join("circle")
    .attr("class", "point")
    .attr("cx", (d) => x(d.year))
    .attr("cy", (d) => y(d.avgPrecip))
    .attr("r", (d) => (props.hoveredYear === d.year ? 8 : 5))
    .attr("fill", "#2563eb")
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 2)
    .style("cursor", "pointer")
    .on("mouseenter", (event, d) => {
      d3.select(event.currentTarget).transition().duration(150).attr("r", 10);

      emit("hover-year", d.year);

      tooltip
        .style("opacity", 1)
        .html(
          `<strong>Year: ${
            d.year
          }</strong><br/>Precipitation: <strong>${d.avgPrecip.toFixed(
            2
          )} in</strong>`
        )
        .style("left", event.clientX + 12 + "px")
        .style("top", event.clientY - 18 + "px");
    })
    .on("mousemove", (event) => {
      tooltip
        .style("left", event.clientX + 12 + "px")
        .style("top", event.clientY - 18 + "px");
    })
    .on("mouseleave", (event, d) => {
      d3.select(event.currentTarget)
        .transition()
        .duration(150)
        .attr("r", props.hoveredYear === d.year ? 8 : 5);

      emit("hover-year", null);
      tooltip.style("opacity", 0);
    });

  const xAxis = d3.axisBottom(x).tickFormat(d3.format("d"));
  const yAxis = d3.axisLeft(y).ticks(5);

  g.append("g")
    .attr("transform", `translate(0,${height})`)
    .call(xAxis)
    .attr("color", "#94a3b8")
    .selectAll("text")
    .attr("font-size", 12);

  g.append("g")
    .call(yAxis)
    .attr("color", "#94a3b8")
    .selectAll("text")
    .attr("font-size", 12);

  g.append("text")
    .attr("x", width / 2)
    .attr("y", height + 40)
    .attr("text-anchor", "middle")
    .attr("fill", "#475569")
    .attr("font-size", 14)
    .text("Year");

  g.append("text")
    .attr("transform", "rotate(-90)")
    .attr("x", -height / 2)
    .attr("y", -45)
    .attr("text-anchor", "middle")
    .attr("fill", "#475569")
    .attr("font-size", 14)
    .text("Precipitation (inches)");
}

onMounted(render);
watch(() => [props.data, props.hoveredYear], render, { deep: true });
</script>

<template>
  <div ref="containerRef" class="state-precip-container"></div>
</template>

<style scoped>
.state-precip-container {
  width: 100%;
  min-height: 300px;
  position: relative;
}
</style>
