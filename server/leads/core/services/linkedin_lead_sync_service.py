from __future__ import annotations

import base64
import hashlib
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

import requests
from django.db import transaction

from config.models import Lead, LinkedInLeadGenResponseCursor, LinkedInLeadSyncConnection


@dataclass(frozen=True)
class LeadSyncPullResult:
    imported: int
    skipped: int
    errors: list[str]
    next_start: int | None


def _build_state(*, user_id: int) -> str:
    raw = f"{user_id}:{secrets.token_urlsafe(16)}".encode("utf-8")
    digest = hashlib.sha256(raw).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def _encode_owner(owner: dict[str, str]) -> str:
    if "organization" in owner:
        return f"(organization:{owner['organization']})"
    if "sponsoredAccount" in owner:
        return f"(sponsoredAccount:{owner['sponsoredAccount']})"
    raise ValueError("owner must include organization or sponsoredAccount")


def _auth_headers(*, access_token: str, linkedin_version: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
        "LinkedIn-Version": linkedin_version,
        "X-Restli-Protocol-Version": "2.0.0",
    }


def _next_start_from_paging(*, paging: Any, start: int, count: int) -> int | None:
    if not isinstance(paging, dict):
        return None
    try:
        total = int(paging.get("total") or 0)
        start_i = int(paging.get("start") or start)
        count_i = int(paging.get("count") or count)
        if total and (start_i + count_i) < total:
            return start_i + count_i
    except Exception:
        return None
    return None


def _extract_response_urn(el: dict[str, Any]) -> str:
    return str(el.get("id") or el.get("urn") or "").strip()


def _extract_answers(el: dict[str, Any]) -> Any:
    answers = el.get("answers") or el.get("formResponse") or el.get("response") or {}
    if isinstance(answers, dict):
        return answers.get("answers") or answers
    return answers


def _extract_common_fields(*, el: dict[str, Any], answers: Any) -> dict[str, str]:
    out: dict[str, str] = {}

    lead_obj = el.get("lead") if isinstance(el.get("lead"), dict) else {}
    if isinstance(lead_obj, dict):
        out["email"] = str(lead_obj.get("email") or out.get("email") or "")
        out["name"] = str(lead_obj.get("fullName") or out.get("name") or "")
        out["company"] = str(lead_obj.get("company") or out.get("company") or "")

    if isinstance(answers, list):
        for a in answers:
            if not isinstance(a, dict):
                continue
            key = str(a.get("field") or a.get("name") or a.get("question") or "").lower()
            val = a.get("value") or a.get("answer") or a.get("text") or ""
            val_s = str(val).strip()
            if not key or not val_s:
                continue
            if "email" in key:
                out["email"] = out.get("email") or val_s
            elif "first" in key:
                out["first"] = out.get("first") or val_s
            elif "last" in key:
                out["last"] = out.get("last") or val_s
            elif "company" in key:
                out["company"] = out.get("company") or val_s

    if not out.get("name"):
        first = (out.get("first") or "").strip()
        last = (out.get("last") or "").strip()
        out["name"] = " ".join([p for p in [first, last] if p]).strip()

    return out


