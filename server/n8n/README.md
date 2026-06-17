# n8n workflows

Workflows under `workflows/` are **templates**. The outreach service provisions per-user Gmail inbound workflows automatically when a user connects Google in SalesMind Settings.

| Template | Purpose |
|----------|---------|
| `gmail-inbound-reply.json` | Poll Gmail for unread replies → `POST /api/outreach/handle-reply/` → send AI draft via Gmail |
| `daily-followups.json` | Daily schedule → `POST /api/outreach/run-followups/` (import once in n8n UI) |

## Google connect (Settings → Connect Google)

1. Start stack: `docker compose up` from `server/`.
2. **Google Cloud Console** (one OAuth client for Gmail + Calendar):
   - Enable **Gmail API** and **Google Calendar API**
   - Add authorized redirect URI:
     - `http://localhost:3000/settings/google-callback`
3. **server/.env**:
   - `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET`
   - `GOOGLE_OAUTH_REDIRECT_URI=http://localhost:3000/settings/google-callback`
   - `N8N_API_KEY` — create in n8n: **Settings → API → Create API key** (credential + workflow scopes)
4. In SalesMind: **Settings → Connect Google**. Outreach will:
   - Store OAuth tokens in Postgres (`GoogleConnection`, per user)
   - Create an n8n `gmailOAuth2` credential for that user
   - Create and **activate** a workflow: `SalesMind — Gmail Inbound Reply (user {id})`
5. Outbound email (inbox send, follow-ups) uses the **Gmail API** with the same connected account.

If connect fails after Google sign-in, check Settings for the n8n error or verify `N8N_API_KEY` and restart outreach.

## Follow-ups workflow

1. Import `daily-followups.json` in n8n (**Settings → Import workflow**).
2. Set `LEADS_SERVICE_INTERNAL_SECRET` in the HTTP node (or use `dev-internal-secret` for local dev).
3. Activate the workflow in n8n.

## Troubleshooting

| Symptom | Likely cause |
|---------|----------------|
| Connect Google fails immediately | `N8N_API_KEY` missing — set in `server/.env` and restart outreach |
| Google sign-in works but connect fails | n8n credential schema mismatch — rebuild outreach; use **Sync to n8n** after updating |
| Settings shows n8n sync error | Click **Sync to n8n** after fixing API key |
| No n8n executions when a lead replies | Per-user workflow inactive, wrong Gmail account, or reply already **read** |
| Reply in Gmail but empty SalesMind inbox | `handle-reply` could not match thread — `from_email` must match the lead's `to_email` |

**Note:** Sending from the SalesMind **Inbox UI** uses the Gmail API (not n8n). n8n handles inbound reply polling only.

## URLs (Docker network)

- Outreach: `http://outreach:8003`
- n8n API: `http://n8n:5678`
- Via host/nginx: `http://localhost:8080`
