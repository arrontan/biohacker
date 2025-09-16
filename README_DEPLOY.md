# Biohacker — Deployment & Setup Guide

This document gathers the deployment, DNS, SMTP, auth, database, and runtime notes discussed in our planning sessions. It's a living guide for local development and production rollout (Vercel frontend + separate backend). Do not store secrets in this file.

---

## Goals
- Local dev: Docker Compose with Postgres, optional MinIO, Node backend (PTY), and Next.js frontend.
- Production: Vercel for frontend, a long-lived host (Fly.io / DigitalOcean / EC2) for backend PTY, S3 for file storage, and Postgres (managed or RDS).
- Authentication: NextAuth with Prisma adapter (Google + GitHub OAuth initially; optional Email provider).
- Execution: Ephemeral job containers that mount user storage for isolated runs (future work).

---

## Quick local checklist
1. Copy `.env.example` to `.env` and fill values (see environment variables section below).
2. Start Postgres in Docker Compose:

```powershell
docker compose up -d postgres
```

3. Start backend and frontend for development:

```powershell
# Backend
cd backend
npm install
npm start

# Frontend
cd frontend/next-app
npm install
npm run dev
```

4. Optional test services:
- MailHog for SMTP testing

```bash
docker run -p 1025:1025 -p 8025:8025 mailhog/mailhog
# set SMTP_URL=smtp://localhost:1025
```

- MinIO for S3-compatible storage

```bash
docker run -p 9000:9000 -e MINIO_ROOT_USER=minio -e MINIO_ROOT_PASSWORD=minio123 quay.io/minio/minio server /data
# use endpoint http://localhost:9000 and the SDK with path-style access
```

---

## Environment variables
Create a `.env` file in the repo root (example variables shown — DO NOT commit secrets):

```
# App
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=long_random_value
DATABASE_URL=postgresql://biohacker:changeme@postgres:5432/biohacker

# NextAuth providers (example placeholders)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_ID=
GITHUB_SECRET=

# Email (SMTP)
SMTP_URL=smtp://USERNAME:PASSWORD@smtp.example.com:587
EMAIL_FROM="Biohacker <no-reply@biohacker.ac>"

# AWS/S3
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-west-2
AWS_S3_BUCKET=

# Backend
PYTHON_BIN=python3
PTY_PORT=3001

# Dev helpers
STRANDS_TOOL_CONSOLE_MODE=enabled
```

Also populate production secrets in Vercel/Host provider and GitHub Actions secrets (GHCR token, AWS creds, NEXTAUTH_SECRET).

---

## Prisma & NextAuth setup (frontend)
1. From `frontend/next-app` install dependencies:

```powershell
npm install prisma @prisma/client next-auth @next-auth/prisma-adapter
npx prisma init
```

2. Use the provided Prisma schema (models: User, Account, Session, VerificationToken, File, Job). Run:

```powershell
npx prisma generate
npx prisma migrate dev --name init
```

3. Add NextAuth API route at `pages/api/auth/[...nextauth].js` and use the Prisma adapter. Configure providers (Google, GitHub) and make sure `NEXTAUTH_URL` is correct.

---

## Google & GitHub OAuth (local dev)
- For Google OAuth client (Web app), add these local settings:
  - Authorized JavaScript origins:
    - http://localhost:3000
    - http://127.0.0.1:3000 (optional)
  - Authorized redirect URIs:
    - http://localhost:3000/api/auth/callback/google
    - http://127.0.0.1:3000/api/auth/callback/google

- For GitHub OAuth app:
  - Homepage URL: http://localhost:3000
  - Authorization callback URL: http://localhost:3000/api/auth/callback/github

- For production, create separate OAuth clients for each domain and add production callback URIs.

---

## DNS & Cloudflare (summary)
You own `biohacker.ac` and use Cloudflare as DNS.

### Records to add:
1. Frontend (Vercel) — add domain in Vercel and follow instructions. Usually add CNAME for `www` and ANAME/ALIAS or A records for root.
2. Backend (Fly.io / host) — add A or CNAME records as provider instructs. Make backend DNS `DNS only` (gray cloud) to avoid WebSocket interference.
3. Email records (DNS-only):
   - TXT @ -> SPF value provided by SMTP provider (e.g., `v=spf1 include:sendgrid.net ~all`)
   - TXT <selector>._domainkey -> DKIM public key (provider gives)
   - TXT _dmarc -> DMARC policy (start with `p=none`)
   - MX records -> provider (if needed for inbound)

### Cloudflare tips:
- Set email-related records to DNS-only (gray cloud).
- For frontend you can proxy (orange cloud); for backend and services that need raw TCP or WebSocket keep DNS-only.

## Cloudflare DNS records (exact examples)

The following is a concrete set of DNS records you can add in Cloudflare for common setups. Replace the `TARGET` or `IP` placeholders with values from your providers (Vercel, Fly.io, SendGrid/Mailgun).

