import { ReactNode } from "react";

type Trend = "up" | "down" | "neutral";

interface MetricCardProps {
  label: string;
  value: string | number | ReactNode;
  trend?: Trend;
  className?: string;
}

export function MetricCard({ label, value, trend = "neutral", className }: MetricCardProps) {
  const trendColor =
    trend === "up" ? "text-green-400" : trend === "down" ? "text-red-400" : "text-slate-100";

  const asString =
    typeof value === "string" || typeof value === "number"
      ? String(value)
      : undefined;

  // Dynamically scale font size for very long values to keep them on one line
  const length = asString ? asString.length : 0;
  const sizeClass =
    length > 18 ? "text-sm sm:text-base md:text-lg" : length > 12 ? "text-base sm:text-lg md:text-xl" : "text-lg sm:text-xl md:text-2xl";

  return (
    <div
      className={`flex h-full flex-col justify-between rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 shadow-sm ${className || ""}`}
    >
      <div className="text-xs font-medium uppercase tracking-wide text-slate-400">
        {label}
      </div>
      <div
        className={`mt-1 font-semibold ${trendColor} ${sizeClass} text-left leading-tight tabular-nums whitespace-nowrap overflow-hidden`}
      >
        {value}
      </div>
    </div>
  );
}

