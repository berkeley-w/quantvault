import { useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";

interface WebSocketEvent {
  type: string;
  data: any;
}

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
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
            // Silently handle parse errors - malformed messages are ignored
          }
        };

        ws.onerror = () => {
          // WebSocket errors are handled by onclose
        };

        ws.onclose = () => {
          // Reconnect after 3 seconds
          reconnectTimeoutRef.current = window.setTimeout(() => {
            connect();
          }, 3000);
        };
      } catch {
        // Failed to create WebSocket - will retry on next connection attempt
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
          // Unknown event types are ignored
          break;
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
