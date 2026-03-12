"""
Fetch engagement (comments + reactions) for a post and return list of profile URLs.
"""

from linkedin.client import get_comments, get_reactions, person_urn_to_profile_url
from linkedin.post_urn import activity_urn_from_post_url


def get_engagement_profile_urls(activity_urn: str) -> list[str]:
    """
    Get all unique profile URLs of people who commented or reacted on the post.
    activity_urn: e.g. urn:li:activity:7302346926123798528
    """
    person_urns = set()

    for comment in get_comments(activity_urn):
        actor = comment.get("actor")
        if actor and isinstance(actor, str) and actor.startswith("urn:li:person:"):
            person_urns.add(actor)

    for reaction in get_reactions(activity_urn):
        created = reaction.get("created") or {}
        actor = created.get("actor")
        if actor and isinstance(actor, str) and actor.startswith("urn:li:person:"):
            person_urns.add(actor)

    return [person_urn_to_profile_url(urn) for urn in person_urns if person_urn_to_profile_url(urn)]


def get_engagement_for_post(post_input: str) -> list[str]:
    """
    Resolve post URL or ID to activity URN, then return profile URLs of engagers.
    post_input: full post URL, activity URL, or numeric activity ID.
    """
    urn = activity_urn_from_post_url(post_input)
    if not urn:
        return []
    return get_engagement_profile_urls(urn)