class LinkedInLeadSyncService:
    AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    API_BASE = "https://api.linkedin.com"

    def __init__(self) -> None:
        self.client_id = (os.environ.get("LINKEDIN_CLIENT_ID") or "").strip()
        self.client_secret = (os.environ.get("LINKEDIN_CLIENT_SECRET") or "").strip()
        self.redirect_uri = (os.environ.get("LINKEDIN_REDIRECT_URI") or "").strip()
        self.default_scopes = (os.environ.get("LINKEDIN_LEADSYNC_SCOPES") or "r_marketing_leadgen_automation").strip()
        self.linkedin_version = (os.environ.get("LINKEDIN_VERSION") or "202601").strip()

        if not self.client_id or not self.client_secret or not self.redirect_uri:
            raise RuntimeError(
                "Missing LinkedIn OAuth config. Set LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, LINKEDIN_REDIRECT_URI."
            )

    def build_authorize_url(self, *, user_id: int, state: str | None = None) -> dict[str, str]:
        state_val = state or _build_state(user_id=user_id)
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.default_scopes,
            "state": state_val,
        }
        return {"url": f"{self.AUTH_URL}?{urlencode(params)}", "state": state_val}

    def connect(self, *, user_id: int, code: str) -> LinkedInLeadSyncConnection:
        code = (code or "").strip()
        if not code:
            raise ValueError("Missing code.")

        resp = requests.post(
            self.TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        access_token = (data.get("access_token") or "").strip()
        refresh_token = (data.get("refresh_token") or "").strip()
        expires_in = int(data.get("expires_in") or 0)
        scope = (data.get("scope") or "").strip()
        token_type = (data.get("token_type") or "Bearer").strip()

        expires_at = None
        if expires_in > 0:
            expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)

        conn, _ = LinkedInLeadSyncConnection.objects.update_or_create(
            user_id=user_id,
            defaults={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at,
                "scope": scope,
                "token_type": token_type or "Bearer",
            },
        )
        return conn

    def pull_and_import(
        self,
        *,
        user_id: int,
        owner: dict[str, str],
        start: int = 0,
        count: int = 50,
    ) -> LeadSyncPullResult:
        conn = LinkedInLeadSyncConnection.objects.filter(user_id=user_id).first()
        if not conn or not conn.access_token:
            raise RuntimeError("LinkedIn Lead Sync is not connected for this user.")

        if "organization" in owner and owner["organization"]:
            conn.organization_urn = owner["organization"]
        if "sponsoredAccount" in owner and owner["sponsoredAccount"]:
            conn.sponsored_account_urn = owner["sponsoredAccount"]
        conn.save(update_fields=["organization_urn", "sponsored_account_urn", "updated_at"])

        url = f"{self.API_BASE}/rest/leadFormResponses"
        params = {
            "q": "owner",
            "owner": _encode_owner(owner),
            "start": int(start or 0),
            "count": int(count or 50),
        }
        resp = requests.get(
            url,
            headers=_auth_headers(access_token=conn.access_token, linkedin_version=self.linkedin_version),
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        payload = resp.json()

        elements = payload.get("elements")
        if not isinstance(elements, list):
            elements = []

        return self._import_elements(user_id=user_id, elements=elements, paging=payload.get("paging"), start=params["start"], count=params["count"])

    def _import_elements(
        self,
        *,
        user_id: int,
        elements: list[Any],
        paging: Any,
        start: int,
        count: int,
    ) -> LeadSyncPullResult:
        imported = skipped = 0
        errors: list[str] = []

        with transaction.atomic():
            for el in elements:
                try:
                    if not isinstance(el, dict):
                        skipped += 1
                        continue

                    response_urn = _extract_response_urn(el)
                    if response_urn:
                        if LinkedInLeadGenResponseCursor.objects.filter(response_urn=response_urn).exists():
                            skipped += 1
                            continue

                    if not self._upsert_lead_from_response(user_id=user_id, response=el):
                        skipped += 1
                        continue

                    if response_urn:
                        LinkedInLeadGenResponseCursor.objects.create(user_id=user_id, response_urn=response_urn)
                    imported += 1
                except Exception as e:
                    skipped += 1
                    errors.append(str(e)[:300])

            LinkedInLeadSyncConnection.objects.filter(user_id=user_id).update(last_synced_at=datetime.now(tz=timezone.utc))

        next_start = _next_start_from_paging(paging=paging, start=start, count=count)
        return LeadSyncPullResult(imported=imported, skipped=skipped, errors=errors, next_start=next_start)

    def _upsert_lead_from_response(self, *, user_id: int, response: dict[str, Any]) -> bool:
        extracted = _extract_common_fields(el=response, answers=_extract_answers(response))

        email = (extracted.get("email") or "").strip()
        if not email:
            return False

        name = (extracted.get("name") or "").strip()
        company = (extracted.get("company") or "").strip()

        Lead.objects.update_or_create(
            user_id=user_id,
            source=Lead.Source.LINKEDIN,
            email=email,
            defaults={
                "name": name,
                "company_name": company,
                "company_website": "",
                "profile_url": "",
                "status": Lead.Status.NEW,
            },
        )
        return True

