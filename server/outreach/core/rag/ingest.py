import re
from pathlib import Path

from .client import get_chroma_client

CHUNK_SIZE = 600
CHUNK_OVERLAP = 100


def _chunk_text(text: str) -> list[str]:
    chunks: list[str] = []
    start = 0
    text = re.sub(r"\s+", " ", text).strip()
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        if chunk:
            chunks.append(chunk)
        start = end - CHUNK_OVERLAP
    return chunks


def ingest_from_path(base_path: str, collection_name: str = "product_docs") -> int:
    base = Path(base_path)
    if not base.exists():
        return 0
    client = get_chroma_client()
    if client is None:
        return 0
    try:
        client.delete_collection(name=collection_name)
    except Exception:
        pass
    coll = client.get_or_create_collection(
        name=collection_name,
        metadata={"description": "Product docs"},
    )
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []
    idx = 0
    for ext in ("*.md", "*.txt"):
        for path in base.rglob(ext):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for chunk in _chunk_text(text):
                ids.append(f"{path.name}_{idx}")
                documents.append(chunk)
                metadatas.append({"source": str(path)})
                idx += 1
    if ids:
        coll.upsert(ids=ids, documents=documents, metadatas=metadatas)
    return len(ids)

