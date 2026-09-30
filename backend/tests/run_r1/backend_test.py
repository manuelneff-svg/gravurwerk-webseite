"""Regression tests for inquiry validation, persistence, and email delivery."""
import os
import uuid

import pytest
import requests


BASE_URL = os.environ.get("REACT_APP_BACKEND_URL")
if not BASE_URL:
    pytest.skip("REACT_APP_BACKEND_URL is required", allow_module_level=True)
BASE_URL = BASE_URL.rstrip("/")


@pytest.fixture(scope="module")
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


def unique_wish(label: str) -> str:
    return f"TEST_r1_{label}_{uuid.uuid4().hex}"


# Core inquiry creation and email integration.
def test_create_inquiry_sends_owner_and_confirmation_and_persists(api_client):
    wish = unique_wish("valid")
    payload = {
        "product": "Handyhülle",
        "wish": wish,
        "email": "delivered@resend.dev",
        "name": "TEST r1",
    }
    response = api_client.post(f"{BASE_URL}/api/inquiries", json=payload, timeout=45)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "success"
    assert isinstance(data["id"], str) and data["id"]
    assert data["confirmation_sent"] is True

    listing = api_client.get(f"{BASE_URL}/api/inquiries", timeout=20)
    assert listing.status_code == 200, listing.text
    rows = listing.json()
    created = next((row for row in rows if row.get("id") == data["id"]), None)
    assert created is not None
    assert created["product"] == payload["product"]
    assert created["wish"] == wish
    assert created["email"] == payload["email"]
    assert created["name"] == payload["name"]
    assert created["email_status"] == "sent"
    assert "_id" not in created


# Pydantic/API input validation for missing, empty, and malformed required fields.
@pytest.mark.parametrize(
    "payload",
    [
        {"product": "Handyhülle", "email": "delivered@resend.dev"},
        {"product": "Handyhülle", "wish": "", "email": "delivered@resend.dev"},
        {"product": "Handyhülle", "wish": "   ", "email": "delivered@resend.dev"},
        {"product": "Handyhülle", "wish": "Bitte gravieren", "email": "not-an-email"},
    ],
)
def test_inquiry_rejects_invalid_required_fields(api_client, payload):
    response = api_client.post(f"{BASE_URL}/api/inquiries", json=payload, timeout=20)
    assert response.status_code == 422, response.text
    body = response.json()
    assert "detail" in body


# GET response shape must be JSON-safe and must not expose MongoDB internals.
def test_list_inquiries_has_no_mongodb_id_leakage(api_client):
    response = api_client.get(f"{BASE_URL}/api/inquiries", timeout=20)
    assert response.status_code == 200, response.text
    rows = response.json()
    assert isinstance(rows, list)
    for row in rows:
        assert "_id" not in row
        assert isinstance(row.get("id"), str)
        assert isinstance(row.get("email_status"), str)
