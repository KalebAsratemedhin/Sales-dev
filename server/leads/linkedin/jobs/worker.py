import logging
import os

from django.contrib.auth import get_user_model

from auth_api.models import OutreachSettings
from linkedin.core.constants import SESSION_REQUIRED_MSG
from linkedin.core.session import refresh_session
from linkedin.models import LinkedInSyncJob
from linkedin.sync import sync_leads_from_profile

logger = logging.getLogger(__name__)
User = get_user_model()

_SESSION_MISSING_PREFIX = "LinkedIn session missing."


def _attempt_self_heal_session() -> tuple[bool, str]:
    email = (os.environ.get("LINKEDIN_EMAIL") or "").strip()
    password = (os.environ.get("LINKEDIN_PASSWORD") or "").strip()
    if not email or not password:
        return (
            False,
            (
                f"{_SESSION_MISSING_PREFIX} Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD "
                "for the leads service, then retry."
            ),
        )

    headless = (os.environ.get("LINKEDIN_HEADLESS", "true") or "true").strip().lower() != "false"
    try:
        ok = refresh_session(email, password, headless=headless)
    except Exception as e:
        logger.exception("LinkedIn session refresh failed")
        return (
            False,
            (
                f"{_SESSION_MISSING_PREFIX} Auto-refresh failed: {str(e)[:300]}. "
                "LinkedIn may require manual login/checkpoint."
            ),
        )

    if not ok:
        return (
            False,
            (
                f"{_SESSION_MISSING_PREFIX} Auto-refresh did not obtain a valid session cookie. "
                "LinkedIn may require manual login/checkpoint."
            ),
        )

    return True, "LinkedIn session refreshed."


def handle_linkedin_sync_profile_message(payload: dict) -> None:
    job_id = payload.get("job_id")
    user_id = payload.get("user_id")
    if job_id is None or user_id is None:
        return

    job = LinkedInSyncJob.objects.filter(id=job_id, user_id=user_id).first()
    if not job:
        return

    if job.status not in {LinkedInSyncJob.Status.QUEUED, LinkedInSyncJob.Status.RUNNING}:
        return

    job.status = LinkedInSyncJob.Status.RUNNING
    job.error = ""
    job.save(update_fields=["status", "error", "updated_at"])

    def run_sync() -> tuple[int, int]:
        return sync_leads_from_profile(
            job.profile_url,
            job.start_date,
            job.end_date,
            user_id=user_id,
            max_activity_scrolls=job.max_scrolls,
        )

    try:
        created, updated = run_sync()
    except RuntimeError as e:
        if str(e).strip() != SESSION_REQUIRED_MSG:
            logger.exception("LinkedIn profile sync failed: job_id=%s user_id=%s", job_id, user_id)
            job.status = LinkedInSyncJob.Status.FAILED
            job.error = str(e)[:4000]
            job.save(update_fields=["status", "error", "updated_at"])
            return

        ok, msg = _attempt_self_heal_session()
        if not ok:
            job.status = LinkedInSyncJob.Status.FAILED
            job.error = msg[:4000]
            job.save(update_fields=["status", "error", "updated_at"])
            return

        try:
            created, updated = run_sync()
        except Exception as e2:
            logger.exception("LinkedIn profile sync failed after refresh: job_id=%s user_id=%s", job_id, user_id)
            job.status = LinkedInSyncJob.Status.FAILED
            job.error = f"{msg} Sync still failed: {str(e2)[:3500]}"
            job.save(update_fields=["status", "error", "updated_at"])
            return
    except Exception as e:
        logger.exception("LinkedIn profile sync failed: job_id=%s user_id=%s", job_id, user_id)
        job.status = LinkedInSyncJob.Status.FAILED
        job.error = str(e)[:4000]
        job.save(update_fields=["status", "error", "updated_at"])
        return

    job.status = LinkedInSyncJob.Status.SUCCEEDED
    job.created = int(created or 0)
    job.updated = int(updated or 0)
    job.error = ""
    job.save(update_fields=["status", "created", "updated", "error", "updated_at"])

    settings_obj, _ = OutreachSettings.objects.get_or_create(user_id=user_id)
    settings_obj.linkedin_last_sync = job.end_date
    settings_obj.save(update_fields=["linkedin_last_sync", "updated_at"])

