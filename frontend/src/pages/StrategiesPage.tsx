import { useState } from "react";
import { useStrategies, useCreateStrategy, useUpdateStrategy, useDeleteStrategy } from "../hooks/useStrategies";
import { DataTable } from "../components/shared/DataTable";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";
import { formatDateTime } from "../lib/formatters";
import toast from "react-hot-toast";

export function StrategiesPage() {
  const { data: strategies, isLoading } = useStrategies();
  const createStrategy = useCreateStrategy();
  const updateStrategy = useUpdateStrategy();
  const deleteStrategy = useDeleteStrategy();

  const [form, setForm] = useState({
    name: "",
    description: "",
    parameters_json: "",
    is_active: true,
  });
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editValues, setEditValues] = useState<any>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createStrategy.mutate({
      name: form.name,
      description: form.description || null,
      parameters_json: form.parameters_json || null,
      is_active: form.is_active,
    });
    setForm({ name: "", description: "", parameters_json: "", is_active: true });
  };

  const startEdit = (strategy: any) => {
    setEditingId(strategy.id);
    setEditValues({
      name: strategy.name,
      description: strategy.description || "",
      parameters_json: strategy.parameters_json || "",
      is_active: strategy.is_active,
    });
  };

  const saveEdit = (id: number) => {
    updateStrategy.mutate({
      id,
      data: {
        name: editValues.name,
        description: editValues.description || null,
        parameters_json: editValues.parameters_json || null,
        is_active: editValues.is_active,
      },
    });
    setEditingId(null);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-100">Trading Strategies</h1>

      {/* Create Form */}
      <form
        onSubmit={handleSubmit}
        className="rounded-xl border border-slate-800 bg-slate-900 p-4"
      >
        <h2 className="mb-3 text-sm font-semibold text-slate-200">Create Strategy</h2>
        <div className="grid gap-3 md:grid-cols-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">Name</label>
            <input
              type="text"
              required
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">Description</label>
            <input
              type="text"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">Parameters JSON</label>
            <input
              type="text"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm"
              value={form.parameters_json}
              onChange={(e) => setForm((f) => ({ ...f, parameters_json: e.target.value }))}
              placeholder='{"threshold": 30}'
            />
          </div>
          <div className="flex items-end">
            <label className="flex items-center gap-2 text-xs text-slate-400">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))}
                className="rounded"
              />
              Active
            </label>
          </div>
        </div>
        <button
          type="submit"
          className="mt-3 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          Create Strategy
        </button>
      </form>

      {/* Strategies Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        {isLoading || !strategies ? (
          <LoadingSpinner />
        ) : (
          <DataTable
            columns={[
              { key: "name", header: "Name" },
              { key: "description", header: "Description" },
              {
                key: "is_active",
                header: "Status",
                render: (r: any) => (
                  <span
                    className={`rounded px-2 py-1 text-xs ${
                      r.is_active
                        ? "bg-green-500/20 text-green-400"
                        : "bg-slate-500/20 text-slate-400"
                    }`}
                  >
                    {r.is_active ? "Active" : "Inactive"}
                  </span>
                ),
              },
              {
                key: "created_at",
                header: "Created",
                render: (r: any) => formatDateTime(r.created_at),
              },
              {
                key: "actions",
                header: "",
                render: (r: any) =>
                  editingId === r.id ? (
                    <div className="flex gap-2">
                      <button
                        className="rounded bg-green-600 px-2 py-1 text-xs text-white"
                        onClick={() => saveEdit(r.id)}
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
                        onClick={() => startEdit(r)}
                      >
                        Edit
                      </button>
                      <button
                        className="rounded bg-red-600 px-2 py-1 text-xs text-white"
                        onClick={() => {
                          if (window.confirm(`Delete strategy "${r.name}"?`)) {
                            deleteStrategy.mutate(r.id);
                          }
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  ),
              },
            ]}
            data={strategies || []}
          />
        )}
      </div>
    </div>
  );
}
