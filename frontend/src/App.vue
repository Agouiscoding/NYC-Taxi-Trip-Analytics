<template>
  <AppShell v-model:active-view="activeView" :nav-items="navItems">
    <CommandBar
      :title="currentTitle"
      :controls="commandControls"
      @update:control="updateCommandControl"
      @reload="reloadAll"
    />

    <div v-if="error" class="error-banner">{{ error }}</div>
    <div v-if="loading" class="loading-bar" />

    <MetricStrip :mode="metricStripMode" :items="metricItems" :context-items="contextItems" />

    <section v-if="activeView === 'command'" class="view-stack">
      <InsightBanner
        title="NYC Taxi Demand Command Center"
        summary="Monitor citywide demand, zone pressure, route flow, and forecast risk from one operating surface."
        :stats="heroStats"
      />

      <div class="command-layout">
        <MapExplorer
          :selected-year="selectedYear"
          :selected-borough="selectedBorough"
          :selected-hour="selectedHour"
          :forecast-zones="forecast.zone_accuracy || []"
          :refresh-key="refreshKey"
        />
      </div>
    </section>

    <section v-else-if="activeView === 'demand'" class="view-stack">
      <SectionHeader
        eyebrow="Demand Patterns"
        title="Temporal rhythm of city movement"
        summary="Use this view to compare long-term recovery, hourly peaks, weekday structure, and borough-level seasonality."
      />

      <section class="analysis-grid">
        <ChartPanel class="span-2" title="Monthly Demand Timeline" eyebrow="Trips over time">
          <LineChart :data="temporal.year_month_demand || []" x-key="year_month" y-key="total_trips" :height="330" />
        </ChartPanel>
        <ChartPanel title="Hour-of-Day Pattern" eyebrow="Operational curve">
          <BarChart :data="overview.hourly_demand || []" x-key="hour" y-key="total_trips" color="#ffd23f" />
        </ChartPanel>
        <ChartPanel title="Seasonality" eyebrow="Average month">
          <BarChart
            :data="temporal.month_of_year_pattern || []"
            x-key="month_name"
            y-key="avg_trips_per_active_year"
            color="#4dd6ff"
          />
        </ChartPanel>
        <ChartPanel class="span-2" title="Weekday-Hour Demand Matrix" eyebrow="Heatmap">
          <HeatmapChart
            :data="temporal.weekday_hour_heatmap || []"
            x-key="hour"
            y-key="weekday_name"
            value-key="total_trips"
            :x-domain="hours"
            :y-domain="weekdayDomain"
          />
        </ChartPanel>
        <ChartPanel title="Weekday vs Weekend" eyebrow="Hourly split">
          <LineChart
            :data="temporal.weekday_weekend_hourly || []"
            x-key="hour"
            y-key="total_trips"
            series-key="day_type"
          />
        </ChartPanel>
        <ChartPanel title="Revenue Efficiency" eyebrow="Economics">
          <LineChart
            :data="temporal.revenue_efficiency || []"
            x-key="year_month"
            y-key="avg_revenue_per_trip"
          />
        </ChartPanel>
      </section>
    </section>

    <section v-else-if="activeView === 'zones'" class="view-stack">
      <SectionHeader
        eyebrow="Zone Intelligence"
        title="Pickup hot zones and local operating profiles"
        summary="Rank demand centers, inspect forecast misses, and compare how zones move through time."
      />

      <section class="analysis-grid">
        <ChartPanel class="span-2" title="Pickup Zone Demand Map" eyebrow="Taxi zones">
          <TaxiZoneMap
            :metrics="spatial.top_zones || []"
            metric-key="total_trips"
            metric-label="trips"
            @select-zone="selectedZone = $event"
          />
        </ChartPanel>
        <ChartPanel title="Top Pickup Zones" eyebrow="Ranking">
          <HorizontalBarChart
            :data="spatial.top_zones || []"
            label-key="pickup_zone"
            value-key="total_trips"
            color="#ffd23f"
          />
        </ChartPanel>
        <ChartPanel title="Hotspots at Selected Hour" eyebrow="Hourly pressure">
          <HorizontalBarChart
            :data="spatial.top_zones_by_hour || []"
            label-key="pickup_zone"
            value-key="total_trips"
            color="#ffd23f"
          />
        </ChartPanel>
        <ChartPanel class="span-2" title="Zone Rank Change" eyebrow="Longitudinal movement">
          <DataTable :rows="spatial.zone_rank_change || []" :columns="zoneRankColumns" :limit="20" />
        </ChartPanel>
      </section>
    </section>

    <section v-else-if="activeView === 'network'" class="view-stack">
      <SectionHeader
        eyebrow="Route Network"
        title="Origin-destination flows and route concentration"
        summary="Explore dominant OD corridors, airport movements, inter-borough connectivity, and route economics."
      />

      <section class="analysis-grid">
        <ChartPanel class="span-2" title="Route Flow Map" eyebrow="OD network">
          <RouteFlowMap :routes="networkRouteRows" :limit="routeLimit" />
        </ChartPanel>
        <ChartPanel class="span-2" :title="networkTableTitle" eyebrow="Pickup to dropoff">
          <DataTable :rows="networkRouteRows" :columns="routeColumns" :limit="routeLimit" />
        </ChartPanel>
        <ChartPanel class="span-2" title="Borough OD Matrix" eyebrow="Trip volume">
          <HeatmapChart
            :data="routes.route_borough_matrix || []"
            x-key="dropoff_borough"
            y-key="pickup_borough"
            value-key="total_trips"
          />
        </ChartPanel>
        <ChartPanel title="Airport Routes" eyebrow="Airports">
          <HorizontalBarChart
            :data="routes.top_airport_routes || []"
            label-key="route_name"
            value-key="trip_count"
            color="#4dd6ff"
          />
        </ChartPanel>
        <ChartPanel title="Inter-Borough Routes" eyebrow="Cross borough">
          <HorizontalBarChart
            :data="routes.top_inter_borough_routes || []"
            label-key="route_name"
            value-key="trip_count"
            color="#ff5d8f"
          />
        </ChartPanel>
      </section>
    </section>

    <section v-else-if="activeView === 'forecast'" class="view-stack">
      <SectionHeader
        eyebrow="Forecast Lab"
        title="Model accuracy and spatial demand risk"
        summary="Compare observed demand with model estimates and inspect where prediction error concentrates."
      />

      <section class="analysis-grid">
        <ChartPanel class="span-2" title="Daily Actual vs Predicted Demand" eyebrow="2024 test set">
          <LineChart
            :data="dailyForecastLong"
            x-key="pickup_date"
            y-key="value"
            series-key="series"
            :height="360"
          />
        </ChartPanel>
        <ChartPanel :title="`Model Test Metrics (${forecastMetric})`" eyebrow="2024 test set">
          <BarChart
            :data="forecast.model_evaluation_metrics || []"
            x-key="model"
            :y-key="forecastMetric"
            :color="forecastMetricColor"
          />
        </ChartPanel>
        <ChartPanel title="Monthly Actual vs Predicted" eyebrow="Demand curve">
          <LineChart :data="monthlyForecastLong" x-key="year_month" y-key="value" series-key="series" />
        </ChartPanel>
        <ChartPanel class="span-2" title="Zone Forecast Error Map" eyebrow="Absolute error">
          <TaxiZoneMap
            :metrics="forecast.zone_accuracy || []"
            metric-key="aggregate_absolute_error"
            metric-label="absolute error"
          />
        </ChartPanel>
        <ChartPanel title="Error by Hour" eyebrow="MAE">
          <BarChart :data="forecast.error_by_hour || []" x-key="hour" y-key="mae" color="#ffd23f" />
        </ChartPanel>
        <ChartPanel title="Error by Borough" eyebrow="MAE">
          <HorizontalBarChart
            :data="forecast.error_by_borough || []"
            label-key="pickup_borough"
            value-key="mae"
            color="#4dd6ff"
          />
        </ChartPanel>
      </section>
    </section>

    <section v-else-if="activeView === 'tables'" class="view-stack">
      <SectionHeader
        eyebrow="Data Tables"
        title="Operational reference tables"
        summary="Compact table views for route ranking, payment behavior, forecast misses, and zone movement."
      />

      <section class="analysis-grid">
        <ChartPanel class="span-2" :title="activeTable.title" :eyebrow="activeTable.eyebrow">
          <DataTable :rows="filteredTableRows" :columns="activeTable.columns" :limit="tableLimit" />
        </ChartPanel>
      </section>
    </section>
  </AppShell>
