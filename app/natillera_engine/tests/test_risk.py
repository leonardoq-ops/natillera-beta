from decimal import Decimal

from natillera_engine.config import RegulatoryParams2026
from natillera_engine.risk import validar_tamano_grupo, validar_tasa_interna


USURA = RegulatoryParams2026().tasa_usura_ea


def test_usura_bloqueo():
    resultado = validar_tasa_interna(Decimal("0.27"), USURA)
    assert resultado["valida"] is False


def test_usura_permitida_bajo_umbral():
    resultado = validar_tasa_interna(Decimal("0.105"), USURA)
    assert resultado["valida"] is True


def test_tamano_grupo_limites():
    assert validar_tamano_grupo(7)["valido"] is False
    assert validar_tamano_grupo(8)["valido"] is True
    assert validar_tamano_grupo(12)["valido"] is True
    assert validar_tamano_grupo(13)["valido"] is False
