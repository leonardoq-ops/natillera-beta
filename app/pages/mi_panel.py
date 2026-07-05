"""Member dashboard: THE NUMBER, personal breakdown, Viva/Niebla,
anonymous group grid, Huella Financiera, ledger hash seal.
"""
from datetime import date, datetime
from decimal import Decimal

import streamlit as st

from auth.auth import require_login
from db.client import get_connection
from db.ledger_store import DbLedger
from natillera_engine.config import PilotParams, RegulatoryParams2026
from natillera_engine.compounding import rendimiento_aporte
from natillera_engine.gmf import gmf_movimiento
from natillera_engine.retefuente import retefuente
from natillera_engine.huella import huella, consistencia_pago
from natillera_engine.mora import EstadoPago
from natillera_engine.ledger import EventType
from ui.components import the_number_card, estado_badge, huella_gauge, ledger_hash_seal, cop
from ui.terms import LA_COSECHA_LABEL

auth = require_login("member")
conn = get_connection()
params = PilotParams()
reg = RegulatoryParams2026()

st.title("Mi Panel")
st.caption(f"Hola, {auth['name']} — {LA_COSECHA_LABEL} se liquida el {params.liquidacion_tramo2}")

ledger = DbLedger(conn)
entries = [e for e in ledger.all_entries() if e["member_code"] == auth["member_code"]]
aportes = [e for e in entries if e["event"] == EventType.APORTE.value]

capital = sum(Decimal(e["amount_cop"]) for e in aportes)
corte = params.liquidacion_tramo2
rendimiento_bruto = sum(
    rendimiento_aporte(datetime.fromisoformat(e["timestamp_utc"]).date(),
                        Decimal(e["amount_cop"]), corte, params.tasa_liquida_ea)
    for e in aportes
)
proyeccion_bruta = capital + rendimiento_bruto

col1, col2, col3 = st.columns(3)
with col1:
    the_number_card(proyeccion_bruta, sub=f"{len(aportes)} aportes realizados")
with col2:
    st.metric("Mi capital aportado", cop(capital))
with col3:
    st.metric("Rendimiento proyectado (bruto)", cop(rendimiento_bruto))

st.subheader("Desglose neto estimado")
gmf_est = gmf_movimiento(rendimiento_bruto, Decimal("0"), reg.gmf_umbral_exento_cop)
rf_est = retefuente(rendimiento_bruto, Decimal("0"))
st.table({
    "Concepto": ["Rendimiento bruto", "GMF estimado", "Retefuente estimada", "Neto estimado"],
    "Monto": [cop(rendimiento_bruto), cop(gmf_est), cop(rf_est["rf_total"]),
              cop(rendimiento_bruto - gmf_est - rf_est["rf_total"])],
})

st.subheader("Estado de pago")
cur = conn.cursor()
cur.execute("SELECT estado FROM mora_state_cache WHERE member_code = ?", (auth["member_code"],))
row = cur.fetchone()
estado_actual = EstadoPago(row[0]) if row else EstadoPago.VIVA
estado_badge(estado_actual)

st.subheader("Huella Financiera")
meses_transcurridos = max(1, len(aportes))
componentes = {
    "consistencia_pago": consistencia_pago(len(aportes), meses_transcurridos),
    # Placeholders until enough pilot history exists to compute these signals for real.
    "antiguedad": Decimal("100"),
    "historial_nivel": Decimal("100"),
    "participacion_grupal": Decimal("100"),
    "respuesta_dificultad": Decimal("100"),
}
huella_gauge(huella(componentes))

st.subheader("Grilla anónima del grupo")
cur.execute("SELECT member_code, estado FROM mora_state_cache ORDER BY member_code ASC")
grid_rows = cur.fetchall()
if grid_rows:
    st.table({"Miembro": [r[0] for r in grid_rows], "Estado": [EstadoPago(r[1]).value for r in grid_rows]})
else:
    st.info("Aún no hay datos de estado de mora registrados.")

st.subheader("Sello de transparencia")
if entries:
    latest = entries[-1]
    ledger_hash_seal(latest["hash"])
    with st.expander("Verificar integridad de mi historial"):
        ok, bad_seq = ledger.verify_chain()
        st.write("Cadena íntegra ✅" if ok else f"Alerta: inconsistencia detectada en seq {bad_seq}")
else:
    st.info("Aún no tienes movimientos registrados.")
