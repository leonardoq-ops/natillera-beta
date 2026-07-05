from decimal import Decimal

from natillera_engine.config import RegulatoryParams2026
from natillera_engine.gmf import gmf_movimiento


UMBRAL = RegulatoryParams2026().gmf_umbral_exento_cop  # 18,330,900


def test_gmf_cero_bajo_umbral():
    assert UMBRAL == Decimal("18330900")
    gmf = gmf_movimiento(UMBRAL, Decimal("0"), UMBRAL)
    assert gmf == Decimal("0")


def test_gmf_positivo_sobre_umbral():
    gmf = gmf_movimiento(UMBRAL + Decimal("1000"), Decimal("0"), UMBRAL)
    assert gmf == Decimal("4")