</template>

<script setup>
import {
  BrainCircuit,
  Clock3,
  Database,
  MapPinned,
  Network,
  Radar,
} from "lucide-vue-next";
import { computed, onMounted, ref, watch } from "vue";

import { api } from "@/api/client";
import BarChart from "@/components/charts/BarChart.vue";
import DataTable from "@/components/charts/DataTable.vue";
import HeatmapChart from "@/components/charts/HeatmapChart.vue";
import HorizontalBarChart from "@/components/charts/HorizontalBarChart.vue";
import LineChart from "@/components/charts/LineChart.vue";
import RouteFlowMap from "@/components/charts/RouteFlowMap.vue";
import TaxiZoneMap from "@/components/charts/TaxiZoneMap.vue";
import MapExplorer from "@/components/MapExplorer.vue";
import ChartPanel from "@/components/layout/ChartPanel.vue";
import AppShell from "@/components/product/AppShell.vue";
import CommandBar from "@/components/product/CommandBar.vue";
import InsightBanner from "@/components/product/InsightBanner.vue";
import MetricStrip from "@/components/product/MetricStrip.vue";
import SectionHeader from "@/components/product/SectionHeader.vue";
import { compact, decimal, integer, money } from "@/utils/format";

const navItems = [
  { key: "command", label: "Command Center", icon: Radar },
  { key: "demand", label: "Demand Patterns", icon: Clock3 },
  { key: "zones", label: "Zone Intelligence", icon: MapPinned },
  { key: "network", label: "Route Network", icon: Network },
  { key: "forecast", label: "Forecast Lab", icon: BrainCircuit },
  { key: "tables", label: "Data Tables", icon: Database },
];

