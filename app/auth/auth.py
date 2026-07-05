"""Login: members by email+PIN, admin by password. Session-state only,
never localStorage - replaces the fake client-side demo login that used
to live in the static site's login.html.
"""
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from db.members_store import get_member_by_email, get_admin_password_hash

_hasher = PasswordHasher()


def hash_secret(secret: str) -> str:
    return _hasher.hash(secret)


def verify_member(conn, email: str, pin: str):
    """Returns the Member on success, else None."""
    member = get_member_by_email(conn, email)
    if member is None:
        return None
    try:
        _hasher.verify(member.access_hash, pin)
    except VerifyMismatchError:
        return None
    return member


def verify_admin(conn, password: str) -> bool:
    password_hash = get_admin_password_hash(conn)
    if password_hash is None:
        return False
    try:
        _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False
    return True


def login_member(conn, email: str, pin: str) -> bool:
    import streamlit as st

    member = verify_member(conn, email, pin)
    if member is None:
        return False
    st.session_state["auth"] = {
        "role": "member",
        "member_code": member.member_code,
        "name": member.name,
        "email": member.email,
    }
    return True


def login_admin(conn, password: str) -> bool:
    import streamlit as st

    if not verify_admin(conn, password):
        return False
    st.session_state["auth"] = {"role": "admin"}
    return True


def logout():
    import streamlit as st

    st.session_state.pop("auth", None)


def current_auth():
    import streamlit as st

    return st.session_state.get("auth")


def render_login_page():
    """Body of the dedicated login st.Page - only ever registered in
    streamlit_app.py's nav when there's no active session, so it's the
    only page Streamlit can route to pre-login."""
    import streamlit as st

    from db.client import get_connection

    st.title("Natillera Digital — Ingresa a Tu Cuenta")
    tab_member, tab_admin = st.tabs(["Miembro", "Admin"])
    conn = get_connection()

    with tab_member:
        with st.form("login_member_form"):
            email = st.text_input("Correo electrónico")
            pin = st.text_input("PIN", type="password")
            if st.form_submit_button("Ingresar") and login_member(conn, email, pin):
                st.rerun()

    with tab_admin:
        with st.form("login_admin_form"):
            password = st.text_input("Contraseña de administrador", type="password")
            if st.form_submit_button("Ingresar") and login_admin(conn, password):
                st.rerun()


def require_login(role: str = "any"):
    """Defense-in-depth guard for individual admin_*/mi_panel pages: they
    should only ever be reachable when streamlit_app.py has already
    registered them in st.navigation() for the right role, but if the
    session expires mid-visit, force back to the login page instead of
    rendering member/admin content without a valid session."""
    import streamlit as st

    auth = current_auth()
    if auth is not None and (role == "any" or auth["role"] == role):
        return auth

    logout()
    st.rerun()
