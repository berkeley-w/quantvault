interface DataLoadErrorProps {
  message?: string;
  onRetry?: () => void;
}

export function DataLoadError({ message, onRetry }: DataLoadErrorProps) {
  const isAuth = message?.toLowerCase().includes("unauthorized") || message?.includes("401");
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-8 text-slate-300">
      <p className="text-center text-sm">
        {isAuth
          ? "Session may have expired. Please log out and log in again."
          : message || "Couldn’t load data. Check your connection or try again."}
      </p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="rounded bg-slate-600 px-4 py-2 text-sm text-white hover:bg-slate-500"
        >
          Retry
        </button>
      )}
    </div>
  );
}
