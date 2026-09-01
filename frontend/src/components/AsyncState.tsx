import type { ReactNode } from "react";
import { LoaderCircle, AlertCircle, RefreshCw } from "lucide-react";

export function LoadingState({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-muted-foreground">
      <LoaderCircle className="size-6 animate-spin text-primary" />
      <p className="text-sm">{label}</p>
    </div>
  );
}

export function ErrorState({
  message = "Unable to connect to server. Please try again.",
  onRetry,
}: {
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="surface-card flex flex-col items-center justify-center gap-3 p-8 text-center">
      <AlertCircle className="size-6 text-destructive" />
      <p className="text-sm text-muted-foreground">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-1 flex items-center gap-2 rounded-lg border border-border bg-card px-3.5 py-2 text-xs font-semibold transition-colors hover:bg-muted"
        >
          <RefreshCw className="size-3.5" /> Retry
        </button>
      )}
    </div>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12 text-muted-foreground">
      <p className="text-sm">{message}</p>
    </div>
  );
}

export function AsyncBoundary({
  isLoading,
  isError,
  errorMessage,
  onRetry,
  children,
}: {
  isLoading: boolean;
  isError: boolean;
  errorMessage?: string;
  onRetry?: () => void;
  children: ReactNode;
}) {
  if (isLoading) return <LoadingState />;
  if (isError) return <ErrorState message={errorMessage} onRetry={onRetry} />;
  return <>{children}</>;
}