"""Admin: verification queue for member-uploaded proofs. Calls the
FastAPI proof service's /api/verify-proof rather than writing to the
ledger directly - keeps the ledger write path single-sourced in the API
service that also handles the Drive upload."""
import os
from collections import defaultdict

import requests
import streamlit as st

from auth.auth import require_login
from db.client import get_connection
from db.ledger_store import DbLedger
from db.members_store import list_members
from natillera_engine.ledger import EventType
from natillera_engine.proof_status import EstadoVerificacion, estado_verificacion_actual

require_login("admin")
conn = get_connection()

API_BASE = st.secrets.get("PROOF_API_BASE_URL", os.environ.get("PROOF_API_BASE_URL", ""))
API_KEY = st.secrets.get("UPLOAD_API_KEY", os.environ.get("UPLOAD_API_KEY", ""))

st.title("Admin — Verificación de Comprobantes")

if not API_BASE:
    st.warning("El servicio de verificación todavía no está configurado (falta PROOF_API_BASE_URL).")
    st.stop()

members_by_code = {m.member_code: m.name for m in list_members(conn)}
ledger = DbLedger(conn)
entries = ledger.all_entries()

# Group by (member_code, month) so estado_verificacion_actual sees the
# full history for that period, not just the raw APORTE row.
by_member_month = defaultdict(list)
aporte_by_member_month = {}
for e in entries:
    if e["event"] not in (EventType.APORTE.value, EventType.VERIFICACION.value):
        continue
    month = e["detail"].get("month")
    if not month:
        continue
    key = (e["member_code"], month)
    by_member_month[key].append(e)
    if e["event"] == EventType.APORTE.value and e["detail"].get("source") == "upload_proof":
        aporte_by_member_month[key] = e

pending = [
    (key, aporte_by_member_month[key])
    for key in aporte_by_member_month
    if estado_verificacion_actual(by_member_month[key]) == EstadoVerificacion.PENDIENTE_VERIFICACION
]

if not pending:
    st.info("No hay comprobantes pendientes de verificación.")

for (member_code, month), aporte in pending:
    name = members_by_code.get(member_code, member_code)
    with st.container():
        st.markdown('<div class="nat-card">', unsafe_allow_html=True)
        st.subheader(f"{member_code} ({name}) — {month}")
        st.write(f"Subido: {aporte['detail'].get('uploaded_timestamp', 'desconocido')}")
        st.link_button("Ver comprobante", aporte["detail"].get("proof_url", "#"))
        admin_notes = st.text_input("Notas (opcional, requerido si rechazas)",
                                     key=f"notes_{member_code}_{month}")

        col1, col2 = st.columns(2)
        if col1.button("Verificar ✓", key=f"verify_{member_code}_{month}"):
            resp = requests.post(
                f"{API_BASE}/api/verify-proof",
                json={"member_code": member_code, "month": month, "action": "VERIFICADO",
                      "admin_notes": admin_notes, "ledger_hash": aporte["hash"]},
                headers={"X-API-Key": API_KEY}, timeout=15,
            )
            if resp.ok:
                st.success("Marcado como VERIFICADO.")
                st.rerun()
            else:
                st.error(f"Error: {resp.text}")
        if col2.button("Rechazar ✗", key=f"reject_{member_code}_{month}"):
            resp = requests.post(
                f"{API_BASE}/api/verify-proof",
                json={"member_code": member_code, "month": month, "action": "RECHAZADO",
                      "admin_notes": admin_notes, "ledger_hash": aporte["hash"]},
                headers={"X-API-Key": API_KEY}, timeout=15,
            )
            if resp.ok:
                st.success("Marcado como RECHAZADO.")
                st.rerun()
            else:
                st.error(f"Error: {resp.text}")
        st.markdown('</div>', unsafe_allow_html=True)
