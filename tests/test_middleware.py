import io

import pytest
from fastapi import FastAPI, File, UploadFile
from fastapi.testclient import TestClient

from app.core.middleware import UploadSizeLimit

LIMIT = 1024 * 1024  # 1MB file limit for these tests


@pytest.fixture
def client():
    app = FastAPI()
    reached = []

    @app.post("/upload")
    async def upload(file: UploadFile = File(...)):
        reached.append(file.filename)
        return {"ok": True}

    @app.post("/chat")
    async def chat():
        return {"ok": True}

    app.add_middleware(UploadSizeLimit, path="/upload", max_bytes=LIMIT, overhead=1024)
    c = TestClient(app)
    c.reached = reached
    return c


def _post(client, path, size):
    return client.post(path, files={"file": ("doc.pdf", io.BytesIO(b"x" * size), "application/pdf")})


def test_oversized_upload_is_rejected_with_413(client):
    r = _post(client, "/upload", LIMIT * 3)
    assert r.status_code == 413
    assert "1MB limit" in r.json()["detail"]


def test_rejection_happens_before_the_endpoint_parses_anything(client):
    _post(client, "/upload", LIMIT * 3)
    assert client.reached == [], "the multipart body should never have been parsed"


def test_upload_within_the_limit_passes_through(client):
    r = _post(client, "/upload", 1000)
    assert r.status_code == 200
    assert client.reached == ["doc.pdf"]


def test_overhead_allowance_admits_a_file_at_exactly_the_limit(client):
    """Multipart framing must not push a legal file over the edge."""
    r = _post(client, "/upload", LIMIT)
    assert r.status_code == 200


def test_other_routes_are_untouched(client):
    r = _post(client, "/chat", LIMIT * 3)
    assert r.status_code != 413


def test_guard_is_wired_to_the_real_upload_route():
    """Catches the router gaining a prefix without the guard following it."""
    from app.main import app

    resolved = app.url_path_for("upload_pdf")
    bound = [m for m in app.user_middleware if m.cls is UploadSizeLimit]
    assert len(bound) == 1
    assert bound[0].kwargs["path"] == resolved


def test_rejection_still_carries_cors_headers():
    """Without CORS outside the guard the browser sees a CORS error, not the 413."""
    import io

    from fastapi.testclient import TestClient

    from app.core.config import settings
    from app.main import app

    body = b"x" * (settings.max_pdf_bytes + 2 * 1024 * 1024)
    r = TestClient(app).post(
        "/upload",
        files={"file": ("big.pdf", io.BytesIO(body), "application/pdf")},
        headers={"Origin": "http://localhost:5173"},
    )
    assert r.status_code == 413
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"
