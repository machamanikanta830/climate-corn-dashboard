<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as d3 from "d3";

const props = defineProps({
  data: { type: Array, required: true },
});

const containerRef = ref(null);
const margin = { top: 65, right: 24, bottom: 50, left: 65 };

const regions = {
  Midwest: [
    "IOWA", "ILLINOIS", "INDIANA", "OHIO", "MICHIGAN", "WISCONSIN",
    "MINNESOTA", "MISSOURI", "KANSAS", "NEBRASKA", "SOUTH DAKOTA",
    "NORTH DAKOTA",
  ],
  South: [
    "TEXAS", "OKLAHOMA", "ARKANSAS", "LOUISIANA", "MISSISSIPPI", "ALABAMA",
    "TENNESSEE", "KENTUCKY", "GEORGIA", "FLORIDA", "SOUTH CAROLINA",
    "NORTH CAROLINA", "VIRGINIA", "WEST VIRGINIA", "MARYLAND", "DELAWARE",
  ],
  West: [
    "CALIFORNIA", "OREGON", "WASHINGTON", "IDAHO", "MONTANA", "WYOMING",
    "NEVADA", "UTAH", "COLORADO", "ARIZONA", "NEW MEXICO",
  ],
  Northeast: ["NEW YORK", "PENNSYLVANIA", "NEW JERSEY"],
};

const regionNames = Object.keys(regions);
const colors = new Map([
  ["Midwest", "#2563eb"],
  ["South", "#d97706"],
  ["West", "#059669"],
  ["Northeast", "#7c3aed"],
]);

function getRegion(state) {
  return regionNames.find((region) => regions[region].includes(state)) ?? "Other";
}

const regionalData = computed(() => {
  if (!props.data?.length) return [];

  const grouped = d3.rollups(
    props.data.filter((row) => getRegion(row.State) !== "Other"),
    (rows) => d3.mean(rows, (row) => row.Yield_bu_acre),
    (row) => row.Year,
    (row) => getRegion(row.State)
  );

  return grouped
    .map(([year, values]) => {
      const byRegion = new Map(values);
      return {
        year,
        ...Object.fromEntries(regionNames.map((region) => [region, byRegion.get(region)])),
      };
    })
    .sort((a, b) => a.year - b.year);
});

function render() {
  if (!containerRef.value || !regionalData.value.length) return;

  const container = d3.select(containerRef.value);
  container.selectAll("*").remove();

  const fullWidth = Math.max(container.node().clientWidth, 420);
  const fullHeight = 420;
  const width = fullWidth - margin.left - margin.right;
  const height = fullHeight - margin.top - margin.bottom;

  const svg = container
    .append("svg")
    .attr("width", "100%")
    .attr("height", fullHeight)
    .attr("viewBox", `0 0 ${fullWidth} ${fullHeight}`)
    .attr("role", "img")
    .attr(
      "aria-label",
      "Line chart comparing average corn yield by U.S. region for each selected year"
    );

  const g = svg
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  const x = d3
    .scaleLinear()
    .domain(d3.extent(regionalData.value, (row) => row.year))
    .range([0, width]);

  const allValues = regionalData.value.flatMap((row) =>
    regionNames.map((region) => row[region]).filter(Number.isFinite)
  );
  const y = d3.scaleLinear().domain(d3.extent(allValues)).nice().range([height, 0]);

  g.append("g")
    .selectAll("line")
    .data(y.ticks(5))
    .join("line")
    .attr("x1", 0)
    .attr("x2", width)
    .attr("y1", (value) => y(value))
    .attr("y2", (value) => y(value))
    .attr("stroke", "#e2e8f0");

  g.append("g")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x).ticks(Math.min(12, regionalData.value.length)).tickFormat(d3.format("d")))
    .call((axis) => axis.select(".domain").attr("stroke", "#94a3b8"));

  g.append("g")
    .call(d3.axisLeft(y).ticks(5))
    .call((axis) => axis.select(".domain").attr("stroke", "#94a3b8"));

  const line = d3
    .line()
    .defined((row) => Number.isFinite(row.value))
    .x((row) => x(row.year))
    .y((row) => y(row.value))
    .curve(d3.curveMonotoneX);

  regionNames.forEach((region) => {
    const values = regionalData.value.map((row) => ({
      year: row.year,
      value: row[region],
    }));

    g.append("path")
      .datum(values)
      .attr("fill", "none")
      .attr("stroke", colors.get(region))
      .attr("stroke-width", 2.5)
      .attr("d", line);
  });

  const legend = svg
    .append("g")
    .attr("transform", `translate(${margin.left},24)`);

  regionNames.forEach((region, index) => {
    const item = legend
      .append("g")
      .attr("transform", `translate(${index * 125},0)`);
    item.append("line").attr("x2", 22).attr("y1", 7).attr("y2", 7)
      .attr("stroke", colors.get(region)).attr("stroke-width", 3);
    item.append("text").attr("x", 29).attr("y", 11).attr("font-size", 12)
      .attr("fill", "#334155").text(region);
  });

  g.append("text")
    .attr("x", width / 2)
    .attr("y", height + 42)
    .attr("text-anchor", "middle")
    .attr("fill", "#475569")
    .text("Year");

  g.append("text")
    .attr("transform", "rotate(-90)")
    .attr("x", -height / 2)
    .attr("y", -48)
    .attr("text-anchor", "middle")
    .attr("fill", "#475569")
    .text("Regional average yield (bu/acre)");

  const hoverLine = g.append("line")
    .attr("y2", height)
    .attr("stroke", "#64748b")
    .attr("stroke-dasharray", "4,4")
    .attr("opacity", 0);

  const tooltip = container.append("div")
    .attr("class", "chart-tooltip")
    .style("position", "absolute")
    .style("pointer-events", "none")
    .style("opacity", 0);

  const years = regionalData.value.map((row) => row.year);
  const bisect = d3.bisector((value) => value).center;

  g.append("rect")
    .attr("width", width)
    .attr("height", height)
    .attr("fill", "transparent")
    .on("mousemove", (event) => {
      const [mouseX] = d3.pointer(event);
      const row = regionalData.value[bisect(years, x.invert(mouseX))];
      if (!row) return;

      hoverLine.attr("x1", x(row.year)).attr("x2", x(row.year)).attr("opacity", 1);
      const details = regionNames
        .map(
          (region) =>
            `<span style="color:${colors.get(region)}">●</span> ${region}: ` +
            `<strong>${row[region].toFixed(1)} bu/acre</strong>`
        )
        .join("<br>");
      const rect = containerRef.value.getBoundingClientRect();
      tooltip
        .style("opacity", 1)
        .html(`<strong>${row.year}</strong><br>${details}`)
        .style("left", `${event.clientX - rect.left + 14}px`)
        .style("top", `${event.clientY - rect.top - 40}px`);
    })
    .on("mouseleave", () => {
      hoverLine.attr("opacity", 0);
      tooltip.style("opacity", 0);
    });
}

onMounted(render);
watch(() => props.data, render, { deep: true });
onBeforeUnmount(() => {
  if (containerRef.value) d3.select(containerRef.value).selectAll("*").remove();
});
</script>

<template>
  <div ref="containerRef" class="regional-trend"></div>
</template>

<style scoped>
.regional-trend {
  position: relative;
  width: 100%;
  min-height: 420px;
  overflow-x: auto;
}
</style>
