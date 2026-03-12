"""
API endpoint to sync leads from LinkedIn post engagement.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from linkedin.leads_sync import sync_leads_from_posts
from linkedin.client import LinkedInAPIError


@api_view(["POST"])
@permission_classes([AllowAny])
def sync(request):
    """
    POST body: { "post_urls": ["url1", "url2"], "persona_id": null }
    Fetches comments/reactions for each post and creates Lead records (get_or_create by profile_url).
    """
    post_urls = request.data.get("post_urls")
    if isinstance(post_urls, str):
        post_urls = [post_urls]
    if not post_urls or not isinstance(post_urls, list):
        return Response(
            {"error": "Provide post_urls (array of post URLs or activity IDs)."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    persona_id = request.data.get("persona_id")
    try:
        created, updated = sync_leads_from_posts(post_urls, persona_id=persona_id)
        return Response(
            {"created": created, "updated": updated},
            status=status.HTTP_200_OK,
        )
    except LinkedInAPIError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_502_BAD_GATEWAY,
        )
