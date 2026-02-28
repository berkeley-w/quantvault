import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../api/client";
import { AuditRecord, PaginatedResponse } from "../types";
import { DataTable } from "../components/shared/DataTable";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";
import { DataLoadError } from "../components/shared/DataLoadError";
import { formatDateTime } from "../lib/formatters";

export function AuditPage() {
  const [page, setPage] = useState(1);
  const pageSize = 50;
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["audit", page, pageSize],
    queryFn: () => {
      const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
      });
      return apiClient<PaginatedResponse<AuditRecord>>(`/api/v1/audit?${params.toString()}`);
    },
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-100">Audit Log</h1>
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        {isError ? (
          <DataLoadError message={error?.message} onRetry={() => refetch()} />
        ) : isLoading || !data ? (
          <LoadingSpinner />
        ) : (
          <>
            <DataTable
              columns={[
                { key: "id", header: "ID" },
                { key: "timestamp", header: "Timestamp", render: (r: any) => formatDateTime(r.timestamp) },
                { key: "action", header: "Action" },
                { key: "entity_type", header: "Entity" },
                { key: "entity_id", header: "Entity ID" },
                { key: "details", header: "Details" },
              ]}
              data={data.items}
            />
            {/* Pagination */}
            {data.total_pages > 1 && (
              <div className="mt-4 flex items-center justify-between">
                <div className="text-sm text-slate-400">
                  Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, data.total)} of {data.total}
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
                    onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
                    disabled={page >= data.total_pages}
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

