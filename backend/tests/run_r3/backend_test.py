"""Regression coverage for inquiry validation, persistence, CORS, and email delivery."""

import os
import uuid

import pytest
import requests


BASE_URL = os.environ.get("REACT_APP_BACKEND_URL")
if not BASE_URL:
    raise RuntimeError("REACT_APP_BACKEND_URL must be provided when running this suite")
BASE_URL = BASE_URL.rstrip("/")


@pytest.fixture(scope="module")
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


def test_create_inquiry_returns_success_and_persists(api_client):
    wish = f"TEST_r3_{uuid.uuid4().hex}: kleine Gravur"
    payload = {
        "product": "Handyhülle",
        "wish": wish,
        "email": "delivered@resend.dev",
        "name": "Test R3",
    }
    response = api_client.post(f"{BASE_URL}/api/inquiries", json=payload, timeout=45)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "success"
    assert isinstance(data["id"], str) and data["id"]
    assert data["confirmation_sent"] is True

    listed = api_client.get(f"{BASE_URL}/api/inquiries", timeout=30)
    assert listed.status_code == 200, listed.text
    rows = listed.json()
    match = next(row for row in rows if row["id"] == data["id"])
    assert match["product"] == payload["product"]
    assert match["wish"] == payload["wish"]
    assert match["email"] == payload["email"]
    assert match["name"] == payload["name"]
    assert match["email_status"] == "sent"
    assert "_id" not in match


def test_missing_wish_returns_422(api_client):
    response = api_client.post(
        f"{BASE_URL}/api/inquiries",
        json={"product": "Handyhülle", "email": "delivered@resend.dev"},
        timeout=30,
    )
    assert response.status_code == 422
    assert response.json()["detail"]


def test_empty_wish_returns_422(api_client):
    response = api_client.post(
        f"{BASE_URL}/api/inquiries",
        json={"product": "Handyhülle", "wish": "", "email": "delivered@resend.dev"},
        timeout=30,
    )
    assert response.status_code == 422
    assert response.json()["detail"]


def test_invalid_email_returns_422(api_client):
    response = api_client.post(
        f"{BASE_URL}/api/inquiries",
        json={"product": "Handyhülle", "wish": "Gravur", "email": "invalid-email"},
        timeout=30,
    )
    assert response.status_code == 422
    assert response.json()["detail"]


def test_list_inquiries_has_serializable_ids_without_mongo_objectid(api_client):
    response = api_client.get(f"{BASE_URL}/api/inquiries", timeout=30)
    assert response.status_code == 200
    rows = response.json()
    assert isinstance(rows, list)
    for row in rows:
        assert "_id" not in row
        assert isinstance(row["id"], str)
        assert isinstance(row["email_status"], str)


def test_external_cors_preflight_allows_frontend_origin(api_client):
    response = api_client.options(
        f"{BASE_URL}/api/inquiries",
        headers={
            "Origin": "https://email-error-debug-1.preview.emergentagent.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
        timeout=30,
    )
    assert response.status_code == 200
    allow_origin = response.headers.get("access-control-allow-origin", "")
    # The preview proxy rewrites the external origin to its cluster hostname.
    assert allow_origin == "*" or allow_origin.endswith(".preview.emergentcf.cloud")
    assert "POST" in response.headers.get("access-control-allow-methods", "")
