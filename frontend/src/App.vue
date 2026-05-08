<template>
  <AppShell v-model:active-view="activeView" :nav-items="navItems">
    <CommandBar
      :title="currentTitle"
      @reload="reloadAll"
    />

    <div v-if="error" class="error-banner">{{ error }}</div>
    <div v-if="loading" class="loading-bar" />

    <MetricStrip :mode="metricStripMode" :items="metricItems" :context-items="contextItems" />

    <section v-if="activeView === 'command'" class="view-stack">
      <InsightBanner
        title="NYC Taxi Demand Command Center"
        summary="Demand, OD flow, revenue, and forecast error across imported yellow taxi records."
        :stats="heroStats"
      />

      <div class="command-layout">
        <MapExplorer
          v-model:selected-year="commandYear"
          v-model:selected-borough="commandBorough"
          v-model:selected-hour="commandHour"
          :year-options="yearOptions"
          :borough-options="boroughOptions"
          :hour-options="hourOptions"
          :forecast-zones="forecast.zone_accuracy || []"
          :refresh-key="refreshKey"
        />
      </div>
    </section>

    <section v-else-if="activeView === 'demand'" class="view-stack">
      <SectionHeader
        eyebrow="Demand Patterns"
        title="Demand by time"
      />

      <section class="analysis-grid">
        <ChartPanel class="span-2" title="Monthly Demand Timeline" eyebrow="Trips over time">
          <template #actions>
            <ChartFilters :controls="demandMonthlyControls" @update:control="updateChartControl" />
          </template>
          <LineChart :data="demandMonthlyRows" x-key="year_month" y-key="total_trips" :height="330" />
        </ChartPanel>
        <ChartPanel title="Hour-of-Day Pattern" eyebrow="Operational curve">
          <template #actions>
            <ChartFilters :controls="demandHourlyControls" @update:control="updateChartControl" />
          </template>
          <BarChart :data="demandHourlyRows" x-key="hour" y-key="total_trips" color="#ffd23f" />
        </ChartPanel>
        <ChartPanel title="Seasonality" eyebrow="Average month">
          <BarChart
            :data="demandMonthOfYearRows"
            x-key="month_name"
            y-key="avg_trips_per_active_year"
            color="#4dd6ff"
          />
        </ChartPanel>
        <ChartPanel class="span-2" title="Weekday-Hour Demand Matrix" eyebrow="Heatmap">
          <template #actions>
            <ChartFilters :controls="demandMatrixControls" @update:control="updateChartControl" />
          </template>
          <HeatmapChart
            :data="demandWeekdayHourRows"
            x-key="hour"
            y-key="weekday_name"
            value-key="total_trips"
            :x-domain="hours"
            :y-domain="weekdayDomain"
          />
        </ChartPanel>
        <ChartPanel title="Weekday vs Weekend" eyebrow="Hourly split">
          <LineChart
            :data="demandWeekdayWeekendRows"
            x-key="hour"
            y-key="total_trips"
            series-key="day_type"
          />
        </ChartPanel>
        <ChartPanel title="Revenue Efficiency" eyebrow="Economics">
          <template #actions>
            <ChartFilters :controls="demandRevenueControls" @update:control="updateChartControl" />
          </template>
          <LineChart
            :data="demandRevenueRows"
            x-key="year_month"
            y-key="avg_revenue_per_trip"
          />
        </ChartPanel>
      </section>
    </section>

    <section v-else-if="activeView === 'zones'" class="view-stack">
      <SectionHeader
        eyebrow="Zone Intelligence"
        title="Pickup zones"
      />

      <section class="analysis-grid">
        <ChartPanel class="span-2" title="Pickup Zone Demand Map" eyebrow="Taxi zones">
          <template #actions>
            <ChartFilters :controls="zoneMapControls" @update:control="updateChartControl" />
          </template>
          <TaxiZoneMap
            :metrics="zoneMapRows"
            metric-key="total_trips"
            metric-label="trips"
          />
        </ChartPanel>
        <ChartPanel title="Top Pickup Zones" eyebrow="Ranking">
          <template #actions>
            <ChartFilters :controls="zoneTopControls" @update:control="updateChartControl" />
          </template>
          <HorizontalBarChart
            :data="zoneTopRows"
            label-key="pickup_zone"
            value-key="total_trips"
            color="#ffd23f"
          />
        </ChartPanel>
        <ChartPanel title="Hotspots at Selected Hour" eyebrow="Hourly pressure">
          <template #actions>
            <ChartFilters :controls="zoneHotspotControls" @update:control="updateChartControl" />
          </template>
          <HorizontalBarChart
            :data="zoneHotspotRows"
            label-key="pickup_zone"
            value-key="total_trips"
            color="#ffd23f"
          />
        </ChartPanel>
        <ChartPanel class="span-2" title="Zone Rank Change" eyebrow="Longitudinal movement">
          <template #actions>
            <ChartFilters :controls="zoneRankControls" @update:control="updateChartControl" />
          </template>
          <DataTable :rows="zoneRankRows" :columns="zoneRankColumns" :limit="zoneRankLimit" />
        </ChartPanel>
      </section>
    </section>

    <section v-else-if="activeView === 'network'" class="view-stack">
      <SectionHeader
        eyebrow="Route Network"
        title="Route flows"
      />

      <section class="analysis-grid">
        <ChartPanel class="span-2" title="Route Flow Map" eyebrow="OD network">
          <template #actions>
            <ChartFilters :controls="routeMapControls" @update:control="updateChartControl" />
          </template>
          <RouteFlowMap :routes="routeMapRows" :limit="routeMapLimit" />
        </ChartPanel>
        <ChartPanel class="span-2" :title="routeTableTitle" eyebrow="Pickup to dropoff">
          <template #actions>
            <ChartFilters :controls="routeTableControls" @update:control="updateChartControl" />
          </template>
          <DataTable :rows="routeTableRows" :columns="routeColumns" :limit="routeTableLimit" paginated :page-size="25" />
        </ChartPanel>
        <ChartPanel class="span-2" title="Borough OD Matrix" eyebrow="Trip volume">
          <HeatmapChart
            :data="routeBoroughMatrixRows"
            x-key="dropoff_borough"
            y-key="pickup_borough"
            value-key="total_trips"
            :height="420"
          />
        </ChartPanel>
        <ChartPanel title="Airport Routes" eyebrow="Airports">
          <template #actions>
            <ChartFilters :controls="airportRouteControls" @update:control="updateChartControl" />
          </template>
          <HorizontalBarChart
            :data="airportRouteRows"
            label-key="route_name"
            value-key="trip_count"
            color="#4dd6ff"
            :limit="airportRouteLimit"
            :height="airportRouteChartHeight"
          />
        </ChartPanel>
        <ChartPanel title="Inter-Borough Routes" eyebrow="Cross borough">
          <template #actions>
            <ChartFilters :controls="interBoroughRouteControls" @update:control="updateChartControl" />
          </template>
          <HorizontalBarChart
            :data="interBoroughRouteRows"
            label-key="route_name"
            value-key="trip_count"
            color="#ff5d8f"
            :limit="interBoroughRouteLimit"
            :height="interBoroughRouteChartHeight"
          />
        </ChartPanel>
      </section>
    </section>

    <section v-else-if="activeView === 'forecast'" class="view-stack">
      <SectionHeader
        eyebrow="Forecast Lab"
        title="Forecast accuracy"
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
          <template #actions>
            <ChartFilters :controls="forecastMetricControls" @update:control="updateChartControl" />
          </template>
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
          <template #actions>
            <ChartFilters :controls="forecastZoneControls" @update:control="updateChartControl" />
          </template>
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
        title="Reference tables"
      />

      <section class="analysis-grid">
        <ChartPanel class="span-2" :title="activeTable.title" :eyebrow="activeTable.eyebrow">
          <template #actions>
            <ChartFilters :controls="tableControls" @update:control="updateChartControl" />
          </template>
          <DataTable
            :rows="filteredTableRows"
            :columns="activeTable.columns"
            :limit="tableLimit"
            paginated
            :page-size="25"
          />
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
import ChartFilters from "@/components/layout/ChartFilters.vue";
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
const filtersLoaded = ref(false);
const commandYear = ref(null);
const commandBorough = ref("");
const commandHour = ref(18);
const demandMonthlyYear = ref(null);
const demandMonthlyBorough = ref("");
const demandHourlyYear = ref(null);
const demandMatrixYear = ref(null);
const demandRevenueYear = ref(null);
const zoneMapYear = ref(null);
const zoneTopYear = ref(null);
const zoneHotspotHour = ref(0);
const zoneRankLimit = ref(20);
const routeMapLens = ref("all");
const routeMapScope = ref("");
const routeMapLimit = ref(100);
const routeTableLens = ref("all");
const routeTableScope = ref("");
const routeTableLimit = 500;
const airportRouteScope = ref("");
const airportRouteLimit = ref(10);
const interBoroughRouteScope = ref("");
const interBoroughRouteLimit = ref(10);
const forecastMetric = ref("RMSE");
const forecastZoneLimit = ref(300);
const tableSource = ref("forecast");
const tableLimit = ref(50);
const tableSearch = ref("");
const tableYear = ref(null);
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
const routeScopeOptions = computed(() => [
  { label: "Overall", value: "" },
  ...boroughs.value.map((borough) => ({ label: borough, value: borough })),
]);
const hourOptions = computed(() =>
  hours.map((hour) => ({ label: `${String(hour).padStart(2, "0")}:00`, value: hour }))
);
const rowLimitOptions = [12, 16, 25, 50].map((value) => ({ label: String(value), value }));
const tableRowLimitOptions = [16, 25, 50, 100, 250, 500].map((value) => ({ label: String(value), value }));
const routeMapLimitOptions = [10, 25, 50, 100, 250, 500].map((value) => ({ label: String(value), value }));
const routeBarLimitOptions = [10, 25, 50, 75, 100].map((value) => ({ label: String(value), value }));
const routeLensOptions = [
  { label: "All routes", value: "all" },
  { label: "Airport", value: "airport" },
  { label: "Inter-borough", value: "interborough" },
];
const forecastMetricOptions = ["RMSE", "MAE", "R2"].map((value) => ({ label: value, value }));
const forecastZoneOptions = [100, 300, 500].map((value) => ({ label: String(value), value }));
const tableSourceOptions = [
  { label: "Forecast misses", value: "forecast" },
  { label: "Route ranking", value: "routes" },
  { label: "Zone rank change", value: "zones" },
  { label: "Payment type", value: "payments" },
];

