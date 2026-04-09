"""
E2E tests for zrelay — real MCP calls against a live Docker container.

Run:
    ZRELAY_URL=http://localhost:8000 \
    ZRELAY_ADMIN_PASSWORD=admin \
    Z_AI_API_KEY=your-upstream-key \
    pytest tests/e2e/ -v

The test suite will:
1. Login to admin
2. Create a temporary API key
3. Run all endpoint tests
4. Delete the temporary key
"""

import os
import uuid

import httpx
import pytest

BASE_URL = os.environ.get("ZRELAY_URL", "").rstrip("/")
ADMIN_PASSWORD = os.environ.get("ZRELAY_ADMIN_PASSWORD", "")

SKIP_MSG = "ZRELAY_URL or ZRELAY_ADMIN_PASSWORD not set — skipping e2e"


@pytest.fixture(scope="session")
def api_client():
    """Create httpx client and a temporary API key for all tests."""
    if not BASE_URL or not ADMIN_PASSWORD:
        pytest.skip(SKIP_MSG)

    client = httpx.Client(base_url=BASE_URL, timeout=300.0, follow_redirects=True)

    # Login to admin
    resp = client.post("/admin/login", data={"username": "admin", "password": ADMIN_PASSWORD})
    assert resp.status_code == 200, f"Admin login failed: {resp.status_code}"

    # Create temporary API key
    key_name = f"e2e-test-{uuid.uuid4().hex[:8]}"
    resp = client.post("/admin/keys/create", data={"name": key_name})
    assert resp.status_code == 200, f"Key creation failed: {resp.status_code}"

    # Get all keys to find ours
    resp = client.get("/admin/keys")
    assert resp.status_code == 200

    # Extract key from page — parse HTML
    import re
    keys = re.findall(r'zr-[A-Za-z0-9_-]+', resp.text)
    assert len(keys) > 0, "No API keys found"
    api_key = keys[-1]  # Last created

    yield client, api_key

    # Cleanup: delete the key
    try:
        client.delete("/admin/keys/delete/")
    except Exception:
        pass
    client.close()


@pytest.fixture(scope="session")
def client(api_client):
    return api_client[0]


@pytest.fixture(scope="session")
def api_key(api_client):
    return api_client[1]


def auth_headers(api_key):
    return {"X-API-Key": api_key, "Content-Type": "application/json"}


# ─── Infrastructure ───────────────────────────────────────────


class TestInfrastructure:
    def test_root_redirects_to_llms(self, client):
        resp = client.get("/", follow_redirects=False)
        assert resp.status_code == 307
        assert "/llms.txt" in resp.headers.get("location", "")

    def test_llms_txt(self, client):
        resp = client.get("/llms.txt")
        assert resp.status_code == 200
        assert "zrelay" in resp.text
        assert "search" in resp.text.lower()
        assert "vision" in resp.text.lower()

    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_ready(self, client):
        resp = client.get("/ready")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ready"

    def test_docs(self, client):
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_404_returns_error_format(self, client):
        resp = client.get("/api/v1/nonexistent")
        assert resp.status_code == 404
        body = resp.json()
        assert "error" in body
        assert "code" in body["error"]


# ─── Auth ──────────────────────────────────────────────────────


class TestAuth:
    def test_no_api_key_returns_401(self, client):
        resp = client.post("/api/v1/search/web-search", json={"query": "test"})
        assert resp.status_code == 401
        body = resp.json()
        assert "error" in body
        assert "code" in body["error"]

    def test_invalid_api_key_returns_401(self, client):
        resp = client.post(
            "/api/v1/search/web-search",
            json={"query": "test"},
            headers={"X-API-Key": "invalid-key-12345"},
        )
        assert resp.status_code == 401
        body = resp.json()
        assert "error" in body

    def test_all_endpoints_require_auth(self, client):
        endpoints = [
            ("/api/v1/search/web-search", {"query": "test"}),
            ("/api/v1/reader/read-web", {"url": "https://example.com"}),
            ("/api/v1/zread/search-doc", {"repo": "test/repo", "query": "test"}),
            ("/api/v1/zread/repo-structure", {"repo": "test/repo"}),
            ("/api/v1/zread/read-file", {"repo": "test/repo", "path": "README.md"}),
            ("/api/v1/vision/image-analysis", {"image_source": "/tmp/test.png"}),
            ("/api/v1/vision/ui-diff-check", {"expected_image_source": "/a.png", "actual_image_source": "/b.png"}),
        ]
        for url, payload in endpoints:
            resp = client.post(url, json=payload)
            assert resp.status_code == 401, f"{url} should require auth, got {resp.status_code}"


# ─── Search ────────────────────────────────────────────────────


