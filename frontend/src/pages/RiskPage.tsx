import { useRiskMetrics } from "../hooks/useRisk";
import { useSnapshots } from "../hooks/useAnalytics";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";
import { MetricCard } from "../components/shared/MetricCard";
import { formatCurrency, formatPercent } from "../lib/formatters";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export function RiskPage() {
  const { data: riskMetrics, isLoading: riskLoading } = useRiskMetrics();
  const { data: snapshots } = useSnapshots();

  // Prepare drawdown chart data
  const drawdownData =
    snapshots?.snapshots.map((s, idx) => {
      const prev = idx > 0 ? snapshots.snapshots[idx - 1] : null;
      const drawdown =
        prev && prev.total_market_value > 0
          ? ((s.total_market_value - prev.total_market_value) / prev.total_market_value) * 100
          : 0;
      return {
        date: new Date(s.date).toLocaleDateString(),
        value: s.total_market_value,
        drawdown: drawdown,
      };
    }) || [];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-100">Risk Dashboard</h1>

      {riskLoading || !riskMetrics ? (
        <LoadingSpinner />
      ) : (
        <>
          {/* Risk Metrics */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <MetricCard
              label="Portfolio Beta"
              value={riskMetrics.portfolio_beta.toFixed(2)}
            />
            <MetricCard
              label="VaR (95%)"
              value={
                riskMetrics.var_95 != null
                  ? formatPercent(riskMetrics.var_95 * 100)
                  : "N/A"
              }
            />
            <MetricCard
              label="VaR (99%)"
              value={
                riskMetrics.var_99 != null
                  ? formatPercent(riskMetrics.var_99 * 100)
                  : "N/A"
              }
            />
            <MetricCard
              label="Sharpe Ratio"
              value={
                riskMetrics.sharpe_ratio != null
                  ? riskMetrics.sharpe_ratio.toFixed(2)
                  : "N/A"
              }
            />
          </div>

          {/* Max Drawdown */}
          {riskMetrics.max_drawdown && (
            <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
              <h2 className="mb-3 text-sm font-semibold text-slate-200">
                Maximum Drawdown
              </h2>
              <div className="grid gap-4 md:grid-cols-4">
                <MetricCard
                  label="Max Drawdown"
                  value={formatCurrency(riskMetrics.max_drawdown.max_drawdown)}
                />
                <MetricCard
                  label="Max Drawdown %"
                  value={formatPercent(riskMetrics.max_drawdown.max_drawdown_pct)}
                />
                <div className="text-sm text-slate-400">
                  <div>Peak: {riskMetrics.max_drawdown.peak_date || "N/A"}</div>
                  <div>Trough: {riskMetrics.max_drawdown.trough_date || "N/A"}</div>
                </div>
              </div>
            </div>
          )}

          {/* Concentration Metrics */}
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
            <h2 className="mb-3 text-sm font-semibold text-slate-200">
              Concentration Analysis
            </h2>
            <div className="grid gap-4 md:grid-cols-4">
              <MetricCard
                label="HHI"
                value={riskMetrics.concentration.hhi.toFixed(4)}
              />
              <MetricCard
                label="Concentration Rating"
                value={riskMetrics.concentration.concentration_rating}
              />
              <MetricCard
                label="Top Position %"
                value={formatPercent(riskMetrics.concentration.top_position_pct)}
              />
              <MetricCard
                label="Top 5 Positions %"
                value={formatPercent(riskMetrics.concentration.top_5_positions_pct)}
              />
            </div>
          </div>

          {/* Drawdown Chart */}
          {drawdownData.length > 0 && (
            <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
              <h2 className="mb-4 text-sm font-semibold text-slate-200">
                Portfolio Value & Drawdown
              </h2>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={drawdownData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="date" stroke="#94a3b8" />
                  <YAxis yAxisId="left" stroke="#94a3b8" />
                  <YAxis yAxisId="right" orientation="right" stroke="#94a3b8" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#1e293b",
                      border: "1px solid #334155",
                      borderRadius: "8px",
                    }}
                  />
                  <Legend />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="value"
                    stroke="#10b981"
                    strokeWidth={2}
                    name="Portfolio Value"
                    dot={false}
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="drawdown"
                    stroke="#ef4444"
                    strokeWidth={1}
                    name="Drawdown %"
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}
    </div>
  );
}
