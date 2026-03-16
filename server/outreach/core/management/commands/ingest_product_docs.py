import os

from django.core.management.base import BaseCommand

from core.models import OutreachConfig
from core.rag import ingest_from_path


class Command(BaseCommand):
    help = "Ingest product docs from configured path into Chroma."

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, help="Override path (else use config or env).")
        parser.add_argument("--collection", type=str, help="Override collection name.")

    def handle(self, *args, **options):
        path = options.get("path")
        collection = options.get("collection")
        if not path:
            try:
                config = OutreachConfig.get_singleton()
                path = (config.product_docs_path or "").strip()
            except Exception:
                path = ""
            if not path:
                path = os.environ.get("PRODUCT_DOCS_PATH") or os.environ.get("CHROMA_PERSIST_DIR")
            if not path:
                self.stderr.write("Set product_docs_path in config or PRODUCT_DOCS_PATH in env.")
                return
        if not collection:
            try:
                config = OutreachConfig.get_singleton()
                collection = (config.chroma_collection_name or "product_docs").strip() or "product_docs"
            except Exception:
                collection = "product_docs"
        n = ingest_from_path(path, collection_name=collection)
        self.stdout.write(f"Ingested {n} chunks into collection {collection!r}.")
