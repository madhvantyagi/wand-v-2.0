import { useEffect, useRef, useCallback, useState } from 'react';

const WS_BASE = 'ws://localhost:8000';

/**
 * Hook for WebSocket connection to receive real-time analysis updates.
 * 
 * @param {function} onStatusUpdate - Callback for status updates
 * @param {function} onComplete - Callback when analysis completes
 * @param {function} onError - Callback on error
 * @returns {object} { isConnected, sendMessage }
 */
export function useAnalysisWebSocket({ onStatusUpdate, onComplete, onError }) {
    const wsRef = useRef(null);
    const [isConnected, setIsConnected] = useState(false);
    const [reconnectAttempt, setReconnectAttempt] = useState(0);
    const reconnectTimeoutRef = useRef(null);
    const pingIntervalRef = useRef(null);
    const callbacksRef = useRef({ onStatusUpdate, onComplete, onError });

    // Keep callbacks ref up to date
    useEffect(() => {
        callbacksRef.current = { onStatusUpdate, onComplete, onError };
    }, [onStatusUpdate, onComplete, onError]);

    // Connect on mount, disconnect on unmount
    useEffect(() => {
        const token = localStorage.getItem('wand_token');
        if (!token) {
            console.warn('No token for WebSocket connection');
            return;
        }

        // Close existing connection
        if (wsRef.current) {
            wsRef.current.close();
            // Clear previous intervals/timeouts to avoid duplicates
            if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
            if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
        }

        console.log(`🔌 Connecting WebSocket (Attempt ${reconnectAttempt})...`);
        const ws = new WebSocket(`${WS_BASE}/ws/analyze/${token}`);

        ws.onopen = () => {
            console.log('🔌 WebSocket connected');
            setIsConnected(true);

            // Ping every 25s to keep alive (less than server timeout)
            pingIntervalRef.current = setInterval(() => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send('ping');
                }
            }, 25000);
        };

        ws.onmessage = (event) => {
            // Ignore pong responses
            if (event.data === 'pong') return;

            try {
                const data = JSON.parse(event.data);
                console.log('📨 WS message:', data);

                if (data.type === 'complete' || data.status === 'complete') {
                    callbacksRef.current.onComplete?.(data);
                } else if (data.type === 'error' || data.status === 'failed') {
                    callbacksRef.current.onError?.(data);
                } else {
                    callbacksRef.current.onStatusUpdate?.(data);
                }
            } catch (e) {
                console.error('WS parse error:', e);
            }
        };

        ws.onclose = (event) => {
            console.log('🔌 WebSocket disconnected', event.code, event.reason);
            setIsConnected(false);

            if (pingIntervalRef.current) {
                clearInterval(pingIntervalRef.current);
            }

            // Auto-reconnect unless intentional close or auth error
            if (event.code !== 1000 && event.code !== 4001) {
                reconnectTimeoutRef.current = setTimeout(() => {
                    console.log('🔄 Reconnecting WebSocket...');
                    setReconnectAttempt(prev => prev + 1);
                }, 5000);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            // Don't close here, wait for onclose
        };

        wsRef.current = ws;

        // Cleanup on unmount (or before re-running effect)
        return () => {
            if (pingIntervalRef.current) {
                clearInterval(pingIntervalRef.current);
            }
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (wsRef.current) {
                // If the effect is re-running due to reconnectAttempt, we want to close the OLD socket.
                // If unmounting, we also want to close.
                // However, we must ensure we don't trigger the onclose handler's reconnect logic IF we are just unmounting.
                // But since onclose is async/event-based, removing the onclose handler is safer.
                wsRef.current.onclose = null; // Prevent reconnect loop during cleanup
                wsRef.current.close();
                wsRef.current = null;
            }
        };
    }, [reconnectAttempt]); // Re-run when reconnectAttempt changes

    const sendMessage = useCallback((message) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(typeof message === 'string' ? message : JSON.stringify(message));
        }
    }, []);

    return { isConnected, sendMessage };
}

export default useAnalysisWebSocket;
