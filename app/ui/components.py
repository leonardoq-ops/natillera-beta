"""Shared render helpers for the member/admin Streamlit pages."""
from decimal import Decimal

import streamlit as st

from ui.terms import ESTADO_LABEL, VERIFICACION_LABEL, BADGE_CLASS, THE_NUMBER_LABEL, HUELLA_LABEL
from ui.theme import the_number_html


def cop(amount: Decimal) -> str:
    return f"${int(amount):,}".replace(",", ".")


def the_number_card(monto_proyectado: Decimal, sub: str = ""):
    st.markdown(f'<div class="nat-card">{the_number_html(int(monto_proyectado))}</div>',
                unsafe_allow_html=True)
    if sub:
        st.caption(sub)


def estado_badge(estado):
    """Polymorphic over both natillera_engine.mora.EstadoPago and
    natillera_engine.proof_status.EstadoVerificacion - both are simple
    string enums with the same badge-rendering need."""
    label = ESTADO_LABEL.get(estado) or VERIFICACION_LABEL.get(estado) or estado.value
    css_class = BADGE_CLASS.get(estado, "nat-badge-teal")
    st.markdown(f'<span class="nat-badge {css_class}">{label}</span>', unsafe_allow_html=True)


def huella_gauge(score: Decimal):
    st.metric(HUELLA_LABEL, f"{score}/100")


def ledger_hash_seal(short_hash: str):
    st.caption(f"Sello de transparencia: `{short_hash[:12]}…`")
