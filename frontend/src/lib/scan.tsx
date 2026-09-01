import { createContext, useContext, useState, type ReactNode } from "react";

export type ScanVerdict = "LOW_RISK" | "HIGH_RISK" | "FAIL";

export interface ScanResult {
  id: string;
  verdict: ScanVerdict;
  riskScore: number;
  faceScore: number;
  extractedData: Record<string, string | number | null>;
  tamperingFlags: string[];
  evidenceImageUrl: string | null;
  forensics?: {
    ai?: { score?: number };
    tamper?: { score?: number };
    face?: { score?: number };
    ocr?: unknown;
  };
}

interface ScanContextValue {
  scanResult: ScanResult | null;
  scanLoading: boolean;
  scanError: string | null;
  setScanResult: (result: ScanResult) => void;
  setScanLoading: (loading: boolean) => void;
  setScanError: (error: string | null) => void;
  resetScan: () => void;
}

const ScanContext = createContext<ScanContextValue | undefined>(undefined);

export function ScanProvider({ children }: { children: ReactNode }) {
  const [scanResult, setScanResultState] = useState<ScanResult | null>(null);
  const [scanLoading, setScanLoading] = useState(false);
  const [scanError, setScanError] = useState<string | null>(null);

  const setScanResult = (result: ScanResult) => {
    setScanResultState(result);
    setScanError(null);
  };

  const resetScan = () => {
    setScanResultState(null);
    setScanLoading(false);
    setScanError(null);
  };

  return (
    <ScanContext.Provider
      value={{
        scanResult,
        scanLoading,
        scanError,
        setScanResult,
        setScanLoading,
        setScanError,
        resetScan,
      }}
    >
      {children}
    </ScanContext.Provider>
  );
}

export function useScan() {
  const ctx = useContext(ScanContext);
  if (!ctx) throw new Error("useScan must be used within a ScanProvider");
  return ctx;
}
