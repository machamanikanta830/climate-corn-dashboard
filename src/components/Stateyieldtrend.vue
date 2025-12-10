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
    (v) => d3.mean(v, (d) => d.Yield_bu_acre),
    (d) => d.Year
  );

  return byYear
    .map(([year, avgYield]) => ({ year, avgYield }))
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
    .domain(d3.extent(aggregatedData.value, (d) => d.avgYield))
    .nice()
    .range([height, 0]);

  const gradient = svg
    .append("defs")
    .append("linearGradient")
    .attr("id", "state-yield-gradient")
    .attr("x1", "0%")
    .attr("x2", "0%")
    .attr("y1", "0%")
    .attr("y2", "100%");

  gradient
    .append("stop")
    .attr("offset", "0%")
    .attr("stop-color", "#22c55e")
    .attr("stop-opacity", 0.6);

  gradient
    .append("stop")
    .attr("offset", "100%")
    .attr("stop-color", "#22c55e")
    .attr("stop-opacity", 0.1);

  const area = d3
    .area()
    .x((d) => x(d.year))
    .y0(height)
    .y1((d) => y(d.avgYield))
    .curve(d3.curveMonotoneX);

  g.append("path")
    .datum(aggregatedData.value)
    .attr("d", area)
    .attr("fill", "url(#state-yield-gradient)");

  const line = d3
    .line()
    .x((d) => x(d.year))
    .y((d) => y(d.avgYield))
    .curve(d3.curveMonotoneX);

  g.append("path")
    .datum(aggregatedData.value)
    .attr("d", line)
    .attr("fill", "none")
    .attr("stroke", "#16a34a")
    .attr("stroke-width", 3);

  g.append("g")
    .selectAll("line")
    .data(y.ticks(5))
    .join("line")
    .attr("x1", 0)
    .attr("x2", width)
    .attr("y1", (d) => y(d))
    .attr("y2", (d) => y(d))
    .attr("stroke", "#334155")
    .attr("stroke-width", 1)
    .attr("opacity", 0.1);

  d3.select("body").selectAll(".state-yield-tooltip").remove();
  const tooltip = d3
    .select("body")
    .append("div")
    .attr("class", "chart-tooltip state-yield-tooltip")
    .style("opacity", 0)
    .style("position", "fixed")
    .style("pointer-events", "none");

  const points = g
    .selectAll(".point")
    .data(aggregatedData.value)
    .join("circle")
    .attr("class", "point")
    .attr("cx", (d) => x(d.year))
    .attr("cy", (d) => y(d.avgYield))
    .attr("r", (d) => (props.hoveredYear === d.year ? 8 : 5))
    .attr("fill", "#16a34a")
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
          }</strong><br/>Yield: <strong>${d.avgYield.toFixed(
            1
          )} bu/acre</strong>`
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
    .text("Corn Yield (bu/acre)");
}

onMounted(render);
watch(() => [props.data, props.hoveredYear], render, { deep: true });
</script>

<template>
  <div ref="containerRef" class="state-yield-container"></div>
</template>

<style scoped>
.state-yield-container {
  width: 100%;
  min-height: 300px;
  position: relative;
}
</style>
