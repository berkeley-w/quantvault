import { useState } from "react";
import { useSecurities, useCreateSecurity, useUpdateSecurity, useDeleteSecurity } from "../hooks/useSecurities";
import { DataTable } from "../components/shared/DataTable";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";
import { formatCurrency } from "../lib/formatters";
import { apiClient } from "../api/client";
import { PriceQuote } from "../types";

export function SecuritiesPage() {
  const [page, setPage] = useState(1);
  const pageSize = 50;
  const { data: securitiesData, isLoading } = useSecurities(page, pageSize);
  const data = securitiesData?.items || [];
  const createSecurity = useCreateSecurity();
  const updateSecurity = useUpdateSecurity();
  const deleteSecurity = useDeleteSecurity();
  const [form, setForm] = useState({
    ticker: "",
    name: "",
    sector: "",
    price: "",
    shares_outstanding: "",
  });
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editValues, setEditValues] = useState<Record<string, any>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.ticker || !form.name || !form.price) return;
    createSecurity.mutate({
      ticker: form.ticker,
      name: form.name,
      sector: form.sector || null,
      price: parseFloat(form.price),
      shares_outstanding: form.shares_outstanding
        ? parseFloat(form.shares_outstanding)
        : null,
    });
    setForm({
      ticker: "",
      name: "",
      sector: "",
      price: "",
      shares_outstanding: "",
    });
  };

  const startEdit = (row: any) => {
    setEditingId(row.id);
    setEditValues({
      ticker: row.ticker,
      name: row.name,
      sector: row.sector || "",
      price: String(row.price),
      shares_outstanding: row.shares_outstanding
        ? String(row.shares_outstanding)
        : "",
    });
  };

  const saveEdit = (id: number) => {
    updateSecurity.mutate({
      id,
      data: {
        ticker: editValues.ticker,
        name: editValues.name,
        sector: editValues.sector || null,
        price: parseFloat(editValues.price),
        shares_outstanding: editValues.shares_outstanding
          ? parseFloat(editValues.shares_outstanding)
          : null,
      },
    });
    setEditingId(null);
  };

  const fetchLivePrice = async (ticker: string, id: number) => {
      const quote = await apiClient<PriceQuote>(`/api/v1/prices/${ticker}`);
    if (quote.current_price != null) {
      updateSecurity.mutate({
        id,
        data: { price: quote.current_price },
      });
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-100">Securities</h1>

      <form
        onSubmit={handleSubmit}
        className="rounded-xl border border-slate-800 bg-slate-900 p-4"
      >
        <h2 className="mb-3 text-sm font-semibold text-slate-200">
          Add Security
        </h2>
        <div className="grid gap-3 md:grid-cols-3 lg:grid-cols-5">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Ticker
            </label>
            <input
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={form.ticker}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, ticker: e.target.value }))
              }
              placeholder="AAPL"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Name
            </label>
            <input
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={form.name}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, name: e.target.value }))
              }
              placeholder="Apple Inc"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Sector
            </label>
            <input
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={form.sector}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, sector: e.target.value }))
              }
              placeholder="Technology"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Price
            </label>
            <input
              type="number"
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
              Shares Outstanding
            </label>
            <input
              type="number"
              step="1"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={form.shares_outstanding}
              onChange={(e) =>
                setForm((prev) => ({
                  ...prev,
                  shares_outstanding: e.target.value,
                }))
              }
            />
          </div>
        </div>
        <div className="mt-3">
          <button
            type="submit"
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Add Security
          </button>
        </div>
      </form>

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        <h2 className="mb-3 text-sm font-semibold text-slate-200">All Securities</h2>
        {isLoading || !data ? (
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
                key: "name",
                header: "Name",
                render: (row: any) =>
                  editingId === row.id ? (
                    <input
                      className="w-40 rounded border border-slate-700 bg-slate-800 px-1 text-sm"
                      value={editValues.name ?? ""}
                      onChange={(e) =>
                        setEditValues((v) => ({
                          ...v,
                          name: e.target.value,
                        }))
                      }
                    />
                  ) : (
                    row.name
                  ),
              },
              {
                key: "sector",
                header: "Sector",
                render: (row: any) =>
                  editingId === row.id ? (
                    <input
                      className="w-32 rounded border border-slate-700 bg-slate-800 px-1 text-sm"
                      value={editValues.sector ?? ""}
                      onChange={(e) =>
                        setEditValues((v) => ({
                          ...v,
                          sector: e.target.value,
                        }))
                      }
                    />
                  ) : (
                    row.sector
                  ),
              },
              {
                key: "price",
                header: "Price",
                align: "right",
                render: (row: any) =>
                  editingId === row.id ? (
                    <input
                      className="w-24 rounded border border-slate-700 bg-slate-800 px-1 text-right text-sm"
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
              {
                key: "shares_outstanding",
                header: "Shares Out.",
                align: "right",
                render: (row: any) =>
                  editingId === row.id ? (
                    <input
                      className="w-28 rounded border border-slate-700 bg-slate-800 px-1 text-right text-sm"
                      value={editValues.shares_outstanding ?? ""}
                      onChange={(e) =>
                        setEditValues((v) => ({
                          ...v,
                          shares_outstanding: e.target.value,
                        }))
                      }
                    />
                  ) : row.shares_outstanding != null ? (
                    row.shares_outstanding.toLocaleString()
                  ) : (
                    "-"
                  ),
              },
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
                        onClick={() => startEdit(row)}
                      >
                        Edit
                      </button>
                      <button
                        className="rounded bg-blue-600 px-2 py-1 text-xs text-white"
                        onClick={() => fetchLivePrice(row.ticker, row.id)}
                      >
                        Live Price
                      </button>
                      <button
                        className="rounded bg-red-600 px-2 py-1 text-xs text-white"
                        onClick={() => deleteSecurity.mutate(row.id)}
                      >
                        Delete
                      </button>
                    </div>
                  ),
              },
            ]}
            data={data}
          />
          {/* Pagination */}
          {securitiesData && securitiesData.total_pages > 1 && (
            <div className="mt-4 flex items-center justify-between">
              <div className="text-sm text-slate-400">
                Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, securitiesData.total)} of {securitiesData.total}
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
                  onClick={() => setPage((p) => Math.min(securitiesData.total_pages, p + 1))}
                  disabled={page >= securitiesData.total_pages}
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

