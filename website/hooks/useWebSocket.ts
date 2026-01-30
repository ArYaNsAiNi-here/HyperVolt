// website/hooks/useWebSocket.ts
import { useEffect, useRef, useState, useCallback } from 'react';

export const useWebSocket = (url: string) => {
  const [data, setData] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Prevent empty URLs or re-connecting if already connected
    if (!url) return;
    if (ws.current?.readyState === WebSocket.OPEN) return;

    const socket = new WebSocket(url);
    ws.current = socket;

    socket.onopen = () => {
      console.log('✅ WebSocket Connected');
      setIsConnected(true);
    };

    socket.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        setData(parsed);
      } catch (e) {
        console.warn('Received non-JSON message:', event.data);
      }
    };

    socket.onclose = () => {
      console.log('❌ WebSocket Disconnected');
      setIsConnected(false);
      ws.current = null;
    };

    socket.onerror = (error) => {
      console.error('WebSocket Error:', error);
      // DO NOT put window.location.reload() here
    };

    return () => {
      if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
        socket.close();
      }
    };
  }, [url]); // Only re-run if URL changes

  const sendMessage = useCallback((msg: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(msg));
    } else {
      console.warn('WebSocket not connected, cannot send:', msg);
    }
  }, []);

  return { data, isConnected, sendMessage };
};