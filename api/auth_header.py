"""Shared-secret header check. Streamlit has already authenticated the
member/admin at login; this only needs to reject the open internet from
hitting the API directly - proportionate for a pilot this size (8-12
members), not per-member auth."""
import os

from fastapi import Header, HTTPException


def require_api_key(x_api_key: str = Header(...)):
    expected = os.environ.get("UPLOAD_API_KEY")
    if not expected or x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
