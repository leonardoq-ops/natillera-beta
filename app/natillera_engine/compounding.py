"""Bloque C - Interes Compuesto Diario."""
from decimal import Decimal, getcontext, ROUND_HALF_UP
from datetime import date

getcontext().prec = 28


def tasa_diaria(ea: Decimal) -> Decimal:
    return ((Decimal(1) + ea) ** (Decimal(1) / Decimal(365))) - Decimal(1)


def rendimiento_aporte(fecha: date, monto: Decimal, fecha_corte: date, ea: Decimal) -> Decimal:
    dias = (fecha_corte - fecha).days
    if dias <= 0:
        return Decimal("0")
    td = tasa_diaria(ea)
    bruto = monto * (((Decimal(1) + td) ** dias) - Decimal(1))
    return bruto.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
