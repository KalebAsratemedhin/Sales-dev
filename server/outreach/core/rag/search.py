from .client import get_chroma_client


def search_chroma(query: str, collection_name: str = "product_docs", n_results: int = 5) -> list[dict]:
    client = get_chroma_client()
    if client is None:
        return []
    try:
        coll = client.get_collection(name=collection_name)
    except Exception:
        return []
    try:
        out = coll.query(query_texts=[query], n_results=n_results)
    except Exception:
        return []
    documents = out.get("documents") or []
    if not documents:
        return []
    metadatas = out.get("metadatas") or [[]]
    meta_row = metadatas[0] if metadatas else []
    results: list[dict] = []
    for i, doc in enumerate(documents[0]):
        meta = meta_row[i] if i < len(meta_row) else {}
        results.append(
            {
                "snippet": doc,
                "path": meta.get("source", ""),
                "score": 1,
            }
        )
    return results

