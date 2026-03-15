from datetime import datetime

from django.core.management.base import BaseCommand

from linkedin.sync import sync_leads_from_profile


class Command(BaseCommand):
    help = (
        "Fetch a profile's posts between two dates, then for each post fetch "
        "comments/reactions and create or update Lead records."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "profile_url",
            help="LinkedIn profile URL (e.g. https://www.linkedin.com/in/username/).",
        )
        parser.add_argument(
            "--start-date",
            required=True,
            help="Start of date range (YYYY-MM-DD).",
        )
        parser.add_argument(
            "--end-date",
            required=True,
            help="End of date range (YYYY-MM-DD).",
        )
        parser.add_argument(
            "--persona-id",
            type=int,
            default=None,
            help="Optional Persona ID to assign to new leads.",
        )
        parser.add_argument(
            "--max-scrolls",
            type=int,
            default=10,
            help="Max scrolls on activity page to load more posts (default 10).",
        )

    def handle(self, *args, **options):
        profile_url = options["profile_url"].strip()
        start_s = options["start_date"].strip()
        end_s = options["end_date"].strip()
        persona_id = options.get("persona_id")
        max_scrolls = options.get("max_scrolls", 10)

        try:
            start_date = datetime.strptime(start_s, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_s, "%Y-%m-%d").date()
        except ValueError as e:
            self.stderr.write(
                self.style.ERROR("Dates must be YYYY-MM-DD: %s" % e)
            )
            return

        if start_date > end_date:
            self.stderr.write(
                self.style.ERROR("start-date must be <= end-date.")
            )
            return

        self.stdout.write(
            "Syncing profile %s from %s to %s..." % (profile_url, start_s, end_s)
        )
        try:
            created, updated = sync_leads_from_profile(
                profile_url,
                start_date,
                end_date,
                persona_id=persona_id,
                max_activity_scrolls=max_scrolls,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    "Created %d new lead(s), updated %d." % (created, updated)
                )
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(str(e)))
            raise
