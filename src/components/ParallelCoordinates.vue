<script setup>
import { ref, watch, onMounted, computed } from "vue";
import * as d3 from "d3";

const props = defineProps({
  data: { type: Array, required: true },
  tempMetric: { type: String, default: "C" },
  selectedState: { type: String, default: "ALL" },
  brushedIds: { type: Array, default: () => [] },
});

const containerRef = ref(null);
const margin = { top: 30, right: 20, bottom: 10, left: 40 };

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

function tempAccessor(d) {
  return props.tempMetric === "C" ? d.TAVG_C : d.TAVG;
}

const displayData = computed(() => {
  if (!props.data || props.data.length === 0) return [];

  if (props.selectedState !== "ALL") {
    return props.data.filter((d) => d.State === props.selectedState);
  }

  const brushedSet = new Set(props.brushedIds);
  if (brushedSet.size > 0) {
    return props.data.filter((d) => brushedSet.has(d._id));
  }

  const byYearRegion = d3.rollups(
    props.data,
    (v) => ({
      Year: v[0].Year,
      temp: d3.mean(v, (d) => tempAccessor(d)),
      PRCP: d3.mean(v, (d) => d.PRCP),
      Yield_bu_acre: d3.mean(v, (d) => d.Yield_bu_acre),
      State: getRegion(v[0].State),
      _id: `${v[0].Year}-${getRegion(v[0].State)}`,
    }),
    (d) => d.Year,
    (d) => getRegion(d.State)
  );

  const regionalData = [];
  byYearRegion.forEach(([, regionsMap]) => {
    regionsMap.forEach(([, data]) => {
      regionalData.push(data);
    });
  });

  return regionalData;
});

