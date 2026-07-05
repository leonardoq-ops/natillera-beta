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
