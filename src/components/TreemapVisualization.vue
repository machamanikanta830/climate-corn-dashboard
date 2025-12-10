<script setup>
import { ref, watch, onMounted, computed } from "vue";
import * as d3 from "d3";

const props = defineProps({
  data: { type: Array, required: true },
  selectedState: { type: String, default: "ALL" },
});

const emit = defineEmits(["select-state"]);

const containerRef = ref(null);

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
  const upper = state.toUpperCase();
  for (const [region, list] of Object.entries(regions)) {
    if (list.includes(upper)) return region;
  }
  return "Other";
}

const regionOrder = ["Midwest", "South", "West", "Northeast", "Other"];

const aggregatedData = computed(() => {
  if (!props.data || !props.data.length) return [];

  const byState = d3.rollups(
    props.data,
    (v) => d3.sum(v, (d) => d.Yield_bu_acre),
    (d) => d.State
  );

  return byState
    .map(([state, totalYield]) => ({
      state,
      totalYield,
      region: getRegion(state),
    }))
    .sort((a, b) => b.totalYield - a.totalYield)
    .slice(0, 20);
});

function render() {
  if (!containerRef.value || !aggregatedData.value.length) return;

  const container = d3.select(containerRef.value);
  container.selectAll("*").remove();

  const width = container.node().clientWidth;
  const height = 500;

  const svg = container
    .append("svg")
    .attr("width", "100%")
    .attr("height", height);

  const root = d3
    .hierarchy({ children: aggregatedData.value })
    .sum((d) => d.totalYield)
    .sort((a, b) => b.value - a.value);

  d3
    .treemap()
    .size([width, height - 40])
    .padding(2)
    .round(true)(root);

  const colorScale = d3
    .scaleOrdinal()
    .domain(regionOrder)
    .range(["#3b82f6", "#f59e0b", "#10b981", "#8b5cf6", "#6b7280"]);

  const tooltip = container
    .append("div")
    .style("position", "absolute")
    .style("background", "rgba(255, 255, 255, 0.98)")
    .style("color", "#1e293b")
    .style("padding", "8px 12px")
    .style("border-radius", "6px")
    .style("font-size", "12px")
    .style("pointer-events", "none")
    .style("opacity", 0)
    .style("z-index", 1000)
    .style("box-shadow", "0 4px 12px rgba(0, 0, 0, 0.15)")
    .style("border", "1px solid rgba(59, 130, 246, 0.3)");

  const cells = svg
    .selectAll("g.cell")
    .data(root.leaves())
    .join("g")
    .attr("class", "cell")
    .attr("transform", (d) => `translate(${d.x0},${d.y0 + 40})`);

  cells
    .append("rect")
    .attr("width", (d) => d.x1 - d.x0)
    .attr("height", (d) => d.y1 - d.y0)
    .attr("fill", (d) => colorScale(d.data.region))
    .attr("stroke", (d) => {
      if (
        props.selectedState !== "ALL" &&
        d.data.state === props.selectedState
      ) {
        return "#ef4444";
      }
      return "#ffffff";
    })
    .attr("stroke-width", (d) => {
      if (
        props.selectedState !== "ALL" &&
        d.data.state === props.selectedState
      ) {
        return 3;
      }
      return 1;
    })
    .attr("cursor", "pointer")
    .on("mouseenter", function (event, d) {
      d3.select(this).attr("stroke", "#3b82f6").attr("stroke-width", 2);

      const rect = containerRef.value.getBoundingClientRect();
      tooltip
        .style("opacity", 1)
        .html(
          `
          <div style="font-weight: 600; margin-bottom: 4px;">${
            d.data.state
          }</div>
          <div>Region: <strong>${d.data.region}</strong></div>
          <div>Total Yield: <strong>${d.data.totalYield.toFixed(
            0
          )} bu/acre</strong></div>
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
      if (props.selectedState === d.data.state) {
        d3.select(this).attr("stroke", "#ef4444").attr("stroke-width", 3);
      } else {
        d3.select(this).attr("stroke", "#ffffff").attr("stroke-width", 1);
      }
      tooltip.style("opacity", 0);
    })
    .on("click", function (event, d) {
      event.stopPropagation();
      emit("select-state", d.data.state);
    });

  cells
    .append("text")
    .attr("x", 4)
    .attr("y", 16)
    .attr("fill", "#f9fafb")
    .attr("font-size", (d) => {
      const w = d.x1 - d.x0;
      const h = d.y1 - d.y0;
      const area = w * h;
      if (area > 5000) return "14px";
      if (area > 2000) return "12px";
      if (area > 1000) return "10px";
      return "8px";
    })
    .attr("font-weight", "600")
    .attr("pointer-events", "none")
    .text((d) => {
      const w = d.x1 - d.x0;
      if (w < 50) return "";
      return d.data.state;
    });

  cells
    .append("text")
    .attr("x", 4)
    .attr("y", 30)
    .attr("fill", "#e5e7eb")
    .attr("font-size", "10px")
    .attr("pointer-events", "none")
    .text((d) => {
      const w = d.x1 - d.x0;
      const h = d.y1 - d.y0;
      if (w < 70 || h < 40) return "";
      return d.data.totalYield.toFixed(0);
    });

  const legend = svg
    .append("g")
    .attr("class", "treemap-legend")
    .attr("transform", "translate(10,10)");

  regionOrder.forEach((region, i) => {
    const row = legend
      .append("g")
      .attr("transform", `translate(${i * 120}, 0)`);

    row
      .append("rect")
      .attr("width", 16)
      .attr("height", 16)
      .attr("fill", colorScale(region));

    row
      .append("text")
      .attr("x", 22)
      .attr("y", 12)
      .attr("fill", "#1e293b")
      .attr("font-size", 12)
      .text(region);
  });
}

watch([() => props.data, () => props.selectedState], render, { deep: true });
onMounted(render);
</script>

<template>
  <div
    ref="containerRef"
    style="position: relative; width: 100%; height: 500px"
  ></div>
</template>

<style scoped>
/* No additional styles needed */
</style>