function render() {
  if (
    !containerRef.value ||
    !displayData.value ||
    displayData.value.length === 0
  )
    return;

  const container = d3.select(containerRef.value);

  container.select("svg").remove();
  container.select(".pc-tooltip").remove();

  const tooltip = container
    .append("div")
    .attr("class", "pc-tooltip")
    .style("position", "absolute")
    .style("pointer-events", "none")
    .style("opacity", 0);

  const svg = container.append("svg").attr("width", "100%").attr("height", 300);

  const width = container.node().clientWidth - margin.left - margin.right;
  const height = 300 - margin.top - margin.bottom;

  const g = svg
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  const dimensions = [
    {
      key: "Year",
      label: "Year",
      scale: d3
        .scaleLinear()
        .domain(d3.extent(props.data, (d) => d.Year))
        .range([height, 0]),
    },
    {
      key: "temp",
      label: `Temp (${props.tempMetric === "C" ? "°C" : "°F"})`,
      scale: d3
        .scaleLinear()
        .domain(d3.extent(props.data, (d) => tempAccessor(d)))
        .range([height, 0]),
    },
    {
      key: "PRCP",
      label: "Precip (in)",
      scale: d3
        .scaleLinear()
        .domain(d3.extent(props.data, (d) => d.PRCP))
        .range([height, 0]),
    },
    {
      key: "Yield_bu_acre",
      label: "Yield (bu/acre)",
      scale: d3
        .scaleLinear()
        .domain(d3.extent(props.data, (d) => d.Yield_bu_acre))
        .range([height, 0]),
    },
  ];

  const x = d3
    .scalePoint()
    .domain(dimensions.map((d) => d.key))
    .range([0, width])
    .padding(0.5);

  const brushedSet = new Set(props.brushedIds);

  const line = d3
    .line()
    .defined((d) => d[1] != null)
    .x(([key]) => x(key))
    .y(([key, value]) => {
      const dim = dimensions.find((d) => d.key === key);
      return dim ? dim.scale(value) : height / 2;
    });

  function path(d) {
    const values = [
      ["Year", d.Year],
      ["temp", d.temp ?? tempAccessor(d)],
      ["PRCP", d.PRCP],
      ["Yield_bu_acre", d.Yield_bu_acre],
    ];
    return line(values);
  }

  const regionColors = {
    Midwest: "#3b82f6",
    South: "#f59e0b",
    West: "#10b981",
    Northeast: "#8b5cf6",
  };

  const color = (d) => {
    if (props.selectedState !== "ALL" && d.State === props.selectedState) {
      return "#ef3b2c";
    }
    if (brushedSet.size && brushedSet.has(d._id)) {
      return "#756bb1";
    }
    return regionColors[d.State] || "rgba(150,150,150,0.6)";
  };

  const strokeWidth = (d) => {
    if (props.selectedState !== "ALL" && d.State === props.selectedState) {
      return 2.5;
    }
    if (brushedSet.size && brushedSet.has(d._id)) {
      return 1.8;
    }
    return 2;
  };

  const opacity = (d) => {
    if (props.selectedState !== "ALL" && d.State === props.selectedState) {
      return 1;
    }
    if (brushedSet.size && brushedSet.has(d._id)) {
      return 0.9;
    }
    return 0.7;
  };

  g.selectAll("path.line")
    .data(displayData.value)
    .enter()
    .append("path")
    .attr("class", "line")
    .attr("d", path)
    .attr("fill", "none")
    .attr("stroke", color)
    .attr("stroke-width", strokeWidth)
    .attr("opacity", opacity)
    .on("mouseover", function (event, d) {
      d3.select(this)
        .attr("stroke-width", strokeWidth(d) + 1)
        .attr("opacity", 1);

      const tempVal = d.temp ?? tempAccessor(d);
      const tempLabel = props.tempMetric === "C" ? "°C" : "°F";

      const brushedSet = new Set(props.brushedIds);
      const isRegionMode =
        props.selectedState === "ALL" && brushedSet.size === 0;

      const titleLabel = isRegionMode ? "Region" : "State";
      const titleValue = d.State;

      tooltip.style("opacity", 1).html(
        `<strong>${titleLabel}: ${titleValue}</strong> — ${d.Year}<br/>
       Temp: ${d3.format(".1f")(tempVal)} ${tempLabel}<br/>
       Precipitation: ${d3.format(".1f")(d.PRCP)} in<br/>
       Yield: ${d3.format(".1f")(d.Yield_bu_acre)} bu/acre`
      );
    })

    .on("mousemove", function (event) {
      tooltip
        .style("left", event.offsetX + 20 + "px")
        .style("top", event.offsetY + 10 + "px");
    })
    .on("mouseout", function (event, d) {
      d3.select(this)
        .attr("stroke-width", strokeWidth(d))
        .attr("opacity", opacity(d));

      tooltip.style("opacity", 0);
    });

  const axisGroup = g
    .selectAll(".dimension")
    .data(dimensions)
    .enter()
    .append("g")
    .attr("class", "dimension")
    .attr("transform", (d) => `translate(${x(d.key)},0)`);

  axisGroup
    .append("g")
    .each(function (d) {
      d3.select(this).call(d3.axisLeft(d.scale).ticks(4));
    })
    .selectAll("text")
    .attr("fill", "#475569")
    .attr("font-size", "11px");

  axisGroup.selectAll(".domain, .tick line").attr("stroke", "#cbd5e1");

  axisGroup
    .append("text")
    .attr("y", -10)
    .attr("text-anchor", "middle")
    .attr("font-size", "12px")
    .attr("fill", "#1e293b")
    .attr("font-weight", "600")
    .text((d) => d.label);

  if (props.selectedState === "ALL" && brushedSet.size === 0) {
    const legend = svg
      .append("g")
      .attr(
        "transform",
        `translate(${width + margin.left - 100},${margin.top})`
      );

    const legendData = [
      { region: "Midwest", color: "#3b82f6" },
      { region: "South", color: "#f59e0b" },
      { region: "West", color: "#10b981" },
      { region: "Northeast", color: "#8b5cf6" },
    ];

    legendData.forEach((item, i) => {
      const legendRow = legend
        .append("g")
        .attr("transform", `translate(0,${i * 22})`);

      legendRow
        .append("line")
        .attr("x1", 0)
        .attr("x2", 20)
        .attr("y1", 10)
        .attr("y2", 10)
        .attr("stroke", item.color)
        .attr("stroke-width", 2);

      legendRow
        .append("text")
        .attr("x", 25)
        .attr("y", 14)
        .attr("fill", "#475569")
        .attr("font-size", "11px")
        .text(item.region);
    });
  }
}

onMounted(render);
watch(
  () => [props.data, props.tempMetric, props.selectedState, props.brushedIds],
  render,
  { deep: true }
);
</script>

<template>
  <div class="parallel-container">
    <p class="parallel-hint">
      {{
        selectedState !== "ALL"
          ? `Showing data for ${selectedState}`
          : brushedIds.length > 0
          ? `Showing ${brushedIds.length} selected points`
          : "Showing regional averages (Midwest, South, West, Northeast)"
      }}
    </p>
    <div ref="containerRef"></div>
  </div>
</template>

<style scoped>
.parallel-container {
  width: 100%;
  min-height: 300px;
  position: relative;
}

.parallel-hint {
  text-align: center;
  font-size: 0.9rem;
  color: #64748b;
  margin-bottom: 0.5rem;
  font-style: italic;
}

:deep(.line) {
  transition: opacity 0.2s ease, stroke-width 0.2s ease;
}

:deep(.dimension .domain),
:deep(.dimension .tick line) {
  stroke: #475569;
}

:deep(.dimension .tick text) {
  fill: #475569;
}

/* NEW: tooltip style */
:deep(.pc-tooltip) {
  background: rgba(15, 23, 42, 0.9);
  color: #f9fafb;
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 12px;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.25);
  pointer-events: none;
}
</style>