const weekdayDomain = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const hours = Array.from({ length: 24 }, (_, index) => index);

const activeView = ref("command");
const loading = ref(false);
const error = ref("");
const refreshKey = ref(0);
const years = ref([]);
const boroughs = ref([]);
const selectedYear = ref(null);
const selectedBorough = ref("");
const selectedHour = ref(18);
const selectedZone = ref(null);
const routeLens = ref("all");
const routeLimit = ref(45);
const forecastMetric = ref("RMSE");
const forecastZoneLimit = ref(300);
const tableSource = ref("forecast");
const tableLimit = ref(16);
const tableSearch = ref("");
const overview = ref({});
const temporal = ref({});
const spatial = ref({});
const routes = ref({});
const business = ref({});
const forecast = ref({});

const currentTitle = computed(() => navItems.find((item) => item.key === activeView.value)?.label || "Dashboard");
const yearOptions = computed(() => [
  { label: "All", value: null },
  ...years.value.map((year) => ({ label: String(year), value: year })),
]);
const boroughOptions = computed(() => [
  { label: "All boroughs", value: "" },
  ...boroughs.value.map((borough) => ({ label: borough, value: borough })),
]);
const hourOptions = computed(() =>
  hours.map((hour) => ({ label: `${String(hour).padStart(2, "0")}:00`, value: hour }))
);
const commandControls = computed(() => {
  if (activeView.value === "command") {
    return [
      { key: "selectedYear", label: "Year", options: yearOptions.value, value: selectedYear.value, valueType: "number" },
      { key: "selectedBorough", label: "Borough", options: boroughOptions.value, value: selectedBorough.value },
      { key: "selectedHour", label: "Hour", options: hourOptions.value, value: selectedHour.value, valueType: "number" },
    ];
  }

  if (activeView.value === "demand") {
    return [
      { key: "selectedYear", label: "Year", options: yearOptions.value, value: selectedYear.value, valueType: "number" },
      { key: "selectedBorough", label: "Borough", options: boroughOptions.value, value: selectedBorough.value },
    ];
  }

  if (activeView.value === "zones") {
    return [
      { key: "selectedYear", label: "Year", options: yearOptions.value, value: selectedYear.value, valueType: "number" },
      { key: "selectedHour", label: "Hour", options: hourOptions.value, value: selectedHour.value, valueType: "number" },
    ];
  }

  if (activeView.value === "network") {
    return [
      {
        key: "routeLens",
        label: "Route lens",
        value: routeLens.value,
        options: [
          { label: "All routes", value: "all" },
          { label: "Airport", value: "airport" },
          { label: "Inter-borough", value: "interborough" },
        ],
      },
      {
        key: "routeLimit",
        label: "Top N",
        value: routeLimit.value,
        valueType: "number",
        options: [25, 45, 80].map((value) => ({ label: String(value), value })),
      },
    ];
  }

  if (activeView.value === "forecast") {
    return [
      {
        key: "forecastMetric",
        label: "Metric",
        value: forecastMetric.value,
        options: ["RMSE", "MAE", "R2"].map((value) => ({ label: value, value })),
      },
      {
        key: "forecastZoneLimit",
        label: "Zones",
        value: forecastZoneLimit.value,
        valueType: "number",
        options: [100, 300, 500].map((value) => ({ label: String(value), value })),
      },
    ];
  }

  if (activeView.value === "tables") {
    return [
      {
        key: "tableSource",
        label: "Table",
        value: tableSource.value,
        options: [
          { label: "Forecast misses", value: "forecast" },
          { label: "Route ranking", value: "routes" },
          { label: "Zone rank change", value: "zones" },
          { label: "Payment type", value: "payments" },
        ],
      },
      {
        key: "tableLimit",
        label: "Rows",
        value: tableLimit.value,
        valueType: "number",
        options: [12, 16, 25, 50].map((value) => ({ label: String(value), value })),
      },
      { key: "tableSearch", label: "Search", type: "search", value: tableSearch.value, placeholder: "Zone, route, borough" },
    ];
  }

  return [];
});
const selectedYearSummary = computed(() => {
  const rows = overview.value.yearly_summary || [];
  return rows.find((row) => row.year === selectedYear.value) || rows.at(-1) || {};
});
const kpiSource = computed(() => (selectedYear.value ? selectedYearSummary.value : overview.value.kpi || {}));
const bestForecastModel = computed(() => {
  const rows = forecast.value.model_evaluation_metrics || [];
  return rows.find((row) => isTrue(row.is_best_model)) || rows[0] || {};
});
const forecastTotals = computed(() => {
  const rows = forecast.value.monthly_actual_predicted || [];
  const actual = rows.reduce((sum, row) => sum + Number(row.trip_count || 0), 0);
  const predicted = rows.reduce((sum, row) => sum + Number(row.predicted_trip_count || 0), 0);
  return {
    actual,
    predicted,
    error: actual - predicted,
  };
});
const metricItems = computed(() => {
  if (activeView.value === "forecast") {
    const model = bestForecastModel.value;
    const totals = forecastTotals.value;
    const bias = totals.error >= 0 ? "under predicted" : "over predicted";
    return [
      { label: "Best model", value: model.model || "Pending", note: "2024 test set" },
      { label: "R2", value: decimal(model.R2, 3), note: `${decimal(model.RMSE, 2)} RMSE` },
      { label: "MAE", value: decimal(model.MAE, 2), note: "zone-hour trips" },
      { label: "Bias", value: compact(Math.abs(totals.error)), note: bias },
    ];
  }

  return [
    {
      label: "Trips",
      value: compact(kpiSource.value.total_trips),
      note: selectedYear.value ? `${selectedYear.value} selected` : "All imported records",
    },
    {
      label: "Revenue",
      value: money(kpiSource.value.total_revenue),
      note: `${money(kpiSource.value.avg_revenue_per_trip || kpiSource.value.avg_revenue_per_day)} avg`,
    },
    { label: "Active days", value: integer(kpiSource.value.active_days), note: "Pipeline coverage" },
    { label: "Pickup zones", value: integer(kpiSource.value.active_pickup_zones), note: "Joined to TLC zones" },
  ];
});
const metricStripMode = computed(() =>
  activeView.value === "command" || activeView.value === "forecast" ? "metrics" : "context"
);
const contextItems = computed(() => {
  const selectedYearLabel = selectedYear.value || "All years";
  const selectedBoroughLabel = selectedBorough.value || "Citywide";

  if (activeView.value === "demand") {
    return [
      { label: "Scope", value: `${selectedYearLabel} / ${selectedBoroughLabel}` },
      { label: "Read", value: "Monthly trend, hourly rhythm, weekday structure" },
      { label: "Filter note", value: "Hour is summarized inside the charts" },
    ];
  }

  if (activeView.value === "zones") {
    return [
      { label: "Scope", value: `${selectedYearLabel} / ${String(selectedHour.value).padStart(2, "0")}:00` },
      { label: "Metric", value: "Pickup demand and selected-hour pressure" },
      { label: "Geometry", value: "TLC taxi zones joined by LocationID" },
    ];
  }

  if (activeView.value === "network") {
    return [
      { label: "Lens", value: networkTableTitle.value },
      { label: "Rows", value: `Top ${routeLimit.value} corridors` },
      { label: "Read", value: "OD concentration, airport movement, borough connectivity" },
    ];
  }

  if (activeView.value === "tables") {
    return [
      { label: "Source", value: activeTable.value.title },
      { label: "Rows", value: `Showing ${tableLimit.value}` },
      { label: "Search", value: tableSearch.value || "All records" },
    ];
  }

  return [];
});
const heroStats = computed(() => [
  { label: "Selected hour", value: `${String(selectedHour.value).padStart(2, "0")}:00` },
  { label: "Borough", value: selectedBorough.value || "Citywide" },
  { label: "Top zones loaded", value: integer((spatial.value.top_zones || []).length) },
]);

