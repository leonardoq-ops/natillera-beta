"""Member: upload proof of payment - calls the FastAPI proof service
(PROOF_API_BASE_URL) instead of writing to the ledger directly, per the
deliberate choice to run proof upload as a separate service."""
import os
from datetime import date

import requests
import streamlit as st

from auth.auth import require_login

auth = require_login("member")

API_BASE = st.secrets.get("PROOF_API_BASE_URL", os.environ.get("PROOF_API_BASE_URL", ""))
API_KEY = st.secrets.get("UPLOAD_API_KEY", os.environ.get("UPLOAD_API_KEY", ""))

st.title("Registrar Aporte — Subir Comprobante")

if not API_BASE:
    st.warning("El servicio de subida de comprobantes todavía no está configurado "
               "(falta PROOF_API_BASE_URL). Mientras tanto, contacta al admin para "
               "registrar tu aporte manualmente.")
    st.stop()

st.markdown('<div class="nat-card">', unsafe_allow_html=True)
month = st.text_input("Mes del aporte (AAAA-MM)", value=date.today().strftime("%Y-%m"))
confirmado = st.checkbox("Confirmo que realicé el pago")
uploaded_file = st.file_uploader("Comprobante de pago (PDF, JPG o PNG)",
                                  type=["pdf", "jpg", "jpeg", "png"])

if st.button("Enviar comprobante", disabled=not (confirmado and uploaded_file)):
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    data = {"member_code": auth["member_code"], "month": month, "confirmado": confirmado}
    headers = {"X-API-Key": API_KEY}
    try:
        resp = requests.post(f"{API_BASE}/api/upload-proof", data=data, files=files,
                              headers=headers, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        st.success(f"Comprobante enviado — estado: {result['status']}")
        st.link_button("Ver comprobante en Drive", result["proof_url"])
    except requests.RequestException as e:
        st.error(f"No se pudo enviar el comprobante: {e}")
st.markdown('</div>', unsafe_allow_html=True)
