"""Bloque K - Validadores (Reducido, sin creditos).

v1.1: Natillera Digital no es una entidad bancaria ni de credito
(Decreto 1981/1988). Solo 2 validadores - no reintroducir ninguna
funcion de credito/prestamo interno.
"""
from decimal import Decimal


def validar_tamano_grupo(n: int, min_: int = 8, max_: int = 12) -> dict:
    """Clausula Tercera.4: 8-12 miembros."""
    valido = min_ <= n <= max_
    return {"valido": valido,
            "mensaje": None if valido else
            f"Grupo fuera de rango {min_}-{max_}: {n} miembros"}


def validar_tasa_interna(tasa_ea: Decimal, usura_ea: Decimal) -> dict:
    """CRITICO: tasa interna nunca debe igualar o exceder la usura.
    Usura 2026: 26.76% E.A."""
    ok = tasa_ea < usura_ea
    return {"valida": ok,
            "mensaje": None if ok else
            f"BLOQUEO LEGAL: tasa {tasa_ea} >= usura {usura_ea}. Operacion prohibida."}
