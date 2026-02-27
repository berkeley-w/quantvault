import { ReactNode } from "react";
import { EmptyState } from "./EmptyState";

export interface Column<T> {
  key: keyof T | string;
  header: string;
  render?: (row: T) => ReactNode;
  align?: "left" | "right" | "center";
  sortable?: boolean;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  onSort?: (key: string, direction: "asc" | "desc") => void;
  sortKey?: string;
  sortDirection?: "asc" | "desc";
}

export function DataTable<T extends Record<string, any>>({
  columns,
  data,
  onSort,
  sortKey,
  sortDirection,
}: DataTableProps<T>) {
  if (!data.length) {
    return <EmptyState />;
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900">
      <table className="min-w-full divide-y divide-slate-800 text-sm">
        <thead className="bg-slate-900">
          <tr>
            {columns.map((col) => {
              const isSorted = sortKey === col.key;
              const dir = isSorted ? sortDirection : undefined;
              const align =
                col.align === "right"
                  ? "text-right"
                  : col.align === "center"
                  ? "text-center"
                  : "text-left";
              return (
                <th
                  key={col.key as string}
                  className={`px-3 py-2 font-medium text-slate-400 ${align} ${
                    col.sortable && onSort ? "cursor-pointer select-none hover:text-slate-200" : ""
                  }`}
                  onClick={() => {
                    if (!col.sortable || !onSort) return;
                    const nextDir = isSorted && dir === "asc" ? "desc" : "asc";
                    onSort(col.key as string, nextDir);
                  }}
                >
                  <span className="inline-flex items-center gap-1">
                    {col.header}
                    {col.sortable && (
                      <span className="text-xs">
                        {isSorted ? (dir === "asc" ? "▲" : "▼") : "↕"}
                      </span>
                    )}
                  </span>
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800 bg-slate-900">
          {data.map((row, idx) => (
            <tr
              key={idx}
              className="hover:bg-slate-800/60"
            >
              {columns.map((col) => {
                const align =
                  col.align === "right"
                    ? "text-right"
                    : col.align === "center"
                    ? "text-center"
                    : "text-left";
                return (
                  <td
                    key={col.key as string}
                    className={`whitespace-nowrap px-3 py-2 text-slate-100 ${align}`}
                  >
                    {col.render ? col.render(row) : String(row[col.key as string] ?? "")}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

