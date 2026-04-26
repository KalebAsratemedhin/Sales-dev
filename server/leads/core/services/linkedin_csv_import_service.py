from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass

from django.db import transaction

from config.models import Lead


def _slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:48] or "unknown"


def _placeholder_email(*, first_name: str, last_name: str, company: str) -> str:
    local = "-".join(filter(None, [_slugify(first_name), _slugify(last_name), _slugify(company)]))[:64]
    return f"{local}@linkedin-export.placeholder"


@dataclass(frozen=True)
class CsvImportResult:
    created: int
    updated: int
    skipped: int
    errors: list[str]


class LinkedInConnectionsCsvImportService:
    def import_file(self, *, user_id: int | None, file_bytes: bytes) -> CsvImportResult:
        text = file_bytes.decode("utf-8-sig", errors="replace")
        reader = csv.DictReader(io.StringIO(text))

        created = updated = skipped = 0
        errors: list[str] = []

        with transaction.atomic():
            for idx, row in enumerate(reader, 1):
                try:
                    first = (row.get("First Name") or "").strip()
                    last = (row.get("Last Name") or "").strip()
                    email = (row.get("Email Address") or "").strip()
                    company = (row.get("Company") or "").strip()

                    name = " ".join([p for p in [first, last] if p]).strip()
                    if not email:
                        email = _placeholder_email(first_name=first, last_name=last, company=company)

                    if not email:
                        skipped += 1
                        continue

                    lead, was_created = Lead.objects.update_or_create(
                        user_id=user_id,
                        source=Lead.Source.LINKEDIN,
                        email=email,
                        defaults={
                            "name": name,
                            "company_name": company,
                            "company_website": "",
                        },
                    )
                    if was_created:
                        created += 1
                    else:
                        updated += 1
                except Exception as e:
                    skipped += 1
                    errors.append(f"row {idx}: {str(e)[:300]}")

        return CsvImportResult(created=created, updated=updated, skipped=skipped, errors=errors)

