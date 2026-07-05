"""Admin: ledger integrity check + read-only raw entries. No edit UI ever."""
import streamlit as st

from auth.auth import require_login
from db.client import get_connection
from db.ledger_store import DbLedger

require_login("admin")
conn = get_connection()

st.title("Admin — Integridad del Ledger")

ledger = DbLedger(conn)
ok, bad_seq = ledger.verify_chain()
if ok:
    st.success("Cadena de hashes íntegra ✅")
else:
    st.error(f"⚠️ Se detectó una inconsistencia en seq {bad_seq}. Investigar de inmediato.")

st.subheader("Entradas del ledger (solo lectura)")
entries = ledger.all_entries()
if entries:
    st.dataframe(entries, use_container_width=True)
else:
    st.info("El ledger aún no tiene movimientos.")
