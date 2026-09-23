from datetime import date
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.patient import PatientCreate, PatientUpdate
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("", summary="List patients")
async def list_patients(
    last_name: Optional[str] = Query(default=None),
    date_of_birth: Optional[date] = Query(default=None),
    phone_number: Optional[str] = Query(default=None),
):
    filters: Dict[str, Any] = {}
    if last_name is not None:
        filters["last_name"] = last_name
    if date_of_birth is not None:
        filters["date_of_birth"] = date_of_birth
    if phone_number is not None:
        filters["phone_number"] = phone_number

    try:
        patients = PatientService.get_patients(filters)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"data": patients, "error": None}


@router.get("/{patient_id}", summary="Get a patient")
async def get_patient(patient_id: str):
    try:
        patient = PatientService.get_patient_by_id(patient_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found.")

    return {"data": patient, "error": None}


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a patient")
async def create_patient(patient: PatientCreate):
    payload = patient.dict(exclude_none=True)

    # Bonus: duplicate-caller detection by phone number. If a matching
    # non-deleted patient already exists, don't silently create a second
    # record — return 409 so the caller (voice agent or API consumer) can
    # offer to update the existing record instead.
    try:
        existing = PatientService.get_patient_by_phone(payload["phone_number"])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": (
                    f"A patient with this phone number already exists: "
                    f"{existing.get('first_name')} {existing.get('last_name')}. "
                    f"Update patient_id {existing.get('patient_id')} instead of creating a new record."
                ),
                "existing_patient": existing,
            },
        )

    try:
        created = PatientService.create_patient(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"data": created, "error": None}


@router.put("/{patient_id}", summary="Update a patient")
async def update_patient(patient_id: str, patient: PatientUpdate):
    payload = patient.dict(exclude_unset=True, exclude_none=True)
    if not payload:
        raise HTTPException(status_code=400, detail="No update fields provided.")

    try:
        updated = PatientService.update_patient(patient_id, payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if updated is None:
        raise HTTPException(status_code=404, detail="Patient not found.")

    return {"data": updated, "error": None}


@router.delete("/{patient_id}", summary="Soft delete a patient")
async def delete_patient(patient_id: str):
    try:
        deleted = PatientService.delete_patient(patient_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if not deleted:
        raise HTTPException(status_code=404, detail="Patient not found.")

    return {"data": {"patient_id": patient_id, "deleted": True}, "error": None}
