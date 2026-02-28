import { useMetrics } from "../hooks/useHoldings";
import { useAnalytics, usePortfolioPerformance } from "../hooks/useAnalytics";
import { useSecurities } from "../hooks/useSecurities";
import { usePriceRefresh } from "../hooks/usePriceRefresh";
import { useRiskMetrics } from "../hooks/useRisk";
import { useSignals } from "../hooks/useSignals";
import { useSnapshots } from "../hooks/useAnalytics";
import { MetricCard } from "../components/shared/MetricCard";
import { DataTable } from "../components/shared/DataTable";
import { formatCurrency, formatPercent, pnlColor } from "../lib/formatters";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";
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

export function DashboardPage() {
  const { data: metrics, isLoading: metricsLoading } = useMetrics();
  const {
    data: perf,
    isLoading: perfLoading,
  } = usePortfolioPerformance();
  const { data: analytics } = useAnalytics();
  const { startRefresh, isRefreshing } = usePriceRefresh();
  const { data: securitiesData } = useSecurities();
  const securities = securitiesData?.items || [];
  const { data: riskMetrics } = useRiskMetrics();
  const { data: recentSignals } = useSignals(undefined, undefined, undefined, undefined, 1, 10);
  const { data: snapshots } = useSnapshots();

  const sharesByTicker =
    securities?.items?.reduce<Record<string, number | null>>((acc, sec) => {
      acc[sec.ticker] = sec.shares_outstanding ?? null;
      return acc;
    }, {}) ?? {};

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-100">
          Portfolio Dashboard
        </h1>
        <button
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
          onClick={() => startRefresh()}
          disabled={isRefreshing}
        >
          {isRefreshing ? "Refreshing prices…" : "Refresh Prices & Performance"}
        </button>
      </div>

      {/* Metrics */}
      {metricsLoading || !metrics ? (
        <LoadingSpinner />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            label="Total Market Value"
            value={formatCurrency(metrics.total_market_value)}
          />
          <MetricCard
            label="Unrealized P&L"
            value={formatCurrency(metrics.total_unrealized_pnl)}
            trend={metrics.total_unrealized_pnl >= 0 ? "up" : "down"}
          />
          <MetricCard
            label="Open Positions"
            value={metrics.number_of_positions}
          />
          <MetricCard
            label="Trades (Active / Rejected / Total)"
            value={`${metrics.trades_active_count} / ${metrics.trades_rejected_count} / ${metrics.trades_total_count}`}
          />
        </div>
      )}

      {/* Sector Breakdown */}
      {metrics && (
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
            <h2 className="mb-3 text-sm font-semibold text-slate-200">
              Sector Breakdown
            </h2>
            <DataTable
              columns={[
                { key: "sector", header: "Sector" },
                { key: "value", header: "Market Value", align: "right" },
                { key: "percent", header: "% of Portfolio", align: "right" },
              ]}
              data={Object.entries(metrics.sector_breakdown || {}).map(
                ([sector, value]) => ({
                  sector,
                  value: formatCurrency(value),
                  percent:
                    metrics.total_market_value > 0
                      ? formatPercent(
                          (value / metrics.total_market_value) * 100
                        )
                      : "0.00%",
                })
              )}
            />
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
            <h2 className="mb-3 text-sm font-semibold text-slate-200">
              Top Holdings
            </h2>
            <DataTable
              columns={[
                { key: "ticker", header: "Ticker" },
                { key: "net_quantity", header: "Net Qty", align: "right" },
                {
                  key: "avg_cost",
                  header: "Avg Cost",
                  align: "right",
                  render: (row: any) => formatCurrency(row.avg_cost),
                },
                {
                  key: "current_price",
                  header: "Price",
                  align: "right",
                  render: (row: any) => formatCurrency(row.current_price),
                },
                {
                  key: "market_value",
                  header: "Market Value",
                  align: "right",
                  render: (row: any) => formatCurrency(row.market_value),
                },
                {
                  key: "unrealized_pnl",
                  header: "Unrealized P&L",
                  align: "right",
                  render: (row: any) => (
                    <span className={pnlColor(row.unrealized_pnl)}>
                      {formatCurrency(row.unrealized_pnl)}
                    </span>
                  ),
                },
                {
                  key: "ownership_pct",
                  header: "Ownership %",
                  align: "right",
                  render: (row: any) => {
                    const shares = sharesByTicker[row.ticker];
                    if (!shares || shares <= 0) return "N/A";
                    const pct = (row.net_quantity / shares) * 100;
                    return formatPercent(pct);
                  },
                },
              ]}
              data={metrics.top_holdings || []}
            />
          </div>
        </div>
      )}

      {/* Performance table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        <h2 className="mb-3 text-sm font-semibold text-slate-200">
          Portfolio Performance
        </h2>
        {perfLoading || !perf ? (
          <LoadingSpinner />
        ) : (
          <>
            <div className="mb-4 grid gap-4 md:grid-cols-4">
              <MetricCard
                label="Total Market Value"
                value={formatCurrency(perf.total_market_value)}
              />
              <MetricCard
                label="Total Cost Basis"
                value={formatCurrency(perf.total_cost_basis)}
              />
              <MetricCard
                label="Total P&L"
                value={formatCurrency(perf.total_pnl)}
                trend={perf.total_pnl >= 0 ? "up" : "down"}
              />
              <MetricCard
                label="Total P&L %"
                value={
                  perf.total_pnl_pct != null
                    ? formatPercent(perf.total_pnl_pct)
                    : "N/A"
                }
                trend={
                  perf.total_pnl_pct != null && perf.total_pnl_pct >= 0
                    ? "up"
                    : "down"
                }
              />
            </div>
            <DataTable
              columns={[
                { key: "ticker", header: "Ticker" },
                { key: "net_quantity", header: "Net Qty", align: "right" },
                {
                  key: "avg_cost",
                  header: "Avg Cost",
                  align: "right",
                  render: (row: any) => formatCurrency(row.avg_cost),
                },
                {
                  key: "current_price",
                  header: "Price",
                  align: "right",
                  render: (row: any) => formatCurrency(row.current_price),
                },
                {
                  key: "cost_basis",
                  header: "Cost Basis",
                  align: "right",
                  render: (row: any) => formatCurrency(row.cost_basis),
                },
                {
                  key: "market_value",
                  header: "Market Value",
                  align: "right",
                  render: (row: any) => formatCurrency(row.market_value),
                },
                {
                  key: "pnl",
                  header: "P&L",
                  align: "right",
                  render: (row: any) => (
                    <span className={pnlColor(row.pnl)}>
                      {formatCurrency(row.pnl)}
                    </span>
                  ),
                },
                {
                  key: "pnl_pct",
                  header: "P&L %",
                  align: "right",
                  render: (row: any) =>
                    row.pnl_pct != null ? formatPercent(row.pnl_pct) : "N/A",
                },
              ]}
              data={perf.breakdown || []}
            />
          </>
        )}
      </div>

      {/* Risk Metrics Summary */}
      {riskMetrics && (
        <div className="grid gap-4 md:grid-cols-4">
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
            label="Sharpe Ratio"
            value={
              riskMetrics.sharpe_ratio != null
                ? riskMetrics.sharpe_ratio.toFixed(2)
                : "N/A"
            }
          />
          <MetricCard
            label="Concentration"
            value={riskMetrics.concentration.concentration_rating}
          />
        </div>
      )}

      {/* Recent Signals */}
      {recentSignals && recentSignals.items && recentSignals.items.length > 0 && (
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
          <h2 className="mb-3 text-sm font-semibold text-slate-200">Recent Signals</h2>
          <DataTable
            columns={[
              { key: "ticker", header: "Ticker" },
              {
                key: "signal_type",
                header: "Type",
                render: (r: any) => (
                  <span
                    className={`rounded px-2 py-1 text-xs ${
                      r.signal_type === "BUY"
                        ? "bg-green-500/20 text-green-400"
                        : r.signal_type === "SELL"
                        ? "bg-red-500/20 text-red-400"
                        : "bg-slate-500/20 text-slate-400"
                    }`}
                  >
                    {r.signal_type}
                  </span>
                ),
              },
              {
                key: "signal_strength",
                header: "Strength",
                align: "right",
                render: (r: any) => `${(r.signal_strength * 100).toFixed(1)}%`,
              },
              {
                key: "timestamp",
                header: "Time",
                render: (r: any) => new Date(r.timestamp).toLocaleString(),
              },
            ]}
            data={recentSignals.items.slice(0, 5)}
          />
        </div>
      )}

      {/* Portfolio Equity Curve */}
      {snapshots && snapshots.snapshots.length > 0 && (
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
          <h2 className="mb-4 text-sm font-semibold text-slate-200">
            Portfolio Equity Curve
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart
              data={snapshots.snapshots.map((s) => ({
                date: new Date(s.date).toLocaleDateString(),
                value: s.total_market_value,
                pnl: s.total_pnl,
              }))}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1e293b",
                  border: "1px solid #334155",
                  borderRadius: "8px",
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#10b981"
                strokeWidth={2}
                name="Portfolio Value"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

