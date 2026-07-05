import os
import tempfile
from decimal import Decimal

import pytest

from natillera_engine.ledger import EventType
from db.client import connect_raw
from db.ledger_store import DbLedger


@pytest.fixture
def conn():
    path = os.path.join(tempfile.gettempdir(), "test_natillera_ledger.db")
    if os.path.exists(path):
        os.remove(path)
    c = connect_raw(path)
    yield c
    c.close()
    if os.path.exists(path):
        os.remove(path)


def test_db_ledger_verify_chain_true_before_tampering(conn):
    ledger = DbLedger(conn)
    ledger.append(EventType.APORTE, "M01", Decimal("100000"), {"nota": "aporte 1"})
    ledger.append(EventType.APORTE, "M02", Decimal("100000"), {"nota": "aporte 2"})

    ok, bad_seq = ledger.verify_chain()
    assert ok is True
    assert bad_seq is None


def test_db_ledger_tamper_detection_if_triggers_bypassed(conn):
    """The append-only triggers are the first line of defense (see the two
    tests below), but verify_chain()'s hash-chain must independently catch
    tampering even in a scenario where the triggers were bypassed/dropped
    (e.g. direct file-level access)."""
    ledger = DbLedger(conn)
    ledger.append(EventType.APORTE, "M01", Decimal("100000"), {"nota": "aporte 1"})
    ledger.append(EventType.APORTE, "M02", Decimal("100000"), {"nota": "aporte 2"})

    cur = conn.cursor()
    cur.execute("DROP TRIGGER forbid_ledger_update")
    cur.execute("UPDATE ledger_entries SET amount_cop = ? WHERE seq = 0", ("999999999",))
    conn.commit()

    ok, bad_seq = ledger.verify_chain()
    assert ok is False
    assert bad_seq == 0


def test_append_only_triggers_reject_update(conn):
    ledger = DbLedger(conn)
    ledger.append(EventType.APORTE, "M01", Decimal("100000"), {})

    cur = conn.cursor()
    with pytest.raises(Exception):
        cur.execute("UPDATE ledger_entries SET amount_cop = ? WHERE seq = 0", ("1",))


def test_append_only_triggers_reject_delete(conn):
    ledger = DbLedger(conn)
    ledger.append(EventType.APORTE, "M01", Decimal("100000"), {})

    cur = conn.cursor()
    with pytest.raises(Exception):
        cur.execute("DELETE FROM ledger_entries WHERE seq = 0")
