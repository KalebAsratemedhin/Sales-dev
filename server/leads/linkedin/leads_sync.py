"""
Sync LinkedIn post engagement to Lead records: create or update by profile_url.
"""

import re

from linkedin.engagement import get_engagement_for_post


def placeholder_email(profile_url: str) -> str:
    """Generate a placeholder email from LinkedIn profile URL for Lead.email."""
    if not profile_url or "/in/" not in profile_url:
        slug = "unknown"
    else:
        slug = profile_url.rstrip("/").split("/")[-1] or "unknown"
    slug = re.sub(r"[^a-zA-Z0-9._-]", "-", slug)[:64]
    return f"{slug}@linkedin.placeholder"


def sync_leads_from_post(
    post_input: str,
    *,
    persona_id: int | None = None,
) -> tuple[int, int]:
    """
    Fetch engagement for the post and create or update Lead records.

    post_input: post URL, activity URL, or numeric activity ID.
    persona_id: optional FK to Persona.

    Returns (created_count, updated_count). Updated = 0 (we only get_or_create, no update).
    """
    from config.models import Lead

    profile_urls = get_engagement_for_post(post_input)
    created = 0
    for profile_url in profile_urls:
        if not profile_url:
            continue
        _, was_created = Lead.objects.get_or_create(
            profile_url=profile_url,
            source=Lead.Source.LINKEDIN,
            defaults={
                "email": placeholder_email(profile_url),
                "name": "",
                "company_name": "",
                "company_website": "",
                "persona_id": persona_id,
                "status": Lead.Status.NEW,
            },
        )
        if was_created:
            created += 1
    return created, 0


def sync_leads_from_posts(
    post_inputs: list[str],
    *,
    persona_id: int | None = None,
) -> tuple[int, int]:
    """
    Sync leads from multiple posts. Deduplication is by profile_url across all posts.
    Returns (total_created, total_updated).
    """
    total_created = 0
    total_updated = 0
    for post_input in post_inputs:
        c, u = sync_leads_from_post(post_input, persona_id=persona_id)
        total_created += c
        total_updated += u
    return total_created, total_updated
