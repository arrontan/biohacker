Dockerizing the biohacker stack (POC)

This project includes a simple Docker Compose setup for local development / hackathon POC.

What is included
- backend: Node.js + Python runner (built from backend/Dockerfile). Exposes port 3001.
- frontend: Next.js dev server (exposes port 3000). For POC we run the dev server so file watching works.

Quick start
1. Copy the example env: cp .env.example .env
2. Edit .env if you need to set PYTHON_BIN to a specific python inside a venv. If left empty the container will rely on system python inside the image.
3. Build and run:
   docker compose build
   docker compose up

Files and volumes
- repl_state/uploads is bind-mounted into the backend so uploaded files persist on the host.
- The repository is mounted read-only into /app inside the backend container so the python runner can import the code.

Notes and caveats
- Do not bake secrets (API keys) into images. For a POC, set secrets in a local .env and keep it out of git.
- The frontend runs Next dev mode inside the container for convenience. For production build the Next app (npm run build) and use next start or a proper static hosting setup.
- The backend image installs Python packages listed in biohacker/requirements.txt at build time; if you need a custom venv or packages, edit backend/Dockerfile.

Troubleshooting
- If the Terminal cannot connect to the backend from a phone on your LAN, ensure your machine firewall allows ports 3000 and 3001 and that you access http://<host-ip>:3000 on your phone. The frontend will connect to the backend using the page hostname by default.
