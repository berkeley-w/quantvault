import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../api/client";
import { AuditRecord } from "../types";
import { DataTable } from "../components/shared/DataTable";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";
import { formatDateTime } from "../lib/formatters";

export function AuditPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["audit"],
    queryFn: () => apiClient<AuditRecord[]>("/api/audit"),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-100">Audit Log</h1>
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        {isLoading || !data ? (
          <LoadingSpinner />
        ) : (
          <DataTable
            columns={[
              { key: "id", header: "ID" },
              { key: "timestamp", header: "Timestamp", render: (r: any) => formatDateTime(r.timestamp) },
              { key: "action", header: "Action" },
              { key: "entity_type", header: "Entity" },
              { key: "entity_id", header: "Entity ID" },
              { key: "details", header: "Details" },
            ]}
            data={data}
          />
        )}
      </div>
    </div>
  );
}

