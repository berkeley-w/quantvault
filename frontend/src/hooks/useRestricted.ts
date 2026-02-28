import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { apiClient } from "../api/client";
import { RestrictedEntry } from "../types";

export function useRestrictedList() {
  return useQuery({
    queryKey: ["restricted"],
    queryFn: () => apiClient<RestrictedEntry[]>("/api/v1/restricted"),
  });
}

interface RestrictedCreate {
  ticker: string;
  reason?: string | null;
  added_by?: string | null;
}

export function useCreateRestricted() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: RestrictedCreate) =>
      apiClient<RestrictedEntry>("/api/v1/restricted", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["restricted"] });
      toast.success("Added to restricted list");
    },
    onError: (err: any) =>
      toast.error(err?.message || "Failed to add restricted entry"),
  });
}

export function useDeleteRestricted() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      apiClient(`/api/v1/restricted/${id}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["restricted"] });
      toast.success("Removed from restricted list");
    },
    onError: (err: any) =>
      toast.error(err?.message || "Failed to remove restricted entry"),
  });
}

