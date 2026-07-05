"""Admin: mora state review and manual overrides
(comunico_en_gracia / acuerdo_escrito feed the mora protocol's state machine).
"""
from datetime import date, datetime

import streamlit as st

from auth.auth import require_login
from db.client import get_connection
from db.members_store import list_members
from natillera_engine.config import PilotParams
from natillera_engine.mora import estado_mora, EstadoPago

require_login("admin")
conn = get_connection()
params = PilotParams()

st.title("Admin — Estado de Mora")

members = list_members(conn)
hoy = st.date_input("Evaluar mora a la fecha de", value=date.today())
fecha_limite = date(hoy.year, hoy.month, params.dia_limite_pago)

cur = conn.cursor()
for m in members:
    with st.expander(f"{m.member_code} — {m.name}"):
        cur.execute("SELECT estado FROM mora_state_cache WHERE member_code = ?", (m.member_code,))
        row = cur.fetchone()
        st.write(f"Estado actual: **{row[0] if row else EstadoPago.VIVA.value}**")

        col1, col2, col3 = st.columns(3)
        pago_realizado = col1.checkbox("Pago realizado", key=f"pago_{m.member_code}")
        comunico = col2.checkbox("Comunicó en gracia", key=f"comunico_{m.member_code}")
        acuerdo = col3.checkbox("Acuerdo escrito (plan de pago)", key=f"acuerdo_{m.member_code}")

        if st.button("Actualizar estado", key=f"btn_{m.member_code}"):
            nuevo_estado = estado_mora(fecha_limite, hoy, pago_realizado, comunico, acuerdo)
            cur.execute(
                """INSERT INTO mora_state_cache (member_code, estado, updated_at_utc)
                   VALUES (?, ?, ?)
                   ON CONFLICT(member_code) DO UPDATE SET estado = excluded.estado, updated_at_utc = excluded.updated_at_utc""",
                (m.member_code, nuevo_estado.value, datetime.utcnow().isoformat()),
            )
            conn.commit()
            st.success(f"Nuevo estado: {nuevo_estado.value}")
            st.rerun()
