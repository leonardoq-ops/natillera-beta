"""Natillera Digital - Proof of Payment API.

Deliberately a separate FastAPI service from the Streamlit app (which
calls this over HTTP via `requests`), deployed to Google Cloud Run.
Reuses natillera_engine/db verbatim - see Dockerfile, which COPYs
app/natillera_engine and app/db into the image alongside this file so
there is exactly one copy of that code in git.
"""
import os
from datetime import date, datetime, timezone
from decimal import Decimal

from fastapi import Depends, FastAPI, Form, HTTPException, UploadFile

from auth_header import require_api_key
from cowork_notify import notify_cowork
from google_drive_utils import upload_to_drive
from schemas import UploadProofResponse, VerifyProofRequest, VerifyProofResponse

from db.client import connect_raw
from db.ledger_store import DbLedger
from natillera_engine.config import PilotParams
from natillera_engine.ledger import EventType
from natillera_engine.mora import EstadoPago, estado_mora

app = FastAPI(title="Natillera Digital - Proof API")

ALLOWED_CONTENT_TYPES = {"application/pdf", "image/jpeg", "image/png"}


def get_ledger() -> DbLedger:
    conn = connect_raw(os.environ["TURSO_DATABASE_URL"], os.environ.get("TURSO_AUTH_TOKEN"))
    return DbLedger(conn)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/upload-proof", response_model=UploadProofResponse,
          dependencies=[Depends(require_api_key)])
async def upload_proof(
    member_code: str = Form(...),
    month: str = Form(...),
    confirmado: bool = Form(...),
    file: UploadFile = None,
):
    if not confirmado:
        raise HTTPException(400, "Debe confirmar que realizó el pago.")
    if file is None or file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(400, "Archivo requerido (PDF, JPG o PNG).")

    file_bytes = await file.read()
    drive_result = upload_to_drive(member_code, file.filename, file_bytes, file.content_type)

    ledger = get_ledger()
    monto = PilotParams().aporte_mensual
    entry = ledger.append(
        EventType.APORTE, member_code, Decimal(monto),
        {
            "month": month,
            "proof_file_id": drive_result["file_id"],
            "proof_url": drive_result["web_view_link"],
            "status": "PENDIENTE_VERIFICACION",
            "uploaded_timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "upload_proof",
        },
    )

    notify_cowork(member_code, month, drive_result["web_view_link"])

    return UploadProofResponse(
        success=True, member_code=member_code,
        status="PENDIENTE_VERIFICACION",
        proof_url=drive_result["web_view_link"],
        ledger_hash=entry.hash,
    )


@app.post("/api/verify-proof", response_model=VerifyProofResponse,
          dependencies=[Depends(require_api_key)])
def verify_proof(body: VerifyProofRequest):
    if body.action not in ("VERIFICADO", "RECHAZADO"):
        raise HTTPException(400, "action debe ser VERIFICADO o RECHAZADO")

    ledger = get_ledger()
    entry = ledger.append(
        EventType.VERIFICACION, body.member_code, Decimal("0"),
        {
            "month": body.month,
            "accion": body.action,
            "admin_notes": body.admin_notes,
            "ledger_hash_referenciado": body.ledger_hash,
            "reviewed_timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    if body.action == "VERIFICADO":
        nuevo_estado = EstadoPago.VIVA
    else:
        params = PilotParams()
        hoy = date.today()
        fecha_limite = date(hoy.year, hoy.month, params.dia_limite_pago)
        nuevo_estado = estado_mora(fecha_limite, hoy, pago_realizado=False,
                                   comunico_en_gracia=False, acuerdo_escrito=False)

    conn = ledger.conn
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO mora_state_cache (member_code, estado, updated_at_utc)
           VALUES (?, ?, ?)
           ON CONFLICT(member_code) DO UPDATE SET estado = excluded.estado, updated_at_utc = excluded.updated_at_utc""",
        (body.member_code, nuevo_estado.value, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()

    return VerifyProofResponse(
        success=True, member_code=body.member_code,
        new_status=body.action, ledger_hash=entry.hash,
    )
