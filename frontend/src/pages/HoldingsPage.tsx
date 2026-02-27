import { useHoldings } from "../hooks/useHoldings";
import { DataTable } from "../components/shared/DataTable";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";
import { formatCurrency, pnlColor } from "../lib/formatters";

export function HoldingsPage() {
  const { data, isLoading } = useHoldings();

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
            { key: "avg_cost", header: "Avg Cost", align: "right" },
            {
              key: "current_price",
              header: "Price",
              align: "right",
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
          data={data}
        />
      )}
    </div>
  );
}

