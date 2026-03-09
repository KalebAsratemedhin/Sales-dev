import re
import requests
from django.core.management.base import BaseCommand

from services.agent.agent import analyze_website


def simple_extract_text(html: str, max_chars: int = 20000) -> str:
    """Strip HTML tags and normalize whitespace."""
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<[^>]+>", " ", html)
    html = re.sub(r"\s+", " ", html)
    return html.strip()[:max_chars]


class Command(BaseCommand):
    help = "Fetch a URL (or use --text) and run analyze_website with the Agent."

    def add_arguments(self, parser):
        parser.add_argument("url", nargs="?", help="Company website URL to analyze")
        parser.add_argument("--text", type=str, help="Use this text instead of fetching URL")
        parser.add_argument(
            "--no-fetch",
            action="store_true",
            help="If URL given, only use URL in prompt, do not fetch",
        )

    def handle(self, *args, **options):
        url = (options.get("url") or "").strip()
        text_input = (options.get("text") or "").strip()
        no_fetch = options.get("no_fetch")

        if not url and not text_input:
            self.stderr.write(self.style.ERROR("Provide either a URL or --text '...'"))
            return

        if text_input:
            text = text_input
        elif url and no_fetch:
            text = "(no content fetched)"
        else:
            try:
                resp = requests.get(
                    url,
                    timeout=15,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; SDRBot/1.0)"},
                )
                resp.raise_for_status()
                text = simple_extract_text(resp.text)
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed to fetch {url}: {e}"))
                return

        result = analyze_website(url=url or "unknown", text=text)
        self.stdout.write(self.style.SUCCESS("Analysis result:"))
        for key, value in result.items():
            if key == "url":
                self.stdout.write(f"  url: {value}")
                continue
            if isinstance(value, list):
                self.stdout.write(f"  {key}:")
                for item in value:
                    self.stdout.write(f"    - {item}")
            else:
                self.stdout.write(f"  {key}: {value}")