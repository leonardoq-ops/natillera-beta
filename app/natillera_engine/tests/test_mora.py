from datetime import date

from natillera_engine.mora import estado_mora, EstadoPago


LIMITE = date(2026, 7, 5)


def test_mora_transiciones():
    # dia 6 (uncommunicated) -> Niebla Auto
    assert estado_mora(LIMITE, date(2026, 7, 11), False, False, False) == EstadoPago.NIEBLA_AUTO
    # dia 7, comunico en gracia -> Niebla Comunicada
    assert estado_mora(LIMITE, date(2026, 7, 12), False, True, False) == EstadoPago.NIEBLA_COMUNICADA
    # dia 15 -> Notificado al grupo
    assert estado_mora(LIMITE, date(2026, 7, 20), False, False, False) == EstadoPago.NOTIFICADO_GRUPO
    # dia 30 -> Retiro forzoso
    assert estado_mora(LIMITE, date(2026, 8, 4), False, False, False) == EstadoPago.RETIRO_FORZOSO
    # acuerdo escrito siempre gana -> Plan de pago
    assert estado_mora(LIMITE, date(2026, 8, 4), False, False, True) == EstadoPago.PLAN_PAGO
    # pago realizado -> Viva
    assert estado_mora(LIMITE, date(2026, 7, 20), True, False, False) == EstadoPago.VIVA
