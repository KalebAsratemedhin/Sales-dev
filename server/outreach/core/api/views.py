import os
from pathlib import Path

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import OutreachConfig
from core.rag import ingest_from_path
from core.permissions import InternalSecretOrAuthenticated


def _config_to_dict(config):
    return {
        "linkedin_url": config.linkedin_url or "",
        "calendly_scheduling_url": config.calendly_scheduling_url or "",
        "product_docs_path": config.product_docs_path or "",
        "chroma_collection_name": config.chroma_collection_name or "product_docs",
        "updated_at": config.updated_at.isoformat() if config.updated_at else "",
    }


@api_view(["GET", "PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def config_detail(request):
    config = OutreachConfig.get_singleton()
    if request.method == "PATCH":
        data = request.data or {}
        allowed = ("linkedin_url", "calendly_scheduling_url", "product_docs_path", "chroma_collection_name")
        for key in allowed:
            if key in data and data[key] is not None:
                val = str(data[key]).strip()
                setattr(config, key, val[:512] if key != "chroma_collection_name" else val[:128])
        config.save()
    return Response(_config_to_dict(config))


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([InternalSecretOrAuthenticated])
def ingest_docs(request):
    user_id = request.data.get("user_id")
    if not user_id and getattr(request, "user", None) is not None and request.user.is_authenticated:
        user_id = request.user.id

    if user_id is None:
        return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        return Response({"error": "user_id must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

    media_root = os.environ.get("MEDIA_ROOT", "/data")
    base_dir = Path(media_root) / "product_docs" / str(uid)
    collection = f"product_docs_{uid}"
    n = ingest_from_path(str(base_dir), collection_name=collection)
    return Response({"ingested": n, "collection": collection, "docs_dir": str(base_dir)})
