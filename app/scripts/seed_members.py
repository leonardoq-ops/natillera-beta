"""One-off local script for the admin to seed members and set the admin
password. Not part of the deployed Streamlit app.

Usage:
    python scripts/seed_members.py --db app/local_natillera.db --set-admin-password
    python scripts/seed_members.py --db app/local_natillera.db \\
        --add-member M01 "Ana Perez" ana@example.com 2026-01-15 1234

Run against a Turso database instead by passing a libsql:// URL as --db
and --auth-token.
"""
import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from auth.auth import hash_secret
from db.client import connect_raw
from db.members_store import add_member, set_admin_password


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, help="Local sqlite path or libsql:// URL")
    parser.add_argument("--auth-token", default=None, help="Turso auth token, if --db is a libsql:// URL")
    parser.add_argument("--set-admin-password", action="store_true")
    parser.add_argument("--add-member", nargs=5, metavar=("MEMBER_CODE", "NAME", "EMAIL", "JOIN_DATE", "PIN"))
    args = parser.parse_args()

    conn = connect_raw(args.db, args.auth_token)

    if args.set_admin_password:
        password = getpass.getpass("Nueva contraseña de administrador: ")
        set_admin_password(conn, hash_secret(password))
        print("Contraseña de administrador actualizada.")

    if args.add_member:
        member_code, name, email, join_date, pin = args.add_member
        add_member(conn, member_code, name, email, hash_secret(pin), join_date)
        print(f"Miembro {member_code} ({name}, {email}) agregado.")

    conn.close()


if __name__ == "__main__":
    main()
