"""Bloque B - Ledger Inmutable (SHA-256)."""
import hashlib
import json
from dataclasses import dataclass, asdict
from decimal import Decimal
from datetime import datetime, timezone
from enum import Enum


class EventType(str, Enum):
    APORTE = "APORTE"
    RENDIMIENTO = "RENDIMIENTO"
    RETIRO_ANTICIPADO = "RETIRO_ANTICIPADO"
    RETIRO_FORZOSO = "RETIRO_FORZOSO"
    REBALANCEO = "REBALANCEO"
    MORA = "MORA"
    REGULARIZACION = "REGULARIZACION"
    LIQUIDACION = "LIQUIDACION"
    VERIFICACION = "VERIFICACION"


@dataclass(frozen=True)
class LedgerEntry:
    seq: int
    timestamp_utc: str
    event: EventType
    member_code: str
    amount_cop: str
    detail: dict
    prev_hash: str
    hash: str = ""


def compute_entry_hash(payload: dict) -> str:
    """Canonical hash used both by the in-memory Ledger and the DB-backed store."""
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# Kept for spec fidelity - internal callers should prefer compute_entry_hash.
_compute_hash = compute_entry_hash


class Ledger:
    GENESIS = "0" * 64

    def __init__(self):
        self.entries: list[LedgerEntry] = []

    def append(self, event: EventType, member_code: str,
               amount: Decimal, detail: dict | None = None) -> LedgerEntry:
        prev = self.entries[-1].hash if self.entries else self.GENESIS
        payload = {
            "seq": len(self.entries),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "event": event.value,
            "member_code": member_code,
            "amount_cop": str(amount),
            "detail": detail or {},
            "prev_hash": prev,
        }
        entry = LedgerEntry(**{**payload, "event": event,
                               "hash": compute_entry_hash(payload)})
        self.entries.append(entry)
        return entry

    def verify_chain(self) -> bool:
        prev = self.GENESIS
        for e in self.entries:
            payload = asdict(e)
            payload.pop("hash")
            payload["event"] = e.event.value
            if e.prev_hash != prev or compute_entry_hash(payload) != e.hash:
                return False
            prev = e.hash
        return True
