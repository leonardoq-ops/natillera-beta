from dataclasses import replace
from decimal import Decimal

from natillera_engine.ledger import Ledger, EventType


def test_ledger_integridad():
    ledger = Ledger()
    ledger.append(EventType.APORTE, "M01", Decimal("100000"), {"nota": "primer aporte"})
    ledger.append(EventType.APORTE, "M02", Decimal("100000"), {"nota": "segundo aporte"})
    assert ledger.verify_chain() is True

    tampered = replace(ledger.entries[0], amount_cop="999999999")
    ledger.entries[0] = tampered
    assert ledger.verify_chain() is False


def test_verificacion_event_chains_correctly():
    ledger = Ledger()
    aporte = ledger.append(EventType.APORTE, "M01", Decimal("100000"),
                            {"month": "2026-07", "status": "PENDIENTE_VERIFICACION"})
    ledger.append(EventType.VERIFICACION, "M01", Decimal("0"),
                  {"month": "2026-07", "accion": "VERIFICADO",
                   "ledger_hash_referenciado": aporte.hash})
    assert ledger.verify_chain() is True
