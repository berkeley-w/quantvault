import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { apiClient } from "../api/client";
import { PriceRefreshStatus } from "../types";

export function usePriceRefresh() {
  const qc = useQueryClient();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const statusQuery = useQuery({
    queryKey: ["price-refresh-status"],
    queryFn: () =>
      apiClient<PriceRefreshStatus>("/api/prices/refresh/status"),
    refetchInterval: isRefreshing ? 5000 : false,
    enabled: isRefreshing,
  });

  useEffect(() => {
    if (statusQuery.data && !statusQuery.data.running && isRefreshing) {
      setIsRefreshing(false);
      toast.success("Prices refreshed");
      qc.invalidateQueries();
    }
  }, [statusQuery.data, isRefreshing, qc]);

  const startRefreshMutation = useMutation({
    mutationFn: () => apiClient("/api/prices/refresh", { method: "POST" }),
    onSuccess: () => {
      setIsRefreshing(true);
    },
    onError: (err: any) => {
      const message = err?.message || "Failed to start refresh";
      if (message.includes("already in progress")) {
        setIsRefreshing(true);
      } else {
        toast.error(message);
      }
    },
  });

  return { startRefresh: startRefreshMutation.mutate, isRefreshing };
}

