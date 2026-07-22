<script setup>
import { ref, watch, onMounted } from "vue";
import * as d3 from "d3";
import * as topojson from "topojson-client";

const props = defineProps({
  data: { type: Array, required: true },
  selectedState: { type: String, default: "ALL" },
  hoveredState: { type: String, default: null },
  tempMetric: { type: String, default: "F" },
});

const emit = defineEmits(["select-state", "hover-state"]);

const containerRef = ref(null);
const colorBy = ref("Yield");
const margin = { top: 10, right: 10, bottom: 60, left: 10 };

const usStates = ref(null);

const stateNames = {
  "01": "ALABAMA",
  "02": "ALASKA",
  "04": "ARIZONA",
  "05": "ARKANSAS",
  "06": "CALIFORNIA",
  "08": "COLORADO",
  "09": "CONNECTICUT",
  15: "HAWAII",
  10: "DELAWARE",
  12: "FLORIDA",
  13: "GEORGIA",
  16: "IDAHO",
  17: "ILLINOIS",
  18: "INDIANA",
  19: "IOWA",
  20: "KANSAS",
  21: "KENTUCKY",
  22: "LOUISIANA",
  24: "MARYLAND",
  25: "MASSACHUSETTS",
  26: "MICHIGAN",
  27: "MINNESOTA",
  28: "MISSISSIPPI",
  29: "MISSOURI",
  30: "MONTANA",
  31: "NEBRASKA",
  32: "NEVADA",
  33: "NEW HAMPSHIRE",
  34: "NEW JERSEY",
  35: "NEW MEXICO",
  36: "NEW YORK",
  37: "NORTH CAROLINA",
  38: "NORTH DAKOTA",
  39: "OHIO",
  40: "OKLAHOMA",
  41: "OREGON",
  42: "PENNSYLVANIA",
  44: "RHODE ISLAND",
  45: "SOUTH CAROLINA",
  46: "SOUTH DAKOTA",
  47: "TENNESSEE",
  48: "TEXAS",
  49: "UTAH",
  50: "VERMONT",
  51: "VIRGINIA",
  53: "WASHINGTON",
  54: "WEST VIRGINIA",
  55: "WISCONSIN",
  56: "WYOMING",
};

