<script setup>
import { ref, watch, onMounted, computed } from "vue";
import * as d3 from "d3";

const props = defineProps({
  data: { type: Array, required: true },
  selectedState: { type: String, default: "ALL" },
  tempMetric: { type: String, default: "F" },
});

const emit = defineEmits(["select-state"]);

const containerRef = ref(null);
const rankBy = ref("Yield");

const rankedData = computed(() => {
  if (!props.data || props.data.length === 0) return { top: [], bottom: [] };

  const byState = d3.rollups(
    props.data,
    (v) => {
      const tempF = d3.mean(v, (d) => d.TAVG);
      const temp = props.tempMetric === "C" ? ((tempF - 32) * 5) / 9 : tempF;

      return {
        yield: d3.mean(v, (d) => d.Yield_bu_acre),
        temp,
        precip: d3.mean(v, (d) => d.PRCP),
      };
    },
    (d) => d.State
  );

  const stateArray = byState.map(([state, values]) => ({
    state,
    ...values,
  }));

  let sortKey = "yield";
  if (rankBy.value === "Temp") sortKey = "temp";
  if (rankBy.value === "Precip") sortKey = "precip";

  stateArray.sort((a, b) => b[sortKey] - a[sortKey]);

  return {
    top: stateArray.slice(0, 10),
    bottom: stateArray.slice(-10).reverse(),
  };
});

