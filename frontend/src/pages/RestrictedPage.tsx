import { useState } from "react";
import { useSecurities } from "../hooks/useSecurities";
import { useRestrictedList, useCreateRestricted, useDeleteRestricted } from "../hooks/useRestricted";
import { DataTable } from "../components/shared/DataTable";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";

export function RestrictedPage() {
  const { data: securities } = useSecurities();
  const { data, isLoading } = useRestrictedList();
  const createRestricted = useCreateRestricted();
  const deleteRestricted = useDeleteRestricted();

  const [form, setForm] = useState({
    ticker: "",
    reason: "",
    added_by: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.ticker) return;
    createRestricted.mutate({
      ticker: form.ticker,
      reason: form.reason || null,
      added_by: form.added_by || null,
    });
    setForm({ ticker: "", reason: "", added_by: "" });
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-100">
        Restricted List
      </h1>

      <form
        onSubmit={handleSubmit}
        className="rounded-xl border border-slate-800 bg-slate-900 p-4"
      >
        <h2 className="mb-3 text-sm font-semibold text-slate-200">
          Add to Restricted List
        </h2>
        <div className="grid gap-3 md:grid-cols-3">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Ticker
            </label>
            <select
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={form.ticker}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, ticker: e.target.value }))
              }
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
              Reason
            </label>
            <input
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={form.reason}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, reason: e.target.value }))
              }
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Added By
            </label>
            <input
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={form.added_by}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, added_by: e.target.value }))
              }
            />
          </div>
        </div>
        <div className="mt-3">
          <button
            type="submit"
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Add
          </button>
        </div>
      </form>

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        <h2 className="mb-3 text-sm font-semibold text-slate-200">
          Restricted List
        </h2>
        {isLoading || !data ? (
          <LoadingSpinner />
        ) : (
          <DataTable
            columns={[
              { key: "ticker", header: "Ticker" },
              { key: "reason", header: "Reason" },
              { key: "added_by", header: "Added By" },
              { key: "created_at", header: "Created At" },
              {
                key: "actions",
                header: "",
                render: (row: any) => (
                  <button
                    className="rounded bg-red-600 px-3 py-1 text-xs text-white hover:bg-red-700"
                    onClick={() => deleteRestricted.mutate(row.id)}
                  >
                    Remove
                  </button>
                ),
              },
            ]}
            data={data}
          />
        )}
      </div>
    </div>
  );
}

