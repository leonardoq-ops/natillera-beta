"""Bloque J - Huella Financiera."""
from decimal import Decimal

PESOS = {
    "consistencia_pago": Decimal("0.50"),
    "antiguedad": Decimal("0.20"),
    "historial_nivel": Decimal("0.15"),
    "participacion_grupal": Decimal("0.10"),
    "respuesta_dificultad": Decimal("0.05"),
}


def huella(componentes: dict[str, Decimal]) -> Decimal:
    assert set(componentes) == set(PESOS), "Faltan componentes"
    return sum(componentes[k] * PESOS[k] for k in PESOS).quantize(Decimal("0.1"))


def consistencia_pago(pagos_a_tiempo: int, meses_transcurridos: int) -> Decimal:
    if meses_transcurridos == 0:
        return Decimal("100")
    return (Decimal(pagos_a_tiempo) / Decimal(meses_transcurridos) * 100).quantize(Decimal("0.1"))
