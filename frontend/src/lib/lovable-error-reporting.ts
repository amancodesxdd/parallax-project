export type LovableErrorContext = {
  boundary?: string;
  [key: string]: unknown;
};

export function reportLovableError(error: unknown, context?: LovableErrorContext) {
  if (import.meta.env.DEV) {
    console.warn("[lovable-error-reporting] boundary error", { error, context });
  }
}
