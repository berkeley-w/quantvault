import { useState } from "react";
import { useSecurities } from "../hooks/useSecurities";
import { useCreateTrade, useTrades, useUpdateTrade, useDeleteTrade } from "../hooks/useTrades";
import { useTraderAccounts } from "../hooks/useTraderAccounts";
import { DataTable } from "../components/shared/DataTable";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";
import { DataLoadError } from "../components/shared/DataLoadError";
import { formatCurrency } from "../lib/formatters";

export function BlotterPage() {
  const { data: securitiesData } = useSecurities();
  const securities = securitiesData?.items || [];
  const { data: traders } = useTraderAccounts();
  const [page, setPage] = useState(1);
  const pageSize = 50;
  const { data: tradesData, isLoading, isError, error, refetch } = useTrades({ status: "ACTIVE" }, page, pageSize);
  const trades = tradesData?.items || [];
  const createTrade = useCreateTrade();
  const updateTrade = useUpdateTrade();
  const deleteTrade = useDeleteTrade();

  const [form, setForm] = useState({
    ticker: "",
    side: "BUY",
    quantity: "",
    price: "",
    trader_name: "",
    strategy: "",
    notes: "",
  });
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editValues, setEditValues] = useState<Record<string, any>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.ticker || !form.trader_name || !form.quantity || !form.price) return;
    createTrade.mutate({
      ticker: form.ticker,
      side: form.side as "BUY" | "SELL",
      quantity: parseFloat(form.quantity),
      price: parseFloat(form.price),
      trader_name: form.trader_name,
      strategy: form.strategy || null,
      notes: form.notes || null,
    });
    setForm({
      ticker: "",
      side: "BUY",
      quantity: "",
      price: "",
      trader_name: "",
      strategy: "",
      notes: "",
    });
  };

  const startEdit = (tradeId: number, row: any) => {
    setEditingId(tradeId);
    setEditValues({
      ticker: row.ticker,
      side: row.side,
      quantity: String(row.quantity),
      price: String(row.price),
      trader_name: row.trader_name,
      strategy: row.strategy || "",
      notes: row.notes || "",
    });
  };

  const saveEdit = (tradeId: number) => {
    updateTrade.mutate({
      id: tradeId,
      data: {
        ticker: editValues.ticker,
        side: editValues.side,
        quantity: parseFloat(editValues.quantity),
        price: parseFloat(editValues.price),
        trader_name: editValues.trader_name,
        strategy: editValues.strategy || null,
        notes: editValues.notes || null,
      },
    });
    setEditingId(null);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-100">Trade Blotter</h1>

      {/* New trade form */}
      <form
        onSubmit={handleSubmit}
        className="rounded-xl border border-slate-800 bg-slate-900 p-4"
      >
        <h2 className="mb-3 text-sm font-semibold text-slate-200">
          New Trade
        </h2>
        <div className="grid gap-3 md:grid-cols-4 lg:grid-cols-7">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Ticker
            </label>
            <select
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={form.ticker}
              onChange={(e) => {
                const ticker = e.target.value;
                const sec = securities?.find((s) => s.ticker === ticker);
                setForm((prev) => ({
                  ...prev,
                  ticker,
                  price: sec ? String(sec.price) : prev.price,
                }));
              }}
            >
              <option value="">Select</option>
              {securities?.map((s) => (
                <option key={s.id} value={s.ticker}>
                  {s.ticker} — {s.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Side
            </label>
            <select
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={form.side}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, side: e.target.value }))
              }
            >
              <option value="BUY">BUY</option>
              <option value="SELL">SELL</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Quantity
            </label>
            <input
              type="number"
              min="0.0001"
              step="any"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={form.quantity}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, quantity: e.target.value }))
              }
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Price
            </label>
            <input
              type="number"
              min="0"
              step="0.01"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={form.price}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, price: e.target.value }))
              }
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Trader
            </label>
            <select
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={form.trader_name}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, trader_name: e.target.value }))
              }
            >
              <option value="">Select</option>
              {traders?.map((t) => (
                <option key={t.id} value={t.username}>
                  {t.username} {t.email ? `(${t.email})` : ""}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Strategy
            </label>
            <input
              type="text"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={form.strategy}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, strategy: e.target.value }))
              }
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Notes
            </label>
            <input
              type="text"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={form.notes}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, notes: e.target.value }))
              }
            />
          </div>
        </div>
        <div className="mt-3">
          <button
            type="submit"
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Submit Trade
          </button>
        </div>
      </form>

      {/* Active trades table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-200">
            Active Trades (editable)
          </h2>
        </div>
        {isError ? (
          <DataLoadError message={error?.message} onRetry={() => refetch()} />
        ) : isLoading || !trades ? (
          <LoadingSpinner />
        ) : (
          <>
          <DataTable
            columns={[
              {
                key: "ticker",
                header: "Ticker",
                render: (row: any) =>
                  editingId === row.id ? (
                    <input
                      className="w-20 rounded border border-slate-700 bg-slate-800 px-1 text-sm"
                      value={editValues.ticker ?? ""}
                      onChange={(e) =>
                        setEditValues((v) => ({
                          ...v,
                          ticker: e.target.value,
                        }))
                      }
                    />
                  ) : (
                    row.ticker
                  ),
              },
              {
                key: "side",
                header: "Side",
                render: (row: any) =>
                  editingId === row.id ? (
                    <select
                      className="w-20 rounded border border-slate-700 bg-slate-800 px-1 text-sm"
                      value={editValues.side ?? ""}
                      onChange={(e) =>
                        setEditValues((v) => ({ ...v, side: e.target.value }))
                      }
                    >
                      <option value="BUY">BUY</option>
                      <option value="SELL">SELL</option>
                    </select>
                  ) : (
                    row.side
                  ),
              },
              {
                key: "quantity",
                header: "Qty",
                align: "right",
                render: (row: any) =>
                  editingId === row.id ? (
                    <input
                      className="w-20 rounded border border-slate-700 bg-slate-800 px-1 text-right text-sm"
                      value={editValues.quantity ?? ""}
                      onChange={(e) =>
                        setEditValues((v) => ({
                          ...v,
                          quantity: e.target.value,
                        }))
                      }
                    />
                  ) : (
                    row.quantity
                  ),
              },
              {
                key: "price",
                header: "Price",
                align: "right",
                render: (row: any) =>
                  editingId === row.id ? (
                    <input
                      className="w-20 rounded border border-slate-700 bg-slate-800 px-1 text-right text-sm"
                      value={editValues.price ?? ""}
                      onChange={(e) =>
                        setEditValues((v) => ({
                          ...v,
                          price: e.target.value,
                        }))
                      }
                    />
                  ) : (
                    formatCurrency(row.price)
                  ),
              },
              { key: "trader_name", header: "Trader" },
              {
                key: "actions",
                header: "",
                render: (row: any) =>
                  editingId === row.id ? (
                    <div className="flex gap-2">
                      <button
                        className="rounded bg-green-600 px-2 py-1 text-xs text-white"
                        onClick={() => saveEdit(row.id)}
                      >
                        Save
                      </button>
                      <button
                        className="rounded bg-slate-700 px-2 py-1 text-xs text-slate-100"
                        onClick={() => setEditingId(null)}
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <div className="flex gap-2">
                      <button
                        className="rounded bg-slate-700 px-2 py-1 text-xs text-slate-100"
                        onClick={() => startEdit(row.id, row)}
                      >
                        Edit
                      </button>
                      <button
                        className="rounded bg-red-600 px-2 py-1 text-xs text-white"
                        onClick={() => deleteTrade.mutate(row.id)}
                      >
                        Delete
                      </button>
                    </div>
                  ),
              },
            ]}
            data={trades}
          />
          {/* Pagination */}
          {tradesData && tradesData.total_pages > 1 && (
            <div className="mt-4 flex items-center justify-between">
              <div className="text-sm text-slate-400">
                Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, tradesData.total)} of {tradesData.total}
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
                  onClick={() => setPage((p) => Math.min(tradesData.total_pages, p + 1))}
                  disabled={page >= tradesData.total_pages}
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

