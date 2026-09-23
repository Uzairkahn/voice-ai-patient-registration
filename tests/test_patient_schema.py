"""
Schema-level validation tests — no database or network calls required.
Run with: pytest
"""

from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.schemas.patient import PatientCreate

VALID_PATIENT = {
    "first_name": "Jane",
    "last_name": "Doe",
    "date_of_birth": "1990-05-14",
    "sex": "Female",
    "phone_number": "5551234567",
    "address_line_1": "123 Main St",
    "city": "Austin",
    "state": "TX",
    "zip_code": "73301",
}


def test_valid_patient_passes():
    patient = PatientCreate(**VALID_PATIENT)
    assert patient.first_name == "Jane"
    assert patient.state == "TX"


def test_future_date_of_birth_rejected():
    bad = {**VALID_PATIENT, "date_of_birth": str(date.today() + timedelta(days=1))}
    with pytest.raises(ValidationError):
        PatientCreate(**bad)


def test_non_numeric_phone_rejected():
    bad = {**VALID_PATIENT, "phone_number": "555-123-abcd"}
    with pytest.raises(ValidationError):
        PatientCreate(**bad)


def test_invalid_state_rejected():
    bad = {**VALID_PATIENT, "state": "Texas"}
    with pytest.raises(ValidationError):
        PatientCreate(**bad)


def test_invalid_sex_rejected():
    bad = {**VALID_PATIENT, "sex": "Unknown"}
    with pytest.raises(ValidationError):
        PatientCreate(**bad)


def test_invalid_zip_rejected():
    bad = {**VALID_PATIENT, "zip_code": "abc"}
    with pytest.raises(ValidationError):
        PatientCreate(**bad)


def test_zip_plus_four_accepted():
    good = {**VALID_PATIENT, "zip_code": "73301-1234"}
    patient = PatientCreate(**good)
    assert patient.zip_code == "73301-1234"


def test_decline_to_answer_sex_accepted():
    good = {**VALID_PATIENT, "sex": "decline to answer"}
    patient = PatientCreate(**good)
    assert patient.sex == "Decline to Answer"


def test_fake_state_abbreviation_rejected():
    bad = {**VALID_PATIENT, "state": "ZZ"}
    with pytest.raises(ValidationError):
        PatientCreate(**bad)


def test_real_state_abbreviation_accepted():
    good = {**VALID_PATIENT, "state": "ca"}
    patient = PatientCreate(**good)
    assert patient.state == "CA"


def test_zip_with_misplaced_hyphen_rejected():
    # 9 total digits, but not in valid 5-4 shape — must be rejected.
    bad = {**VALID_PATIENT, "zip_code": "12-3456789"}
    with pytest.raises(ValidationError):
        PatientCreate(**bad)


def test_name_with_digits_rejected():
    bad = {**VALID_PATIENT, "first_name": "Jane2"}
    with pytest.raises(ValidationError):
        PatientCreate(**bad)


def test_name_with_hyphen_and_apostrophe_accepted():
    good = {**VALID_PATIENT, "first_name": "Mary-Jane", "last_name": "O'Brien"}
    patient = PatientCreate(**good)
    assert patient.first_name == "Mary-Jane"
    assert patient.last_name == "O'Brien"


def test_non_alphanumeric_insurance_member_id_rejected():
    bad = {**VALID_PATIENT, "insurance_member_id": "ABC-123!"}
    with pytest.raises(ValidationError):
        PatientCreate(**bad)


def test_alphanumeric_insurance_member_id_accepted():
    good = {**VALID_PATIENT, "insurance_member_id": "ABC123"}
    patient = PatientCreate(**good)
    assert patient.insurance_member_id == "ABC123"
