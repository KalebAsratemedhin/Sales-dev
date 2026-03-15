# LinkedIn engagement → Leads

Session-based integration (Option B): log in once with Selenium and save cookies; when syncing, load the post page in a browser with those cookies and scrape profile links (commenters/reactors) from the DOM. No LinkedIn REST API or OAuth app.

## Setup

1. **Install dependencies** (already in `requirements.txt`):
   - `selenium`, `undetected-chromedriver`
   - Chrome or Chromium on the machine (or in the Docker image; see Dockerfile).

2. **Set credentials** (env or `.env`):
   - `LINKEDIN_EMAIL`
   - `LINKEDIN_PASSWORD`

3. **Refresh session** (run when needed, or after expiry):
   ```bash
   python manage.py linkedin_refresh_session
   ```
   Use `--no-headless` if you need to complete 2FA in a visible browser.

4. **Sync leads from post(s)** (opens the post in a headless browser and scrapes profile URLs):
   ```bash
   python manage.py linkedin_sync_post "https://www.linkedin.com/feed/update/urn:li:activity:123/"
   python manage.py linkedin_sync_post 7302346926123798528 "https://..." --persona-id=1
   ```

   Or via API:
   - **Sync from posts**: `POST /api/linkedin/sync/posts/` with `{"post_urls": ["..."], "persona_id": null}`.
   - **Sync from profile (date range)**: `POST /api/linkedin/sync/profile/` with `{"profile_url": "https://www.linkedin.com/in/username/", "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "persona_id": null, "max_scrolls": 10}`.

## Package layout

- **core** – `constants`, `session` (cookies, `refresh_session`), `post_urn` (URL/URN normalization), `client` (legacy REST API).
- **browser** – `driver`, `engagement` (post → profile URLs), `profile` (name/email/website), `posts` (profile activity → post URLs); `get_engagement_for_post` re-exported.
- **sync** – `sync_leads_from_post`, `sync_leads_from_posts`, `sync_leads_from_profile`.
- **api** – REST views and serializers: `sync/posts/`, `sync/profile/`.

Session file: `data/linkedin_session.json` (or `LINKEDIN_SESSION_PATH` in settings).
