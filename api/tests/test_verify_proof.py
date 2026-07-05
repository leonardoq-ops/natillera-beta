"""Pure-logic test of /api/verify-proof against a temp sqlite DB - no
live Google Drive/Cowork credentials needed (upload-proof is Drive/Cowork
dependent and covered only by the manual smoke-test checklist)."""
import os
import tempfile
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("UPLOAD_API_KEY", "test-key")


@pytest.fixture
def client(monkeypatch):
    path = os.path.join(tempfile.gettempdir(), "test_natillera_api.db")
    if os.path.exists(path):
        os.remove(path)

    from db.client import connect_raw
    from db.ledger_store import DbLedger
    from natillera_engine.ledger import EventType

    conn = connect_raw(path)
    ledger = DbLedger(conn)
    aporte = ledger.append(EventType.APORTE, "M01", Decimal("100000"),
                            {"month": "2026-07", "status": "PENDIENTE_VERIFICACION"})

    import main
    monkeypatch.setattr(main, "get_ledger", lambda: DbLedger(conn))

    with TestClient(main.app) as c:
        c._aporte_hash = aporte.hash
        yield c

    conn.close()
    if os.path.exists(path):
        os.remove(path)


def test_verify_proof_missing_api_key_header_is_rejected(client):
    resp = client.post("/api/verify-proof", json={
        "member_code": "M01", "month": "2026-07", "action": "VERIFICADO",
        "ledger_hash": client._aporte_hash,
    })
    assert resp.status_code == 422  # FastAPI rejects a missing required header before our check runs


def test_verify_proof_wrong_api_key_is_401(client):
    resp = client.post(
        "/api/verify-proof",
        json={"member_code": "M01", "month": "2026-07", "action": "VERIFICADO",
              "ledger_hash": client._aporte_hash},
        headers={"X-API-Key": "wrong-key"},
    )
    assert resp.status_code == 401


def test_verify_proof_marks_verificado(client):
    resp = client.post(
        "/api/verify-proof",
        json={"member_code": "M01", "month": "2026-07", "action": "VERIFICADO",
              "admin_notes": "ok", "ledger_hash": client._aporte_hash},
        headers={"X-API-Key": "test-key"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["new_status"] == "VERIFICADO"


def test_verify_proof_rejects_invalid_action(client):
    resp = client.post(
        "/api/verify-proof",
        json={"member_code": "M01", "month": "2026-07", "action": "MAYBE",
              "ledger_hash": client._aporte_hash},
        headers={"X-API-Key": "test-key"},
    )
    assert resp.status_code == 400
