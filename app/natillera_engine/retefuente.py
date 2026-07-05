"""Bloque E - Retefuente Diferenciada."""
from decimal import Decimal, ROUND_HALF_UP


def retefuente(rend_liquida: Decimal, rend_cdt: Decimal) -> dict:
    rf_liq = (rend_liquida * Decimal("0.07")).quantize(Decimal("1"), ROUND_HALF_UP)
    rf_cdt = (rend_cdt * Decimal("0.04")).quantize(Decimal("1"), ROUND_HALF_UP)
    return {"rf_ahorro": rf_liq, "rf_cdt": rf_cdt, "rf_total": rf_liq + rf_cdt}
