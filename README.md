# SalesMind — Autonomous SDR

A full-stack **autonomous sales development** system: lead storage, website research (LLM), personalized outreach email, and inbox reply handling with product-docs RAG and a static Calendly link. The dashboard (SalesMind) is a Next.js app; backend services are Django with RabbitMQ and optional n8n for workflows.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│  client/  — Next.js (App Router, TypeScript, Tailwind, RTK Query)       │
│  SalesMind dashboard: leads, config, research/outreach monitors, inbox   │
│  Talks to backend via HTTP (Leads API, Outreach config)                  │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  server/  — Backend services (Django)                                    │
│  • Lead Service    — CRUD leads, enqueue research via RabbitMQ          │
│  • Research Service — Fetch website, Gemini analysis, pain points        │
│  • Outreach Service — Draft/send email (Gmail), store threads, config    │
│  • Inbox reply handling — HTTP endpoint for n8n; agent + product docs   │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                             ▼                             ▼
   RabbitMQ (research.request,   Gemini / LangChain            Gmail (SMTP,
   outreach.request,             (research + outreach          inbox via n8n)
   lead.status.update)           + product docs RAG)
```

- **Orchestration:** Lead creation → `research.request` → Research runs → `outreach.request` → Outreach drafts and sends email → lead status updated. Replies are handled by n8n calling Outreach’s `handle-reply` endpoint; the agent uses thread memory and product-docs search to draft replies.
- **Data:** Each service has its own Django DB. Outreach stores `EmailThread`, `SentEmail`, and `OutreachConfig`. Redis is used for rate limiting.

---

## Features

| Area | What it does |
|------|----------------|
| **Leads** | Store and list leads; filter by status (new, researched, emailed, replied, meeting_booked). Creation can trigger research via queue. |
| **Research** | Fetch company website, run Gemini-based analysis, store summary and pain points; then enqueue outreach. |
| **Outreach** | Consume research events; draft one personalized email per lead (Gemini + research + optional persona); send via Gmail (or stub); store thread and sent emails. |
| **Inbox** | n8n watches Gmail for replies and POSTs to Outreach; Outreach runs the inbox agent (product-docs RAG + static Calendly link, per-lead memory) and returns a reply body for n8n to send. |
| **Dashboard** | Leads list and detail, system configuration (LinkedIn URL, Calendly, product docs path, Chroma), research/outreach monitors (UI), inbox-style thread view (UI). Wired today: Leads API and Outreach config. |

*Planned but not yet implemented:* automated lead discovery from LinkedIn/Twitter; richer n8n ingestion workflows.

---

## Repository structure

| Path | Description |
|------|-------------|
| **`client/`** | Next.js app — SalesMind UI (dashboard, leads, config, research, outreach, inbox). |
| **`server/`** | Django apps: leads (core + LinkedIn), research, outreach (config, ingest, handle-reply). |
| **`docs/`** | Design and implementation docs (overview, architecture, walkthroughs, frontend plan). |
| **`stitch_salesmind_prd/`** | Stitch design exports (HTML + PNG) used as UI reference for the client. |

---

## Getting started

### Prerequisites

- Node.js and npm (for the client)
- Python 3.x and pip (for the server)
- RabbitMQ and Redis (for backend workers and rate limiting)
- Optional: n8n for Gmail polling and reply handling

### Client (dashboard)

```bash
cd client
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The dashboard shows leads, configuration, and research/outreach status when the backend is available.

### Server (backend)

Backend layout and how to run it (Nginx, RabbitMQ, Celery, etc.) are described in the docs:

- **`docs/01-overview-and-features.md`** — Features and logical architecture
- **`docs/05-server-nginx-rabbitmq-walkthrough.md`** — Server layout and RabbitMQ
- **`docs/06-docker-full-stack-walkthrough.md`** — Full stack with Docker

Configure the Lead and Outreach services (DB, broker, Gmail env vars, etc.) per those guides.

---

## Documentation

| Doc | Contents |
|-----|----------|
| **01-overview-and-features.md** | Features, logical architecture, data flow |
| **02-design.md** | Service boundaries, data flow, technology choices |
| **03-implementation-plan.md** | APIs, Celery tasks, structure |
| **13-frontend-implementation-plan.md** | Client stack, screens, phasing |
| **05–08, 10, 12** | Server/RabbitMQ, Docker, n8n, outreach ops, roadmap |

---

## License

Private / internal use unless otherwise specified.
