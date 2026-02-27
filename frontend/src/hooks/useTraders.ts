import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { apiClient } from "../api/client";
import { Trader } from "../types";

export function useTraders() {
  return useQuery({
    queryKey: ["traders"],
    queryFn: () => apiClient<Trader[]>("/api/traders"),
  });
}

interface TraderCreate {
  name: string;
  desk?: string | null;
  email?: string | null;
}

interface TraderUpdate {
  name?: string;
  desk?: string | null;
  email?: string | null;
}

export function useCreateTrader() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: TraderCreate) =>
      apiClient<Trader>("/api/traders", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["traders"] });
      toast.success("Trader added");
    },
    onError: (err: any) => toast.error(err?.message || "Failed to add trader"),
  });
}

export function useUpdateTrader() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (params: { id: number; data: TraderUpdate }) =>
      apiClient<Trader>(`/api/traders/${params.id}`, {
        method: "PUT",
        body: JSON.stringify(params.data),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["traders"] });
      toast.success("Trader updated");
    },
    onError: (err: any) =>
      toast.error(err?.message || "Failed to update trader"),
  });
}

export function useDeleteTrader() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      apiClient(`/api/traders/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["traders"] });
      toast.success("Trader deleted");
    },
    onError: (err: any) =>
      toast.error(err?.message || "Failed to delete trader"),
  });
}

