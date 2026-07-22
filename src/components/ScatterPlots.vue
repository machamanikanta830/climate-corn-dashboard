<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from "vue";
import * as d3 from "d3";
import { regressionFromPairs } from "../utils/statistics";

const props = defineProps({
  data: { type: Array, required: true },
  tempMetric: { type: String, default: "F" },
  selectedState: { type: String, default: "ALL" },
  resetKey: { type: Number, default: 0 },
});

const emit = defineEmits(["select-state", "brush-selection"]);

const containerRef = ref(null);
const enableBrush = ref(false);
const margin = { top: 40, right: 20, bottom: 50, left: 60 };

function render() {
  if (!containerRef.value || !props.data.length) return;

  const container = d3.select(containerRef.value);
  container.selectAll("*").remove();

  const containerWidth = container.node().clientWidth || 800;
  const stacked = containerWidth < 820;
  const plotWidth = stacked ? containerWidth : (containerWidth - 60) / 2;
  const plotHeight = stacked ? 350 : 400;
  const fullHeight = stacked
    ? plotHeight * 2 + margin.top + margin.bottom + 60
    : plotHeight + margin.top + margin.bottom;

  const svg = container
    .append("svg")
    .attr("width", "100%")
    .attr("height", fullHeight)
    .attr("role", "img")
    .attr(
      "aria-label",
      "Two scatterplots showing corn yield against temperature and precipitation"
    );

  const innerWidth = plotWidth - margin.left - margin.right;
  const innerHeight = plotHeight - margin.top - margin.bottom;

  const tooltip = container
    .append("div")
    .attr("class", "scatter-tooltip-shared")
    .style("position", "absolute")
    .style("background", "rgba(255, 255, 255, 0.98)")
    .style("color", "#18332b")
    .style("padding", "10px 14px")
    .style("border-radius", "6px")
    .style("font-size", "13px")
    .style("pointer-events", "none")
    .style("opacity", 0)
    .style("z-index", 10000)
    .style("box-shadow", "0 4px 12px rgba(0, 0, 0, 0.15)")
    .style("border", "1px solid rgba(59, 130, 246, 0.3)");

  const tempAccessor = (d) =>
    props.tempMetric === "C" ? ((d.TAVG - 32) * 5) / 9 : d.TAVG;

  const g1 = svg
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  const x1 = d3
    .scaleLinear()
    .domain(d3.extent(props.data, tempAccessor))
    .nice()
    .range([0, innerWidth]);

  const y1 = d3
    .scaleLinear()
    .domain(d3.extent(props.data, (d) => d.Yield_bu_acre))
    .nice()
    .range([innerHeight, 0]);

  g1.append("g")
    .attr("transform", `translate(0,${innerHeight})`)
    .call(d3.axisBottom(x1))
    .selectAll("text")
    .attr("fill", "#5f6f68");

  g1.append("g")
    .call(d3.axisLeft(y1))
    .selectAll("text")
    .attr("fill", "#5f6f68");

  g1.selectAll(".domain, .tick line").attr("stroke", "#c9c4b6");

  g1.append("text")
    .attr("x", innerWidth / 2)
    .attr("y", innerHeight + 40)
    .attr("text-anchor", "middle")
    .attr("fill", "#18332b")
    .attr("font-size", "12px")
    .attr("font-weight", "600")
    .text(`Temperature (°${props.tempMetric})`);

  g1.append("text")
    .attr("transform", "rotate(-90)")
    .attr("y", -45)
    .attr("x", -innerHeight / 2)
    .attr("text-anchor", "middle")
    .attr("fill", "#18332b")
    .attr("font-size", "12px")
    .attr("font-weight", "600")
    .text("Yield (bu/acre)");

  const regression1 = regressionFromPairs(
    props.data.map((d) => [tempAccessor(d), d.Yield_bu_acre])
  );

  g1.append("line")
    .attr("x1", x1(d3.min(props.data, tempAccessor)))
    .attr(
      "y1",
      y1(
        regression1.slope * d3.min(props.data, tempAccessor) +
          regression1.intercept
      )
    )
    .attr("x2", x1(d3.max(props.data, tempAccessor)))
    .attr(
      "y2",
      y1(
        regression1.slope * d3.max(props.data, tempAccessor) +
          regression1.intercept
      )
    )
    .attr("stroke", "#b7653b")
    .attr("stroke-width", 2)
    .attr("stroke-dasharray", "5,5")
    .attr("opacity", 0.6);

  g1.append("text")
    .attr("x", innerWidth - 10)
    .attr("y", 15)
    .attr("text-anchor", "end")
    .attr("fill", "#b7653b")
    .attr("font-size", "12px")
    .attr("font-weight", "600")
    .text(`r = ${regression1.r.toFixed(3)}`);

  const g2 = svg
    .append("g")
    .attr(
      "transform",
      stacked
        ? `translate(${margin.left},${plotHeight + margin.top + 50})`
        : `translate(${plotWidth + 30 + margin.left},${margin.top})`
    );

  const x2 = d3
    .scaleLinear()
    .domain(d3.extent(props.data, (d) => d.PRCP))
    .nice()
    .range([0, innerWidth]);

  const y2 = d3
    .scaleLinear()
    .domain(d3.extent(props.data, (d) => d.Yield_bu_acre))
    .nice()
    .range([innerHeight, 0]);

  g2.append("g")
    .attr("transform", `translate(0,${innerHeight})`)
    .call(d3.axisBottom(x2))
    .selectAll("text")
    .attr("fill", "#5f6f68");

  g2.append("g")
    .call(d3.axisLeft(y2))
    .selectAll("text")
    .attr("fill", "#5f6f68");

  g2.selectAll(".domain, .tick line").attr("stroke", "#c9c4b6");

  g2.append("text")
    .attr("x", innerWidth / 2)
    .attr("y", innerHeight + 40)
    .attr("text-anchor", "middle")
    .attr("fill", "#18332b")
    .attr("font-size", "12px")
    .attr("font-weight", "600")
    .text("Precipitation (inches)");

  g2.append("text")
    .attr("transform", "rotate(-90)")
    .attr("y", -45)
    .attr("x", -innerHeight / 2)
    .attr("text-anchor", "middle")
    .attr("fill", "#18332b")
    .attr("font-size", "12px")
    .attr("font-weight", "600")
    .text("Yield (bu/acre)");

  const regression2 = regressionFromPairs(
    props.data.map((d) => [d.PRCP, d.Yield_bu_acre])
  );

  g2.append("line")
    .attr("x1", x2(d3.min(props.data, (d) => d.PRCP)))
    .attr(
      "y1",
      y2(
        regression2.slope * d3.min(props.data, (d) => d.PRCP) +
          regression2.intercept
      )
    )
    .attr("x2", x2(d3.max(props.data, (d) => d.PRCP)))
    .attr(
      "y2",
      y2(
        regression2.slope * d3.max(props.data, (d) => d.PRCP) +
          regression2.intercept
      )
    )
    .attr("stroke", "#4f7475")
    .attr("stroke-width", 2)
    .attr("stroke-dasharray", "5,5")
    .attr("opacity", 0.6);

  g2.append("text")
    .attr("x", innerWidth - 10)
    .attr("y", 15)
    .attr("text-anchor", "end")
    .attr("fill", "#4f7475")
    .attr("font-size", "12px")
    .attr("font-weight", "600")
    .text(`r = ${regression2.r.toFixed(3)}`);

  const points1 = g1
    .selectAll(".point1")
    .data(props.data)
    .join("circle")
    .attr("class", "point1")
    .attr("cx", (d) => x1(tempAccessor(d)))
    .attr("cy", (d) => y1(d.Yield_bu_acre))
    .attr("r", (d) =>
      props.selectedState !== "ALL" && d.State === props.selectedState ? 7 : 4
    )
    .attr("fill", "#b7653b")
    .attr("opacity", (d) => {
      if (props.selectedState === "ALL") return 0.6;
      return d.State === props.selectedState ? 1 : 0.15;
    })
    .attr("stroke", "#fffdf7")
    .attr("stroke-width", 1)
    .attr("cursor", "pointer");

  const points2 = g2
    .selectAll(".point2")
    .data(props.data)
    .join("circle")
    .attr("class", "point2")
    .attr("cx", (d) => x2(d.PRCP))
    .attr("cy", (d) => y2(d.Yield_bu_acre))
    .attr("r", (d) =>
      props.selectedState !== "ALL" && d.State === props.selectedState ? 7 : 4
    )
    .attr("fill", "#4f7475")
    .attr("opacity", (d) => {
      if (props.selectedState === "ALL") return 0.6;
      return d.State === props.selectedState ? 1 : 0.15;
    })
    .attr("stroke", "#fffdf7")
    .attr("stroke-width", 1)
    .attr("cursor", "pointer");

  if (!enableBrush.value) {
    [points1, points2].forEach((points) => {
      points
        .on("mouseover", function (event, d) {
          container
            .selectAll(".point1, .point2")
            .attr("r", (dd) =>
              dd._id === d._id
                ? 10
                : props.selectedState !== "ALL" &&
                  dd.State === props.selectedState
                ? 7
                : 4
            )
            .attr("opacity", (dd) =>
              dd._id === d._id
                ? 1
                : props.selectedState !== "ALL"
                ? dd.State === props.selectedState
                  ? 1
                  : 0.15
                : 0.3
            );

          const [mx, my] = d3.pointer(event, container.node());

          tooltip
            .style("opacity", 1)
            .html(
              `
              <div style="font-weight: 700; color: #18332b; margin-bottom: 6px; border-bottom: 2px solid #e3aa35; padding-bottom: 4px;">
                ${d.State} (${d.Year})
              </div>
              <div style="color: #b7653b; margin: 4px 0;">
                <strong>Temp:</strong> ${tempAccessor(d).toFixed(1)}°${
                props.tempMetric
              }
              </div>
              <div style="color: #4f7475; margin: 4px 0;">
                <strong>Precip:</strong> ${d.PRCP.toFixed(1)} in
              </div>
              <div style="color: #2f6b4f; margin: 4px 0;">
                <strong>Yield:</strong> ${d.Yield_bu_acre.toFixed(1)} bu/acre
              </div>
            `
            )
            .style("left", mx + 15 + "px")
            .style("top", my - 40 + "px");
        })
        .on("mousemove", function (event) {
          const [mx, my] = d3.pointer(event, container.node());
          tooltip.style("left", mx + 15 + "px").style("top", my - 40 + "px");
        })
        .on("mouseout", function () {
          container
            .selectAll(".point1, .point2")
            .attr("r", (dd) =>
              props.selectedState !== "ALL" && dd.State === props.selectedState
                ? 7
                : 4
            )
            .attr("opacity", (dd) => {
              if (props.selectedState === "ALL") return 0.6;
              return dd.State === props.selectedState ? 1 : 0.15;
            });

          tooltip.style("opacity", 0);
        })
        .on("click", function (event, d) {
          event.stopPropagation();
          emit("select-state", d.State);
        });
    });
  } else {
    const x1Scale = x1;
    const x2Scale = x2;

    let brush1, brush2;

    function resetOpacities() {
      points1.attr("opacity", (d) => {
        if (props.selectedState === "ALL") return 0.6;
        return d.State === props.selectedState ? 1 : 0.15;
      });
      points2.attr("opacity", (d) => {
        if (props.selectedState === "ALL") return 0.6;
        return d.State === props.selectedState ? 1 : 0.15;
      });
    }

    function handleBrush(event, isFirst) {
      const selection = event.selection;

      if (!selection) {
        emit("brush-selection", []);
        resetOpacities();
        return;
      }

      const [[x0, y0], [x1b, y1b]] = selection;
      const selectedIds = [];

      if (isFirst) {
        props.data.forEach((d) => {
          const px = x1Scale(tempAccessor(d));
          const py = y1(d.Yield_bu_acre);
          if (px >= x0 && px <= x1b && py >= y0 && py <= y1b) {
            selectedIds.push(d._id);
          }
        });
        g2.select(".brush").call(brush2.move, null);
      } else {
        props.data.forEach((d) => {
          const px = x2Scale(d.PRCP);
          const py = y2(d.Yield_bu_acre);
          if (px >= x0 && px <= x1b && py >= y0 && py <= y1b) {
            selectedIds.push(d._id);
          }
        });
        g1.select(".brush").call(brush1.move, null);
      }

      emit("brush-selection", selectedIds);

      points1.attr("opacity", (d) => (selectedIds.includes(d._id) ? 1 : 0.15));
      points2.attr("opacity", (d) => (selectedIds.includes(d._id) ? 1 : 0.15));
    }

    brush1 = d3
      .brush()
      .extent([
        [0, 0],
        [innerWidth, innerHeight],
      ])
      .on("end", (event) => handleBrush(event, true));

    brush2 = d3
      .brush()
      .extent([
        [0, 0],
        [innerWidth, innerHeight],
      ])
      .on("end", (event) => handleBrush(event, false));

    g1.append("g").attr("class", "brush").call(brush1);
    g2.append("g").attr("class", "brush").call(brush2);
  }
}