class TestSearch:
    def test_search_web(self, client, api_key):
        resp = client.post(
            "/api/v1/search/web-search",
            json={"query": "Python FastAPI tutorial", "max_results": 3},
            headers=auth_headers(api_key),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["tool"] == "web_search_prime"
        assert body["operation"] == "web_search_prime"
        assert body["request_id"]
        assert body["data"] is not None

    def test_search_web_russian(self, client, api_key):
        resp = client.post(
            "/api/v1/search/web-search",
            json={"query": "Python REST API", "location": "us"},
            headers=auth_headers(api_key),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True

    def test_search_web_missing_query(self, client, api_key):
        resp = client.post(
            "/api/v1/search/web-search",
            json={},
            headers=auth_headers(api_key),
        )
        assert resp.status_code == 422


# ─── Reader ────────────────────────────────────────────────────


class TestReader:
    def test_read_web(self, client, api_key):
        resp = client.post(
            "/api/v1/reader/read-web",
            json={"url": "https://example.com"},
            headers=auth_headers(api_key),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["tool"] == "web_reader"
        assert body["operation"] == "webReader"
        assert body["data"] is not None

    def test_read_web_missing_url(self, client, api_key):
        resp = client.post(
            "/api/v1/reader/read-web",
            json={},
            headers=auth_headers(api_key),
        )
        assert resp.status_code == 422


# ─── Zread ─────────────────────────────────────────────────────


class TestZread:
    def test_search_doc(self, client, api_key):
        resp = client.post(
            "/api/v1/zread/search-doc",
            json={"repo": "fastapi/fastapi", "query": "routing", "language": "en"},
            headers=auth_headers(api_key),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "ok" in body
        assert body["operation"] == "search_doc"

    def test_repo_structure(self, client, api_key):
        resp = client.post(
            "/api/v1/zread/repo-structure",
            json={"repo": "fastapi/fastapi"},
            headers=auth_headers(api_key),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["operation"] == "get_repo_structure"

    def test_read_file(self, client, api_key):
        resp = client.post(
            "/api/v1/zread/read-file",
            json={"repo": "fastapi/fastapi", "path": "README.md"},
            headers=auth_headers(api_key),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "ok" in body
        assert body["operation"] == "read_file"

    def test_search_doc_missing_query(self, client, api_key):
        resp = client.post(
            "/api/v1/zread/search-doc",
            json={"repo": "fastapi/fastapi"},
            headers=auth_headers(api_key),
        )
        assert resp.status_code == 422


# ─── Vision ────────────────────────────────────────────────────


class TestVision:
    def test_image_analysis(self, client, api_key):
        """Vision — may return ok=false if file doesn't exist, but endpoint must respond 200."""
        resp = client.post(
            "/api/v1/vision/image-analysis",
            json={"image_source": "/tmp/nonexistent_test_image.png", "prompt": "What do you see?"},
            headers=auth_headers(api_key),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "ok" in body
        assert body["tool"] == "vision"
        assert body["operation"] == "image_analysis"

    def test_ui_diff_check(self, client, api_key):
        resp = client.post(
            "/api/v1/vision/ui-diff-check",
            json={"expected_image_source": "/tmp/before.png", "actual_image_source": "/tmp/after.png"},
            headers=auth_headers(api_key),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "ok" in body
        assert body["operation"] == "ui_diff_check"


# ─── Admin ─────────────────────────────────────────────────────


class TestAdmin:
    def test_login_page(self, client):
        resp = client.get("/admin/login")
        assert resp.status_code == 200

    def test_dashboard_accessible(self, client):
        resp = client.get("/admin")
        assert resp.status_code == 200
        assert "Dashboard" in resp.text or "dashboard" in resp.text

    def test_logs_accessible(self, client):
        resp = client.get("/admin/logs")
        assert resp.status_code == 200

    def test_keys_accessible(self, client):
        resp = client.get("/admin/keys")
        assert resp.status_code == 200


# ─── Response Format ──────────────────────────────────────────


class TestResponseFormat:
    def test_success_has_request_id(self, client, api_key):
        resp = client.post(
            "/api/v1/search/web-search",
            json={"query": "test request_id", "max_results": 1},
            headers=auth_headers(api_key),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "request_id" in body
        assert len(body["request_id"]) > 0

    def test_success_has_tool_operation_data_meta(self, client, api_key):
        resp = client.post(
            "/api/v1/search/web-search",
            json={"query": "test structure", "max_results": 1},
            headers=auth_headers(api_key),
        )
        body = resp.json()
        assert "tool" in body
        assert "operation" in body
        assert "ok" in body
        assert "data" in body
        assert "meta" in body
