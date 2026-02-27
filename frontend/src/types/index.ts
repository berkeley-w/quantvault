export interface Security {
  id: number;
  ticker: string;
  name: string;
  sector: string | null;
  price: number;
  shares_outstanding: number | null;
  created_at: string;
  updated_at: string;
}

export interface Trader {
  id: number;
  name: string;
  desk: string | null;
  email: string | null;
  created_at: string;
  updated_at: string;
}

export type TradeSide = "BUY" | "SELL";
export type TradeStatus = "ACTIVE" | "REJECTED";

export interface Trade {
  id: number;
  ticker: string;
  side: TradeSide;
  quantity: number;
  price: number;
  trader_name: string;
  trader_id: number | null;
  strategy: string | null;
  notes: string | null;
  status: TradeStatus;
  rejection_reason: string | null;
  rejected_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface RestrictedEntry {
  id: number;
  ticker: string;
  reason: string | null;
  added_by: string | null;
  created_at: string;
}

export interface AuditRecord {
  id: number;
  action: string;
  entity_type: string | null;
  entity_id: number | null;
  details: string | null;
  timestamp: string;
}

export interface Metrics {
  total_market_value: number;
  total_unrealized_pnl: number;
  number_of_positions: number;
  top_holdings: HoldingSummary[];
  sector_breakdown: Record<string, number>;
  trades_active_count: number;
  trades_rejected_count: number;
  trades_total_count: number;
}

export interface HoldingSummary {
  ticker: string;
  net_quantity: number;
  avg_cost: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
}

export interface Holding {
  ticker: string;
  net_quantity: number;
  avg_cost: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
}

export interface PortfolioPerformancePosition {
  ticker: string;
  net_quantity: number;
  avg_cost: number;
  current_price: number;
  market_value: number;
  cost_basis: number;
  pnl: number;
  pnl_pct: number | null;
}

export interface PortfolioPerformance {
  total_market_value: number;
  total_cost_basis: number;
  total_pnl: number;
  total_pnl_pct: number | null;
  breakdown: PortfolioPerformancePosition[];
}

export interface Snapshot {
  date: string;
  total_market_value: number;
  total_pnl: number;
  total_pnl_pct: number | null;
}

export interface AnalyticsPosition {
  ticker: string;
  net_quantity: number;
  avg_cost: number;
  current_price: number;
  market_value: number;
  cost_basis: number;
  pnl: number;
  pnl_pct: number | null;
  portfolio_weight_pct: number;
  shares_outstanding: number | null;
  ownership_pct: number | null;
  beta: number | null;
  pe_ratio: number | null;
  dividend_yield: number | null;
  fifty_two_week_high: number | null;
  fifty_two_week_low: number | null;
  distance_from_52w_high_pct: number | null;
  distance_from_52w_low_pct: number | null;
  sector: string | null;
  industry: string | null;
}

export interface AnalyticsPortfolioSummary {
  total_market_value: number;
  total_cost_basis: number;
  total_pnl: number;
  total_pnl_pct: number | null;
  portfolio_beta: number;
  hhi_concentration: number;
  concentration_rating: string;
  number_of_positions: number;
  sector_allocation: Record<
    string,
    {
      market_value: number;
      weight_pct: number;
    }
  >;
}

export interface AnalyticsResponse {
  positions: AnalyticsPosition[];
  portfolio: AnalyticsPortfolioSummary;
}

export interface TradeAnalyticsResponse {
  total_trades: number;
  buy_trades: number;
  sell_trades: number;
  total_buy_value: number;
  total_sell_value: number;
  completed_round_trips: number;
  win_count: number;
  loss_count: number;
  win_rate_pct: number | null;
  average_win: number | null;
  average_loss: number | null;
  largest_win: number;
  largest_loss: number;
  avg_trade_size: number;
  most_traded_ticker: string | null;
  trades_by_ticker: Record<string, number>;
}

export interface PriceQuote {
  ticker: string;
  current_price: number | null;
  change: number | null;
  change_percent: number | null;
  volume: number | null;
}

export interface PriceRefreshStatus {
  running: boolean;
  last_result: any;
  last_run_at: string | null;
}

// ============== Auth ==============

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}