const routeColumns = [
  {
    key: "route_rank",
    label: "Rank",
    numeric: true,
    format: (value, row) => integer(value || row.route_rank_in_hour || row.route_rank_in_year_month || row.route_rank),
  },
  { key: "route_name", label: "Route" },
  { key: "trip_count", label: "Trips", numeric: true, format: integer },
  { key: "avg_trip_distance", label: "Miles", numeric: true, format: (value) => decimal(value, 2) },
  { key: "avg_trip_duration_min", label: "Minutes", numeric: true, format: (value) => decimal(value, 1) },
  { key: "total_revenue", label: "Revenue", numeric: true, format: money },
];
const zoneRankColumns = [
  { key: "pickup_zone", label: "Zone" },
  { key: "pickup_borough", label: "Borough" },
  { key: "first_rank", label: "First Rank", numeric: true, format: integer },
  { key: "last_rank", label: "Last Rank", numeric: true, format: integer },
  { key: "rank_improvement", label: "Improvement", numeric: true, format: integer },
  { key: "trip_count_change", label: "Trip Change", numeric: true, format: integer },
];
const forecastZoneColumns = [
  { key: "pickup_zone", label: "Zone" },
  { key: "pickup_borough", label: "Borough" },
  { key: "actual_trip_count", label: "Actual", numeric: true, format: integer },
  { key: "predicted_trip_count", label: "Predicted", numeric: true, format: (value) => decimal(value, 0) },
  { key: "mae", label: "MAE", numeric: true, format: (value) => decimal(value, 2) },
  {
    key: "aggregate_absolute_percentage_error",
    label: "Agg APE",
    numeric: true,
    format: percentPoints,
  },
];
const paymentColumns = [
  { key: "payment_type_desc", label: "Payment Type" },
  { key: "trip_count", label: "Trips", numeric: true, format: integer },
  { key: "total_revenue", label: "Revenue", numeric: true, format: money },
  { key: "avg_fare_amount", label: "Avg Fare", numeric: true, format: money },
  { key: "avg_tip_amount", label: "Avg Tip", numeric: true, format: money },
];