1) Frontend (Vercel) — example

  - Type: CNAME
    Name: www
    Target: cname.vercel-dns.com   # use the CNAME Vercel gives
    Proxy status: Proxied (orange cloud)

  - Type: A (if Vercel provides A records for apex)
    Name: @
    Content: <VERCEL_A_IP_1>
    Proxy status: Proxied

  - Alternate: If Vercel gives an ALIAS/ANAME for the apex, use that instead of A records.

2) Backend (Fly.io or self-hosted) — example (DNS-only)

  - Type: A
    Name: api
    Content: <BACKEND_IP_OR_PROVIDER_IP>
    Proxy status: DNS only (gray cloud)

  - Or (if provider gives a hostname):
    Type: CNAME
    Name: api
    Target: <provider-hostname>
    Proxy status: DNS only

  - Notes: Keep backend records DNS-only for WebSocket and PTY reliability. If you must proxy, ensure the proxy supports WebSockets and long-lived TCP connections.

3) Email deliverability records (DNS-only) — example placeholders

  - SPF (TXT)
    Type: TXT
    Name: @
    Content: "v=spf1 include:sendgrid.net ~all"   # replace include:... with your provider
    Proxy status: DNS only

  - DKIM (TXT) – provider gives selector(s)
    Type: TXT
    Name: s1._domainkey
    Content: "v=DKIM1; k=rsa; p=<LONG_PUBLIC_KEY_FROM_PROVIDER>"
    Proxy status: DNS only

    (If provider supplies s2._domainkey, add that too.)

  - DMARC (TXT)
    Type: TXT
    Name: _dmarc
    Content: "v=DMARC1; p=none; rua=mailto:postmaster@biohacker.ac; pct=100"
    Proxy status: DNS only

  - MX (if you need inbound email routed via provider)
    Type: MX
    Name: @
    Content: <provider-mx-hostname>
    Priority: 10
    Proxy status: DNS only

4) Misc / helpful records

  - TXT for verification (Google, GitHub, etc.)
    Type: TXT
    Name: @ or the value provider asks for
    Content: <verification-string>
    Proxy status: DNS only

Cloudflare behavior notes:
- Make DKIM/SPF/DMARC/TXT/MX records DNS-only (gray cloud) — Cloudflare should not proxy these.
- Use proxied records (orange cloud) for the frontend to gain CDN and TLS benefits.
- Keep backend/API records DNS-only unless you use a Cloudflare product that explicitly supports proxied TCP/WebSocket (Spectrum/Enterprise).

---

## SMTP provider options
- SendGrid: easy magic-link/email sending, good docs.
- Mailgun: developer-friendly, good for transactional email.
- Amazon SES: low cost, more setup (IAM & verification).

Recommended local/test flow:
- Run MailHog for testing and set `SMTP_URL=smtp://localhost:1025`.
- For production, add SendGrid/Mailgun keys as secrets and set `SMTP_URL` accordingly.

SMTP URL examples:
- SendGrid (SMTP): `smtp://apikey:SENDGRID_API_KEY@smtp.sendgrid.net:587` (username is `apikey`)
- Mailgun: `smtp://postmaster%40your-domain:MAILGUN_SMTP_PASSWORD@smtp.mailgun.org:587` (URL-encode `@`)

---

## Cloud / Hosting recommendations
- Frontend: Vercel (Next.js native). Use Vercel to host NextAuth pages.
- Backend (PTY + runner): Use a separate container host (Fly.io, EC2, DigitalOcean App Platform). Vercel cannot host long-lived PTY child processes.
- Storage: S3 for production; MinIO for dev.

---

## Security and secrets
- Rotate any keys accidentally exposed. Do not commit `.env`.
- Store CI and production secrets in GitHub Actions Secrets and your hosting platform secret store.
- Use `NEXTAUTH_SECRET` for NextAuth session encryption.

---

## Deployment order (recommended)
1. Add domain to Vercel and follow DNS instructions.
2. Deploy backend to Fly.io (or chosen host) and get its hostname/IP.
3. Add backend DNS record (DNS-only).
4. Configure SMTP provider DNS (SPF/DKIM) and verify.
5. Add production env vars/secrets to Vercel and backend host.
6. Test OAuth + email flows, then switch DMARC to stricter policy after monitoring.

---

## Future work (not in this doc)
- Implement ephemeral job containers for user jobs (spawned on demand, mount user storage, enforce resource limits).
- Add shared container with default apps like python and R
- Add multi-tenant storage quotas, scheduled storage accounting, and cleanup jobs.
- Migrate orchestration to Docker Swarm or Kubernetes for scale.

---

## Important TODOs (from conversation)
- Rotate exposed AWS and GHCR tokens immediately.
- Implement Prisma models and migrations.
- Wire NextAuth with Prisma adapter in `frontend/next-app`.
- Add backend upload endpoints to write to S3 and update user file metadata.
- Add `README_DEPLOY.md` (this file) to repository root.

---

## Contact & notes
Keep secrets out of PRs; create GitHub Secrets and Vercel environment variables for production deployments. For any DNS/SMTP provider you choose, paste their DNS record outputs here and I can convert them into exact Cloudflare entries.


---

(End of deployment guide)
