"""
Service layer — all Supabase queries live here, kept separate from the
route/HTTP layer so the persistence logic can be tested or swapped out
independently (e.g. if we later move off Supabase).
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from typing import Any, Dict, Optional

from app.database import get_supabase_client

logger = logging.getLogger("patient_api")


class PatientService:
    @staticmethod
    def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare a validated Pydantic payload for insertion/update into Supabase."""
        cleaned = dict(payload)

        if "date_of_birth" in cleaned and isinstance(cleaned["date_of_birth"], date):
            cleaned["date_of_birth"] = cleaned["date_of_birth"].isoformat()

        # Don't send empty-string optional fields — let the DB keep them NULL.
        for optional_field in [
            "email",
            "address_line_2",
            "insurance_provider",
            "insurance_member_id",
            "emergency_contact_name",
            "emergency_contact_phone",
        ]:
            if optional_field in cleaned and cleaned[optional_field] in (None, ""):
                cleaned.pop(optional_field, None)

        return cleaned

    @staticmethod
    def get_patients(filters: Optional[Dict[str, Any]] = None):
        client = get_supabase_client()
        query = client.table("patients").select("*").is_("deleted_at", "null")

        if filters:
            for key, value in filters.items():
                if value is None:
                    continue
                if key == "date_of_birth" and isinstance(value, date):
                    value = value.isoformat()
                query = query.eq(key, value)

        response = query.execute()
        return response.data or []

    @staticmethod
    def get_patient_by_id(patient_id: str):
        client = get_supabase_client()
        response = (
            client.table("patients")
            .select("*")
            .eq("patient_id", patient_id)
            .is_("deleted_at", "null")
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return rows[0] if rows else None

    @staticmethod
    def get_patient_by_phone(phone_number: str):
        """Bonus: used for duplicate-caller detection before creating a new record."""
        client = get_supabase_client()
        response = (
            client.table("patients")
            .select("*")
            .eq("phone_number", phone_number)
            .is_("deleted_at", "null")
            .limit(1)
            .execute()
        )
        rows = response.data or []
        return rows[0] if rows else None

    @staticmethod
    def create_patient(payload: Dict[str, Any]):
        client = get_supabase_client()
        cleaned = PatientService._normalize_payload(payload)
        response = client.table("patients").insert(cleaned).execute()
        items = response.data or []
        created = items[0] if items else None

        # Observability requirement: log the final collected data payload.
        if created:
            logger.info("Patient created — final collected data payload: %s", created)
        return created

    @staticmethod
    def update_patient(patient_id: str, payload: Dict[str, Any]):
        client = get_supabase_client()
        cleaned = PatientService._normalize_payload(payload)
        if not cleaned:
            return None

        # The `patients` table's updated_at column only auto-fills on INSERT
        # (DEFAULT NOW()), not on UPDATE — Postgres has no trigger for that
        # here. Set it explicitly so "auto-generated on modification" holds
        # without requiring a schema/trigger change.
        cleaned["updated_at"] = datetime.now(timezone.utc).isoformat()

        response = (
            client.table("patients")
            .update(cleaned)
            .eq("patient_id", patient_id)
            .is_("deleted_at", "null")
            .select("*")
            .execute()
        )
        rows = response.data or []
        updated = rows[0] if rows else None
        if updated:
            logger.info("Patient updated — final collected data payload: %s", updated)
        return updated

    @staticmethod
    def delete_patient(patient_id: str) -> bool:
        client = get_supabase_client()
        deleted_at = datetime.now(timezone.utc).isoformat()

        response = (
            client.table("patients")
            .update({"deleted_at": deleted_at})
            .eq("patient_id", patient_id)
            .is_("deleted_at", "null")
            .execute()
        )
        success = bool(response.data)
        if success:
            logger.info("Patient soft-deleted: patient_id=%s", patient_id)
        return success
