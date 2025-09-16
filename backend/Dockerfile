FROM node:18-bookworm-slim AS nodebase

# We'll use a multi-stage build: 'nodebase' gives us the correct libnode
# artifacts to copy into the final image. The rest of the image is built from
# the same node base to ensure ABI compatibility.

FROM node:18-bookworm-slim

# Install Python 3 and common build deps.
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ca-certificates \
    python3 \
    python3-venv \
    python3-dev \
    python3-pip \
    build-essential \
    pkg-config \
    cmake \
    ninja-build \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install backend npm deps first so native addons compile against the same
# node runtime that will be used at container runtime.
COPY backend/package*.json ./backend/
# Install node deps inside the image. Use npm ci when a lockfile exists for
# reproducible installs; fall back to npm install otherwise. Fail the build on
# errors so missing deps are visible instead of producing an image without
# node_modules.
RUN cd backend && \
    if [ -f package-lock.json ]; then \
      npm ci --only=production --no-audit --prefer-offline; \
    else \
      npm install --production --no-audit; \
    fi && \
    npm rebuild node-pty --build-from-source

# Copy the rest of the repository
COPY . /app

# Create an isolated virtualenv and install Python deps into it to avoid
# PEP 668 'externally-managed-environment' errors when modifying system
# site-packages inside Debian-based images.
RUN python3 -m venv /opt/venv && \
  /opt/venv/bin/pip install --upgrade pip setuptools wheel && \
  if [ -f /app/biohacker/requirements.txt ]; then \
    # Install the project's requirements into the venv. Use --no-cache-dir
    # to avoid leaving cached wheels behind, and do not silence errors so
    # build fails loudly if a package cannot be installed.
    /opt/venv/bin/pip install --no-cache-dir -r /app/biohacker/requirements.txt; \
  fi && \
  # remove any pip cache left in the layer (keeps image smaller)
  rm -rf /root/.cache/pip /tmp/pip-* || true

ENV PYTHON_BIN=/opt/venv/bin/python
ENV PATH=/opt/venv/bin:${PATH}

# Copy libnode from the nodebase stage so that native addons compiled
# here can find the lib at runtime (libnode.so.*). We copy any matching
# libnode files from the nodebase image into /usr/lib.
COPY --from=nodebase /usr/lib/x86_64-linux-gnu/libnode.so.* /usr/lib/x86_64-linux-gnu/
ENV STRANDS_TOOL_CONSOLE_MODE=enabled

WORKDIR /app/backend
EXPOSE 3001
# Run the app directly with node for simpler signal handling in containers.
CMD ["node", "server.js"]
