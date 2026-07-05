"""Connection factory for the ledger/members store.

Reads TURSO_DATABASE_URL / TURSO_AUTH_TOKEN from st.secrets when running
inside Streamlit (production: Turso). Falls back to LOCAL_SQLITE_PATH for
local dev. Tests should call connect_raw(path) directly and bypass secrets
entirely.
"""
from pathlib import Path

import libsql

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def ensure_schema(conn) -> None:
    conn.executescript(_SCHEMA_PATH.read_text(encoding="utf-8"))


def connect_raw(target: str, auth_token: str | None = None):
    """Open a connection to a local file path or a libsql:// URL."""
    conn = libsql.connect(target, auth_token=auth_token) if auth_token else libsql.connect(target)
    ensure_schema(conn)
    return conn


def get_connection():
    """Streamlit-facing entrypoint: cached connection resolved from st.secrets."""
    import streamlit as st

    @st.cache_resource
    def _cached():
        secrets = st.secrets
        turso_url = secrets.get("TURSO_DATABASE_URL")
        if turso_url:
            return connect_raw(turso_url, secrets.get("TURSO_AUTH_TOKEN"))
        local_path = secrets.get("LOCAL_SQLITE_PATH", "app/local_natillera.db")
        return connect_raw(local_path)

    return _cached()
