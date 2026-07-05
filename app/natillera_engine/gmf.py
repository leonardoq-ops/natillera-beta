"""Bloque D - GMF (4x1000) con Exencion."""
from decimal import Decimal, ROUND_HALF_UP


def gmf_movimiento(monto_retiro: Decimal, retirado_mes_acumulado: Decimal,
                    umbral: Decimal) -> Decimal:
    exento_restante = max(Decimal("0"), umbral - retirado_mes_acumulado)
    gravado = max(Decimal("0"), monto_retiro - exento_restante)
    return (gravado * Decimal("0.004")).quantize(Decimal("1"), ROUND_HALF_UP)


def plan_liquidacion_bimestral(fondo_total: Decimal, umbral: Decimal) -> dict:
    tramo1 = min(fondo_total, umbral)
    tramo2 = fondo_total - tramo1
    gmf_t1 = gmf_movimiento(tramo1, Decimal("0"), umbral)
    gmf_t2 = gmf_movimiento(tramo2, Decimal("0"), umbral)
    return {"tramo_noviembre": tramo1, "tramo_diciembre": tramo2,
            "gmf_total": gmf_t1 + gmf_t2,
            "estrategia_valida": (gmf_t1 + gmf_t2) == 0}
