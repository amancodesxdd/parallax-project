import { apiGet, apiPost, type ApiSuccess } from "./apiClient";
import type { ScanListResponse, Stats } from "./types";

export async function fetchStats(): Promise<Stats> {
  const res = await apiGet<ApiSuccess<Stats>>("/stats");
  return res.data;
}

export async function fetchRecentScans(limit = 6): Promise<ScanListResponse> {
  return await apiGet<ScanListResponse>("/scans", { limit, page: 1 });
}

export async function askAssistant(message: string): Promise<string> {
  const res = await apiPost<ApiSuccess<{ answer: string }>>("/assistant", { message });
  return res.data.answer;
}