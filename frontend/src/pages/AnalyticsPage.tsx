import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LineChart,
  Line,
} from "recharts";
import { useAnalytics, usePortfolioPerformance, useSnapshots, useTradeAnalytics } from "../hooks/useAnalytics";
import { MetricCard } from "../components/shared/MetricCard";
import { DataTable } from "../components/shared/DataTable";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";
import { formatCurrency, formatPercent, pnlColor } from "../lib/formatters";

const COLORS = ["#60a5fa", "#22c55e", "#a855f7", "#eab308", "#f97316", "#38bdf8"];

export function AnalyticsPage() {
  const { data: analytics, isLoading: loadingAnalytics } = useAnalytics();
  const { data: perf } = usePortfolioPerformance();
  const { data: snapshots } = useSnapshots();
  const { data: tradeAnalytics, isLoading: loadingTradeAnalytics } =
    useTradeAnalytics();

  const positions = analytics?.positions || [];
  const sectorAlloc =
    analytics?.portfolio?.sector_allocation || ({} as Record<string, any>);

  const snapshotSeries = snapshots?.snapshots || [];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-100">
        Portfolio Analytics
      </h1>

      {loadingAnalytics || !analytics ? (
        <LoadingSpinner />
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
            <MetricCard
              label="Total Market Value"
              value={formatCurrency(analytics.portfolio.total_market_value)}
            />
            <MetricCard
              label="Total Cost Basis"
              value={formatCurrency(analytics.portfolio.total_cost_basis)}
            />
            <MetricCard
              label="Total P&L"
              value={formatCurrency(analytics.portfolio.total_pnl)}
              trend={
                analytics.portfolio.total_pnl >= 0 ? "up" : "down"
              }
            />
            <MetricCard
              label="Total P&L %"
              value={
                analytics.portfolio.total_pnl_pct != null
                  ? formatPercent(analytics.portfolio.total_pnl_pct)
                  : "N/A"
              }
            />
            <MetricCard
              label="Portfolio Beta"
              value={analytics.portfolio.portfolio_beta.toFixed(2)}
            />
            <MetricCard
              label="Concentration"
              value={analytics.portfolio.concentration_rating}
            />
          </div>

          {/* Positions table */}
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
            <h2 className="mb-3 text-sm font-semibold text-slate-200">
              Position Analytics
            </h2>
            <DataTable
              columns={[
                { key: "ticker", header: "Ticker" },
                { key: "sector", header: "Sector" },
                { key: "market_value", header: "Mkt Value", align: "right", render: (r: any) => formatCurrency(r.market_value) },
                { key: "pnl", header: "P&L", align: "right", render: (r: any) => <span className={pnlColor(r.pnl)}>{formatCurrency(r.pnl)}</span> },
                { key: "pnl_pct", header: "P&L %", align: "right", render: (r: any) => r.pnl_pct != null ? formatPercent(r.pnl_pct) : "N/A" },
                { key: "portfolio_weight_pct", header: "Weight %", align: "right", render: (r: any) => formatPercent(r.portfolio_weight_pct) },
                { key: "beta", header: "Beta", align: "right" },
              ]}
              data={positions}
            />
          </div>

          {/* Trade performance cards */}
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
            <h2 className="mb-3 text-sm font-semibold text-slate-200">
              Trade Performance
            </h2>
            {loadingTradeAnalytics || !tradeAnalytics ? (
              <LoadingSpinner />
            ) : (
              <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
                <MetricCard
                  label="Total Trades"
                  value={tradeAnalytics.total_trades}
                />
                <MetricCard
                  label="Buy Trades"
                  value={tradeAnalytics.buy_trades}
                />
                <MetricCard
                  label="Sell Trades"
                  value={tradeAnalytics.sell_trades}
                />
                <MetricCard
                  label="Win Rate"
                  value={
                    tradeAnalytics.win_rate_pct != null
                      ? formatPercent(tradeAnalytics.win_rate_pct)
                      : "N/A"
                  }
                />
                <MetricCard
                  label="Avg Win"
                  value={
                    tradeAnalytics.average_win != null
                      ? formatCurrency(tradeAnalytics.average_win)
                      : "N/A"
                  }
                  trend="up"
                />
                <MetricCard
                  label="Avg Loss"
                  value={
                    tradeAnalytics.average_loss != null
                      ? formatCurrency(tradeAnalytics.average_loss)
                      : "N/A"
                  }
                  trend="down"
                />
              </div>
            )}
          </div>

          {/* Charts */}
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Allocation by position */}
            <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
              <h3 className="mb-2 text-sm font-semibold text-slate-200">
                Allocation by Position
              </h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={positions}
                      dataKey="portfolio_weight_pct"
                      nameKey="ticker"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label
                    >
                      {positions.map((_, idx) => (
                        <Cell
                          key={idx}
                          fill={COLORS[idx % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#1e293b",
                        border: "1px solid #334155",
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Sector allocation */}
            <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
              <h3 className="mb-2 text-sm font-semibold text-slate-200">
                Sector Allocation
              </h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={Object.entries(sectorAlloc).map(([sector, v]) => ({
                        sector,
                        weight_pct: v.weight_pct,
                      }))}
                      dataKey="weight_pct"
                      nameKey="sector"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label
                    >
                      {Object.keys(sectorAlloc).map((_, idx) => (
                        <Cell
                          key={idx}
                          fill={COLORS[idx % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#1e293b",
                        border: "1px solid #334155",
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* P&L by position */}
            <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
              <h3 className="mb-2 text-sm font-semibold text-slate-200">
                P&L by Position
              </h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={positions}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="ticker" stroke="#cbd5f5" />
                    <YAxis stroke="#cbd5f5" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#1e293b",
                        border: "1px solid #334155",
                      }}
                    />
                    <Bar dataKey="pnl" fill="#22c55e" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Distance from 52W high */}
            <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
              <h3 className="mb-2 text-sm font-semibold text-slate-200">
                Distance from 52W High
              </h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={positions.filter(
                      (p) => p.distance_from_52w_high_pct != null
                    )}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="ticker" stroke="#cbd5f5" />
                    <YAxis stroke="#cbd5f5" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#1e293b",
                        border: "1px solid #334155",
                      }}
                    />
                    <Bar
                      dataKey="distance_from_52w_high_pct"
                      fill="#38bdf8"
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Historical portfolio value */}
            <div className="rounded-xl border border-slate-800 bg-slate-900 p-4 lg:col-span-2">
              <h3 className="mb-2 text-sm font-semibold text-slate-200">
                Historical Portfolio Value
              </h3>
              <div className="h-72">
                {snapshotSeries.length < 2 ? (
                  <div className="flex h-full items-center justify-center text-sm text-slate-400">
                    Not enough data yet.
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={snapshotSeries}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="date" stroke="#cbd5f5" />
                      <YAxis stroke="#cbd5f5" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#1e293b",
                          border: "1px solid #334155",
                        }}
                      />
                      <Line
                        type="monotone"
                        dataKey="total_market_value"
                        stroke="#60a5fa"
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

