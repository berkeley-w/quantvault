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
    queryFn: () => apiClient<AnalyticsResponse>("/api/v1/analytics"),
  });
}

export function useTradeAnalytics() {
  return useQuery({
    queryKey: ["trade-analytics"],
    queryFn: () => apiClient<TradeAnalyticsResponse>("/api/v1/trade-analytics"),
  });
}

export function usePortfolioPerformance() {
  return useQuery({
    queryKey: ["portfolio-performance"],
    queryFn: () => apiClient<PortfolioPerformance>("/api/v1/portfolio/performance"),
  });
}

export function useSnapshots() {
  return useQuery({
    queryKey: ["snapshots"],
    queryFn: () => apiClient<{ snapshots: Snapshot[] }>("/api/v1/snapshots"),
  });
}

