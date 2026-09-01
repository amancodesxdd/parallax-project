import { apiDelete, apiGet, type ApiSuccess } from "./apiClient";
import type { AuditListResponse } from "./types";

export async function fetchAuditEvents(params?: {
  page?: number;
  limit?: number;
  resource?: string;
  result?: string;
  actor?: string;
}): Promise<AuditListResponse> {
  return await apiGet<AuditListResponse>("/audit", {
    page: params?.page,
    limit: params?.limit,
    resource: params?.resource,
    result: params?.result,
    actor: params?.actor,
  });
}

export async function deleteAuditEvent(id: string): Promise<void> {
  await apiDelete<ApiSuccess<{ message: string }>>(`/audit/${id}`);
}