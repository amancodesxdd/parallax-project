export type Verdict = "APPROVE" | "REVIEW" | "REJECT";

export type ScanRecord = {
  id: string;
  documentType: string;
  extractedData: Record<string, unknown>;
  validationResults: Record<string, unknown>;
  tamperingFlags: string[];
  faceScore: number;
  riskScore: number;
  verdict: Verdict;
  needsReview?: boolean;
  reviewedBy?: string | null;
  reviewedAt?: string | null;
  createdAt: string;
};

export type ScanDetail = {
  id: string;
  verdict: Verdict;
  riskScore: number;
  faceScore: number;
  extractedData: Record<string, unknown>;
  tamperingFlags: string[];
  forensics: {
    ocr?: { raw_text?: string; fields?: Record<string, { value: string }>; ok?: boolean };
    ai?: { aiScore?: number; isAiGenerated?: boolean; flags?: string[] };
    tamper?: { tamperScore?: number; isTampered?: boolean; flags?: string[] };
    face?: { face_score?: number; matched?: boolean; skipped?: boolean; details?: string };
  };
};

export type Stats = {
  totalScans: number;
  approved: number;
  review: number;
  rejected: number;
  blacklisted: number;
};

export type Pagination = {
  total: number;
  page: number;
  limit: number;
  pages: number;
};

export type ScanListResponse = {
  success: boolean;
  pagination: Pagination;
  data: ScanRecord[];
};

export type BlacklistEntry = {
  id: string;
  documentNumber: string;
  documentType: string | null;
  reason: string;
  addedBy: string | null;
  createdAt: string;
};

export type BlacklistCheckResult = {
  isBlacklisted: boolean;
  documentNumber: string;
  reason: string | null;
  matchId: string | null;
};

export type AuditEvent = {
  id: string;
  action: string;
  actor: string | null;
  resource: string;
  result: string;
  detail: Record<string, unknown> | null;
  createdAt: string;
};

export type AuditListResponse = {
  success: boolean;
  pagination: Pagination;
  data: AuditEvent[];
};

export const VERDICT_LABELS: Record<string, string> = {
  APPROVE: "Pass",
  REVIEW: "Review",
  REJECT: "Fail",
};

export function formatVerdict(verdict: string): string {
  return VERDICT_LABELS[verdict] ?? verdict;
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}