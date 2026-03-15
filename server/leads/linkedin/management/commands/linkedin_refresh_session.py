import os
import sys
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from linkedin.core.session import refresh_session


def check_selenium_available():
    try:
        import selenium
        import undetected_chromedriver
    except ImportError as e:
        raise CommandError(
            "Selenium or undetected-chromedriver not found in this Python environment.\n"
            "Python used: %s\n"
            "Install in the same environment: pip install selenium undetected-chromedriver\n"
            "Original error: %s" % (sys.executable, e)
        )


def load_env():
    try:
        from dotenv import load_dotenv
        env_path = Path(settings.BASE_DIR) / ".env"
        load_dotenv(env_path)
    except ImportError:
        pass


class Command(BaseCommand):
    help = "Log in to LinkedIn with Selenium and save session cookies for the API client."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-headless",
            action="store_true",
            help="Run browser visible (e.g. to complete 2FA manually).",
        )

    def handle(self, *args, **options):
        check_selenium_available()
        load_env()
        email = os.environ.get("LINKEDIN_EMAIL", "").strip()
        password = os.environ.get("LINKEDIN_PASSWORD", "").strip()
        if not email or not password:
            raise CommandError(
                "Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in the environment or .env."
            )
        headless = not options["no_headless"]
        self.stdout.write("Logging in to LinkedIn (headless=%s)..." % headless)
        try:
            ok = refresh_session(email, password, headless=headless)
            if ok:
                self.stdout.write(self.style.SUCCESS("Session saved. You can run linkedin_sync_post now."))
                return
            raise CommandError(
                "Login may have failed (no li_at cookie). "
                "Try --no-headless and complete 2FA in the browser, then run again."
            )
        except CommandError:
            raise
        except Exception as e:
            raise CommandError(str(e))
