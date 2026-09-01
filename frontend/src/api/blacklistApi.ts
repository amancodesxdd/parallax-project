import { apiDelete, apiGet, apiPost, type ApiSuccess } from "./apiClient";
import type { BlacklistCheckResult, BlacklistEntry } from "./types";

export async function fetchBlacklist(search?: string): Promise<BlacklistEntry[]> {
  const res = await apiGet<ApiSuccess<BlacklistEntry[]>>("/blacklist", { search });
  return res.data;
}

export async function addBlacklistEntry(input: {
  documentNumber: string;
  reason?: string;
  addedBy?: string;
  documentType?: string;
}): Promise<BlacklistEntry> {
  const res = await apiPost<ApiSuccess<BlacklistEntry>>("/blacklist", input);
  return res.data;
}

export async function deleteBlacklistEntry(id: string): Promise<void> {
  await apiDelete<ApiSuccess<{ message: string }>>(`/blacklist/${id}`);
}

export async function checkBlacklist(documentNumber: string): Promise<BlacklistCheckResult> {
  const res = await apiPost<ApiSuccess<BlacklistCheckResult>>("/blacklist/check", { documentNumber });
  return res.data;
}