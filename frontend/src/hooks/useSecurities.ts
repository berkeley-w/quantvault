import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { apiClient } from "../api/client";
import { Security, PaginatedResponse } from "../types";

export function useSecurities(page: number = 1, pageSize: number = 50) {
  return useQuery({
    queryKey: ["securities", page, pageSize],
    queryFn: () => {
      const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
      });
      return apiClient<PaginatedResponse<Security>>(`/api/v1/securities?${params.toString()}`);
    },
  });
}

interface SecurityCreate {
  ticker: string;
  name: string;
  sector?: string | null;
  price: number;
  shares_outstanding?: number | null;
}

interface SecurityUpdate {
  ticker?: string;
  name?: string;
  sector?: string | null;
  price?: number;
  shares_outstanding?: number | null;
}

export function useCreateSecurity() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SecurityCreate) =>
      apiClient<Security>("/api/v1/securities", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["securities"] });
      toast.success("Security added");
    },
    onError: (err: any) => toast.error(err?.message || "Failed to add security"),
  });
}

export function useUpdateSecurity() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (params: { id: number; data: SecurityUpdate }) =>
      apiClient<Security>(`/api/v1/securities/${params.id}`, {
        method: "PUT",
        body: JSON.stringify(params.data),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["securities"] });
      toast.success("Security updated");
    },
    onError: (err: any) =>
      toast.error(err?.message || "Failed to update security"),
  });
}

export function useDeleteSecurity() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      apiClient(`/api/v1/securities/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["securities"] });
      toast.success("Security deleted");
    },
    onError: (err: any) =>
      toast.error(err?.message || "Failed to delete security"),
  });
}

