"""
Service-layer tests for the get_patient_by_phone / get_patient_by_id fix.

Root cause being tested: supabase==2.7.4's .maybe_single() returns a bare
None (instead of a response object with data=None) when zero rows match,
which crashed the duplicate-phone check with
"'NoneType' object has no attribute 'data'". The fix uses .limit(1) and
manually unwraps the first row, so these tests mock the Supabase client to
verify both the zero-row and one-row cases without needing live credentials.

Run with: pytest
"""

from unittest.mock import MagicMock, patch

from app.services.patient_service import PatientService


def _build_mock_client(returned_rows):
    """A mock Supabase client whose chained .select/.eq/.is_/.limit calls
    all return the same query object, ending in .execute() -> rows."""
    mock_response = MagicMock()
    mock_response.data = returned_rows

    mock_query = MagicMock()
    mock_query.execute.return_value = mock_response
    mock_query.select.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.is_.return_value = mock_query
    mock_query.limit.return_value = mock_query

    mock_table = MagicMock()
    mock_table.select.return_value = mock_query

    mock_client = MagicMock()
    mock_client.table.return_value = mock_table
    return mock_client


@patch("app.services.patient_service.get_supabase_client")
def test_get_patient_by_phone_returns_none_when_no_match(mock_get_client):
    """This is the exact scenario that used to raise
    'NoneType' object has no attribute 'data'."""
    mock_get_client.return_value = _build_mock_client([])
    result = PatientService.get_patient_by_phone("2025550147")
    assert result is None


@patch("app.services.patient_service.get_supabase_client")
def test_get_patient_by_phone_returns_existing_record_when_match(mock_get_client):
    existing = {"patient_id": "abc-123", "phone_number": "2025550147"}
    mock_get_client.return_value = _build_mock_client([existing])
    result = PatientService.get_patient_by_phone("2025550147")
    assert result == existing


@patch("app.services.patient_service.get_supabase_client")
def test_get_patient_by_id_returns_none_when_no_match(mock_get_client):
    mock_get_client.return_value = _build_mock_client([])
    result = PatientService.get_patient_by_id("nonexistent-id")
    assert result is None


@patch("app.services.patient_service.get_supabase_client")
def test_get_patient_by_id_returns_existing_record_when_match(mock_get_client):
    existing = {"patient_id": "abc-123", "first_name": "Jane"}
    mock_get_client.return_value = _build_mock_client([existing])
    result = PatientService.get_patient_by_id("abc-123")
    assert result == existing
