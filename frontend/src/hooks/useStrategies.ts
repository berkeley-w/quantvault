import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { apiClient } from "../api/client";

export interface Strategy {
  id: number;
  name: string;
  description: string | null;
  parameters_json: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PaginatedStrategies {
  items: Strategy[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export function useStrategies(page: number = 1, pageSize: number = 50) {
  return useQuery({
    queryKey: ["strategies", page, pageSize],
    queryFn: () => {
      const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
      });
      return apiClient<Strategy[]>(`/api/v1/strategies?${params.toString()}`);
    },
  });
}

interface StrategyCreate {
  name: string;
  description?: string | null;
  parameters_json?: string | null;
  is_active?: boolean;
}

interface StrategyUpdate {
  name?: string;
  description?: string | null;
  parameters_json?: string | null;
  is_active?: boolean;
}

export function useCreateStrategy() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: StrategyCreate) =>
      apiClient<Strategy>("/api/v1/strategies", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["strategies"] });
      toast.success("Strategy created");
    },
    onError: (err: any) =>
      toast.error(err?.message || "Failed to create strategy"),
  });
}

export function useUpdateStrategy() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (params: { id: number; data: StrategyUpdate }) =>
      apiClient<Strategy>(`/api/v1/strategies/${params.id}`, {
        method: "PUT",
        body: JSON.stringify(params.data),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["strategies"] });
      toast.success("Strategy updated");
    },
    onError: (err: any) =>
      toast.error(err?.message || "Failed to update strategy"),
  });
}

export function useDeleteStrategy() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      apiClient(`/api/v1/strategies/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["strategies"] });
      toast.success("Strategy deleted");
    },
    onError: (err: any) =>
      toast.error(err?.message || "Failed to delete strategy"),
  });
}
