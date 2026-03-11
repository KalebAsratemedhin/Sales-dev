import logging
import os
import re
import scrapy
import requests


def _placeholder_email(profile_url: str) -> str:
    slug = (profile_url or "").rstrip("/").split("/")[-1] or "unknown"
    slug = re.sub(r"[^a-zA-Z0-9._-]", "-", slug)[:64]
    return f"{slug}@linkedin.placeholder"


class LeadItemPipeline:
    def __init__(self, api_url=None):
        self.api_url = api_url or os.environ.get("LEADS_API_URL")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(api_url=crawler.settings.get("LEADS_API_URL"))

    def process_item(self, item, spider):
        if not isinstance(item, scrapy.Item):
            return item
        item.setdefault("source", "linkedin")
        if not item.get("email") or "@" not in str(item.get("email", "")):
            item["email"] = _placeholder_email(item.get("profile_url") or "")
        if self.api_url:
            self._post(item)
        return item

    def _post(self, item):
        url = self.api_url.rstrip("/") + "/"
        payload = {
            "email": item.get("email"),
            "name": (item.get("name") or "").strip() or None,
            "company_name": (item.get("company_name") or "").strip() or None,
            "company_website": (item.get("company_website") or "").strip() or None,
            "source": item.get("source", "linkedin"),
            "profile_url": (item.get("profile_url") or "").strip() or None,
        }
        try:
            requests.post(url, json=payload, timeout=10).raise_for_status()
        except requests.RequestException as e:
            logging.getLogger(__name__).warning("POST lead failed %s: %s", url, e)
