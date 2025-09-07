import React, { useEffect, useRef } from 'react';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';

export default function XTerminal() {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const termRef = useRef<Terminal | null>(null);
  const fitTimeout = useRef<number | null>(null);
  const reconnectTimer = useRef<number | null>(null);
  const reconnectAttempts = useRef(0);

  useEffect(() => {
    // require a real container DOM node before instantiating xterm
    if (!containerRef.current) {
      return;
    }

    const term = new Terminal({ convertEol: true });
    const fit = new FitAddon();
    term.loadAddon(fit);
    term.open(containerRef.current as HTMLElement);

    // defer fit() so xterm has time to initialize its renderer; avoids
    // "_renderer.value is undefined" when the renderer isn't ready yet.
    fitTimeout.current = window.setTimeout(() => {
      try { fit.fit(); } catch (e) { console.warn('fit failed', e); }
      try { term.focus(); } catch (e) { /* ignore focus errors */ }
    }, 0) as unknown as number;

    termRef.current = term;

    function makeWs() {
      // Use the same host the page was served from so devices on the LAN
      // (phone) connect back to the server running on the laptop.
      const host = window.location.hostname || 'localhost';
      const proto = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
      const url = `${proto}${host}:3001/pty`;
      console.debug('terminal: connecting ws ->', url);
      let ws: WebSocket;
      try {
        ws = new WebSocket(url);
      } catch (e) {
        console.error('terminal: websocket construction failed', e);
        scheduleReconnect();
        // return a noop cleanup so callers can continue
        return () => {};
      }
      wsRef.current = ws;

      ws.onopen = () => {
        reconnectAttempts.current = 0;
        console.debug('terminal: ws open');
        term.write('\r\nConnected to biohacker PTY server\r\n');
        ws.send(JSON.stringify({ type: 'resize', cols: term.cols, rows: term.rows }));
      };

      ws.onmessage = (ev) => {
        const data = typeof ev.data === 'string' ? ev.data : '';
        term.write(data);
      };

      ws.onclose = (ev) => {
        console.warn('terminal: ws closed', ev);
        term.write('\r\n[connection closed]\r\n');
        scheduleReconnect();
      };

      ws.onerror = (e) => {
        console.error('terminal: ws error', e);
      };

      // wire terminal input to the websocket
      term.onData((d) => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'input', data: d }));
        }
      });

      // handle resize events and notify the server when connected
      const handleResize = () => {
        fit.fit();
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'resize', cols: term.cols, rows: term.rows }));
        }
      };

      window.addEventListener('resize', handleResize);

      // cleanup callback for this ws instance
      const cleanup = () => {
        window.removeEventListener('resize', handleResize);
        try { if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) ws.close(); } catch (e) {}
      };

      return cleanup;
    }

    function scheduleReconnect() {
      if (reconnectTimer.current) return; // already scheduled
      reconnectAttempts.current += 1;
      const backoff = Math.min(1000 * Math.pow(2, reconnectAttempts.current - 1), 30000);
      reconnectTimer.current = window.setTimeout(() => {
        reconnectTimer.current = null;
        try { makeWs(); } catch (e) { console.warn('reconnect failed', e); scheduleReconnect(); }
      }, backoff);
    }

    // start first connection
    const wsCleanup = makeWs();

    return () => {
  if (reconnectTimer.current) { clearTimeout(reconnectTimer.current); reconnectTimer.current = null; }
  if (fitTimeout.current) { clearTimeout(fitTimeout.current); fitTimeout.current = null; }
  try { wsCleanup(); } catch (e) {}
  try { term.dispose(); } catch (e) {}
    };
  }, []);

  return <div className="xterm-container" ref={containerRef} tabIndex={0} />;
}
