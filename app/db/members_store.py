"""CRUD for members and admin auth rows."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Member:
    member_code: str
    name: str
    email: str
    access_hash: str
    join_date: str
    is_active: bool


def add_member(conn, member_code: str, name: str, email: str,
               access_hash: str, join_date: str) -> None:
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO members (member_code, name, email, access_hash, join_date)
           VALUES (?, ?, ?, ?, ?)""",
        (member_code, name, email, access_hash, join_date),
    )
    conn.commit()


def get_member_by_email(conn, email: str) -> Member | None:
    cur = conn.cursor()
    cur.execute(
        """SELECT member_code, name, email, access_hash, join_date, is_active
           FROM members WHERE email = ? AND is_active = 1""",
        (email,),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return Member(
        member_code=row[0], name=row[1], email=row[2],
        access_hash=row[3], join_date=row[4], is_active=bool(row[5]),
    )


def list_members(conn) -> list[Member]:
    cur = conn.cursor()
    cur.execute(
        """SELECT member_code, name, email, access_hash, join_date, is_active
           FROM members ORDER BY member_code ASC"""
    )
    return [
        Member(member_code=r[0], name=r[1], email=r[2], access_hash=r[3],
               join_date=r[4], is_active=bool(r[5]))
        for r in cur.fetchall()
    ]


def set_admin_password(conn, password_hash: str) -> None:
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO admin_auth (id, password_hash) VALUES (1, ?)
           ON CONFLICT(id) DO UPDATE SET password_hash = excluded.password_hash""",
        (password_hash,),
    )
    conn.commit()


def get_admin_password_hash(conn) -> str | None:
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM admin_auth WHERE id = 1")
    row = cur.fetchone()
    return row[0] if row else None
