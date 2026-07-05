"""Estado de Verificacion de Comprobantes (derivado del ledger).

A member can be VIVA (paid on time, per mora.py) and simultaneously
PENDIENTE_VERIFICACION (proof not yet reviewed) - these are different
axes, so this enum is kept separate from mora.EstadoPago rather than
folded into it.
"""
from enum import Enum


class EstadoVerificacion(str, Enum):
    NINGUNO = "NINGUNO"
    PENDIENTE_VERIFICACION = "PENDIENTE_VERIFICACION"
    VERIFICADO = "VERIFICADO"
    RECHAZADO = "RECHAZADO"


def estado_verificacion_actual(entries_member_month: list[dict]) -> EstadoVerificacion:
    """entries_member_month: ledger entries (dicts, as returned by
    DbLedger.all_entries()) already filtered to one member_code + one
    month, in any order. A later VERIFICACION entry's `accion` overrides
    the originating APORTE entry's `status`.
    """
    latest_status = None
    for e in sorted(entries_member_month, key=lambda x: x["seq"]):
        if e["event"] == "APORTE":
            latest_status = e["detail"].get("status", "VERIFICADO")
        elif e["event"] == "VERIFICACION":
            latest_status = e["detail"].get("accion")
    return EstadoVerificacion(latest_status) if latest_status else EstadoVerificacion.NINGUNO
