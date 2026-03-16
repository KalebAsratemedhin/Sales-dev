import os

import chromadb


def _chroma_host_port() -> tuple[str | None, int | None]:
    raw = (os.environ.get("CHROMA_HOST") or "").strip()
    if not raw:
        return None, None
    if raw.startswith("http://"):
        raw = raw[7:]
    elif raw.startswith("https://"):
        raw = raw[8:]
    parts = raw.split(":", 1)
    host = parts[0] or "localhost"
    try:
        port = int(parts[1]) if len(parts) > 1 else 8000
    except ValueError:
        port = 8000
    return host, port


def get_chroma_client():
    host, port = _chroma_host_port()
    if host is None or port is None:
        return None
    try:
        return chromadb.HttpClient(host=host, port=port)
    except Exception:
        return None

