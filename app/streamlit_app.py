"""Entrypoint. Renders the login gate, then a role-filtered nav menu -
admins see all admin_* pages, members only see Mi Panel."""
import streamlit as st

from auth.auth import require_login, logout

st.set_page_config(page_title="Natillera Digital", page_icon="💰", layout="wide")

auth = require_login("any")

with st.sidebar:
    st.caption(f"Sesión: {auth.get('name', 'Admin')} ({auth['role']})")
    if st.button("Cerrar sesión", key="sidebar_logout"):
        logout()
        st.rerun()

mi_panel = st.Page("pages/mi_panel.py", title="Mi Panel", icon="📊", default=(auth["role"] == "member"))
admin_aportes = st.Page("pages/admin_aportes.py", title="Aportes", icon="🧾", default=(auth["role"] == "admin"))
admin_mora = st.Page("pages/admin_mora.py", title="Mora", icon="⚠️")
admin_reserva = st.Page("pages/admin_reserva.py", title="Reserva", icon="💧")
admin_ledger = st.Page("pages/admin_ledger.py", title="Ledger", icon="🔗")
admin_cosecha = st.Page("pages/admin_cosecha.py", title="La Cosecha", icon="🌾")

if auth["role"] == "admin":
    pages = [admin_aportes, admin_mora, admin_reserva, admin_ledger, admin_cosecha]
else:
    pages = [mi_panel]

nav = st.navigation(pages)
nav.run()
