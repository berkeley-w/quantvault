import { ReactNode } from "react";
import { useWebSocket } from "../hooks/useWebSocket";

interface WebSocketProviderProps {
  children: ReactNode;
}

export function WebSocketProvider({ children }: WebSocketProviderProps) {
  useWebSocket();
  return <>{children}</>;
}
