<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand__mark">NY</div>
        <div>
          <p class="eyebrow">Big Data Project</p>
          <h1>Taxi Analytics</h1>
        </div>
      </div>

      <nav class="nav-list" aria-label="Dashboard sections">
        <button
          v-for="item in navItems"
          :key="item.key"
          type="button"
          :class="['nav-item', { active: activeView === item.key }]"
          @click="activeView = item.key"
        >
          <component :is="item.icon" :size="18" />
          <span>{{ item.label }}</span>
        </button>
      </nav>
    </aside>

    <main class="workspace">
      <header class="topbar">
        <div>
          <p class="eyebrow">MongoDB Atlas + FastAPI + Vue/D3</p>
          <h2>{{ currentTitle }}</h2>
        </div>

        <div class="filters">
          <label>
            <span>Year</span>
            <select v-model="selectedYear">
              <option :value="null">All</option>
              <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
            </select>
          </label>
          <label>
            <span>Borough</span>
            <select v-model="selectedBorough">
              <option value="">All</option>
              <option v-for="borough in boroughs" :key="borough" :value="borough">
                {{ borough }}
              </option>
            </select>
          </label>
          <label>
            <span>Hour</span>
            <select v-model.number="selectedHour">
              <option v-for="hour in hours" :key="hour" :value="hour">
                {{ String(hour).padStart(2, "0") }}:00
              </option>
            </select>
          </label>
          <button class="icon-button" type="button" title="Reload data" @click="loadAll">
            <RefreshCw :size="18" />
          </button>
        </div>
      </header>

      <div v-if="error" class="error-banner">{{ error }}</div>
      <div v-if="loading" class="loading-bar" />

      <KpiGrid :items="kpiItems" />

      <section v-if="activeView === 'overview'" class="dashboard-grid">
        <ChartPanel class="span-2" title="Demand Trend" eyebrow="Overview">
          <LineChart :data="overview.year_month_demand || []" x-key="year_month" y-key="total_trips" />
        </ChartPanel>
        <ChartPanel title="Hourly Pattern" eyebrow="Temporal">
          <BarChart :data="overview.hourly_demand || []" x-key="hour" y-key="total_trips" color="#2f6fbb" />
        </ChartPanel>
        <ChartPanel title="Top Pickup Zones" eyebrow="Spatial">
          <HorizontalBarChart
            :data="overview.top_zones || []"
            label-key="pickup_zone"
            value-key="total_trips"
            color="#2f855a"
          />
        </ChartPanel>
        <ChartPanel class="span-2" title="Weekday-Hour Demand" eyebrow="Heatmap">
          <HeatmapChart
            :data="overview.weekday_hour_heatmap || []"
            x-key="hour"
            y-key="weekday_name"
            value-key="total_trips"
            :x-domain="hours"
            :y-domain="weekdayDomain"
          />
        </ChartPanel>
        <ChartPanel class="span-2" title="Taxi Zone Demand Map" eyebrow="Map">
          <TaxiZoneMap :metrics="overview.top_zones || []" metric-key="total_trips" />
        </ChartPanel>
        <ChartPanel class="span-2" title="Top Routes" eyebrow="Routes">
          <DataTable :rows="overview.top_routes || []" :columns="routeColumns" :limit="8" />
        </ChartPanel>
      </section>

      <section v-else-if="activeView === 'temporal'" class="dashboard-grid">
        <ChartPanel title="Yearly Demand" eyebrow="Multi-year">
          <LineChart :data="temporal.yearly_summary || []" x-key="year" y-key="total_trips" />
        </ChartPanel>
        <ChartPanel title="Month Pattern" eyebrow="Seasonality">
          <BarChart
            :data="temporal.month_of_year_pattern || []"
            x-key="month_name"
            y-key="avg_trips_per_active_year"
            color="#137b80"
          />
        </ChartPanel>
        <ChartPanel class="span-2" title="Monthly Demand" eyebrow="Timeline">
          <LineChart :data="temporal.year_month_demand || []" x-key="year_month" y-key="total_trips" />
        </ChartPanel>
        <ChartPanel class="span-2" title="Weekday-Hour Heatmap" eyebrow="Temporal">
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
        <ChartPanel class="span-2" title="Borough Monthly Trend" eyebrow="Spatial time">
          <LineChart
            :data="temporal.borough_year_month || []"
            x-key="year_month"
            y-key="total_trips"
            series-key="pickup_borough"
          />
        </ChartPanel>
      </section>

      <section v-else-if="activeView === 'spatial'" class="dashboard-grid">
        <ChartPanel class="span-2" title="Taxi Zone Choropleth" eyebrow="Spatial">
          <TaxiZoneMap :metrics="spatial.top_zones || []" metric-key="total_trips" />
        </ChartPanel>
        <ChartPanel title="Top Zones" eyebrow="Ranking">
          <HorizontalBarChart
            :data="spatial.top_zones || []"
            label-key="pickup_zone"
            value-key="total_trips"
            color="#2f855a"
          />
        </ChartPanel>
        <ChartPanel title="Hotspots by Selected Hour" eyebrow="Hour slider">
          <HorizontalBarChart
            :data="spatial.top_zones_by_hour || []"
            label-key="pickup_zone"
            value-key="total_trips"
            color="#b7791f"
          />
        </ChartPanel>
        <ChartPanel class="span-2" title="Zone Rank Change" eyebrow="2021-2024">
          <DataTable :rows="spatial.zone_rank_change || []" :columns="zoneRankColumns" :limit="20" />
        </ChartPanel>
      </section>

      <section v-else-if="activeView === 'routes'" class="dashboard-grid">
        <ChartPanel class="span-2" title="Route Flow Map" eyebrow="Network">
          <RouteFlowMap :routes="routes.top_routes || []" :limit="35" />
        </ChartPanel>
        <ChartPanel class="span-2" title="Top Routes" eyebrow="Pickup to dropoff">
          <DataTable :rows="routes.top_routes || []" :columns="routeColumns" :limit="12" />
        </ChartPanel>
        <ChartPanel class="span-2" title="Borough Route Matrix" eyebrow="OD matrix">
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
            color="#2f6fbb"
          />
        </ChartPanel>
        <ChartPanel title="Inter-Borough Routes" eyebrow="Cross borough">
          <HorizontalBarChart
            :data="routes.top_inter_borough_routes || []"
            label-key="route_name"
            value-key="trip_count"
            color="#c2415d"
          />
        </ChartPanel>
        <ChartPanel title="Revenue per Mile" eyebrow="Efficiency">
          <HorizontalBarChart
            :data="routes.route_efficiency_ranking || []"
            label-key="route_name"
            value-key="revenue_per_mile"
            color="#137b80"
          />
        </ChartPanel>
        <ChartPanel title="Tip Share" eyebrow="Payment behavior">
          <HorizontalBarChart
            :data="routes.route_tip_ranking || []"
            label-key="route_name"
            value-key="route_tip_share"
            color="#b7791f"
          />
        </ChartPanel>
      </section>

      <section v-else class="dashboard-grid">
        <ChartPanel title="Payment Type" eyebrow="Business">
          <HorizontalBarChart
            :data="business.payment_type || []"
            label-key="payment_type_desc"
            value-key="trip_count"
            color="#2f6fbb"
          />
        </ChartPanel>
        <ChartPanel title="Trip Behavior by Hour" eyebrow="Hourly">
          <LineChart :data="business.trip_behavior_by_hour || []" x-key="hour" y-key="avg_revenue_per_trip" />
        </ChartPanel>
        <ChartPanel class="span-2" title="Payment Type Table" eyebrow="Details">
          <DataTable :rows="business.payment_type || []" :columns="paymentColumns" :limit="12" />
        </ChartPanel>
      </section>
    </main>
  </div>
