"""Bloque I - Reserva y Rebalanceo."""
from decimal import Decimal
from enum import Enum


class ZonaReserva(str, Enum):
    CONFORT = "CONFORT"
    OBSERVACION = "OBSERVACION"
    ALERTA = "ALERTA"


def evaluar_reserva(liquido: Decimal, fondo_total: Decimal) -> dict:
    pct = liquido / fondo_total if fondo_total else Decimal("0")
    if pct < Decimal("0.10"):
        zona, accion = ZonaReserva.ALERTA, "REBALANCEO_OBLIGATORIO_5_DIAS_HABILES"
        monto_a_liquidar = (Decimal("0.12") * fondo_total) - liquido
    elif pct < Decimal("0.12"):
        zona, accion, monto_a_liquidar = ZonaReserva.OBSERVACION, "MONITOREAR", Decimal("0")
    else:
        zona, accion, monto_a_liquidar = ZonaReserva.CONFORT, "NINGUNA", Decimal("0")
    return {"pct_reserva": pct, "zona": zona, "accion": accion,
            "monto_a_liquidar_de_cdt": max(Decimal("0"), monto_a_liquidar)}
