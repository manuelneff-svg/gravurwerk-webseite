import os
import uuid

import pytest
import requests


BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")


@pytest.fixture(scope="module")
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def valid_inquiry(api_client):
    payload = {
        "product": "Handyhülle",
        "wish": f"TEST_r2_{uuid.uuid4().hex}: goldene Initialen",
        "email": "delivered@resend.dev",
        "name": "Test r2",
    }
    response = api_client.post(f"{BASE_URL}/api/inquiries", json=payload, timeout=45)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "success"
    assert isinstance(data["id"], str) and data["id"]
    assert data["confirmation_sent"] is True
    return payload, data["id"]


# Inquiry creation, validation, persistence, serialization, and CORS coverage.
def test_create_inquiry_sends_both_emails_and_returns_success(valid_inquiry):
    payload, inquiry_id = valid_inquiry
    assert inquiry_id
    assert payload["email"] == "delivered@resend.dev"


def test_create_inquiry_rejects_missing_or_empty_wish(api_client):
    for wish in (None, ""):
        payload = {"product": "Feuerzeug", "email": "delivered@resend.dev"}
        if wish is not None:
            payload["wish"] = wish
        response = api_client.post(f"{BASE_URL}/api/inquiries", json=payload, timeout=20)
        assert response.status_code == 422, response.text


def test_create_inquiry_rejects_invalid_email(api_client):
    response = api_client.post(
        f"{BASE_URL}/api/inquiries",
        json={"product": "Feuerzeug", "wish": "TEST_r2 invalid email", "email": "not-an-email"},
        timeout=20,
    )
    assert response.status_code == 422, response.text


def test_list_inquiries_has_persisted_record_without_object_id_leak(api_client, valid_inquiry):
    _, inquiry_id = valid_inquiry
    response = api_client.get(f"{BASE_URL}/api/inquiries", timeout=20)
    assert response.status_code == 200, response.text
    rows = response.json()
    assert isinstance(rows, list)
    match = next((row for row in rows if row.get("id") == inquiry_id), None)
    assert match is not None
    assert "_id" not in match
    assert match["email_status"] == "sent"
    assert match["email"] == "delivered@resend.dev"


def test_api_allows_cross_origin_browser_request(api_client):
    response = api_client.options(
        f"{BASE_URL}/api/inquiries",
        headers={
            "Origin": "https://email-error-debug-1.preview.emergentagent.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
        timeout=20,
    )
    assert response.status_code in (200, 204), response.text
    allow_origin = response.headers.get("access-control-allow-origin")
    assert allow_origin in {
        "*",
        "https://email-error-debug-1.preview.emergentagent.com",
        "https://email-error-debug-1.cluster-5.preview.emergentcf.cloud",
    }
    assert "POST" in response.headers.get("access-control-allow-methods", "")
    assert "content-type" in response.headers.get("access-control-allow-headers", "").lower()
