const express = require('express');
const http = require('http');
const WebSocket = require('ws');
let pty = null;
try {
  pty = require('node-pty');
} catch (e) {
  console.warn('node-pty native require failed, trying prebuilt fallback:', e && e.message);
  try {
    pty = require('node-pty-prebuilt-multiarch');
  } catch (e2) {
    console.error('prebuilt node-pty fallback also failed:', e2 && e2.message);
    throw e; // rethrow the original error so the process still fails loudly
  }
}
const path = require('path');

const app = express();
const server = http.createServer(app);

// Simple CORS for local development so the Next frontend (usually on :3000)
// can POST files to this backend on :3001. In production use a stricter policy.
app.use((req, res, next) => {
  // permissive CORS for local dev; include credentials header to be explicit.
  // Note: when Access-Control-Allow-Origin is '*', browsers won't send credentials.
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.header('Access-Control-Allow-Credentials', 'true');
  if (req.method === 'OPTIONS') {
    // respond to preflight immediately
    return res.sendStatus(200);
  }
  next();
});

// WebSocket server used for terminal pty proxying
const fs = require('fs');
const wss = new WebSocket.Server({ server, path: '/pty' });
const multer = require('multer');
// Determine the uploads directory. Prefer an explicit UPLOAD_DIR environment
// variable (set by docker-compose) but fall back to backend/uploads when
// unspecified. This lets a compose mount like ./repl_state:/app/repl_state be
// authoritative while preserving local dev behaviour.
const defaultUploadDir = path.resolve(__dirname, 'uploads');
const uploadDir = process.env.UPLOAD_DIR || defaultUploadDir;

if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// configure multer for uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    // keep original name; in production you might want to sanitize or add a UUID
    cb(null, file.originalname);
  }
});
const upload = multer({ storage: storage, limits: { fileSize: 50 * 1024 * 1024 } }); // 50MBf

// POST /upload to receive files for Python scripts. exposes uploaded files at /files/<name>
app.post('/upload', upload.single('file'), (req, res) => {
  try {
    if (!req.file) return res.status(400).json({ error: 'no file uploaded' });
    res.json({ ok: true, filename: req.file.filename, path: `/files/${encodeURIComponent(req.file.filename)}` });
  } catch (err) {
    console.error('upload handler error', err && err.stack || err);
    // Ensure we send JSON so the frontend doesn't attempt to parse HTML
    res.status(500).json({ error: err && err.message ? err.message : 'internal server error' });
  }
});

// static serve uploaded files
app.use('/files', express.static(uploadDir));

// simple health endpoint
app.get('/health', (req, res) => res.json({ ok: true }));

// list uploaded files as JSON
app.get('/uploads', (req, res) => {
  fs.readdir(uploadDir, (err, files) => {
    if (err) {
      console.error('uploads list error for', uploadDir, err && err.stack || err);
      return res.status(500).json({ error: err.message });
    }
    const list = files.map((f) => ({ filename: f, path: `/files/${encodeURIComponent(f)}` }));
    res.json({ ok: true, files: list });
  });
});

wss.on('connection', (ws, req) => {
  console.log('pty: new websocket connection');

  // Resolve the python runner script relative to repo
  const runnerPath = path.resolve(__dirname, '..', 'python', 'runner', 'agent_runner.py');
  // Prefer an explicit PYTHON_BIN, otherwise fall back to the project's
  // .venv python if present, then to system python3. This makes starting
  // the backend with `npm start` still pick up the project's virtualenv.
  let pythonBin = process.env.PYTHON_BIN || null;
  try {
    const venvPython = require('path').resolve(__dirname, '..', '.venv', 'bin', 'python');
    const fs = require('fs');
    if (!pythonBin && fs.existsSync(venvPython) && fs.statSync(venvPython).mode & 0o111) {
      pythonBin = venvPython;
    }
  } catch (e) {
    // ignore
  }
  if (!pythonBin) pythonBin = process.env.PYTHON_BIN || 'python3';

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

      // spawn the python runner with its working directory set to the uploads
      // directory and expose UPLOAD_DIR in the child's environment so it can
      // restrict filesystem access.
      // Preserve any UPLOAD_DIR already present in process.env (for example from
      // docker-compose). Only set UPLOAD_DIR for the child when it isn't defined
      // in the environment, which avoids overwriting a mounted path.
      const childEnv = Object.assign({}, process.env);
      if (!childEnv.UPLOAD_DIR) {
        childEnv.UPLOAD_DIR = uploadDir;
      }
      shell = pty.spawn(pythonBin, ['-u', runnerPath], {
        name: 'xterm-color',
        cols: 80,
        rows: 24,
        cwd: uploadDir,
        env: childEnv,
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

// Global error handler - ensures JSON responses for uncaught errors
app.use((err, req, res, next) => {
  console.error('Unhandled server error', err && err.stack || err);
  if (res.headersSent) return next(err);
  res.status(500).json({ error: err && err.message ? err.message : 'internal server error' });
});