function render() {
  if (!containerRef.value || !rankedData.value) return;

  const container = d3.select(containerRef.value);
  container.selectAll("*").remove();

  const width = container.node().clientWidth;
  const height = 600;
  const margin = { top: 20, right: 30, bottom: 20, left: 150 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = (height - 60) / 2;

  const svg = container
    .append("svg")
    .attr("width", "100%")
    .attr("height", height);

  let valueAccessor, color, unit;
  if (rankBy.value === "Yield") {
    valueAccessor = (d) => d.yield;
    color = "#3b82f6";
    unit = "bu/acre";
  } else if (rankBy.value === "Temp") {
    valueAccessor = (d) => d.temp;
    color = "#ef4444";
    unit = `°${props.tempMetric}`;
  } else {
    valueAccessor = (d) => d.precip;
    color = "#10b981";
    unit = "inches";
  }

  const topG = svg
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  topG
    .append("text")
    .attr("x", innerWidth / 2)
    .attr("y", -5)
    .attr("text-anchor", "middle")
    .attr("fill", "#10b981")
    .attr("font-size", "16px")
    .attr("font-weight", "700")
    .text(`Top 10 - Highest ${rankBy.value}`);

  const xTop = d3
    .scaleLinear()
    .domain([0, d3.max(rankedData.value.top, valueAccessor)])
    .range([0, innerWidth]);

  const yTop = d3
    .scaleBand()
    .domain(rankedData.value.top.map((d) => d.state))
    .range([0, innerHeight])
    .padding(0.2);

  topG
    .selectAll(".bar-top")
    .data(rankedData.value.top)
    .join("rect")
    .attr("class", "bar-top")
    .attr("x", 0)
    .attr("y", (d) => yTop(d.state))
    .attr("width", (d) => xTop(valueAccessor(d)))
    .attr("height", yTop.bandwidth())
    .attr("fill", color)
    .attr("opacity", (d) =>
      props.selectedState !== "ALL" && d.state === props.selectedState ? 1 : 0.7
    )
    .attr("stroke", (d) =>
      props.selectedState === d.state ? "#ef4444" : "none"
    )
    .attr("stroke-width", 3)
    .attr("cursor", "pointer")
    .on("mouseenter", function () {
      d3.select(this).attr("opacity", 1);
    })
    .on("mouseleave", function (event, d) {
      d3.select(this).attr(
        "opacity",
        props.selectedState !== "ALL" && d.state === props.selectedState
          ? 1
          : 0.7
      );
    })
    .on("click", function (event, d) {
      event.stopPropagation();
      emit("select-state", d.state);
    });

  topG
    .selectAll(".label-top")
    .data(rankedData.value.top)
    .join("text")
    .attr("class", "label-top")
    .attr("x", -5)
    .attr("y", (d) => yTop(d.state) + yTop.bandwidth() / 2)
    .attr("text-anchor", "end")
    .attr("alignment-baseline", "middle")
    .attr("fill", "#1e293b")
    .attr("font-size", "12px")
    .attr("font-weight", "600")
    .text((d) => d.state);

  topG
    .selectAll(".value-top")
    .data(rankedData.value.top)
    .join("text")
    .attr("class", "value-top")
    .attr("x", (d) => {
      const w = xTop(valueAccessor(d));
      return w > innerWidth * 0.8 ? w - 5 : w + 5;
    })
    .attr("y", (d) => yTop(d.state) + yTop.bandwidth() / 2)
    .attr("text-anchor", (d) => {
      const w = xTop(valueAccessor(d));
      return w > innerWidth * 0.8 ? "end" : "start";
    })
    .attr("alignment-baseline", "middle")
    .attr("fill", "#1e293b")
    .attr("font-size", "11px")
    .attr("font-weight", "600")
    .text((d) => valueAccessor(d).toFixed(1) + " " + unit);

  const bottomG = svg
    .append("g")
    .attr(
      "transform",
      `translate(${margin.left},${margin.top + innerHeight + 40})`
    );

  bottomG
    .append("text")
    .attr("x", innerWidth / 2)
    .attr("y", -5)
    .attr("text-anchor", "middle")
    .attr("fill", "#ef4444")
    .attr("font-size", "16px")
    .attr("font-weight", "700")
    .text(`Bottom 10 - Lowest ${rankBy.value}`);

  const xBottom = d3
    .scaleLinear()
    .domain([0, d3.max(rankedData.value.bottom, valueAccessor)])
    .range([0, innerWidth]);

  const yBottom = d3
    .scaleBand()
    .domain(rankedData.value.bottom.map((d) => d.state))
    .range([0, innerHeight])
    .padding(0.2);

  bottomG
    .selectAll(".bar-bottom")
    .data(rankedData.value.bottom)
    .join("rect")
    .attr("class", "bar-bottom")
    .attr("x", 0)
    .attr("y", (d) => yBottom(d.state))
    .attr("width", (d) => xBottom(valueAccessor(d)))
    .attr("height", yBottom.bandwidth())
    .attr("fill", color)
    .attr("opacity", (d) =>
      props.selectedState !== "ALL" && d.state === props.selectedState ? 1 : 0.7
    )
    .attr("stroke", (d) =>
      props.selectedState === d.state ? "#ef4444" : "none"
    )
    .attr("stroke-width", 3)
    .attr("cursor", "pointer")
    .on("mouseenter", function () {
      d3.select(this).attr("opacity", 1);
    })
    .on("mouseleave", function (event, d) {
      d3.select(this).attr(
        "opacity",
        props.selectedState !== "ALL" && d.state === props.selectedState
          ? 1
          : 0.7
      );
    })
    .on("click", function (event, d) {
      event.stopPropagation();
      emit("select-state", d.state);
    });

  bottomG
    .selectAll(".label-bottom")
    .data(rankedData.value.bottom)
    .join("text")
    .attr("class", "label-bottom")
    .attr("x", -5)
    .attr("y", (d) => yBottom(d.state) + yBottom.bandwidth() / 2)
    .attr("text-anchor", "end")
    .attr("alignment-baseline", "middle")
    .attr("fill", "#1e293b")
    .attr("font-size", "12px")
    .attr("font-weight", "600")
    .text((d) => d.state);

  bottomG
    .selectAll(".value-bottom")
    .data(rankedData.value.bottom)
    .join("text")
    .attr("class", "value-bottom")
    .attr("x", (d) => {
      const w = xBottom(valueAccessor(d));
      return w > innerWidth * 0.8 ? w - 5 : w + 5;
    })
    .attr("y", (d) => yBottom(d.state) + yBottom.bandwidth() / 2)
    .attr("text-anchor", (d) => {
      const w = xBottom(valueAccessor(d));
      return w > innerWidth * 0.8 ? "end" : "start";
    })
    .attr("alignment-baseline", "middle")
    .attr("fill", "#1e293b")
    .attr("font-size", "11px")
    .attr("font-weight", "600")
    .text((d) => valueAccessor(d).toFixed(1) + " " + unit);
}

watch([() => props.data, rankBy, () => props.selectedState], render, {
  deep: true,
});
onMounted(render);
</script>

<template>
  <div>
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
        "
      >
        <input type="radio" v-model="rankBy" value="Yield" name="rankBy" />
        <span style="color: #3b82f6">Yield</span>
      </label>
      <label
        style="
          display: flex;
          align-items: center;
          gap: 0.5rem;
          cursor: pointer;
          font-weight: 600;
        "
      >
        <input type="radio" v-model="rankBy" value="Temp" name="rankBy" />
        <span style="color: #ef4444">Temperature</span>
      </label>
      <label
        style="
          display: flex;
          align-items: center;
          gap: 0.5rem;
          cursor: pointer;
          font-weight: 600;
        "
      >
        <input type="radio" v-model="rankBy" value="Precip" name="rankBy" />
        <span style="color: #10b981">Precipitation</span>
      </label>
    </div>
    <div ref="containerRef" style="position: relative; width: 100%"></div>
  </div>
</template>

<style scoped>
/* No additional styles needed */
</style>
