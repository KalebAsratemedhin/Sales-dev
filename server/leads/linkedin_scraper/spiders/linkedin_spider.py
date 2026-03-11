import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import scrapy
from dotenv import load_dotenv

from linkedin_scraper.items import LeadItem

LOGIN_URL = "https://www.linkedin.com/uas/login"
LOGIN_SUBMIT_URL = "https://www.linkedin.com/uas/login-submit"

DATE_FMT = "%Y-%m-%d"


def _placeholder_email(profile_url: str) -> str:
    slug = (profile_url or "").rstrip("/").split("/")[-1] or "unknown"
    slug = re.sub(r"[^a-zA-Z0-9._-]", "-", slug)[:64]
    return f"{slug}@linkedin.placeholder"


def _normalize_profile_url(href: str) -> str | None:
    if not href or "/in/" not in href:
        return None
    path = urlparse(href).path
    if "/in/" not in path:
        return None
    return urljoin("https://www.linkedin.com", path.split("?")[0])


# Skip strings that are UI labels, not names
_NAME_SKIP = re.compile(r"^(Report|Like|Reply|React|Comment|Follow|Message|\.\.\.|[\d]+[wdhm]|·)$", re.I)


def _clean_name(s: str) -> str:
    s = (s or "").strip()
    if not s or len(s) > 80 or _NAME_SKIP.match(s):
        return ""
    return s


def _parse_date_from_page(response: scrapy.http.Response) -> datetime | None:
    dt = response.css("time::attr(datetime)").get()
    if dt:
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%f"):
            try:
                return datetime.strptime(dt.strip()[:19], fmt)
            except ValueError:
                continue
    return None


def _in_date_range(d: datetime | None, start: str, end: str) -> bool:
    if d is None:
        return True
    try:
        s = datetime.strptime(start, DATE_FMT)
        e = datetime.strptime(end, DATE_FMT)
        return s.date() <= d.date() <= e.date()
    except ValueError:
        return True


def _is_feed_url(url: str) -> bool:
    u = (url or "").strip().lower()
    return "/feed/" in u and "/feed/update/urn:li:activity" not in u


def _is_post_url(url: str) -> bool:
    return "/feed/update/urn:li:activity" in (url or "") or "/posts/" in (url or "")


def _is_company_url(url: str) -> bool:
    return "/company/" in (url or "").strip().lower()


def _is_profile_url(url: str) -> bool:
    u = (url or "").strip()
    return "/in/" in u and not _is_post_url(u)


def _normalize_post_url(response: scrapy.http.Response, href: str) -> str | None:
    if not href:
        return None
    if "/feed/update/urn:li:activity" in href:
        path = urlparse(href).path
        path = path.split("?")[0].rstrip("/") + "/"
        return urljoin("https://www.linkedin.com", path)
    if "/posts/" in href:
        return response.urljoin(href.split("?")[0].rstrip("/") + "/")
    return None


