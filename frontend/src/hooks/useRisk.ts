import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../api/client";

export interface RiskMetrics {
  portfolio_beta: number;
  var_95: number | null;
  var_99: number | null;
  max_drawdown: {
    max_drawdown: number;
    max_drawdown_pct: number;
    peak_date: string | null;
    trough_date: string | null;
  } | null;
  sharpe_ratio: number | null;
  concentration: {
    hhi: number;
    concentration_rating: string;
    top_position_pct: number;
    top_5_positions_pct: number;
  };
}

export function useRiskMetrics() {
  return useQuery({
    queryKey: ["risk-metrics"],
    queryFn: () => apiClient<RiskMetrics>("/api/v1/risk"),
  });
}

// Export for use in pages
export { useRiskMetrics as useRisk };
