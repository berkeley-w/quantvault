import { useState } from "react";
import { useTrades, useRejectTrade, useReinstateTrade } from "../hooks/useTrades";
import { DataTable } from "../components/shared/DataTable";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";
import { formatCurrency } from "../lib/formatters";

export function CompliancePage() {
  const { data: active, isLoading: loadingActive } = useTrades({
    status: "ACTIVE",
  });
  const { data: rejected, isLoading: loadingRejected } = useTrades({
    status: "REJECTED",
  });
  const rejectTrade = useRejectTrade();
  const reinstateTrade = useReinstateTrade();
  const [rejectingId, setRejectingId] = useState<number | null>(null);
  const [reason, setReason] = useState("");

  const submitReject = () => {
    if (!rejectingId || !reason) return;
    rejectTrade.mutate({ id: rejectingId, rejection_reason: reason });
    setRejectingId(null);
    setReason("");
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-100">Compliance</h1>

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        <h2 className="mb-3 text-sm font-semibold text-slate-200">
          Active Trades for Review
        </h2>
        {loadingActive || !active ? (
          <LoadingSpinner />
        ) : (
          <DataTable
            columns={[
              { key: "id", header: "ID" },
              { key: "ticker", header: "Ticker" },
              { key: "side", header: "Side" },
              { key: "quantity", header: "Qty", align: "right" },
              {
                key: "price",
                header: "Price",
                align: "right",
                render: (row: any) => formatCurrency(row.price),
              },
              { key: "trader_name", header: "Trader" },
              {
                key: "actions",
                header: "",
                render: (row: any) => (
                  <button
                    className="rounded bg-red-600 px-3 py-1 text-xs text-white hover:bg-red-700"
                    onClick={() => {
                      setRejectingId(row.id);
                      setReason("");
                    }}
                  >
                    Reject
                  </button>
                ),
              },
            ]}
            data={active}
          />
        )}
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        <h2 className="mb-3 text-sm font-semibold text-slate-200">
          Rejected Trades
        </h2>
        {loadingRejected || !rejected ? (
          <LoadingSpinner />
        ) : (
          <DataTable
            columns={[
              { key: "id", header: "ID" },
              { key: "ticker", header: "Ticker" },
              { key: "side", header: "Side" },
              { key: "quantity", header: "Qty", align: "right" },
              {
                key: "price",
                header: "Price",
                align: "right",
                render: (row: any) => formatCurrency(row.price),
              },
              { key: "trader_name", header: "Trader" },
              { key: "rejection_reason", header: "Reason" },
              {
                key: "actions",
                header: "",
                render: (row: any) => (
                  <button
                    className="rounded bg-green-600 px-3 py-1 text-xs text-white hover:bg-green-700"
                    onClick={() => reinstateTrade.mutate(row.id)}
                  >
                    Reinstate
                  </button>
                ),
              },
            ]}
            data={rejected}
          />
        )}
      </div>

      {/* Simple inline reject "modal" */}
      {rejectingId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="w-full max-w-md rounded-xl border border-slate-700 bg-slate-900 p-4">
            <h3 className="mb-3 text-sm font-semibold text-slate-100">
              Reject Trade #{rejectingId}
            </h3>
            <textarea
              className="mb-3 w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm text-slate-100"
              rows={3}
              placeholder="Rejection reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
            <div className="flex justify-end gap-2">
              <button
                className="rounded-lg bg-slate-700 px-3 py-1 text-xs text-slate-100"
                onClick={() => {
                  setRejectingId(null);
                  setReason("");
                }}
              >
                Cancel
              </button>
              <button
                className="rounded-lg bg-red-600 px-3 py-1 text-xs text-white"
                onClick={submitReject}
                disabled={!reason}
              >
                Reject
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

