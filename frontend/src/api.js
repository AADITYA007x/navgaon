const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const res = await fetch(API + path, options);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export const api = {
  city: () => request("/city"),
  stats: () => request("/stats"),
  neighborhoods: () => request("/neighborhoods"),
  buildings: () => request("/buildings"),
  residents: () => request("/residents?limit=5000"),
  events: (limit = 40) => request(`/events?limit=${limit}`),
  newspaper: (day) => request(day ? `/newspaper/${day}` : "/newspaper/latest"),
  nextDay: () => request("/simulate/next-day", { method: "POST" }),
    simulate: (days) => request(`/simulate/${days}`, { method: "POST" }),
  actions: () => request("/actions"),
    autorun: () => request("/autorun"),
  doAction: (key) => request(`/actions/${key}`, { method: "POST" }),
};