const networkRouteRows = computed(() => {
  if (routeLens.value === "airport") {
    return routes.value.top_airport_routes || [];
  }

  if (routeLens.value === "interborough") {
    return routes.value.top_inter_borough_routes || [];
  }

  return routes.value.top_routes || [];
});
const networkTableTitle = computed(() => {
  if (routeLens.value === "airport") {
    return "Airport Routes";
  }

  if (routeLens.value === "interborough") {
    return "Inter-Borough Routes";
  }

  return "Top Routes";
});
const forecastMetricColor = computed(() => {
  if (forecastMetric.value === "R2") {
    return "#5cffa8";
  }

  if (forecastMetric.value === "MAE") {
    return "#ffd23f";
  }

  return "#ff5d8f";
});
const tableConfigs = computed(() => ({
  forecast: {
    title: "Largest Zone Forecast Misses",
    eyebrow: "Forecast",
    rows: forecast.value.zone_accuracy || [],
    columns: forecastZoneColumns,
  },
  routes: {
    title: "Route Ranking",
    eyebrow: "Network",
    rows: routes.value.top_routes || [],
    columns: routeColumns,
  },
  zones: {
    title: "Zone Rank Change",
    eyebrow: "Spatial",
    rows: spatial.value.zone_rank_change || [],
    columns: zoneRankColumns,
  },
  payments: {
    title: "Payment Type Summary",
    eyebrow: "Business",
    rows: business.value.payment_type || [],
    columns: paymentColumns,
  },
}));
const activeTable = computed(() => tableConfigs.value[tableSource.value] || tableConfigs.value.forecast);
const filteredTableRows = computed(() => {
  const query = tableSearch.value.trim().toLowerCase();
  const rows = activeTable.value.rows || [];

  if (!query) {
    return rows;
  }

  return rows.filter((row) =>
    Object.values(row).some((value) => String(value ?? "").toLowerCase().includes(query))
  );
});

