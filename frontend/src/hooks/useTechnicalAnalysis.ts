import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../api/client";

export interface PriceBar {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number | null;
}

export interface IndicatorDataPoint {
  timestamp: string;
  value: number | null;
  parameters: Record<string, any> | null;
}

export interface TechnicalAnalysisResponse {
  ticker: string;
  price_bars: PriceBar[];
  indicators: Record<string, IndicatorDataPoint[]>;
}

export function useTechnicalAnalysis(
  ticker: string,
  indicators: string = "SMA_20,RSI_14,MACD",
  start?: string,
  end?: string
) {
  return useQuery({
    queryKey: ["technical-analysis", ticker, indicators, start, end],
    queryFn: () => {
      const params = new URLSearchParams({
        indicators,
      });
      if (start) params.append("start", start);
      if (end) params.append("end", end);
      return apiClient<TechnicalAnalysisResponse>(
        `/api/v1/analytics/technical/${ticker}?${params.toString()}`
      );
    },
    enabled: !!ticker,
  });
}
