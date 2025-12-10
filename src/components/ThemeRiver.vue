<script setup>
import { ref, watch, onMounted, computed } from "vue";
import * as d3 from "d3";

const props = defineProps({
  data: { type: Array, required: true },
  hoveredYear: { type: Number, default: null },
});

const emit = defineEmits(["hover-year"]);

const containerRef = ref(null);
const margin = { top: 30, right: 120, bottom: 50, left: 60 };

const regions = {
  Midwest: [
    "IOWA",
    "ILLINOIS",
    "INDIANA",
    "OHIO",
    "MICHIGAN",
    "WISCONSIN",
    "MINNESOTA",
    "MISSOURI",
    "KANSAS",
    "NEBRASKA",
    "SOUTH DAKOTA",
    "NORTH DAKOTA",
  ],
  South: [
    "TEXAS",
    "OKLAHOMA",
    "ARKANSAS",
    "LOUISIANA",
    "MISSISSIPPI",
    "ALABAMA",
    "TENNESSEE",
    "KENTUCKY",
    "GEORGIA",
    "FLORIDA",
    "SOUTH CAROLINA",
    "NORTH CAROLINA",
    "VIRGINIA",
    "WEST VIRGINIA",
    "MARYLAND",
    "DELAWARE",
  ],
  West: [
    "CALIFORNIA",
    "OREGON",
    "WASHINGTON",
    "IDAHO",
    "MONTANA",
    "WYOMING",
    "NEVADA",
    "UTAH",
    "COLORADO",
    "ARIZONA",
    "NEW MEXICO",
  ],
  Northeast: ["NEW YORK", "PENNSYLVANIA", "NEW JERSEY"],
};

function getRegion(state) {
  for (const [region, states] of Object.entries(regions)) {
    if (states.includes(state)) return region;
  }
  return "Other";
}

const regionalData = computed(() => {
  if (!props.data || props.data.length === 0) return [];

  const dataWithRegion = props.data.map((d) => ({
    ...d,
    Region: getRegion(d.State),
  }));

  const nested = d3.rollups(
    dataWithRegion,
    (v) => d3.sum(v, (d) => d.Yield_bu_acre),
    (d) => d.Year,
    (d) => d.Region
  );

  const years = Array.from(new Set(props.data.map((d) => d.Year))).sort();
  const regionNames = ["Midwest", "South", "West", "Northeast"];

  const formattedData = years.map((year) => {
    const yearData = { year };
    const regionMap = new Map(nested.find(([y]) => y === year)?.[1] || []);

    regionNames.forEach((region) => {
      yearData[region] = regionMap.get(region) || 0;
    });

    return yearData;
  });

  return formattedData;
});

