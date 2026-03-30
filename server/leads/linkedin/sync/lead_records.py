"""Lead model helpers for LinkedIn sync (no browser)."""

import logging
import re

from django.db.models import F

from config.models import Lead

logger = logging.getLogger(__name__)


def placeholder_email(profile_url: str) -> str:
    if not profile_url or "/in/" not in profile_url:
        slug = "unknown"
    else:
        slug = profile_url.rstrip("/").split("/")[-1] or "unknown"
    slug = re.sub(r"[^a-zA-Z0-9._-]", "-", slug)[:64]
    return f"{slug}@linkedin.placeholder"


def build_name(info: dict) -> str:
    first = (info.get("first_name") or "").strip()
    last = (info.get("last_name") or "").strip()
    return " ".join(filter(None, [first, last])).strip()


def lead_create_defaults(
    profile_url: str,
    name: str,
    email: str,
    website: str,
    persona_id: int | None,
) -> dict:
    return {
        "email": email or placeholder_email(profile_url),
        "name": name,
        "company_name": "",
        "company_website": website or "",
        "persona_id": persona_id,
        "status": Lead.Status.NEW,
    }


def get_or_create_linkedin_lead(
    profile_url: str,
    user_id: int | None,
    persona_id: int | None,
    name: str,
    scraped_email: str,
    scraped_website: str,
) -> tuple[Lead, bool] | None:
    try:
        return Lead.objects.get_or_create(
            profile_url=profile_url,
            source=Lead.Source.LINKEDIN,
            user_id=user_id,
            defaults=lead_create_defaults(
                profile_url, name, scraped_email, scraped_website, persona_id
            ),
        )
    except Exception as e:
        logger.error("Failed to create/update Lead for %s: %s", profile_url, e)
        return None


def persist_existing_lead_updates(
    lead: Lead,
    profile_url: str,
    *,
    name: str,
    scraped_email: str,
    scraped_website: str,
    comment_url_set: frozenset[str],
) -> bool:
    lead.name = name
    update_fields = ["name"]
    if scraped_email:
        lead.email = scraped_email
        update_fields.append("email")
    if scraped_website:
        lead.company_website = scraped_website
        update_fields.append("company_website")
    if profile_url in comment_url_set:
        lead.linkedin_comment_count = F("linkedin_comment_count") + 1
        update_fields.append("linkedin_comment_count")
    try:
        lead.save(update_fields=update_fields)
    except Exception as e:
        logger.error("Failed to save Lead id=%s: %s", lead.id, e)
        return False
    if profile_url in comment_url_set:
        lead.refresh_from_db(fields=["linkedin_comment_count"])
    return True
