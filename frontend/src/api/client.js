const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8001/api";

function buildUrl(path, params = {}) {
  const url = new URL(`${API_BASE}${path}`);

  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") {
      url.searchParams.set(key, value);
    }
  });

  return url;
}

export async function apiGet(path, params = {}) {
  const response = await fetch(buildUrl(path, params));

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`API ${response.status}: ${detail}`);
  }

  return response.json();
}

export const api = {
  filters: () => apiGet("/meta/filters"),
  overview: (params) => apiGet("/dashboard/overview", params),
  businessStory: (params) => apiGet("/dashboard/business-story", params),
  forecastStory: (params) => apiGet("/forecast/story", params),
  yearMonthDemand: (params) => apiGet("/temporal/year-month-demand", params),
  hourlyDemand: (params) => apiGet("/temporal/hourly-demand", params),
  weekdayHourHeatmap: (params) => apiGet("/temporal/weekday-hour-heatmap", params),
  boroughYearMonth: (params) => apiGet("/temporal/borough-year-month", params),
  monthOfYearPattern: () => apiGet("/temporal/month-of-year-pattern"),
  weekdayWeekendHourly: (params) => apiGet("/temporal/weekday-weekend-hourly", params),
  revenueEfficiency: (params) => apiGet("/temporal/revenue-efficiency", params),
  topZones: (params) => apiGet("/spatial/top-zones", params),
  topZonesByHour: (params) => apiGet("/spatial/top-zones-by-hour", params),
  zoneRankChange: (params) => apiGet("/spatial/zone-rank-change", params),
  routesTop: (params) => apiGet("/routes/top", params),
  routesAirport: (params) => apiGet("/routes/airport", params),
  routesInterBorough: (params) => apiGet("/routes/inter-borough", params),
  routeBoroughMatrix: () => apiGet("/routes/borough-matrix"),
  routeConcentration: (params) => apiGet("/routes/concentration", params),
  mapOdFlowHour: (params) => apiGet("/map/od-flow-hour", params),
  mapOdFlowYearMonth: (params) => apiGet("/map/od-flow-year-month", params),
  zoneProfiles: (params) => apiGet("/profiles/zones", params),
  zoneProfile: (locationId) => apiGet(`/profiles/zones/${locationId}`),
  routeProfile: (pickupLocationId, dropoffLocationId) =>
    apiGet(`/profiles/routes/${pickupLocationId}/${dropoffLocationId}`),
};
