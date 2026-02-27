import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../api/client";
import {
  AnalyticsResponse,
  PortfolioPerformance,
  Snapshot,
  TradeAnalyticsResponse,
} from "../types";

export function useAnalytics() {
  return useQuery({
    queryKey: ["analytics"],
    queryFn: () => apiClient<AnalyticsResponse>("/api/analytics"),
  });
}

export function useTradeAnalytics() {
  return useQuery({
    queryKey: ["trade-analytics"],
    queryFn: () => apiClient<TradeAnalyticsResponse>("/api/trade-analytics"),
  });
}

export function usePortfolioPerformance() {
  return useQuery({
    queryKey: ["portfolio-performance"],
    queryFn: () => apiClient<PortfolioPerformance>("/api/portfolio/performance"),
  });
}

export function useSnapshots() {
  return useQuery({
    queryKey: ["snapshots"],
    queryFn: () => apiClient<{ snapshots: Snapshot[] }>("/api/snapshots"),
  });
}

