import { useState } from "react";
import { useTraders, useCreateTrader, useUpdateTrader, useDeleteTrader } from "../hooks/useTraders";
import { DataTable } from "../components/shared/DataTable";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";

export function TradersPage() {
  const { data, isLoading } = useTraders();
  const createTrader = useCreateTrader();
  const updateTrader = useUpdateTrader();
  const deleteTrader = useDeleteTrader();

  const [form, setForm] = useState({
    name: "",
    desk: "",
    email: "",
  });
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editValues, setEditValues] = useState<Record<string, any>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name) return;
    createTrader.mutate({
      name: form.name,
      desk: form.desk || null,
      email: form.email || null,
    });
    setForm({ name: "", desk: "", email: "" });
  };

  const startEdit = (row: any) => {
    setEditingId(row.id);
    setEditValues({
      name: row.name,
      desk: row.desk || "",
      email: row.email || "",
    });
  };

  const saveEdit = (id: number) => {
    updateTrader.mutate({
      id,
      data: {
        name: editValues.name,
        desk: editValues.desk || null,
        email: editValues.email || null,
      },
    });
    setEditingId(null);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-100">Traders</h1>

      <form
        onSubmit={handleSubmit}
        className="rounded-xl border border-slate-800 bg-slate-900 p-4"
      >
        <h2 className="mb-3 text-sm font-semibold text-slate-200">
          Add Trader
        </h2>
        <div className="grid gap-3 md:grid-cols-3">
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
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Desk
            </label>
            <input
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={form.desk}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, desk: e.target.value }))
              }
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">
              Email
            </label>
            <input
              type="email"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={form.email}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, email: e.target.value }))
              }
            />
          </div>
        </div>
        <div className="mt-3">
          <button
            type="submit"
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Add Trader
          </button>
        </div>
      </form>

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        <h2 className="mb-3 text-sm font-semibold text-slate-200">All Traders</h2>
        {isLoading || !data ? (
          <LoadingSpinner />
        ) : (
          <DataTable
            columns={[
              {
                key: "name",
                header: "Name",
                render: (row: any) =>
                  editingId === row.id ? (
                    <input
                      className="w-32 rounded border border-slate-700 bg-slate-800 px-1 text-sm"
                      value={editValues.name ?? ""}
                      onChange={(e) =>
                        setEditValues((v) => ({ ...v, name: e.target.value }))
                      }
                    />
                  ) : (
                    row.name
                  ),
              },
              {
                key: "desk",
                header: "Desk",
                render: (row: any) =>
                  editingId === row.id ? (
                    <input
                      className="w-24 rounded border border-slate-700 bg-slate-800 px-1 text-sm"
                      value={editValues.desk ?? ""}
                      onChange={(e) =>
                        setEditValues((v) => ({ ...v, desk: e.target.value }))
                      }
                    />
                  ) : (
                    row.desk
                  ),
              },
              {
                key: "email",
                header: "Email",
                render: (row: any) =>
                  editingId === row.id ? (
                    <input
                      className="w-40 rounded border border-slate-700 bg-slate-800 px-1 text-sm"
                      value={editValues.email ?? ""}
                      onChange={(e) =>
                        setEditValues((v) => ({ ...v, email: e.target.value }))
                      }
                    />
                  ) : (
                    row.email
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
                        className="rounded bg-red-600 px-2 py-1 text-xs text-white"
                        onClick={() => deleteTrader.mutate(row.id)}
                      >
                        Delete
                      </button>
                    </div>
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