function render() {
  if (!containerRef.value || !props.data.length || !usStates.value) return;

  const container = d3.select(containerRef.value);
  container.selectAll("svg").remove();
  container.selectAll(".map-tooltip").remove();

  const containerWidth = container.node().clientWidth;
  const containerHeight = 450;

  const width = containerWidth - margin.left - margin.right;
  const height = containerHeight - margin.top - margin.bottom;

  const svg = container
    .append("svg")
    .attr("width", "100%")
    .attr("height", containerHeight)
    .attr("viewBox", `0 0 ${containerWidth} ${containerHeight}`)
    .attr("preserveAspectRatio", "xMidYMid meet");

  const g = svg
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  const tempAccessor = (d) =>
    props.tempMetric === "C" ? ((d.TAVG - 32) * 5) / 9 : d.TAVG;

  const stateData = d3.rollup(
    props.data,
    (v) => ({
      yield: d3.mean(v, (d) => d.Yield_bu_acre),
      temp: d3.mean(v, tempAccessor),
      precip: d3.mean(v, (d) => d.PRCP),
    }),
    (d) => d.State
  );

  let colorScale, values, label;

  if (colorBy.value === "Yield") {
    values = Array.from(stateData.values()).map((d) => d.yield);
    colorScale = d3
      .scaleSequential(d3.interpolateBlues)
      .domain(d3.extent(values));
    label = "Average Corn Yield (bu/acre)";
  } else if (colorBy.value === "Temp") {
    values = Array.from(stateData.values()).map((d) => d.temp);
    colorScale = d3
      .scaleSequential(d3.interpolateReds)
      .domain(d3.extent(values));
    label = `Average Temperature (°${props.tempMetric})`;
  } else {
    values = Array.from(stateData.values()).map((d) => d.precip);
    colorScale = d3
      .scaleSequential(d3.interpolateGreens)
      .domain(d3.extent(values));
    label = "Average Precipitation (inches)";
  }

  const states = usStates.value;

  const projection = d3.geoAlbersUsa().fitSize([width, height - 40], states);

  const currentScale = projection.scale();
  const currentTranslate = projection.translate();

  projection
    .scale(currentScale * 1.15)
    .translate([currentTranslate[0], currentTranslate[1] + 5]);

  const path = d3.geoPath().projection(projection);

  const tooltip = container
    .append("div")
    .attr("class", "map-tooltip")
    .style("position", "absolute")
    .style("background", "rgba(255, 255, 255, 0.98)")
    .style("color", "#1e293b")
    .style("padding", "10px 14px")
    .style("border-radius", "8px")
    .style("font-size", "13px")
    .style("pointer-events", "none")
    .style("opacity", 0)
    .style("z-index", 10000)
    .style("box-shadow", "0 6px 16px rgba(0, 0, 0, 0.2)")
    .style("border", "2px solid rgba(59, 130, 246, 0.5)")
    .style("font-weight", "500");

  g.selectAll("path")
    .data(states.features)
    .join("path")
    .attr("d", path)
    .attr("fill", (d) => {
      const stateName = stateNames[d.id];
      const data = stateData.get(stateName);
      if (!data) return "#e5e7eb";

      if (colorBy.value === "Yield") return colorScale(data.yield);
      if (colorBy.value === "Temp") return colorScale(data.temp);
      return colorScale(data.precip);
    })
    .attr("stroke", (d) => {
      const stateName = stateNames[d.id];

      if (props.selectedState !== "ALL" && stateName === props.selectedState) {
        return "#ef4444";
      }
      if (props.hoveredState && stateName === props.hoveredState) {
        return "#3b82f6";
      }
      return "#fff";
    })
    .attr("stroke-width", (d) => {
      const stateName = stateNames[d.id];

      if (props.selectedState !== "ALL" && stateName === props.selectedState) {
        return 3;
      }
      if (props.hoveredState && stateName === props.hoveredState) {
        return 2;
      }
      return 0.5;
    })
    .attr("cursor", "pointer")
    .attr("class", "state-path")
    .on("mouseenter", function (event, d) {
      const stateName = stateNames[d.id];
      if (!stateName) return;

      const data = stateData.get(stateName);

      d3.select(this).attr("stroke", "#3b82f6").attr("stroke-width", 2);

      const containerRect = containerRef.value.getBoundingClientRect();

      if (!data) {
        tooltip
          .style("opacity", 1)
          .html(
            `
        <div style="font-weight: 700; margin-bottom: 6px; border-bottom: 2px solid #3b82f6; padding-bottom: 4px;">
          ${stateName}
        </div>
        <div>No corn yield data available for this state.</div>
      `
          )
          .style("left", event.clientX - containerRect.left + 15 + "px")
          .style("top", event.clientY - containerRect.top - 10 + "px");

        emit("hover-state", stateName);
        return;
      }

      tooltip
        .style("opacity", 1)
        .html(
          `
      <div style="font-weight: 700; margin-bottom: 6px; border-bottom: 2px solid #3b82f6; padding-bottom: 4px;">
        ${stateName}
      </div>
      <div style="margin: 4px 0;">Avg Yield: <strong>${data.yield.toFixed(
        1
      )} bu/acre</strong></div>
      <div style="margin: 4px 0;">Avg Temp: <strong>${data.temp.toFixed(1)}°${
            props.tempMetric
          }</strong></div>
      <div style="margin: 4px 0;">Avg Precip: <strong>${data.precip.toFixed(
        1
      )} in</strong></div>
    `
        )
        .style("left", event.clientX - containerRect.left + 15 + "px")
        .style("top", event.clientY - containerRect.top - 10 + "px");

      emit("hover-state", stateName);
    })
    .on("mousemove", function (event) {
      const containerRect = containerRef.value.getBoundingClientRect();
      tooltip
        .style("left", event.clientX - containerRect.left + 15 + "px")
        .style("top", event.clientY - containerRect.top - 10 + "px");
    })
    .on("mouseleave", function (event, d) {
      const stateName = stateNames[d.id];

      if (props.selectedState !== stateName) {
        d3.select(this).attr("stroke", "#fff").attr("stroke-width", 0.5);
      }

      tooltip.style("opacity", 0);
      emit("hover-state", null);
    })
    .on("click", function (event, d) {
      event.stopPropagation();
      const stateName = stateNames[d.id];
      if (stateData.has(stateName)) {
        emit("select-state", stateName);
      }
    });

  const legendWidth = 300;
  const legendHeight = 10;
  const legendX = (width - legendWidth) / 2;
  const legendY = height - 30;

  const legendScale = d3
    .scaleLinear()
    .domain(colorScale.domain())
    .range([0, legendWidth]);

  const legendAxis = d3
    .axisBottom(legendScale)
    .ticks(5)
    .tickFormat((d) => d.toFixed(0));

  const defs = svg.append("defs");
  const legendGradient = defs
    .append("linearGradient")
    .attr("id", "legend-gradient-" + colorBy.value)
    .attr("x1", "0%")
    .attr("x2", "100%");

  legendGradient
    .selectAll("stop")
    .data(d3.range(0, 1.1, 0.1))
    .join("stop")
    .attr("offset", (d) => d * 100 + "%")
    .attr("stop-color", (d) => colorScale(legendScale.invert(d * legendWidth)));

  const legendGroup = g
    .append("g")
    .attr("transform", `translate(${legendX},${legendY})`);

  legendGroup
    .append("rect")
    .attr("width", legendWidth)
    .attr("height", legendHeight)
    .style("fill", `url(#legend-gradient-${colorBy.value})`);

  legendGroup
    .append("g")
    .attr("transform", `translate(0,${legendHeight})`)
    .call(legendAxis)
    .selectAll("text")
    .attr("fill", "#475569")
    .attr("font-size", "11px");

  legendGroup.selectAll(".domain, .tick line").attr("stroke", "#cbd5e1");

  legendGroup
    .append("text")
    .attr("x", legendWidth / 2)
    .attr("y", -5)
    .attr("text-anchor", "middle")
    .attr("fill", "#1e293b")
    .attr("font-size", "12px")
    .attr("font-weight", "600")
    .text(label);
}

