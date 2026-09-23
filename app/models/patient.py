from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class PatientBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: date
    sex: str = Field(..., min_length=1, max_length=20)
    phone_number: str = Field(..., min_length=10, max_length=10)
    email: Optional[str] = Field(default=None, max_length=255)
    address_line_1: str = Field(..., min_length=1)
    address_line_2: Optional[str] = None
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: str = Field(..., min_length=1, max_length=10)
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: str = Field(default="English", max_length=100)
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = Field(default=None, min_length=10, max_length=10)

    @validator("first_name", "last_name", "city", "insurance_provider")
    def strip_names(cls, value: str) -> str:
        return value.strip()

    @validator("phone_number", "emergency_contact_phone")
    def validate_phone_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned.isdigit():
            raise ValueError("Phone number must contain only digits.")
        return cleaned

    @validator("email")
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "":
            return None
        return value.strip().lower()

    @validator("state")
    def validate_state(cls, value: str) -> str:
        state = value.strip().upper()
        if len(state) != 2 or not state.isalpha():
            raise ValueError("State must be a 2-letter abbreviation.")
        return state

    @validator("sex")
    def validate_sex(cls, value: str) -> str:
        normalized = value.strip().lower()
        allowed = {"male", "female", "other", "non-binary", "prefer not to say"}
        if normalized not in allowed:
            raise ValueError("Sex must be one of: Male, Female, Other, Non-binary, Prefer not to say.")
        return value.strip().title() if value.strip() else value.strip()

    @validator("date_of_birth")
    def validate_date_of_birth(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        return value

    @validator("zip_code")
    def validate_zip_code(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("ZIP code is required.")
        return cleaned


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    date_of_birth: Optional[date] = None
    sex: Optional[str] = Field(default=None, min_length=1, max_length=20)
    phone_number: Optional[str] = Field(default=None, min_length=10, max_length=10)
    email: Optional[str] = Field(default=None, max_length=255)
    address_line_1: Optional[str] = Field(default=None, min_length=1)
    address_line_2: Optional[str] = None
    city: Optional[str] = Field(default=None, min_length=1, max_length=100)
    state: Optional[str] = Field(default=None, min_length=2, max_length=2)
    zip_code: Optional[str] = Field(default=None, min_length=1, max_length=10)
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: Optional[str] = Field(default=None, max_length=100)
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = Field(default=None, min_length=10, max_length=10)

    @validator("first_name", "last_name", "city", "insurance_provider")
    def strip_names(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return value.strip()

    @validator("phone_number", "emergency_contact_phone")
    def validate_phone_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned.isdigit():
            raise ValueError("Phone number must contain only digits.")
        return cleaned

    @validator("email")
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "":
            return None
        return value.strip().lower()

    @validator("state")
    def validate_state(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        state = value.strip().upper()
        if len(state) != 2 or not state.isalpha():
            raise ValueError("State must be a 2-letter abbreviation.")
        return state

    @validator("sex")
    def validate_sex(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.strip().lower()
        allowed = {"male", "female", "other", "non-binary", "prefer not to say"}
        if normalized not in allowed:
            raise ValueError("Sex must be one of: Male, Female, Other, Non-binary, Prefer not to say.")
        return value.strip().title()

    @validator("date_of_birth")
    def validate_date_of_birth(cls, value: Optional[date]) -> Optional[date]:
        if value is None:
            return value
        if value > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        return value


class PatientRecord(PatientBase):
    patient_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