</template>

<script setup>
import {
  BarChart3,
  CarTaxiFront,
  Map,
  RefreshCw,
  Route,
  WalletCards,
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
import ChartPanel from "@/components/layout/ChartPanel.vue";
import KpiGrid from "@/components/layout/KpiGrid.vue";
import { compact, decimal, integer, money, pct } from "@/utils/format";

const navItems = [
  { key: "overview", label: "Overview", icon: BarChart3 },
  { key: "temporal", label: "Temporal", icon: CarTaxiFront },
  { key: "spatial", label: "Spatial", icon: Map },
  { key: "routes", label: "Routes", icon: Route },
  { key: "business", label: "Business", icon: WalletCards },
];
const weekdayDomain = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const hours = Array.from({ length: 24 }, (_, index) => index);

const activeView = ref("overview");
const loading = ref(false);
const error = ref("");
const years = ref([]);
const boroughs = ref([]);
const selectedYear = ref(null);
const selectedBorough = ref("");
const selectedHour = ref(18);
const overview = ref({});
const temporal = ref({});
const spatial = ref({});
const routes = ref({});
const business = ref({});

const currentTitle = computed(() => navItems.find((item) => item.key === activeView.value)?.label || "Dashboard");
const selectedYearSummary = computed(() => {
  const rows = overview.value.yearly_summary || [];
  return rows.find((row) => row.year === selectedYear.value) || rows.at(-1) || {};
});
const kpiSource = computed(() => (selectedYear.value ? selectedYearSummary.value : overview.value.kpi || {}));
const kpiItems = computed(() => [
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
  {
    label: "Active Days",
    value: integer(kpiSource.value.active_days),
    note: "Coverage after pipeline",
  },
  {
    label: "Pickup Zones",
    value: integer(kpiSource.value.active_pickup_zones),
    note: "Joined with taxi zone lookup",
  },
]);

const routeColumns = [
  { key: "route_rank", label: "Rank", numeric: true, format: integer },
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
const paymentColumns = [
  { key: "payment_type_desc", label: "Payment Type" },
  { key: "trip_count", label: "Trips", numeric: true, format: integer },
  { key: "total_revenue", label: "Revenue", numeric: true, format: money },
  { key: "avg_revenue_per_trip", label: "Revenue / Trip", numeric: true, format: money },
  { key: "avg_tip_share_of_total", label: "Tip Share", numeric: true, format: pct },
];

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
    const [overviewResult, temporalResult, spatialResult, routesResult, businessResult] = await Promise.all([
      api.overview({ year: selectedYear.value, zone_limit: 20, route_limit: 12 }),
      api.temporalStory(params),
      api.spatialStory({ year: selectedYear.value, hour: selectedHour.value, zone_limit: 25 }),
      api.routesStory({ route_limit: 25 }),
      api.businessStory({ year: selectedYear.value }),
    ]);

    overview.value = overviewResult.data;
    temporal.value = temporalResult.data;
    spatial.value = spatialResult.data;
    routes.value = routesResult.data;
    business.value = businessResult.data;
  } catch (caught) {
    error.value = caught.message || "Failed to load dashboard data.";
  } finally {
    loading.value = false;
  }
}

watch([selectedYear, selectedBorough, selectedHour], loadAll);

onMounted(async () => {
  await loadFilters();
  await loadAll();
});
</script>
