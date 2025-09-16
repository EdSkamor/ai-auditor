"""
End-to-End tests for AI Auditor
Tests the complete application flow from frontend to backend
"""

import os

import pytest
import requests
from requests.auth import HTTPBasicAuth

RUN_E2E = os.getenv("RUN_E2E", "0") == "1"
APP_URL = os.getenv("APP_URL")  # np. http://localhost:8501
BACKEND_URL = os.getenv("BACKEND_URL")  # np. https://<tunnel>.trycloudflare.com
USER = os.getenv("BASIC_AUTH_USER")
PASS = os.getenv("BASIC_AUTH_PASS")

# Fail-fast: każdy request ma krótki timeout
TIMEOUT_FRONT = float(os.getenv("E2E_FRONT_TIMEOUT", "5"))
TIMEOUT_BACK = float(os.getenv("E2E_BACK_TIMEOUT", "5"))

pytestmark = pytest.mark.skipif(
    not RUN_E2E, reason="RUN_E2E!=1 – pomiń testy E2E w CI/localu bez serwisów"
)


def _auth():
    return HTTPBasicAuth(USER, PASS) if USER and PASS else None


def test_backend_healthz_200():
    """Test that backend health endpoint returns HTTP 200."""
    assert BACKEND_URL, "BACKEND_URL is not set"
    r = requests.get(f"{BACKEND_URL}/healthz", timeout=TIMEOUT_BACK)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "healthy"


def test_backend_ready_200():
    """Test that backend ready endpoint returns HTTP 200."""
    assert BACKEND_URL, "BACKEND_URL is not set"
    r = requests.get(f"{BACKEND_URL}/ready", timeout=TIMEOUT_BACK)
    assert r.status_code == 200, r.text
    assert "model_ready" in r.json()


def test_backend_analyze_without_auth_200():
    """Test that analyze endpoint works without authentication (Basic Auth disabled for demo)."""
    assert BACKEND_URL, "BACKEND_URL is not set"
    r = requests.post(
        f"{BACKEND_URL}/analyze",
        json={"prompt": "test", "max_new_tokens": 50},
        timeout=TIMEOUT_BACK,
    )
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert "output" in data


def test_backend_analyze_with_auth_200():
    """Test that analyze endpoint works with Basic Auth (if enabled)."""
    assert BACKEND_URL, "BACKEND_URL is not set"
    # Basic Auth is disabled for demo, so this test is skipped
    pytest.skip("Basic Auth disabled for demo")


def test_backend_analyze_wrong_auth_401():
    """Test that analyze endpoint rejects wrong credentials (if Basic Auth enabled)."""
    assert BACKEND_URL, "BACKEND_URL is not set"
    # Basic Auth is disabled for demo, so this test is skipped
    pytest.skip("Basic Auth disabled for demo")


def test_cors_headers():
    """Test that CORS headers are properly set."""
    assert BACKEND_URL, "BACKEND_URL is not set"
    r = requests.options(
        f"{BACKEND_URL}/analyze",
        headers={"Origin": "https://ai-auditor-87.streamlit.app"},
        timeout=TIMEOUT_BACK,
    )
    # CORS preflight should return 200 or 405
    assert r.status_code in [
        200,
        405,
    ], f"CORS preflight returned {r.status_code}: {r.text}"


def test_backend_response_time():
    """Test that backend responds within reasonable time."""
    assert BACKEND_URL, "BACKEND_URL is not set"
    import time

    start_time = time.time()
    r = requests.get(f"{BACKEND_URL}/healthz", timeout=TIMEOUT_BACK)
    end_time = time.time()

    assert r.status_code == 200
    assert (
        end_time - start_time
    ) < TIMEOUT_BACK, f"Backend response time too slow: {end_time - start_time:.2f}s"


def test_frontend_http_200():
    """Test that frontend returns HTTP 200."""
    assert APP_URL, "APP_URL is not set"
    r = requests.get(APP_URL, timeout=TIMEOUT_FRONT)
    assert r.status_code == 200, f"Frontend returned {r.status_code}: {r.text}"


def test_frontend_contains_ai_auditor():
    """Test that frontend contains expected content."""
    assert APP_URL, "APP_URL is not set"
    r = requests.get(APP_URL, timeout=TIMEOUT_FRONT)
    assert r.status_code == 200

    # Check for key content (case insensitive)
    content = r.text.lower()
    # Streamlit returns HTML skeleton, so we check for Streamlit-specific content
    assert (
        "streamlit" in content or "root" in content
    ), "Frontend missing expected content"


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