const demandMonthlyControls = computed(() => [
  { key: "demandMonthlyYear", label: "Year", options: yearOptions.value, value: demandMonthlyYear.value, valueType: "number" },
  { key: "demandMonthlyBorough", label: "Borough", options: boroughOptions.value, value: demandMonthlyBorough.value },
]);
const demandHourlyControls = computed(() => [
  { key: "demandHourlyYear", label: "Year", options: yearOptions.value, value: demandHourlyYear.value, valueType: "number" },
]);
const demandMatrixControls = computed(() => [
  { key: "demandMatrixYear", label: "Year", options: yearOptions.value, value: demandMatrixYear.value, valueType: "number" },
]);
const demandRevenueControls = computed(() => [
  { key: "demandRevenueYear", label: "Year", options: yearOptions.value, value: demandRevenueYear.value, valueType: "number" },
]);
const zoneMapControls = computed(() => [
  { key: "zoneMapYear", label: "Year", options: yearOptions.value, value: zoneMapYear.value, valueType: "number" },
]);
const zoneTopControls = computed(() => [
  { key: "zoneTopYear", label: "Year", options: yearOptions.value, value: zoneTopYear.value, valueType: "number" },
]);
const zoneHotspotControls = computed(() => [
  { key: "zoneHotspotHour", label: "Hour", options: hourOptions.value, value: zoneHotspotHour.value, valueType: "number" },
]);
const zoneRankControls = computed(() => [
  { key: "zoneRankLimit", label: "Rows", options: rowLimitOptions, value: zoneRankLimit.value, valueType: "number" },
]);
const routeMapControls = computed(() => [
  { key: "routeMapLens", label: "Lens", options: routeLensOptions, value: routeMapLens.value },
  { key: "routeMapScope", label: "Scope", options: routeScopeOptions.value, value: routeMapScope.value },
  routeLimitControl("routeMapLimit", "Top N", routeMapLimit.value, 500, routeMapLimitOptions),
]);
const routeTableControls = computed(() => [
  { key: "routeTableLens", label: "Lens", options: routeLensOptions, value: routeTableLens.value },
  { key: "routeTableScope", label: "Scope", options: routeScopeOptions.value, value: routeTableScope.value },
]);
const airportRouteControls = computed(() => [
  { key: "airportRouteScope", label: "Scope", options: routeScopeOptions.value, value: airportRouteScope.value },
  routeLimitControl("airportRouteLimit", "Top N", airportRouteLimit.value, 100, routeBarLimitOptions),
]);
const interBoroughRouteControls = computed(() => [
  { key: "interBoroughRouteScope", label: "Scope", options: routeScopeOptions.value, value: interBoroughRouteScope.value },
  routeLimitControl("interBoroughRouteLimit", "Top N", interBoroughRouteLimit.value, 100, routeBarLimitOptions),
]);
const forecastMetricControls = computed(() => [
  { key: "forecastMetric", label: "Metric", options: forecastMetricOptions, value: forecastMetric.value },
]);
const forecastZoneControls = computed(() => [
  { key: "forecastZoneLimit", label: "Zones", options: forecastZoneOptions, value: forecastZoneLimit.value, valueType: "number" },
]);
const tableControls = computed(() => {
  const controls = [
    { key: "tableSource", label: "Table", options: tableSourceOptions, value: tableSource.value },
    { key: "tableLimit", label: "Rows", options: tableRowLimitOptions, value: tableLimit.value, valueType: "number" },
  ];

  if (tableSource.value === "payments") {
    controls.push({ key: "tableYear", label: "Year", options: yearOptions.value, value: tableYear.value, valueType: "number" });
  }

  controls.push({ key: "tableSearch", label: "Search", type: "search", value: tableSearch.value, placeholder: "Zone, route, borough" });
  return controls;
});
const selectedYearSummary = computed(() => {
  const rows = overview.value.yearly_summary || [];
  return rows.find((row) => row.year === commandYear.value) || rows.at(-1) || {};
});
const kpiSource = computed(() => (commandYear.value ? selectedYearSummary.value : overview.value.kpi || {}));
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
      note: commandYear.value ? `${commandYear.value} selected` : "All imported records",
    },
    {
      label: "Revenue",
      value: money(kpiSource.value.total_revenue),
      note: `${money(kpiSource.value.avg_revenue_per_trip || kpiSource.value.avg_revenue_per_day)} avg`,
    },
    { label: "Active days", value: integer(kpiSource.value.active_days), note: "days covered" },
    { label: "Pickup zones", value: integer(kpiSource.value.active_pickup_zones), note: "pickup IDs" },
  ];
});
const metricStripMode = computed(() =>
  activeView.value === "command" || activeView.value === "forecast" ? "metrics" : "context"
);
const contextItems = computed(() => {
  if (activeView.value === "demand") {
    return [
      { label: "Monthly", value: `${demandMonthlyYear.value || "All years"} / ${demandMonthlyBorough.value || "Citywide"}` },
      { label: "Hourly", value: demandHourlyYear.value || "All years" },
      { label: "Revenue", value: demandRevenueYear.value || "All years" },
    ];
  }

  if (activeView.value === "zones") {
    return [
      { label: "Map", value: zoneMapYear.value || "All years" },
      { label: "Hotspots", value: `${String(zoneHotspotHour.value).padStart(2, "0")}:00` },
      { label: "Rank rows", value: zoneRankLimit.value },
    ];
  }

  if (activeView.value === "network") {
    return [
      { label: "Map", value: `${routeLensTitle(routeMapLens.value)} / ${routeMapScope.value || "Overall"}` },
      { label: "Table", value: `${routeTableTitle.value} / ${routeTableScope.value || "Overall"}` },
      { label: "Lines", value: routeMapLimit.value },
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
  { label: "Selected hour", value: `${String(commandHour.value).padStart(2, "0")}:00` },
  { label: "Borough", value: commandBorough.value || "Citywide" },
  { label: "Top zones loaded", value: integer(zoneMapRows.value.length) },
]);

const routeColumns = [
  {
    key: "route_rank",
    label: "Rank",
    numeric: true,
    format: (value, row) =>
      integer(
        row.route_rank_in_borough ||
          value ||
          row.route_rank_in_hour ||
          row.route_rank_in_year_month ||
          row.route_rank
      ),
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

const demandMonthlyRows = computed(() => temporal.value.year_month_demand || []);
const demandHourlyRows = computed(() => temporal.value.hourly_demand || []);
const demandMonthOfYearRows = computed(() => temporal.value.month_of_year_pattern || []);
const demandWeekdayHourRows = computed(() => temporal.value.weekday_hour_heatmap || []);
const demandWeekdayWeekendRows = computed(() => temporal.value.weekday_weekend_hourly || []);
const demandRevenueRows = computed(() => temporal.value.revenue_efficiency || []);
const zoneMapRows = computed(() => spatial.value.map_zones || []);
const zoneTopRows = computed(() => spatial.value.top_zones || []);
const zoneHotspotRows = computed(() => spatial.value.top_zones_by_hour || []);
const zoneRankRows = computed(() => spatial.value.zone_rank_change || []);
const airportRouteRows = computed(() => routes.value.top_airport_routes || []);
const interBoroughRouteRows = computed(() => routes.value.top_inter_borough_routes || []);
const routeBoroughMatrixRows = computed(() => routes.value.route_borough_matrix || []);
const airportRouteChartHeight = computed(() => rankingChartHeight(airportRouteRows.value, airportRouteLimit.value));
const interBoroughRouteChartHeight = computed(() =>
  rankingChartHeight(interBoroughRouteRows.value, interBoroughRouteLimit.value)
);

function rankingChartHeight(rows, limit) {
  const count = Math.min(rows.length || limit, limit);
  return Math.max(360, count * 28 + 96);
}

function routeLensTitle(lens) {
  if (lens === "airport") {
    return "Airport Routes";
  }

  if (lens === "interborough") {
    return "Inter-Borough Routes";
  }

  return "Top Routes";
}

function routeApiForLens(lens) {
  if (lens === "airport") {
    return api.routesAirport;
  }

  if (lens === "interborough") {
    return api.routesInterBorough;
  }

  return api.routesTop;
}

const routeMapRows = computed(() => routes.value.route_map || []);
const routeTableRows = computed(() => routes.value.route_table || []);
const routeTableTitle = computed(() => routeLensTitle(routeTableLens.value));
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
    rows: zoneRankRows.value,
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

function routeLimitControl(key, label, value, max, options) {
  return {
    key,
    label,
    type: "limit",
    min: 10,
    max,
    step: 1,
    options,
    value,
    valueType: "number",
  };
}

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

function updateChartControl(key, value) {
  const handlers = {
    demandMonthlyYear: () => {
      demandMonthlyYear.value = value;
    },
    demandMonthlyBorough: () => {
      demandMonthlyBorough.value = value;
    },
    demandHourlyYear: () => {
      demandHourlyYear.value = value;
    },
    demandMatrixYear: () => {
      demandMatrixYear.value = value;
    },
    demandRevenueYear: () => {
      demandRevenueYear.value = value;
    },
    zoneMapYear: () => {
      zoneMapYear.value = value;
    },
    zoneTopYear: () => {
      zoneTopYear.value = value;
    },
    zoneHotspotHour: () => {
      zoneHotspotHour.value = Number(value);
    },
    zoneRankLimit: () => {
      zoneRankLimit.value = Number(value);
    },
    routeMapLens: () => {
      routeMapLens.value = value;
    },
    routeMapScope: () => {
      routeMapScope.value = value;
    },
    routeMapLimit: () => {
      routeMapLimit.value = clampRouteLimit(value);
    },
    routeTableLens: () => {
      routeTableLens.value = value;
    },
    routeTableScope: () => {
      routeTableScope.value = value;
    },
    airportRouteScope: () => {
      airportRouteScope.value = value;
    },
    airportRouteLimit: () => {
      airportRouteLimit.value = clampRouteLimit(value, 100);
    },
    interBoroughRouteScope: () => {
      interBoroughRouteScope.value = value;
    },
    interBoroughRouteLimit: () => {
      interBoroughRouteLimit.value = clampRouteLimit(value, 100);
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
    tableYear: () => {
      tableYear.value = value;
    },
  };

  handlers[key]?.();
}

function clampRouteLimit(value, max = 500) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return max;
  }

  return Math.min(max, Math.max(10, parsed));
}

async function loadFilters() {
  const result = await api.filters();
  years.value = result.data.years || [];
  boroughs.value = result.data.boroughs || [];
  commandYear.value = years.value.includes(2024) ? 2024 : years.value.at(-1) || null;
}

async function loadAll({ refreshOverview = false } = {}) {
  loading.value = true;
  error.value = "";

  try {
    const [
      overviewResult,
      monthlyResult,
      hourlyResult,
      monthPatternResult,
      matrixResult,
      weekendResult,
      revenueResult,
      zoneMapResult,
      zoneTopResult,
      zoneHotspotResult,
      zoneRankResult,
      routeMapResult,
      routeTableResult,
      topRoutesResult,
      airportRoutesResult,
      interBoroughRoutesResult,
      routeMatrixResult,
      businessResult,
      forecastResult,
    ] = await Promise.all([
      refreshOverview ? api.overview() : Promise.resolve({ data: overview.value }),
      demandMonthlyBorough.value
        ? api.boroughYearMonth({ year: demandMonthlyYear.value, borough: demandMonthlyBorough.value })
        : api.yearMonthDemand({ year: demandMonthlyYear.value }),
      api.hourlyDemand({ year: demandHourlyYear.value }),
      api.monthOfYearPattern(),
      api.weekdayHourHeatmap({ year: demandMatrixYear.value }),
      api.weekdayWeekendHourly(),
      api.revenueEfficiency({ year: demandRevenueYear.value }),
      api.topZones({ year: zoneMapYear.value, limit: 25 }),
      api.topZones({ year: zoneTopYear.value, limit: 25 }),
      api.topZonesByHour({ hour: zoneHotspotHour.value, limit: 25 }),
      api.zoneRankChange({
        limit: Math.max(zoneRankLimit.value, tableSource.value === "zones" ? tableLimit.value : 0),
      }),
      routeApiForLens(routeMapLens.value)({ borough: routeMapScope.value || null, limit: routeMapLimit.value }),
      routeApiForLens(routeTableLens.value)({ borough: routeTableScope.value || null, limit: routeTableLimit }),
      api.routesTop({ limit: tableSource.value === "routes" ? tableLimit.value : 45 }),
      api.routesAirport({ borough: airportRouteScope.value || null, limit: airportRouteLimit.value }),
      api.routesInterBorough({ borough: interBoroughRouteScope.value || null, limit: interBoroughRouteLimit.value }),
      api.routeBoroughMatrix(),
      api.businessStory({ year: tableSource.value === "payments" ? tableYear.value : null }),
      api.forecastStory({
        zone_limit: Math.max(forecastZoneLimit.value, tableSource.value === "forecast" ? tableLimit.value : 0),
      }),
    ]);

    overview.value = overviewResult.data;
    temporal.value = {
      year_month_demand: monthlyResult.data || [],
      hourly_demand: hourlyResult.data || [],
      month_of_year_pattern: monthPatternResult.data || [],
      weekday_hour_heatmap: matrixResult.data || [],
      weekday_weekend_hourly: weekendResult.data || [],
      revenue_efficiency: revenueResult.data || [],
    };
    spatial.value = {
      map_zones: zoneMapResult.data || [],
      top_zones: zoneTopResult.data || [],
      top_zones_by_hour: zoneHotspotResult.data || [],
      zone_rank_change: zoneRankResult.data || [],
    };
    routes.value = {
      route_map: routeMapResult.data || [],
      route_table: routeTableResult.data || [],
      top_routes: topRoutesResult.data || [],
      top_airport_routes: airportRoutesResult.data || [],
      top_inter_borough_routes: interBoroughRoutesResult.data || [],
      route_borough_matrix: routeMatrixResult.data || [],
    };
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
  await loadAll({ refreshOverview: true });
}

watch(
  [
    demandMonthlyYear,
    demandMonthlyBorough,
    demandHourlyYear,
    demandMatrixYear,
    demandRevenueYear,
    zoneMapYear,
    zoneTopYear,
    zoneHotspotHour,
    zoneRankLimit,
    routeMapLens,
    routeMapScope,
    routeMapLimit,
    routeTableLens,
    routeTableScope,
    airportRouteScope,
    airportRouteLimit,
    interBoroughRouteScope,
    interBoroughRouteLimit,
    forecastZoneLimit,
    tableSource,
    tableLimit,
    tableYear,
  ],
  () => {
    if (filtersLoaded.value) {
      loadAll();
    }
  }
);

onMounted(async () => {
  await loadFilters();
  filtersLoaded.value = true;
  await loadAll({ refreshOverview: true });
});
</script>
