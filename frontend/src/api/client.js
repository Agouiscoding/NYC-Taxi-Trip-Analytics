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
  temporalStory: (params) => apiGet("/dashboard/temporal-story", params),
  spatialStory: (params) => apiGet("/dashboard/spatial-story", params),
  routesStory: (params) => apiGet("/dashboard/routes-story", params),
  businessStory: (params) => apiGet("/dashboard/business-story", params),
};
