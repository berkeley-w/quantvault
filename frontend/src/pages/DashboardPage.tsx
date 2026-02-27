import { useMetrics } from "../hooks/useHoldings";
import { useAnalytics, usePortfolioPerformance } from "../hooks/useAnalytics";
import { usePriceRefresh } from "../hooks/usePriceRefresh";
import { MetricCard } from "../components/shared/MetricCard";
import { DataTable } from "../components/shared/DataTable";
import { formatCurrency, formatPercent, pnlColor } from "../lib/formatters";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";

export function DashboardPage() {
  const { data: metrics, isLoading: metricsLoading } = useMetrics();
  const {
    data: perf,
    isLoading: perfLoading,
  } = usePortfolioPerformance();
  const { data: analytics } = useAnalytics();
  const { startRefresh, isRefreshing } = usePriceRefresh();

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

      {/* Optional summary from analytics (beta, concentration) */}
      {analytics && (
        <div className="grid gap-4 md:grid-cols-3">
          <MetricCard
            label="Portfolio Beta"
            value={
              analytics.portfolio.portfolio_beta != null
                ? analytics.portfolio.portfolio_beta.toFixed(2)
                : "N/A"
            }
          />
          <MetricCard
            label="HHI Concentration"
            value={analytics.portfolio.hhi_concentration.toFixed(3)}
          />
          <MetricCard
            label="Concentration Rating"
            value={analytics.portfolio.concentration_rating}
          />
        </div>
      )}
    </div>
  );
}

