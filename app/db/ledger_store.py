"""SQL-backed ledger, mirroring natillera_engine.ledger.Ledger's interface
but durable across restarts. Reuses the exact same hash function so
integrity checking is identical to the in-memory reference algorithm.
"""
import json
from datetime import datetime, timezone
from decimal import Decimal

from natillera_engine.ledger import EventType, LedgerEntry, Ledger, compute_entry_hash

GENESIS = Ledger.GENESIS


class LedgerTamperedError(Exception):
    pass


class DbLedger:
    def __init__(self, conn):
        self.conn = conn

    def _last_hash(self) -> str:
        cur = self.conn.cursor()
        cur.execute("SELECT hash FROM ledger_entries ORDER BY seq DESC LIMIT 1")
        row = cur.fetchone()
        return row[0] if row else GENESIS

    def _next_seq(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM ledger_entries")
        return cur.fetchone()[0]

    def append(self, event: EventType, member_code: str,
               amount: Decimal, detail: dict | None = None) -> LedgerEntry:
        seq = self._next_seq()
        prev_hash = self._last_hash()
        payload = {
            "seq": seq,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "event": event.value,
            "member_code": member_code,
            "amount_cop": str(amount),
            "detail": detail or {},
            "prev_hash": prev_hash,
        }
        entry_hash = compute_entry_hash(payload)

        cur = self.conn.cursor()
        cur.execute(
            """INSERT INTO ledger_entries
               (seq, timestamp_utc, event, member_code, amount_cop, detail_json, prev_hash, hash)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                seq,
                payload["timestamp_utc"],
                payload["event"],
                payload["member_code"],
                payload["amount_cop"],
                json.dumps(payload["detail"], sort_keys=True, ensure_ascii=False),
                prev_hash,
                entry_hash,
            ),
        )
        self.conn.commit()

        return LedgerEntry(
            seq=seq,
            timestamp_utc=payload["timestamp_utc"],
            event=event,
            member_code=member_code,
            amount_cop=payload["amount_cop"],
            detail=payload["detail"],
            prev_hash=prev_hash,
            hash=entry_hash,
        )

    def verify_chain(self) -> tuple[bool, int | None]:
        """Returns (is_valid, first_bad_seq_or_None)."""
        cur = self.conn.cursor()
        cur.execute(
            """SELECT seq, timestamp_utc, event, member_code, amount_cop,
                      detail_json, prev_hash, hash
               FROM ledger_entries ORDER BY seq ASC"""
        )
        prev = GENESIS
        for row in cur.fetchall():
            seq, timestamp_utc, event, member_code, amount_cop, detail_json, prev_hash, hash_ = row
            payload = {
                "seq": seq,
                "timestamp_utc": timestamp_utc,
                "event": event,
                "member_code": member_code,
                "amount_cop": amount_cop,
                "detail": json.loads(detail_json),
                "prev_hash": prev_hash,
            }
            if prev_hash != prev or compute_entry_hash(payload) != hash_:
                return False, seq
            prev = hash_
        return True, None

    def all_entries(self) -> list[dict]:
        """Each row includes both `detail_json` (raw, for display/audit) and
        `detail` (parsed dict, for callers that need to read fields like
        detail["status"])."""
        cur = self.conn.cursor()
        cur.execute(
            """SELECT seq, timestamp_utc, event, member_code, amount_cop, detail_json, prev_hash, hash
               FROM ledger_entries ORDER BY seq ASC"""
        )
        cols = ["seq", "timestamp_utc", "event", "member_code", "amount_cop", "detail_json", "prev_hash", "hash"]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        for row in rows:
            row["detail"] = json.loads(row["detail_json"])
        return rows
