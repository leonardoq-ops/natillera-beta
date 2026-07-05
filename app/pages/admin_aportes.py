"""Admin: manual aporte entry (Google Forms integration is out of scope)."""
from datetime import date, datetime
from decimal import Decimal

import streamlit as st

from auth.auth import require_login
from db.client import get_connection
from db.ledger_store import DbLedger
from db.members_store import list_members
from natillera_engine.config import PilotParams
from natillera_engine.ledger import EventType
from natillera_engine.mora import EstadoPago

require_login("admin")
conn = get_connection()
params = PilotParams()

st.title("Admin — Registrar Aporte")

members = list_members(conn)
if not members:
    st.warning("No hay miembros registrados. Usa scripts/seed_members.py para agregarlos.")
    st.stop()

with st.form("aporte_form"):
    member_code = st.selectbox("Miembro", [m.member_code for m in members],
                                format_func=lambda code: next(m.name for m in members if m.member_code == code))
    monto = st.number_input("Monto (COP)", value=int(params.aporte_mensual), step=10000)
    fecha_pago = st.date_input("Fecha de pago", value=date.today())
    submitted = st.form_submit_button("Registrar aporte")

if submitted:
    ledger = DbLedger(conn)
    ledger.append(EventType.APORTE, member_code, Decimal(str(monto)),
                  {"fecha_pago": fecha_pago.isoformat()})

    a_tiempo = fecha_pago.day <= params.dia_limite_pago
    estado = EstadoPago.VIVA if a_tiempo else EstadoPago.NIEBLA_AUTO
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO mora_state_cache (member_code, estado, updated_at_utc)
           VALUES (?, ?, ?)
           ON CONFLICT(member_code) DO UPDATE SET estado = excluded.estado, updated_at_utc = excluded.updated_at_utc""",
        (member_code, estado.value, datetime.utcnow().isoformat()),
    )
    conn.commit()
    st.success(f"Aporte de {member_code} registrado — estado: {estado.value}")