watch(enableBrush, (newVal) => {
  if (!newVal) {
    emit("brush-selection", []);
  }
});

watch(
  [
    () => props.data,
    () => props.tempMetric,
    () => props.selectedState,
    enableBrush,
  ],
  render,
  { deep: true }
);

onMounted(render);

onBeforeUnmount(() => {
  if (containerRef.value) {
    d3.select(containerRef.value).selectAll("*").remove();
  }
});

watch(
  () => props.resetKey,
  () => {
    emit("brush-selection", []);
    render();
  }
);
</script>

<template>
  <div>
    <div
      style="
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
      "
    >
      <label
        style="
          display: flex;
          align-items: center;
          gap: 0.5rem;
          cursor: pointer;
          font-size: 0.95rem;
          color: #5f6f68;
        "
      >
        <input type="checkbox" v-model="enableBrush" style="cursor: pointer" />
        <span style="font-weight: 600">
          Enable rectangular selection
        </span>
      </label>
      <span style="font-size: 0.85rem; color: #5f6f68; font-style: italic">
        {{
          enableBrush
            ? "Drag inside either plot to highlight the same records below"
            : "Hover to see details, click to select state"
        }}
      </span>
    </div>
    <div ref="containerRef" class="scatter-chart"></div>
  </div>
</template>

<style scoped>
.scatter-chart {
  position: relative;
  width: 100%;
  min-width: 300px;
}
</style>
