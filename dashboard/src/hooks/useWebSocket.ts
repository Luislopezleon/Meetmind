"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import type { WebSocketMessage } from "@/types";

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8001";

interface UseWebSocketOptions {
  meetingId: number;
  onTranscriptChunk?: (data: Record<string, unknown>) => void;
  onInsightDetected?: (data: Record<string, unknown>) => void;
  onStatusUpdate?: (data: Record<string, unknown>) => void;
}

export function useWebSocket({
  meetingId,
  onTranscriptChunk,
  onInsightDetected,
  onStatusUpdate,
}: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [meetingInfo, setMeetingInfo] = useState<Record<string, unknown> | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(`${WS_BASE}/ws/${meetingId}`);

    ws.onopen = () => {
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);

        switch (message.type) {
          case "meeting_connected":
            setMeetingInfo(message.data);
            break;
          case "transcript_chunk":
            onTranscriptChunk?.(message.data);
            break;
          case "insight_detected":
            onInsightDetected?.(message.data);
            break;
          case "status_update":
            onStatusUpdate?.(message.data);
            break;
        }
      } catch {
        // Invalid JSON, ignore
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      // Reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, 3000);
    };

    ws.onerror = () => {
      ws.close();
    };

    wsRef.current = ws;
  }, [meetingId, onTranscriptChunk, onInsightDetected, onStatusUpdate]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const sendPing = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "ping" }));
    }
  }, []);

  return { isConnected, meetingInfo, sendPing };
}
