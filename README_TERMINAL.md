Biohacker terminal integration

This workspace adds a Node.js PTY websocket backend and a Next.js xterm frontend to proxy the existing
CLI at `biohacker/biohacker_agent.py`.

Quick start (from repo root)

1. Backend

```bash
cd backend
npm install
npm start
```

2. Frontend (Next.js)

```bash
cd frontend/next-app
npm install
npm run dev
```

Open http://localhost:3000 and the terminal will connect to ws://localhost:3001/pty.

If the agent requires a specific Python environment, set PYTHON_BIN before starting the backend:

```bash
PYTHON_BIN=/path/to/python npm start
```

Troubleshooting
- Check backend logs for spawn errors (path to agent script).
- Test backend with a simpler spawn (e.g. '/bin/bash') to verify pty wiring.
