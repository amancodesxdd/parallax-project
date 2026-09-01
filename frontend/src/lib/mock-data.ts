export type Verdict = "Pass" | "Fail" | "Pending";

export const verificationHistory: {
  name: string;
  tag: string;
  id: string;
  verdict: Verdict;
  date: string;
  verifiedBy: string;
}[] = [
  { name: "Sarah Jenkins", tag: "IN", id: "VRF-9482-AD", verdict: "Pass", date: "Oct 24, 2023, 14:32", verifiedBy: "Alex Rivera" },
  { name: "Michael Chang", tag: "SG", id: "VRF-1029-9C", verdict: "Fail", date: "Oct 24, 2023, 11:15", verifiedBy: "Alex Rivera" },
  { name: "Amara Okoyo", tag: "AE", id: "VRF-8840-XX", verdict: "Pending", date: "Oct 23, 2023, 17:40", verifiedBy: "System" },
  { name: "David Vance", tag: "US", id: "VRF-7741-LP", verdict: "Pass", date: "Oct 23, 2023, 16:05", verifiedBy: "Helen Vance" },
  { name: "Elena Rostova", tag: "RU", id: "VRF-3301-KL", verdict: "Pass", date: "Oct 23, 2023, 09:22", verifiedBy: "Helen Vance" },
  { name: "Liam O'Connor", tag: "IE", id: "VRF-5542-MM", verdict: "Fail", date: "Oct 22, 2023, 15:47", verifiedBy: "Helen Vance" },
  { name: "Chloe Dupont", tag: "FR", id: "VRF-2190-QW", verdict: "Pass", date: "Oct 22, 2023, 13:11", verifiedBy: "System" },
  { name: "Marcus Aurelius", tag: "IT", id: "VRF-1100-RW", verdict: "Pending", date: "Oct 22, 2023, 10:02", verifiedBy: "Alex Rivera" },
  { name: "Yuki Tanaka", tag: "JP", id: "VRF-6743-YT", verdict: "Pass", date: "Oct 21, 2023, 18:55", verifiedBy: "Helen Vance" },
  { name: "Zahir Al-Amin", tag: "SA", id: "VRF-4491-ZA", verdict: "Pass", date: "Oct 21, 2023, 11:40", verifiedBy: "Alex Rivera" },
];

export const blacklistEntries = [
  { docType: "Passport", number: "NLD8840192A", reason: "Fraudulent document", addedBy: "Alexander W.", date: "Oct 24, 2023" },
  { docType: "Driver's License", number: "DL-TX-99842", reason: "Reported stolen", addedBy: "Marcus K.", date: "Oct 23, 2023" },
  { docType: "National ID", number: "NID-772941-K", reason: "Expired and revoked", addedBy: "Alexander W.", date: "Oct 22, 2023" },
  { docType: "Passport", number: "USA-99261945", reason: "Identity theft", addedBy: "Sarah T.", date: "Oct 20, 2023" },
  { docType: "Passport", number: "IND-4471023X", reason: "Tampering detected", addedBy: "Priya M.", date: "Oct 19, 2023" },
];

export type AuditResult = "SUCCESS" | "DENIED" | "PENDING";

export const auditTrail: {
  timestamp: string;
  actor: string;
  resource: string;
  result: AuditResult;
  supervisor?: boolean;
}[] = [
  { timestamp: "2026-08-30 05:17:30", actor: "R. Iyer (Supervisor)", resource: "VERIFICATION_APPROVE", result: "SUCCESS", supervisor: true },
  { timestamp: "2026-08-30 05:17:33", actor: "system@identra", resource: "LOG_IN", result: "SUCCESS" },
  { timestamp: "2026-08-30 05:17:29", actor: "Pramita mitra", resource: "VERIFICATION_RUN", result: "DENIED" },
  { timestamp: "2026-08-29 17:00:00", actor: "Sushant raj", resource: "BLACKLIST_ADD", result: "PENDING" },
  { timestamp: "2026-08-29 16:53:29", actor: "Mamatha paul", resource: "VERIFICATION_OVERRIDE", result: "SUCCESS" },
  { timestamp: "2026-08-29 15:26:56", actor: "Riddhi chatterjee", resource: "VERIFICATION_APPROVE", result: "DENIED" },
  { timestamp: "2026-08-29 14:39:27", actor: "Dubey sohane", resource: "VERIFICATION_RUN", result: "PENDING" },
  { timestamp: "2026-08-29 13:52:56", actor: "Krisha vedik", resource: "BLACKLIST_ADD", result: "SUCCESS" },
];

export const riskDistribution = [
  { name: "Low Risk / कम", value: 57, key: "low" },
  { name: "Medium Risk / मध्यम", value: 36, key: "medium" },
  { name: "High Risk / उच्च", value: 7, key: "high" },
];

export const weeklyVolume = [
  { day: "Mon", value: 820 },
  { day: "Tue", value: 3120 },
  { day: "Wed", value: 1980 },
  { day: "Thu", value: 3480 },
  { day: "Fri", value: 4180 },
  { day: "Sat", value: 640 },
  { day: "Sun", value: 5020 },
];

export const screeningSteps = [
  "Uploading",
  "OCR Extraction",
  "Data Validation",
  "Blacklist Check",
  "Tampering Scan",
  "AI-Generated Content Check",
  "Risk Assessment",
  "Finalizing Report",
];