function render() {
  if (
    !containerRef.value ||
    !regionalData.value ||
    regionalData.value.length === 0
  )
    return;

  const container = d3.select(containerRef.value);
  container.select("svg").remove();
  container.selectAll(".chart-tooltip").remove();

  const width = container.node().clientWidth - margin.left - margin.right;
  const height = 400 - margin.top - margin.bottom;

  const svg = container.append("svg").attr("width", "100%").attr("height", 400);

  const g = svg
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  const regionNames = ["Midwest", "South", "West", "Northeast"];
  const stack = d3
    .stack()
    .keys(regionNames)
    .offset(d3.stackOffsetWiggle) 
    .order(d3.stackOrderInsideOut);

  const series = stack(regionalData.value);

  const x = d3
    .scaleLinear()
    .domain(d3.extent(regionalData.value, (d) => d.year))
    .range([0, width]);

  const y = d3
    .scaleLinear()
    .domain([
      d3.min(series, (s) => d3.min(s, (d) => d[0])),
      d3.max(series, (s) => d3.max(s, (d) => d[1])),
    ])
    .range([height, 0]);

  const colorScale = d3
    .scaleOrdinal()
    .domain(regionNames)
    .range(["#3b82f6", "#f59e0b", "#10b981", "#8b5cf6"]);

  const area = d3
    .area()
    .x((d) => x(d.data.year))
    .y0((d) => y(d[0]))
    .y1((d) => y(d[1]))
    .curve(d3.curveBasis);

  const tooltip = container
    .append("div")
    .attr("class", "chart-tooltip")
    .style("opacity", 0)
    .style("position", "absolute")
    .style("pointer-events", "none");

  const streams = g
    .selectAll(".stream")
    .data(series)
    .join("path")
    .attr("class", "stream")
    .attr("d", area)
    .attr("fill", (d) => colorScale(d.key))
    .attr("opacity", 0.7)
    .style("cursor", "pointer")
    .on("mouseenter", function (event, d) {
      d3.select(this).transition().duration(150).attr("opacity", 1);
    })
    .on("mouseleave", function () {
      d3.select(this).transition().duration(150).attr("opacity", 0.7);
    });

  const hoverLine = g
    .append("line")
    .attr("class", "hover-line")
    .attr("y1", 0)
    .attr("y2", height)
    .attr("stroke", "#fff")
    .attr("stroke-width", 2)
    .attr("opacity", 0);

    const yearsArray = regionalData.value.map((d) => +d.year);
    const bisectYear = d3.bisector((d) => d).left;
  const overlay = g
  .append("rect")
  .attr("width", width)
  .attr("height", height)
  .attr("fill", "transparent")
  .style("pointer-events", "all")
  .on("mousemove", function (event) {
    const [mouseX] = d3.pointer(event);
    const x0 = x.invert(mouseX);

    let idx = bisectYear(yearsArray, x0);
    if (idx >= yearsArray.length) idx = yearsArray.length - 1;
    if (idx < 0) idx = 0;

    const yearData = regionalData.value[idx];
    const year = yearData.year;

    emit("hover-year", year);

    hoverLine
      .attr("x1", x(year))
      .attr("x2", x(year))
      .attr("opacity", 0.5);

    const total = regionNames.reduce((sum, r) => sum + yearData[r], 0);
    const tooltipContent = regionNames
      .map((region) => {
        const val = yearData[region];
        const share = total > 0 ? (val / total) * 100 : 0;
        return `<strong>${region}:</strong> ${val.toFixed(
          0
        )} bu/acre (${share.toFixed(1)}%)`;
      })
      .join("<br/>");

    const rect = containerRef.value.getBoundingClientRect();

    tooltip
      .style("opacity", 1)
      .html(`<strong>Year: ${year}</strong><br/>${tooltipContent}`)
      .style("left", `${event.clientX - rect.left + 10}px`)
      .style("top", `${event.clientY - rect.top - 10}px`);
  })
  .on("mouseleave", function () {
    emit("hover-year", null);
    hoverLine.attr("opacity", 0);
    tooltip.style("opacity", 0);
  });

  const xAxis = d3.axisBottom(x).tickFormat(d3.format("d"));
  const yAxis = d3.axisLeft(y).ticks(5);

  g.append("g")
    .attr("transform", `translate(0,${height})`)
    .call(xAxis)
    .attr("color", "#94a3b8")
    .selectAll("text")
    .attr("font-size", "12px");

  g.append("g")
    .call(yAxis)
    .attr("color", "#94a3b8")
    .selectAll("text")
    .attr("font-size", "12px");

  g.append("text")
    .attr("x", width / 2)
    .attr("y", height + 40)
    .attr("text-anchor", "middle")
    .attr("fill", "#475569")
    .attr("font-size", "14px")
    .text("Year");

  g.append("text")
    .attr("transform", "rotate(-90)")
    .attr("x", -height / 2)
    .attr("y", -45)
    .attr("text-anchor", "middle")
    .attr("fill", "#475569")
    .attr("font-size", "14px")
    .text("Total Yield (bu/acre)");

  const legend = svg
    .append("g")
    .attr("transform", `translate(${width + margin.left + 10},${margin.top})`);

  regionNames.forEach((region, i) => {
    const legendRow = legend
      .append("g")
      .attr("transform", `translate(0,${i * 25})`);

    legendRow
      .append("rect")
      .attr("width", 18)
      .attr("height", 18)
      .attr("fill", colorScale(region))
      .attr("opacity", 0.7);

    legendRow
      .append("text")
      .attr("x", 24)
      .attr("y", 13)
      .attr("fill", "#1e293b")
      .attr("font-size", "13px")
      .text(region);
  });

  if (props.hoveredYear) {
    hoverLine
      .attr("x1", x(props.hoveredYear))
      .attr("x2", x(props.hoveredYear))
      .attr("opacity", 0.5);
  }
}

onMounted(render);
watch(() => [props.data, props.hoveredYear], render, { deep: true });
</script>

<template>
  <div ref="containerRef" class="themeriver-container"></div>
</template>

<style scoped>
.themeriver-container {
  width: 100%;
  min-height: 400px;
  position: relative;
}

:deep(.chart-tooltip) {
  background: rgba(255, 255, 255, 0.98);
  color: #1e293b;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.6;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid #3b82f6;
  backdrop-filter: blur(10px);
}

.stream {
  transition: opacity 150ms ease;
}
</style>
