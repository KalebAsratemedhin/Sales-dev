# n8n workflows

Import JSON files from `workflows/` via n8n UI (**Settings → Import workflow**).

| Workflow | Purpose |
|----------|---------|
| `gmail-inbound-reply.json` | Poll Gmail for unread replies → `POST /api/outreach/handle-reply/` → send AI draft via **Gmail** |
| `daily-followups.json` | Daily schedule → `POST /api/outreach/run-followups/` |

## Setup

1. Start stack: `docker compose up` from `server/`.
2. Open n8n at http://localhost:5678 (default `admin` / `changeme`).
3. **Gmail OAuth (required for inbound workflow):**
   - Google Cloud Console → enable **Gmail API** → OAuth consent screen → create OAuth client (Web application).
   - Authorized redirect URI: `http://localhost:5678/rest/oauth2-credential/callback`
   - In n8n: **Credentials → Add → Gmail OAuth2** → paste Client ID / Secret → **Connect my account**.
   - Open **SalesMind — Gmail Inbound Reply** → assign that credential on **both** Gmail nodes (Trigger + Send).
   - Use the **same Gmail account** as `GMAIL_SENDER` in `server/.env` (outreach sends via SMTP from that inbox; n8n must read replies there).
4. **Activate** the workflow (toggle on). Import/publish alone is not enough.
5. Set n8n env `LEADS_SERVICE_INTERNAL_SECRET` for the follow-up workflow (or hardcode in the HTTP node for local dev: `dev-internal-secret`).

### Troubleshooting inbound replies

| Symptom | Likely cause |
|---------|----------------|
| n8n logs: `problem in 'Gmail Trigger' ... 'undefined'` | Gmail OAuth not connected on the trigger node |
| No n8n executions when a lead replies | Workflow inactive, wrong Gmail account, or reply already **read** (trigger filters `unread` only) |
| Execution runs but Handle Reply fails with `JSON parameter needs to be valid JSON` | Re-import `gmail-inbound-reply.json` — Handle Reply must use `JSON.stringify(...)` for the body |
| Execution runs but Handle Reply fails | Re-import workflow after URL fix; outreach must allow Docker hostnames (`ALLOWED_HOSTS` in compose) |
| Reply in Gmail but empty SalesMind inbox | `handle-reply` could not match thread — `from_email` must match the lead's `to_email` on the thread |

**Note:** Sending from the SalesMind **Inbox UI** goes through the outreach API directly (SMTP). That path does **not** use n8n and will not appear in n8n executions.

## URLs (Docker network)

- Outreach: `http://outreach:8003`
- Via host/nginx: `http://localhost:8080`