const monthlyForecastLong = computed(() =>
  actualPredictedLong(forecast.value.monthly_actual_predicted || [], "year_month")
);
const dailyForecastLong = computed(() =>
  actualPredictedLong(forecast.value.daily_actual_predicted || [], "pickup_date")
);

function isTrue(value) {
  return value === true || value === "true" || value === "True";
}

function percentPoints(value) {
  return `${decimal(value, 1)}%`;
}

function actualPredictedLong(rows, xKey) {
  return rows.flatMap((row) => [
    {
      [xKey]: row[xKey],
      series: "Actual",
      value: Number(row.trip_count || row.actual_trip_count || 0),
    },
    {
      [xKey]: row[xKey],
      series: "Predicted",
      value: Number(row.predicted_trip_count || 0),
    },
  ]);
}

function updateCommandControl(key, value) {
  const handlers = {
    selectedYear: () => {
      selectedYear.value = value;
    },
    selectedBorough: () => {
      selectedBorough.value = value;
    },
    selectedHour: () => {
      selectedHour.value = Number(value);
    },
    routeLens: () => {
      routeLens.value = value;
    },
    routeLimit: () => {
      routeLimit.value = Number(value);
    },
    forecastMetric: () => {
      forecastMetric.value = value;
    },
    forecastZoneLimit: () => {
      forecastZoneLimit.value = Number(value);
    },
    tableSource: () => {
      tableSource.value = value;
      tableSearch.value = "";
    },
    tableLimit: () => {
      tableLimit.value = Number(value);
    },
    tableSearch: () => {
      tableSearch.value = value;
    },
  };

  handlers[key]?.();
}

async function loadFilters() {
  const result = await api.filters();
  years.value = result.data.years || [];
  boroughs.value = result.data.boroughs || [];
  selectedYear.value = years.value.includes(2024) ? 2024 : years.value.at(-1) || null;
}

async function loadAll() {
  loading.value = true;
  error.value = "";

  try {
    const params = {
      year: selectedYear.value,
      borough: selectedBorough.value || null,
    };
    const [overviewResult, temporalResult, spatialResult, routesResult, businessResult, forecastResult] = await Promise.all([
      api.overview({ year: selectedYear.value, zone_limit: 20, route_limit: 12 }),
      api.temporalStory(params),
      api.spatialStory({ year: selectedYear.value, hour: selectedHour.value, zone_limit: 25 }),
      api.routesStory({ route_limit: routeLimit.value }),
      api.businessStory({ year: selectedYear.value }),
      api.forecastStory({ zone_limit: forecastZoneLimit.value }),
    ]);

    overview.value = overviewResult.data;
    temporal.value = temporalResult.data;
    spatial.value = spatialResult.data;
    routes.value = routesResult.data;
    business.value = businessResult.data;
    forecast.value = forecastResult.data;
  } catch (caught) {
    error.value = caught.message || "Failed to load dashboard data.";
  } finally {
    loading.value = false;
  }
}

async function reloadAll() {
  refreshKey.value += 1;
  await loadAll();
}

watch([selectedYear, selectedBorough, selectedHour, routeLimit, forecastZoneLimit], loadAll);

onMounted(async () => {
  await loadFilters();
  await loadAll();
});
</script>
