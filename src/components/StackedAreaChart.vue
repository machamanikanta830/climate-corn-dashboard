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
const margin = { top: 30, right: 140, bottom: 50, left: 60 };

const aggregatedData = computed(() => {
  if (!props.data || props.data.length === 0) return [];

  const byYear = d3.rollups(
    props.data,
    (v) => ({
      avgTemp: d3.mean(v, (d) =>
        props.tempMetric === "C" ? ((d.TAVG - 32) * 5) / 9 : d.TAVG
      ),
      avgPrecip: d3.mean(v, (d) => d.PRCP),
    }),
    (d) => d.Year
  );

  return byYear
    .map(([year, values]) => ({
      year,
      temperature: values.avgTemp,
      precipitation: values.avgPrecip * 10,
    }))
    .sort((a, b) => a.year - b.year);
});

function render() {
  if (!containerRef.value || !aggregatedData.value.length) return;

  const container = d3.select(containerRef.value);
  container.selectAll("*").remove();

  const fullWidth = container.node().clientWidth;
  const fullHeight = 400;
  const width = fullWidth - margin.left - margin.right;
  const height = fullHeight - margin.top - margin.bottom;

  const svg = container
    .append("svg")
    .attr("width", "100%")
    .attr("height", fullHeight);

  const g = svg
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  const stack = d3
    .stack()
    .keys(["precipitation", "temperature"])
    .order(d3.stackOrderNone)
    .offset(d3.stackOffsetNone);

  const series = stack(aggregatedData.value);

  const x = d3
    .scaleLinear()
    .domain(d3.extent(aggregatedData.value, (d) => d.year))
    .range([0, width]);

  const y = d3
    .scaleLinear()
    .domain([0, d3.max(series, (s) => d3.max(s, (d) => d[1]))])
    .nice()
    .range([height, 0]);

  const area = d3
    .area()
    .x((d) => x(d.data.year))
    .y0((d) => y(d[0]))
    .y1((d) => y(d[1]))
    .curve(d3.curveMonotoneX);

  const tooltip = container
    .append("div")
    .attr("class", "chart-tooltip")
    .style("opacity", 0)
    .style("position", "absolute")
    .style("pointer-events", "none");

  series.forEach((s) => {
    const gradientId = `stacked-gradient-${s.key}`;

    const gradient = svg
      .append("defs")
      .append("linearGradient")
      .attr("id", gradientId)
      .attr("x1", "0%")
      .attr("x2", "0%")
      .attr("y1", "0%")
      .attr("y2", "100%");

    if (s.key === "temperature") {
      gradient
        .append("stop")
        .attr("offset", "0%")
        .attr("stop-color", "#ef4444")
        .attr("stop-opacity", 0.8);
      gradient
        .append("stop")
        .attr("offset", "100%")
        .attr("stop-color", "#ef4444")
        .attr("stop-opacity", 0.3);
    } else {
      gradient
        .append("stop")
        .attr("offset", "0%")
        .attr("stop-color", "#3b82f6")
        .attr("stop-opacity", 0.8);
      gradient
        .append("stop")
        .attr("offset", "100%")
        .attr("stop-color", "#3b82f6")
        .attr("stop-opacity", 0.3);
    }

    g.append("path")
      .datum(s)
      .attr("class", `area-${s.key}`)
      .attr("d", area)
      .attr("fill", `url(#${gradientId})`)
      .attr("opacity", 0.9);
  });

  const hoverLine = g
    .append("line")
    .attr("class", "hover-line")
    .attr("y1", 0)
    .attr("y2", height)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 2)
    .attr("opacity", 0);

  g.append("rect")
    .attr("width", width)
    .attr("height", height)
    .attr("opacity", 0)
    .on("mousemove", (event) => {
      const [mouseX] = d3.pointer(event);
      const year = Math.round(x.invert(mouseX));

      emit("hover-year", year);

      hoverLine.attr("x1", x(year)).attr("x2", x(year)).attr("opacity", 0.5);

      const yearData = aggregatedData.value.find((d) => d.year === year);
      if (yearData) {
        tooltip
          .style("opacity", 1)
          .html(
            `
            <strong>Year: ${year}</strong><br/>
            <span style="color:#ef4444;">●</span> Temperature: <strong>${yearData.temperature.toFixed(
              1
            )}°${props.tempMetric}</strong><br/>
            <span style="color:#3b82f6;">●</span> Precipitation: <strong>${(
              yearData.precipitation / 10
            ).toFixed(2)} in</strong>
          `
          )
          .style(
            "left",
            event.pageX -
              container.node().getBoundingClientRect().left +
              10 +
              "px"
          )
          .style(
            "top",
            event.pageY -
              container.node().getBoundingClientRect().top -
              10 +
              "px"
          );
      }
    })
    .on("mouseleave", () => {
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
    .text("Normalized Climate Index");

  const legend = g
    .append("g")
    .attr("transform", `translate(${width + 20}, 20)`);

  const legendData = [
    {
      key: "temperature",
      label: `Temperature (°${props.tempMetric})`,
      color: "#ef4444",
    },
    { key: "precipitation", label: "Precipitation (×10)", color: "#3b82f6" },
  ];

  legendData.forEach((item, i) => {
    const row = legend.append("g").attr("transform", `translate(0,${i * 24})`);

    row
      .append("rect")
      .attr("width", 16)
      .attr("height", 16)
      .attr("fill", item.color)
      .attr("opacity", 0.7);

    row
      .append("text")
      .attr("x", 22)
      .attr("y", 12)
      .attr("fill", "#1e293b")
      .attr("font-size", 12)
      .text(item.label);
  });

  if (props.hoveredYear) {
    hoverLine
      .attr("x1", x(props.hoveredYear))
      .attr("x2", x(props.hoveredYear))
      .attr("opacity", 0.5);
  }
}

onMounted(render);
watch(() => [props.data, props.tempMetric, props.hoveredYear], render, {
  deep: true,
});
</script>

<template>
  <div ref="containerRef" class="stacked-area-container"></div>
</template>

<style scoped>
.stacked-area-container {
  width: 100%;
  min-height: 400px;
  position: relative;
}
</style>
