"""Admin: run La Cosecha (year-end liquidación). Orchestrates
compounding -> GMF bimestral plan -> retefuente -> VNR -> LIQUIDACION
ledger entries. Irreversible-by-design (append-only ledger), gated
behind an explicit confirmation step.
"""
from datetime import datetime
from decimal import Decimal

import streamlit as st

from auth.auth import require_login
from db.client import get_connection
from db.ledger_store import DbLedger
from db.members_store import list_members
from natillera_engine.config import PilotParams, RegulatoryParams2026
from natillera_engine.compounding import rendimiento_aporte
from natillera_engine.gmf import plan_liquidacion_bimestral
from natillera_engine.retefuente import retefuente
from natillera_engine.vnr import liquidacion_grupo
from natillera_engine.ledger import EventType
from ui.components import cop

require_login("admin")
conn = get_connection()
params = PilotParams()
reg = RegulatoryParams2026()

st.title(f"Admin — Ejecutar La Cosecha ({params.liquidacion_tramo2})")

ledger = DbLedger(conn)
members = list_members(conn)
entries = ledger.all_entries()

capitales: dict[str, Decimal] = {}
rendimiento_total = Decimal("0")
for m in members:
    aportes = [e for e in entries if e["member_code"] == m.member_code and e["event"] == EventType.APORTE.value]
    capital_m = sum(Decimal(e["amount_cop"]) for e in aportes)
    rend_m = sum(
        rendimiento_aporte(datetime.fromisoformat(e["timestamp_utc"]).date(),
                            Decimal(e["amount_cop"]), params.liquidacion_tramo2, params.tasa_liquida_ea)
        for e in aportes
    )
    capitales[m.member_code] = capital_m
    rendimiento_total += rend_m

fondo_total = sum(capitales.values()) + rendimiento_total
plan_gmf = plan_liquidacion_bimestral(fondo_total, reg.gmf_umbral_exento_cop)
rf = retefuente(rendimiento_total, Decimal("0"))

st.subheader("Resumen previo a liquidar")
st.write(f"Fondo total proyectado: {cop(fondo_total)}")
st.write(f"Rendimiento total: {cop(rendimiento_total)}")
st.write(f"GMF total (plan bimestral): {cop(plan_gmf['gmf_total'])} — estrategia válida: {plan_gmf['estrategia_valida']}")
st.write(f"Retefuente total: {cop(rf['rf_total'])}")

if not capitales or fondo_total == 0:
    st.warning("No hay capital registrado todavía — nada que liquidar.")
    st.stop()

resultados = liquidacion_grupo(capitales, rendimiento_total, plan_gmf["gmf_total"], rf["rf_total"])
st.subheader("Distribución (VNR) por miembro")
st.dataframe(
    [{"member_code": code, **{k: (cop(v) if isinstance(v, Decimal) else v) for k, v in r.items()}}
     for code, r in resultados.items()],
    use_container_width=True,
)

st.divider()
st.warning("Esta acción escribe entradas LIQUIDACION en el ledger (append-only, irreversible).")
confirm = st.checkbox("Confirmo que quiero ejecutar La Cosecha ahora")
if st.button("Ejecutar La Cosecha", disabled=not confirm):
    for code, r in resultados.items():
        ledger.append(EventType.LIQUIDACION, code, r["vnr"], {
            "capital": str(r["capital"]),
            "rendimiento_asignado": str(r["rendimiento_asignado"]),
            "gmf_asignado": str(r["gmf_asignado"]),
            "retefuente_asignada": str(r["retefuente_asignada"]),
        })
    st.success("La Cosecha ejecutada. Revisa la integridad del ledger en Admin — Integridad del Ledger.")