class LinkedInSpider(scrapy.Spider):
    name = "linkedin"
    allowed_domains = ["www.linkedin.com", "linkedin.com", "et.linkedin.com"]
    custom_settings = {"DOWNLOAD_DELAY": 3, "CONCURRENT_REQUESTS": 1}

    def start_requests(self):
        urls_arg = (getattr(self, "urls", "") or "").strip()
        date_start = (getattr(self, "date_start", "") or "").strip()
        date_end = (getattr(self, "date_end", "") or "").strip()
        if not urls_arg:
            self.logger.warning("No urls= provided; pass company, profile, feed, or post URL(s) and date_start/date_end.")
            return

        urls_list = [u.strip() for u in urls_arg.split(",") if u.strip()]
        if not urls_list:
            return

        env_path = Path(os.getcwd()) / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        email = os.environ.get("LINKEDIN_EMAIL", "").strip()
        password = os.environ.get("LINKEDIN_PASSWORD", "").strip()
        if email and password:
            self._pending_urls_list = urls_list
            self._date_start = date_start
            self._date_end = date_end
            self.logger.info("Logging in with LINKEDIN_EMAIL from .env")
            yield scrapy.Request(
                LOGIN_URL,
                callback=self.parse_login_page,
                cb_kwargs={"email": email, "password": password},
            )
            return

        for url in urls_list:
            yield self._crawl_request(url, date_start, date_end)

    def _crawl_request(self, url, date_start, date_end):
        if _is_feed_url(url):
            return scrapy.Request(
                url,
                callback=self.parse_feed,
                cb_kwargs={"date_start": date_start, "date_end": date_end},
            )
        if _is_post_url(url):
            return scrapy.Request(
                url,
                callback=self.parse_post_page,
                cb_kwargs={"date_start": date_start, "date_end": date_end},
            )
        if _is_company_url(url) or _is_profile_url(url):
            return scrapy.Request(
                url,
                callback=self.parse_company_or_profile,
                cb_kwargs={"date_start": date_start, "date_end": date_end},
            )
        self.logger.warning("Skipped URL (not company, profile, feed, or post): %s", url[:80])
        return None

    def parse_login_page(self, response, email=None, password=None):
        csrf = (
            response.css("#loginCsrfParam-login::attr(value)").get()
            or response.css('input[name="loginCsrfParam"]::attr(value)').get()
        )
        if not csrf:
            self.logger.error("Could not find loginCsrfParam on LinkedIn login page")
            return
        yield scrapy.FormRequest(
            LOGIN_SUBMIT_URL,
            formdata={
                "session_key": email,
                "session_password": password,
                "loginCsrfParam": csrf,
            },
            callback=self.after_login,
        )

    def after_login(self, response):
        if "login" in response.url and "checkpoint" not in response.url.lower():
            self.logger.warning("Login may have failed (still on login page); continuing anyway.")
        urls_list = getattr(self, "_pending_urls_list", [])
        date_start = getattr(self, "_date_start", "")
        date_end = getattr(self, "_date_end", "")
        for url in urls_list:
            req = self._crawl_request(url, date_start, date_end)
            if req is not None:
                yield req

    def parse_feed(self, response, date_start=None, date_end=None):
        seen = set()
        for a in response.css('a[href*="/feed/update/urn:li:activity"]'):
            href = a.xpath("@href").get()
            full = _normalize_post_url(response, href)
            if full and full not in seen:
                seen.add(full)
                yield scrapy.Request(
                    full,
                    callback=self.parse_post_page,
                    cb_kwargs={"date_start": date_start, "date_end": date_end},
                )

    def parse_company_or_profile(self, response, date_start=None, date_end=None):
        seen = set()
        for a in response.css('a[href*="/feed/update/urn:li:activity"], a[href*="/posts/"]'):
            href = a.xpath("@href").get()
            full = _normalize_post_url(response, href)
            if full and full not in seen:
                seen.add(full)
                yield scrapy.Request(
                    full,
                    callback=self.parse_post_page,
                    cb_kwargs={"date_start": date_start, "date_end": date_end},
                )
        if not seen:
            for aid in re.findall(r"urn:li:activity:(\d+)", response.text):
                full = f"https://www.linkedin.com/feed/update/urn:li:activity:{aid}/"
                if full not in seen:
                    seen.add(full)
                    yield scrapy.Request(
                        full,
                        callback=self.parse_post_page,
                        cb_kwargs={"date_start": date_start, "date_end": date_end},
                    )
        if not seen:
            for slug in re.findall(r"/posts/([^\"'?>\s]+)", response.text):
                slug = slug.rstrip("/").split("?")[0]
                if slug and "-activity-" in slug:
                    full = response.urljoin(f"/posts/{slug}/")
                    if full not in seen:
                        seen.add(full)
                        yield scrapy.Request(
                            full,
                            callback=self.parse_post_page,
                            cb_kwargs={"date_start": date_start, "date_end": date_end},
                        )
        if not seen and "/company/" in response.url and "/posts/" not in response.url.split("?")[0]:
            posts_url = response.url.split("?")[0].rstrip("/") + "/posts/?feedView=all"
            yield scrapy.Request(
                posts_url,
                callback=self.parse_company_or_profile,
                cb_kwargs={"date_start": date_start, "date_end": date_end},
            )
        elif not seen:
            self.logger.info("No post links found on %s (page may need JS or different structure)", response.url[:60])

    def parse_post_page(self, response, date_start=None, date_end=None):
        if date_start and date_end:
            d = _parse_date_from_page(response)
            if not _in_date_range(d, date_start, date_end):
                return
        yield from self._extract_engagement_from_response(response, interaction_type="engagement")

    def _extract_engagement_from_response(self, response, interaction_type="engagement"):
        seen = set()
        exclude = getattr(self, "_exclude_profile_url", None)
        for a in response.css('a[href*="/in/"]'):
            href = a.xpath("@href").get()
            profile_url = _normalize_profile_url(href)
            if not profile_url or profile_url in seen:
                continue
            if exclude and _profile_url_canonical(profile_url) == exclude:
                continue
            seen.add(profile_url)
            name = (
                a.css("::text").get()
                or a.xpath("./@aria-label").get()
                or a.xpath("./parent::*/span/text()").get()
                or a.xpath("./preceding-sibling::span[1]/text()").get()
                or a.xpath("./following-sibling::span[1]/text()").get()
                or a.xpath("./ancestor::*[.//span][1]//span[@dir='ltr']/text()").get()
                or a.xpath("./ancestor::*[.//span][1]//span/text()").get()
                or ""
            )
            name = _clean_name(name)
            yield LeadItem(
                email=_placeholder_email(profile_url),
                name=name,
                company_name="",
                company_website="",
                source="linkedin",
                profile_url=profile_url,
                interaction_type=interaction_type,
            )
        for match in re.findall(r'linkedin\.com/in/([a-zA-Z0-9_-]+)', response.text):
            slug = match.strip()
            if len(slug) > 1:
                profile_url = f"https://www.linkedin.com/in/{slug}/"
                if profile_url in seen:
                    continue
                if exclude and _profile_url_canonical(profile_url) == exclude:
                    continue
                seen.add(profile_url)
                yield LeadItem(
                    email=_placeholder_email(profile_url),
                    name="",
                    company_name="",
                    company_website="",
                    source="linkedin",
                    profile_url=profile_url,
                    interaction_type=interaction_type,
                )
