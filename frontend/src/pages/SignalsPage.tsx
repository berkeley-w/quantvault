import { useState } from "react";
import { useSignals } from "../hooks/useSignals";
import { useStrategies } from "../hooks/useStrategies";
import { useSecurities } from "../hooks/useSecurities";
import { DataTable } from "../components/shared/DataTable";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";
import { formatDateTime } from "../lib/formatters";

export function SignalsPage() {
  const [ticker, setTicker] = useState<string>("");
  const [strategyId, setStrategyId] = useState<number | undefined>();
  const [page, setPage] = useState(1);
  const pageSize = 50;

  const { data: signals, isLoading } = useSignals(
    ticker || undefined,
    strategyId,
    undefined,
    undefined,
    page,
    pageSize
  );
  const { data: strategies } = useStrategies();
  const { data: securitiesData } = useSecurities();
  const securities = securitiesData?.items || [];

  const signalStrengthColor = (strength: number) => {
    if (strength >= 0.7) return "text-green-400";
    if (strength >= 0.4) return "text-yellow-400";
    return "text-orange-400";
  };

  const signalTypeColor = (type: string) => {
    if (type === "BUY") return "bg-green-500/20 text-green-400";
    if (type === "SELL") return "bg-red-500/20 text-red-400";
    return "bg-slate-500/20 text-slate-400";
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-100">Trading Signals</h1>

      {/* Filters */}
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Ticker
            </label>
            <select
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={ticker}
              onChange={(e) => {
                setTicker(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All tickers</option>
              {securities?.map((s) => (
                <option key={s.id} value={s.ticker}>
                  {s.ticker}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Strategy
            </label>
            <select
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={strategyId || ""}
              onChange={(e) => {
                setStrategyId(e.target.value ? Number(e.target.value) : undefined);
                setPage(1);
              }}
            >
              <option value="">All strategies</option>
              {strategies?.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Signals Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        {isLoading || !signals ? (
          <LoadingSpinner />
        ) : (
          <>
            <DataTable
              columns={[
                { key: "timestamp", header: "Timestamp", render: (r: any) => formatDateTime(r.timestamp) },
                { key: "ticker", header: "Ticker" },
                {
                  key: "signal_type",
                  header: "Type",
                  render: (r: any) => (
                    <span
                      className={`rounded px-2 py-1 text-xs font-semibold ${signalTypeColor(
                        r.signal_type
                      )}`}
                    >
                      {r.signal_type}
                    </span>
                  ),
                },
                {
                  key: "signal_strength",
                  header: "Strength",
                  align: "right",
                  render: (r: any) => (
                    <span className={signalStrengthColor(r.signal_strength)}>
                      {(r.signal_strength * 100).toFixed(1)}%
                    </span>
                  ),
                },
                {
                  key: "value",
                  header: "Indicator Value",
                  align: "right",
                  render: (r: any) => (r.value != null ? r.value.toFixed(2) : "N/A"),
                },
                { key: "strategy_id", header: "Strategy ID" },
              ]}
              data={signals.items || []}
            />
            {/* Pagination */}
            {signals.total_pages > 1 && (
              <div className="mt-4 flex items-center justify-between">
                <div className="text-sm text-slate-400">
                  Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, signals.total)} of {signals.total}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="rounded bg-slate-800 px-3 py-1 text-sm text-slate-100 hover:bg-slate-700 disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage((p) => Math.min(signals.total_pages, p + 1))}
                    disabled={page >= signals.total_pages}
                    className="rounded bg-slate-800 px-3 py-1 text-sm text-slate-100 hover:bg-slate-700 disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
