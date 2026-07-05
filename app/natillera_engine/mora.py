"""Bloque H - Protocolo de Mora."""
from datetime import date
from enum import Enum


class EstadoPago(str, Enum):
    VIVA = "VIVA"
    NIEBLA_AUTO = "NIEBLA_AUTO"
    NIEBLA_COMUNICADA = "NIEBLA_COMUNICADA"
    NOTIFICADO_GRUPO = "NOTIFICADO_GRUPO"
    PLAN_PAGO = "PLAN_PAGO"
    RETIRO_FORZOSO = "RETIRO_FORZOSO"


def estado_mora(fecha_limite: date, hoy: date, pago_realizado: bool,
                 comunico_en_gracia: bool, acuerdo_escrito: bool) -> EstadoPago:
    if pago_realizado:
        return EstadoPago.VIVA
    dias_mora = (hoy - fecha_limite).days
    if dias_mora <= 0:
        return EstadoPago.VIVA
    if acuerdo_escrito:
        return EstadoPago.PLAN_PAGO
    if dias_mora >= 30:
        return EstadoPago.RETIRO_FORZOSO
    if dias_mora >= 15:
        return EstadoPago.NOTIFICADO_GRUPO
    if 1 <= dias_mora <= 9 and comunico_en_gracia:
        return EstadoPago.NIEBLA_COMUNICADA
    return EstadoPago.NIEBLA_AUTO
