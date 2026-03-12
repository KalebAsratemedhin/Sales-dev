# LinkedIn engagement → Leads

Session-based integration: log in once with Selenium, then call LinkedIn’s REST API to fetch comments and reactions on posts and create Lead records.

## Setup

1. **Install dependencies** (already in `requirements.txt`):
   - `selenium`, `undetected-chromedriver`
   - Chrome or Chromium must be installed on the machine (for headless login).

2. **Set credentials** (env or `.env`):
   - `LINKEDIN_EMAIL`
   - `LINKEDIN_PASSWORD`

3. **Refresh session** (run when needed, or after expiry):
   ```bash
   python manage.py linkedin_refresh_session
   ```
   Use `--no-headless` if you need to complete 2FA in a visible browser.

4. **Sync leads from post(s)**:
   ```bash
   python manage.py linkedin_sync_post "https://www.linkedin.com/feed/update/urn:li:activity:123/"
   python manage.py linkedin_sync_post 7302346926123798528 "https://..." --persona-id=1
   ```

   Or via API:
   ```bash
   curl -X POST http://localhost:8000/api/linkedin/sync/ \
     -H "Content-Type: application/json" \
     -d '{"post_urls": ["https://www.linkedin.com/feed/update/urn:li:activity:123/"], "persona_id": null}'
   ```

## Modules

- **session** – Load/save cookies; `refresh_session()` logs in with Selenium and saves cookies.
- **client** – HTTP client for `socialActions/.../comments` and `reactions/(entity:...)`.
- **post_urn** – Normalize post URL or ID → `urn:li:activity:...`.
- **engagement** – Fetch all commenters + reactors for a post → list of profile URLs.
- **leads_sync** – Create/update `Lead` records (get_or_create by `profile_url`, source=linkedin).

Session file: `data/linkedin_session.json` (or `LINKEDIN_SESSION_PATH` in settings).
