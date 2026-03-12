"""
Sync leads from LinkedIn post engagement (comments + reactions).
Accepts post URLs, activity URLs, or numeric activity IDs.
"""

from django.core.management.base import BaseCommand

from linkedin.leads_sync import sync_leads_from_posts


class Command(BaseCommand):
    help = "Fetch comments/reactions for the given post(s) and create Lead records."

    def add_arguments(self, parser):
        parser.add_argument(
            "post",
            nargs="+",
            help="Post URL, activity URL, or numeric activity ID (one or more).",
        )
        parser.add_argument(
            "--persona-id",
            type=int,
            default=None,
            help="Optional Persona ID to assign to new leads.",
        )

    def handle(self, *args, **options):
        post_inputs = options["post"]
        persona_id = options.get("persona_id")
        self.stdout.write("Syncing %d post(s)..." % len(post_inputs))
        try:
            created, updated = sync_leads_from_posts(
                post_inputs,
                persona_id=persona_id,
            )
            self.stdout.write(
                self.style.SUCCESS("Created %d new lead(s), updated %d." % (created, updated))
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(str(e)))
            raise
