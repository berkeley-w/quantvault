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

  const isNumericValue =
    typeof value === "number" ||
    (typeof value === "string" && /[0-9]/.test(value));

  const valueAlignment = isNumericValue ? "text-right tabular-nums" : "text-left";

  return (
    <div
      className={`rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 shadow-sm ${className || ""}`}
    >
      <div className="text-xs font-medium uppercase tracking-wide text-slate-400">
        {label}
      </div>
      <div className={`mt-1 text-xl md:text-2xl font-semibold ${trendColor} ${valueAlignment} break-words`}>
        {value}
      </div>
    </div>
  );
}

