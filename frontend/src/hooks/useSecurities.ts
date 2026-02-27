import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { apiClient } from "../api/client";
import { Security } from "../types";

export function useSecurities() {
  return useQuery({
    queryKey: ["securities"],
    queryFn: () => apiClient<Security[]>("/api/securities"),
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
      apiClient<Security>("/api/securities", {
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
      apiClient<Security>(`/api/securities/${params.id}`, {
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
      apiClient(`/api/securities/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["securities"] });
      toast.success("Security deleted");
    },
    onError: (err: any) =>
      toast.error(err?.message || "Failed to delete security"),
  });
}

