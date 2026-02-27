import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../api/client";
import type { AuthUser } from "../types";

export function useTraderAccounts() {
  return useQuery({
    queryKey: ["trader-accounts"],
    queryFn: () => apiClient<AuthUser[]>("/api/auth/trader-choices"),
  });
}

