from datetime import date
from decimal import Decimal

from natillera_engine.compounding import rendimiento_aporte


def test_compounding_orden():
    """Aporte enero rinde mas que aporte identico de junio, al mismo corte."""
    monto = Decimal("100000")
    ea = Decimal("0.105")
    corte = date(2026, 12, 10)

    rend_enero = rendimiento_aporte(date(2026, 1, 5), monto, corte, ea)
    rend_junio = rendimiento_aporte(date(2026, 6, 5), monto, corte, ea)

    assert rend_enero > rend_junio


def test_compounding_dias_no_positivos_es_cero():
    monto = Decimal("100000")
    ea = Decimal("0.105")
    corte = date(2026, 1, 1)
    assert rendimiento_aporte(date(2026, 1, 5), monto, corte, ea) == Decimal("0")
