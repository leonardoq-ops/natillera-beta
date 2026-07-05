"""Bloque F - VNR: Distribucion de La Cosecha."""
from decimal import Decimal, ROUND_HALF_UP


def liquidacion_grupo(capitales: dict[str, Decimal], rg: Decimal,
                       gmfg: Decimal, rfg: Decimal) -> dict[str, dict]:
    cg = sum(capitales.values())
    if cg == 0:
        raise ValueError("Capital total del grupo es cero")
    neto_grupo = cg + rg - gmfg - rfg
    resultados, acumulado = {}, Decimal("0")
    items = list(capitales.items())
    for i, (code, ci) in enumerate(items):
        prop = ci / cg
        if i < len(items) - 1:
            vnr = (ci + (rg - gmfg - rfg) * prop).quantize(Decimal("1"), ROUND_HALF_UP)
        else:
            vnr = neto_grupo - acumulado
        acumulado += vnr
        resultados[code] = {
            "capital": ci,
            "rendimiento_asignado": (rg * prop).quantize(Decimal("1"), ROUND_HALF_UP),
            "gmf_asignado": (gmfg * prop).quantize(Decimal("1"), ROUND_HALF_UP),
            "retefuente_asignada": (rfg * prop).quantize(Decimal("1"), ROUND_HALF_UP),
            "vnr": vnr,
        }
    return resultados
