# LinkedIn engagement scraper

Starts from a **company page**, **profile**, or **feed** URL; discovers **posts** from that page; filters posts by **date range**; extracts users who **liked** or **commented** on those posts. No need to pass post URLs.

**Authentication:** If `LINKEDIN_EMAIL` and `LINKEDIN_PASSWORD` are set in `server/leads/.env`, the spider logs in before crawling. Set `LINKEDIN_MY_PROFILE_URL` to your profile URL (e.g. `https://www.linkedin.com/in/yourusername`) to exclude yourself from the scraped leads. Run from `server/leads` so `.env` is found.

## Test (no network)

From `server/leads`:

```bash
python -m unittest linkedin_scraper.tests.test_spider -v
```

## Run

From `server/leads`:

```bash
scrapy crawl linkedin -a date_start=2026-01-01 -a date_end=2026-03-15 -a urls="https://et.linkedin.com/company/mereb-technologies" -O out.json
```

- **urls**: Company page (`.../company/name`), profile (`.../in/username`), feed (`.../feed/`), or post URL(s). The spider finds that entity’s posts from the page (no post URLs required).
- **date_start**, **date_end**: `YYYY-MM-DD`. Only posts published in this range are considered; engagers (likes/comments) are extracted from those posts.

Flow: fetch the given URL → collect post links (e.g. from company `/posts/?feedView=all`) → for each post in date range, parse the post page and extract profile links (commenters/engagers) as leads. Names are taken from link context when possible. To POST leads to the Lead Service, set `LEADS_API_URL` and enable `LeadItemPipeline` in `settings.py`.
