import axios, { AxiosInstance } from "axios";

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api: AxiosInstance = axios.create({ baseURL, timeout: 30_000 });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("agentforge_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export interface Agent {
  id: string;
  slug: string;
  name: string;
  description: string;
  category: string;
  tags: string[];
  price_cents: number;
  total_runs: number;
  avg_rating: number;
  rating_count: number;
  author_id: string;
}

export interface RunResult {
  id: string;
  status: string;
  output_data?: Record<string, unknown> | null;
  error_message?: string | null;
  duration_ms?: number;
  cost_cents: number;
}

export const agentsApi = {
  list: (params: { category?: string; search?: string; sort?: "popular" | "newest" | "top_rated" } = {}) =>
    api.get<Agent[]>("/agents/", { params }).then((r) => r.data),
  get: (slug: string) => api.get<Agent>(`/agents/${slug}`).then((r) => r.data),
};

export const runsApi = {
  create: (slug: string, input_data: Record<string, unknown>) =>
    api.post<RunResult>(`/runs/${slug}`, { input_data }).then((r) => r.data),
  get: (id: string) => api.get<RunResult>(`/runs/${id}`).then((r) => r.data),
};