"""Shared render helpers for the member/admin Streamlit pages."""
from decimal import Decimal

import streamlit as st

from natillera_engine.mora import EstadoPago
from ui.terms import ESTADO_LABEL, ESTADO_COLOR, THE_NUMBER_LABEL, HUELLA_LABEL


def cop(amount: Decimal) -> str:
    return f"${int(amount):,}".replace(",", ".")


def the_number_card(monto_proyectado: Decimal, sub: str = ""):
    st.metric(THE_NUMBER_LABEL, cop(monto_proyectado), delta=sub)


def estado_badge(estado: EstadoPago):
    color = ESTADO_COLOR[estado]
    label = ESTADO_LABEL[estado]
    st.markdown(f":{color}[**{label}**]")


def huella_gauge(score: Decimal):
    st.metric(HUELLA_LABEL, f"{score}/100")


def ledger_hash_seal(short_hash: str):
    st.caption(f"Sello de transparencia: `{short_hash[:12]}…`")
