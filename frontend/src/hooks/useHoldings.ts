import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../api/client";
import { Holding, Metrics } from "../types";

export function useHoldings() {
  return useQuery({
    queryKey: ["holdings"],
    queryFn: () => apiClient<Holding[]>("/api/holdings"),
  });
}

export function useMetrics() {
  return useQuery({
    queryKey: ["metrics"],
    queryFn: () => apiClient<Metrics>("/api/metrics"),
  });
}