watch(
  [
    () => props.data,
    () => props.selectedState,
    () => props.hoveredState,
    () => props.tempMetric,
    colorBy,
  ],
  render,
  { deep: true }
);

onMounted(async () => {
  const us = await d3.json(
    "https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json"
  );
  usStates.value = topojson.feature(us, us.objects.states);
  render();
});
</script>

<template>
  <div>
    <!-- Color By Options -->
    <div
      style="
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-bottom: 1rem;
      "
    >
      <label
        style="
          display: flex;
          align-items: center;
          gap: 0.5rem;
          cursor: pointer;
          font-weight: 600;
          color: #475569;
        "
      >
        <input
          type="radio"
          v-model="colorBy"
          value="Yield"
          name="mapColor"
          style="cursor: pointer"
        />
        <span style="color: #2563eb">Yield</span>
      </label>
      <label
        style="
          display: flex;
          align-items: center;
          gap: 0.5rem;
          cursor: pointer;
          font-weight: 600;
          color: #475569;
        "
      >
        <input
          type="radio"
          v-model="colorBy"
          value="Temp"
          name="mapColor"
          style="cursor: pointer"
        />
        <span style="color: #ef4444">Temperature</span>
      </label>
      <label
        style="
          display: flex;
          align-items: center;
          gap: 0.5rem;
          cursor: pointer;
          font-weight: 600;
          color: #475569;
        "
      >
        <input
          type="radio"
          v-model="colorBy"
          value="Precip"
          name="mapColor"
          style="cursor: pointer"
        />
        <span style="color: #10b981">Precipitation</span>
      </label>
    </div>

    <div
      ref="containerRef"
      style="position: relative; width: 100%; height: 450px"
    ></div>
  </div>
</template>

<style scoped>
.state-path {
  transition: stroke 0.2s, stroke-width 0.2s;
}
</style>
