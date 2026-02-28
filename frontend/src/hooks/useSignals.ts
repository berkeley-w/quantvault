import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../api/client";

export interface Signal {
  id: number;
  strategy_id: number;
  ticker: string;
  signal_type: string;
  signal_strength: number;
  value: number | null;
  metadata_json: string | null;
  timestamp: string;
  created_at: string;
}

export interface PaginatedSignals {
  items: Signal[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export function useSignals(
  ticker?: string,
  strategyId?: number,
  start?: string,
  end?: string,
  page: number = 1,
  pageSize: number = 50
) {
  return useQuery({
    queryKey: ["signals", ticker, strategyId, start, end, page, pageSize],
    queryFn: () => {
      const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
      });
      if (ticker) params.append("ticker", ticker);
      if (strategyId) params.append("strategy_id", String(strategyId));
      if (start) params.append("start", start);
      if (end) params.append("end", end);
      return apiClient<PaginatedSignals>(
        `/api/v1/signals?${params.toString()}`
      );
    },
  });
}
