<script setup>
import { ref, watch, onMounted, computed } from "vue";
import * as d3 from "d3";

const props = defineProps({
  data: { type: Array, required: true },
  tempMetric: { type: String, default: "F" },
  hoveredYear: { type: Number, default: null },
});

const emit = defineEmits(["hover-year"]);
const containerRef = ref(null);
const margin = { top: 30, right: 30, bottom: 50, left: 60 };

const tempAccessor = (d) =>
  props.tempMetric === "C" ? ((d.TAVG - 32) * 5) / 9 : d.TAVG;

const aggregatedData = computed(() => {
  if (!props.data || !props.data.length) return [];

  const byYear = d3.rollups(
    props.data,
    (v) => ({
      avgPrecip: d3.mean(v, (d) => d.PRCP),
      avgYield: d3.mean(v, (d) => d.Yield_bu_acre),
      avgTemp: d3.mean(v, (d) => tempAccessor(d)),
    }),
    (d) => d.Year
  );

  return byYear
    .map(([year, vals]) => ({ year, ...vals }))
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
    .attr("id", "national-precip-gradient")
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
    .attr("fill", "url(#national-precip-gradient)")
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

  const tooltip = container
    .append("div")
    .attr("class", "chart-tooltip")
    .style("position", "absolute")
    .style("background", "rgba(255,255,255,0.98)")
    .style("color", "#1e293b")
    .style("padding", "10px 14px")
    .style("border-radius", "8px")
    .style("font-size", "12px")
    .style("pointer-events", "none")
    .style("box-shadow", "0 4px 12px rgba(0,0,0,0.15)")
    .style("border", "1px solid rgba(59,130,246,0.4)")
    .style("opacity", 0);

  const points = g
    .selectAll(".point")
    .data(aggregatedData.value)
    .join("circle")
    .attr("class", "point")
    .attr("cx", (d) => x(d.year))
    .attr("cy", (d) => y(d.avgPrecip))
    .attr("r", (d) => (props.hoveredYear === d.year ? 8 : 5))
    .attr("fill", "#2563eb")
    .attr("stroke", "#fff")
    .attr("stroke-width", 2)
    .style("cursor", "pointer")
    .on("mouseenter", function (event, d) {
      d3.select(this).attr("r", 10);
      emit("hover-year", d.year);

      const rect = containerRef.value.getBoundingClientRect();
      tooltip
        .style("opacity", 1)
        .html(
          `
          <div style="font-weight:600;margin-bottom:4px;">Year: ${d.year}</div>
          <div>Precipitation: <strong>${d.avgPrecip.toFixed(
            2
          )} in</strong></div>
          <div style="color:#16a34a;margin-top:4px;">Yield: <strong>${d.avgYield.toFixed(
            1
          )} bu/acre</strong></div>
          <div style="color:#f97316;margin-top:2px;">Temp: <strong>${d.avgTemp.toFixed(
            1
          )}°${props.tempMetric}</strong></div>
        `
        )
        .style("left", `${event.clientX - rect.left + 10}px`)
        .style("top", `${event.clientY - rect.top - 30}px`);
    })
    .on("mousemove", function (event) {
      const rect = containerRef.value.getBoundingClientRect();
      tooltip
        .style("left", `${event.clientX - rect.left + 10}px`)
        .style("top", `${event.clientY - rect.top - 30}px`);
    })
    .on("mouseleave", function (event, d) {
      if (props.hoveredYear !== d.year) {
        d3.select(this).attr("r", 5);
      }
      tooltip.style("opacity", 0);
      emit("hover-year", null);
    });

  points.attr("r", (d) => (props.hoveredYear === d.year ? 8 : 5));

  g.append("g")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x).tickFormat(d3.format("d")))
    .attr("color", "#94a3b8")
    .selectAll("text")
    .attr("font-size", 12);

  g.append("g")
    .call(d3.axisLeft(y).ticks(5))
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
watch(() => [props.data, props.hoveredYear, props.tempMetric], render, {
  deep: true,
});
</script>

<template>
  <div
    ref="containerRef"
    style="position: relative; width: 100%; height: 300px"
  ></div>
</template>
