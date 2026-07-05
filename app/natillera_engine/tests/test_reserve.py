from decimal import Decimal

from natillera_engine.reserve import evaluar_reserva, ZonaReserva


def test_reserva_alerta():
    fondo_total = Decimal("10000000")
    liquido = fondo_total * Decimal("0.09")
    resultado = evaluar_reserva(liquido, fondo_total)
    assert resultado["zona"] == ZonaReserva.ALERTA
    objetivo = Decimal("0.12") * fondo_total
    assert liquido + resultado["monto_a_liquidar_de_cdt"] == objetivo


def test_reserva_confort():
    fondo_total = Decimal("10000000")
    liquido = fondo_total * Decimal("0.15")
    resultado = evaluar_reserva(liquido, fondo_total)
    assert resultado["zona"] == ZonaReserva.CONFORT
    assert resultado["monto_a_liquidar_de_cdt"] == Decimal("0")
