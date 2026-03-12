"""
Refresh LinkedIn session: log in with Selenium and save cookies for API use.
Requires LINKEDIN_EMAIL and LINKEDIN_PASSWORD in environment or .env.
"""

import os

from django.core.management.base import BaseCommand

from linkedin.session import refresh_session


class Command(BaseCommand):
    help = "Log in to LinkedIn with Selenium and save session cookies for the API client."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-headless",
            action="store_true",
            help="Run browser visible (e.g. to complete 2FA manually).",
        )

    def handle(self, *args, **options):
        email = os.environ.get("LINKEDIN_EMAIL", "").strip()
        password = os.environ.get("LINKEDIN_PASSWORD", "").strip()
        if not email or not password:
            self.stderr.write(
                "Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in the environment or .env."
            )
            return 1
        headless = not options["no_headless"]
        self.stdout.write("Logging in to LinkedIn (headless=%s)..." % headless)
        try:
            ok = refresh_session(email, password, headless=headless)
            if ok:
                self.stdout.write(self.style.SUCCESS("Session saved. You can run linkedin_sync_post now."))
                return 0
            self.stderr.write(
                "Login may have failed (no li_at cookie). "
                "Try --no-headless and complete 2FA in the browser, then run again."
            )
            return 1
        except Exception as e:
            self.stderr.write(self.style.ERROR(str(e)))
            return 1
