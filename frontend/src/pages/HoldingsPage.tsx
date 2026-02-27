import { useHoldings } from "../hooks/useHoldings";
import { useSecurities } from "../hooks/useSecurities";
import { DataTable } from "../components/shared/DataTable";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";
import { formatCurrency, formatPercent, pnlColor } from "../lib/formatters";

export function HoldingsPage() {
  const { data, isLoading } = useHoldings();
  const { data: securities } = useSecurities();

  const sharesByTicker =
    securities?.reduce<Record<string, number | null>>((acc, sec) => {
      acc[sec.ticker] = sec.shares_outstanding ?? null;
      return acc;
    }, {}) ?? {};

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold text-slate-100">Holdings</h1>
      {isLoading || !data ? (
        <LoadingSpinner />
      ) : (
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
          data={data}
        />
      )}
    </div>
  );
}

