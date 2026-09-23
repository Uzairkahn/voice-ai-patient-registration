"""
Pydantic schemas for patient records.

This is the single source of truth for request/response validation
(no duplicate/unused validators elsewhere in the codebase).
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

# Per spec: "sex Enum Male, Female, Other, Decline to Answer"
ALLOWED_SEX_VALUES = {"male", "female", "other", "decline to answer"}

# Per spec: "first_name/last_name: 1-50 chars, alphabetic + hyphens/apostrophes"
NAME_PATTERN = re.compile(r"^[A-Za-z'\-]+$")

# Per spec: "state: Valid 2-letter U.S. state abbreviation"
US_STATE_ABBREVIATIONS = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC",
}

# Per spec: "zip_code: 5-digit or ZIP+4 U.S. format"
ZIP_PATTERN = re.compile(r"^\d{5}(-\d{4})?$")


class PatientBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: date
    sex: str = Field(..., min_length=1, max_length=20)
    phone_number: str = Field(..., min_length=10, max_length=10)
    email: Optional[EmailStr] = None
    address_line_1: str = Field(..., min_length=1)
    address_line_2: Optional[str] = None
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: str = Field(..., min_length=5, max_length=10)
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: str = Field(default="English", max_length=100)
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = Field(default=None, min_length=10, max_length=10)

    @field_validator("first_name", "last_name", "city", "insurance_provider")
    @classmethod
    def strip_text_fields(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name_characters(cls, value: str) -> str:
        if not NAME_PATTERN.fullmatch(value):
            raise ValueError("Name must contain only letters, hyphens, and apostrophes.")
        return value

    @field_validator("insurance_member_id")
    @classmethod
    def validate_insurance_member_id(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        if cleaned == "":
            return None
        if not cleaned.isalnum():
            raise ValueError("Insurance member ID must be alphanumeric.")
        return cleaned

    @field_validator("phone_number", "emergency_contact_phone")
    @classmethod
    def validate_phone_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned.isdigit():
            raise ValueError("Phone number must contain exactly 10 digits.")
        return cleaned

    @field_validator("state")
    @classmethod
    def validate_state(cls, value: str) -> str:
        state = value.strip().upper()
        if state not in US_STATE_ABBREVIATIONS:
            raise ValueError("State must be a valid 2-letter U.S. state abbreviation.")
        return state

    @field_validator("sex")
    @classmethod
    def validate_sex(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in ALLOWED_SEX_VALUES:
            raise ValueError("Sex must be one of: Male, Female, Other, Decline to Answer.")
        return "Decline to Answer" if normalized == "decline to answer" else normalized.title()

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        return value

    @field_validator("zip_code")
    @classmethod
    def validate_zip_code(cls, value: str) -> str:
        cleaned = value.strip()
        if not ZIP_PATTERN.fullmatch(cleaned):
            raise ValueError("ZIP code must be 5 digits or ZIP+4 format (e.g. 12345 or 12345-6789).")
        return cleaned


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    """All fields optional — partial updates allowed."""

    first_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    date_of_birth: Optional[date] = None
    sex: Optional[str] = Field(default=None, min_length=1, max_length=20)
    phone_number: Optional[str] = Field(default=None, min_length=10, max_length=10)
    email: Optional[EmailStr] = None
    address_line_1: Optional[str] = Field(default=None, min_length=1)
    address_line_2: Optional[str] = None
    city: Optional[str] = Field(default=None, min_length=1, max_length=100)
    state: Optional[str] = Field(default=None, min_length=2, max_length=2)
    zip_code: Optional[str] = Field(default=None, min_length=5, max_length=10)
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: Optional[str] = Field(default=None, max_length=100)
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = Field(default=None, min_length=10, max_length=10)

    @field_validator("first_name", "last_name", "city", "insurance_provider")
    @classmethod
    def strip_text_fields(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name_characters(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not NAME_PATTERN.fullmatch(value):
            raise ValueError("Name must contain only letters, hyphens, and apostrophes.")
        return value

    @field_validator("insurance_member_id")
    @classmethod
    def validate_insurance_member_id(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        if cleaned == "":
            return None
        if not cleaned.isalnum():
            raise ValueError("Insurance member ID must be alphanumeric.")
        return cleaned

    @field_validator("phone_number", "emergency_contact_phone")
    @classmethod
    def validate_phone_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned.isdigit():
            raise ValueError("Phone number must contain exactly 10 digits.")
        return cleaned

    @field_validator("state")
    @classmethod
    def validate_state(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        state = value.strip().upper()
        if state not in US_STATE_ABBREVIATIONS:
            raise ValueError("State must be a valid 2-letter U.S. state abbreviation.")
        return state

    @field_validator("sex")
    @classmethod
    def validate_sex(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.strip().lower()
        if normalized not in ALLOWED_SEX_VALUES:
            raise ValueError("Sex must be one of: Male, Female, Other, Decline to Answer.")
        return "Decline to Answer" if normalized == "decline to answer" else normalized.title()

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: Optional[date]) -> Optional[date]:
        if value is None:
            return value
        if value > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        return value

    @field_validator("zip_code")
    @classmethod
    def validate_zip_code(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        if not ZIP_PATTERN.fullmatch(cleaned):
            raise ValueError("ZIP code must be 5 digits or ZIP+4 format (e.g. 12345 or 12345-6789).")
        return cleaned


class PatientFilters(BaseModel):
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = None


class PatientRecord(PatientBase):
    patient_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
