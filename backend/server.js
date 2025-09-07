const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const pty = require('node-pty');
const path = require('path');

const app = express();
const server = http.createServer(app);

// WebSocket server used for terminal pty proxying
const fs = require('fs');
const wss = new WebSocket.Server({ server, path: '/pty' });

// simple health endpoint
app.get('/health', (req, res) => res.json({ ok: true }));

wss.on('connection', (ws, req) => {
  console.log('pty: new websocket connection');

  // Resolve the python runner script relative to repo
  const runnerPath = path.resolve(__dirname, '..', 'python', 'runner', 'agent_runner.py');
  const pythonBin = process.env.PYTHON_BIN || 'python3';

  console.log('pty: spawn requested', { pythonBin, runnerPath });

  // Spawn logic with respawn/backoff when the client is still connected.
  let shell = null;
  let respawnAttempts = 0;

  function spawnPty() {
    respawnAttempts += 1;
    try {
      if (!fs.existsSync(runnerPath)) {
        throw new Error('runner not found: ' + runnerPath);
      }

      shell = pty.spawn(pythonBin, ['-u', runnerPath], {
        name: 'xterm-color',
        cols: 80,
        rows: 24,
        cwd: process.cwd(),
        env: process.env,
      });

      console.log('pty: spawned child', { pid: shell.pid });
      respawnAttempts = 0; // reset on successful spawn

      shell.on('data', (data) => {
        if (ws.readyState === WebSocket.OPEN) {
          try { ws.send(data); } catch (e) { /* ignore send errors */ }
        }
      });

      shell.on('exit', (code, signal) => {
        console.log('pty child exited', { code, signal });
        try { if (ws.readyState === WebSocket.OPEN) ws.send('\r\n[server] child exited code=' + code + ' signal=' + signal + '\r\n'); } catch (e) {}

        // If the websocket is still connected, attempt to respawn the child with backoff
        if (ws.readyState === WebSocket.OPEN) {
          const backoffMs = Math.min(1000 * Math.pow(2, Math.max(0, respawnAttempts - 1)), 30000);
          console.log('pty: scheduling respawn in', backoffMs, 'ms');
          setTimeout(() => {
            try {
              spawnPty();
            } catch (e) {
              console.error('pty: respawn attempt failed', e && e.message);
            }
          }, backoffMs);
        }
      });

    } catch (err) {
      console.warn('pty spawn failed; falling back to /bin/bash', err && err.message);
      try {
        shell = pty.spawn('/bin/bash', [], {
          name: 'xterm-color',
          cols: 80,
          rows: 24,
          cwd: process.cwd(),
          env: process.env,
        });
        // notify the client that a fallback shell was started
        if (ws.readyState === WebSocket.OPEN) {
          ws.send('\r\n[server] started fallback /bin/bash because: ' + (err && err.message) + '\r\n');
        }

        shell.on('data', (data) => {
          if (ws.readyState === WebSocket.OPEN) {
            try { ws.send(data); } catch (e) { /* ignore send errors */ }
          }
        });

        shell.on('exit', (code, signal) => {
          console.log('pty fallback child exited', { code, signal });
          try { if (ws.readyState === WebSocket.OPEN) ws.send('\r\n[server] fallback child exited code=' + code + ' signal=' + signal + '\r\n'); } catch (e) {}
        });

      } catch (err2) {
        console.error('pty fallback spawn also failed', err2 && err2.message);
        try { if (ws.readyState === WebSocket.OPEN) ws.send('\r\n[server] fatal: cannot start pty (' + (err2 && err2.message) + ')\r\n'); } catch (e) {}
        ws.close();
        return;
      }
    }
  }

  // start initial child
  spawnPty();

  // message handler forwards input/resize to current shell if present
  ws.on('message', (msg) => {
    // try to parse a small JSON framing protocol, otherwise forward raw
    try {
      const obj = JSON.parse(msg.toString());
      if (obj.type === 'input') {
        if (shell) shell.write(obj.data);
      } else if (obj.type === 'resize') {
        if (shell) shell.resize(Number(obj.cols) || 80, Number(obj.rows) || 24);
      }
    } catch (e) {
      // write raw payload
      if (shell) shell.write(msg.toString());
    }
  });

  ws.on('close', () => {
    try { if (shell) shell.kill(); } catch (e) { /* ignore */ }
  });

  ws.on('error', (err) => {
    console.warn('ws error', err && err.message);
  });
});

const PORT = process.env.PTY_PORT || 3001;
server.listen(PORT, () => {
  console.log(`PTY WebSocket server listening on :${PORT} (path=/pty)`);
});
