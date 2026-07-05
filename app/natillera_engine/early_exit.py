"""Bloque G - Retiro Anticipado (Clausula Octava)."""
from decimal import Decimal

from .config import RegulatoryParams2026


def retiro_anticipado(capital: Decimal, rendimientos: Decimal,
                       costo_transferencia: Decimal,
                       retirado_mes_fondo: Decimal,
                       gmf_tasa: Decimal = Decimal("0.004")) -> dict:
    # Umbral parametrizado (350 UVT) en vez de literal hardcodeado - mismo valor.
    gmf_umbral = RegulatoryParams2026().gmf_umbral_exento_cop
    exento = max(Decimal("0"), gmf_umbral - retirado_mes_fondo)
    gravado = max(Decimal("0"), capital - exento)
    gmf = (gravado * gmf_tasa).quantize(Decimal("1"))
    a_devolver = capital - gmf - costo_transferencia
    return {
        "capital": capital,
        "gmf_descuento": gmf,
        "costo_transferencia": costo_transferencia,
        "a_devolver": max(Decimal("0"), a_devolver),
        "rendimientos_al_colectivo": rendimientos,
        "aviso_previo_dias": 30,
    }
