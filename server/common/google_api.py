import os


def get_google_api_key() -> str:
    api_key = (os.environ.get("GOOGLE_API_KEY") or "").strip()
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    return api_key
