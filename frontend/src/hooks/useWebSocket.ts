import { useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";

const MAX_RECONNECT_ATTEMPTS = 5;
const INITIAL_RECONNECT_MS = 3000;
const MAX_RECONNECT_MS = 60000;

interface WebSocketEvent {
  type: string;
  data: any;
}

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const reconnectCountRef = useRef(0);
  const qc = useQueryClient();

  useEffect(() => {
    const token =
      typeof window !== "undefined"
        ? window.localStorage.getItem("authToken")
        : null;

    if (!token) return;

    const connect = () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) return;

      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const host = window.location.host;
      const wsUrl = `${protocol}//${host}/ws?token=${encodeURIComponent(token)}`;

      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          reconnectCountRef.current = 0;
          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
          }
        };

        ws.onmessage = (event) => {
          try {
            const message: WebSocketEvent = JSON.parse(event.data);
            handleWebSocketEvent(message);
          } catch (e) {
            console.error("Failed to parse WebSocket message:", e);
          }
        };

        ws.onerror = () => {
          // Avoid console spam; close handler will run and handle reconnect
        };

        ws.onclose = () => {
          wsRef.current = null;
          if (reconnectCountRef.current >= MAX_RECONNECT_ATTEMPTS) {
            return;
          }
          reconnectCountRef.current += 1;
          const delay = Math.min(
            INITIAL_RECONNECT_MS * Math.pow(2, reconnectCountRef.current - 1),
            MAX_RECONNECT_MS
          );
          reconnectTimeoutRef.current = window.setTimeout(() => {
            reconnectTimeoutRef.current = null;
            connect();
          }, delay);
        };
      } catch (error) {
        console.error("Failed to create WebSocket:", error);
      }
    };

    const handleWebSocketEvent = (event: WebSocketEvent) => {
      // Invalidate relevant React Query caches based on event type
      switch (event.type) {
        case "trade_created":
        case "trade_updated":
        case "trade_deleted":
        case "trade_rejected":
        case "trade_reinstated":
          qc.invalidateQueries({ queryKey: ["trades"] });
          qc.invalidateQueries({ queryKey: ["holdings"] });
          qc.invalidateQueries({ queryKey: ["metrics"] });
          qc.invalidateQueries({ queryKey: ["analytics"] });
          qc.invalidateQueries({ queryKey: ["portfolio-performance"] });
          break;
        case "prices_refreshed":
          qc.invalidateQueries({ queryKey: ["holdings"] });
          qc.invalidateQueries({ queryKey: ["metrics"] });
          qc.invalidateQueries({ queryKey: ["analytics"] });
          qc.invalidateQueries({ queryKey: ["portfolio-performance"] });
          qc.invalidateQueries({ queryKey: ["price-refresh-status"] });
          break;
        case "signal_generated":
          qc.invalidateQueries({ queryKey: ["signals"] });
          break;
        default:
          console.log("Unknown WebSocket event type:", event.type);
      }
    };

    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [qc]);
}
