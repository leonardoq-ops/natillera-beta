"""Entrypoint. st.navigation() must be called on EVERY run - including
before login - otherwise Streamlit falls back to its classic automatic
sidebar (built from the mere existence of pages/*.py files), which would
list every admin page to an unauthenticated visitor. Login itself is
just another st.Page, swapped in when there's no active session.
"""
import streamlit as st

from auth.auth import current_auth, render_login_page, logout
from ui.theme import inject_theme

st.set_page_config(page_title="Natillera Digital", page_icon="💰", layout="wide")
inject_theme()

auth = current_auth()

login_page = st.Page(render_login_page, title="Ingresar", icon="🔐")
mi_panel = st.Page("pages/mi_panel.py", title="Mi Panel", icon="📊")
subir_comprobante = st.Page("pages/subir_comprobante.py", title="Registrar Aporte", icon="📤")
admin_aportes = st.Page("pages/admin_aportes.py", title="Aportes", icon="🧾")
admin_verificacion = st.Page("pages/admin_verificacion.py", title="Verificación", icon="✅")
admin_mora = st.Page("pages/admin_mora.py", title="Mora", icon="⚠️")
admin_reserva = st.Page("pages/admin_reserva.py", title="Reserva", icon="💧")
admin_ledger = st.Page("pages/admin_ledger.py", title="Ledger", icon="🔗")
admin_cosecha = st.Page("pages/admin_cosecha.py", title="La Cosecha", icon="🌾")

if auth is None:
    pages = [login_page]
else:
    with st.sidebar:
        st.caption(f"Sesión: {auth.get('name', 'Admin')} ({auth['role']})")
        if st.button("Cerrar sesión", key="sidebar_logout"):
            logout()
            st.rerun()
    pages = [admin_aportes, admin_verificacion, admin_mora, admin_reserva, admin_ledger, admin_cosecha] \
        if auth["role"] == "admin" else [mi_panel, subir_comprobante]

st.navigation(pages).run()
