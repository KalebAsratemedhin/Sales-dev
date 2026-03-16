from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.models import OutreachConfig
from core.rag import ingest_from_path


def _config_to_dict(config):
    return {
        "linkedin_url": config.linkedin_url or "",
        "calendly_scheduling_url": config.calendly_scheduling_url or "",
        "product_docs_path": config.product_docs_path or "",
        "chroma_collection_name": config.chroma_collection_name or "product_docs",
        "updated_at": config.updated_at.isoformat() if config.updated_at else "",
    }


@api_view(["GET", "PATCH"])
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
def ingest_docs(request):
    config = OutreachConfig.get_singleton()
    path = (config.product_docs_path or "").strip() or None
    if not path:
        return Response({"error": "product_docs_path not set in config"}, status=status.HTTP_400_BAD_REQUEST)
    collection = (config.chroma_collection_name or "product_docs").strip() or "product_docs"
    n = ingest_from_path(path, collection_name=collection)
    return Response({"ingested": n, "collection": collection})
