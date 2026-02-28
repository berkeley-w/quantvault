import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { apiClient } from "../api/client";
import { Trade, TradeSide, PaginatedResponse, TradeResponseWithWarnings } from "../types";

interface UseTradesOptions {
  status?: "ACTIVE" | "REJECTED" | "ALL";
}

export function useTrades(options: UseTradesOptions = {}, page: number = 1, pageSize: number = 50) {
  const status = options.status ?? "ALL";
  return useQuery({
    queryKey: ["trades", { status }, page, pageSize],
    queryFn: () => {
      const params = new URLSearchParams({
        status,
        page: String(page),
        page_size: String(pageSize),
      });
      return apiClient<PaginatedResponse<Trade>>(`/api/v1/trades?${params.toString()}`);
    },
  });
}

interface TradeCreate {
  ticker: string;
  side: TradeSide;
  quantity: number;
  price: number;
  trader_name: string;
  strategy?: string | null;
  notes?: string | null;
}

interface TradeUpdate {
  ticker?: string;
  side?: TradeSide;
  quantity?: number;
  price?: number;
  trader_name?: string;
  strategy?: string | null;
  notes?: string | null;
}

function invalidateAfterTradeChange(qc: ReturnType<typeof useQueryClient>) {
  qc.invalidateQueries({ queryKey: ["trades"] });
  qc.invalidateQueries({ queryKey: ["holdings"] });
  qc.invalidateQueries({ queryKey: ["metrics"] });
  qc.invalidateQueries({ queryKey: ["analytics"] });
  qc.invalidateQueries({ queryKey: ["portfolio-performance"] });
}

export function useCreateTrade() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: TradeCreate) =>
      apiClient<TradeResponseWithWarnings>("/api/v1/trades", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: (response) => {
      invalidateAfterTradeChange(qc);
      if (response.risk_warnings && response.risk_warnings.length > 0) {
        const warnings = response.risk_warnings.map((w) => w.message).join("; ");
        toast.success("Trade created", { duration: 4000 });
        toast(`Risk warnings: ${warnings}`, {
          duration: 6000,
          icon: "⚠️",
        });
      } else {
        toast.success("Trade created");
      }
    },
    onError: (err: any) => toast.error(err?.message || "Failed to create trade"),
  });
}

export function useUpdateTrade() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (params: { id: number; data: TradeUpdate }) =>
      apiClient<Trade>(`/api/v1/trades/${params.id}`, {
        method: "PUT",
        body: JSON.stringify(params.data),
      }),
    onSuccess: () => {
      invalidateAfterTradeChange(qc);
      toast.success("Trade updated");
    },
    onError: (err: any) => toast.error(err?.message || "Failed to update trade"),
  });
}

export function useDeleteTrade() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      apiClient(`/api/v1/trades/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      invalidateAfterTradeChange(qc);
      toast.success("Trade deleted");
    },
    onError: (err: any) => toast.error(err?.message || "Failed to delete trade"),
  });
}

export function useRejectTrade() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (params: { id: number; rejection_reason: string }) =>
      apiClient(`/api/v1/trades/${params.id}/reject`, {
        method: "POST",
        body: JSON.stringify({ rejection_reason: params.rejection_reason }),
      }),
    onSuccess: () => {
      invalidateAfterTradeChange(qc);
      toast.success("Trade rejected");
    },
    onError: (err: any) => toast.error(err?.message || "Failed to reject trade"),
  });
}

export function useReinstateTrade() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      apiClient(`/api/v1/trades/${id}/reinstate`, { method: "POST" }),
    onSuccess: () => {
      invalidateAfterTradeChange(qc);
      toast.success("Trade reinstated");
    },
    onError: (err: any) =>
      toast.error(err?.message || "Failed to reinstate trade"),
  });
}

