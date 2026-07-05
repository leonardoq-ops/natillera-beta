"""Admin: liquidity reserve health."""
from decimal import Decimal

import streamlit as st

from auth.auth import require_login
from db.client import get_connection
from natillera_engine.reserve import evaluar_reserva, ZonaReserva
from ui.components import cop

require_login("admin")
conn = get_connection()

st.title("Admin — Salud de la Reserva")

fondo_total = Decimal(str(st.number_input("Fondo total (COP)", value=10000000, step=100000)))
liquido = Decimal(str(st.number_input("Líquido disponible (COP)", value=1000000, step=100000)))

resultado = evaluar_reserva(liquido, fondo_total)

color = {"CONFORT": "green", "OBSERVACION": "orange", "ALERTA": "red"}[resultado["zona"].value]
st.markdown(f"### Zona: :{color}[{resultado['zona'].value}]")
st.metric("% de reserva líquida", f"{resultado['pct_reserva'] * 100:.1f}%")
st.write(f"Acción: **{resultado['accion']}**")
if resultado["monto_a_liquidar_de_cdt"] > 0:
    st.warning(f"Monto a liquidar del CDT para volver al 12%: {cop(resultado['monto_a_liquidar_de_cdt'])}")
