"""Bloque A - Parametros Regulatorios y de Producto."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class RegulatoryParams2026:
    """Valores certificados 2026 - Master Doc v5.1."""
    uvt: Decimal = Decimal("52374")
    gmf_exencion_uvt: int = 350
    gmf_tasa: Decimal = Decimal("0.004")
    retefuente_ahorro: Decimal = Decimal("0.07")
    retefuente_cdt: Decimal = Decimal("0.04")
    tasa_usura_ea: Decimal = Decimal("0.2676")
    ibc_ea: Decimal = Decimal("0.1784")
    ipc_proyectado: Decimal = Decimal("0.0517")

    @property
    def gmf_umbral_exento_cop(self) -> Decimal:
        return self.uvt * self.gmf_exencion_uvt


@dataclass(frozen=True)
class PilotParams:
    """Piloto Nivel Raices - Contrato v2.4."""
    aporte_mensual: Decimal = Decimal("100000")
    dia_limite_pago: int = 5
    miembros_min: int = 8
    miembros_max: int = 12
    reserva_min_pct: Decimal = Decimal("0.10")
    reserva_rebalanceo_pct: Decimal = Decimal("0.12")
    tasa_liquida_ea: Decimal = Decimal("0.105")
    tasa_cdt_ea: Decimal = Decimal("0.12")
    liquidacion_tramo1: date = date(2026, 11, 19)
    liquidacion_tramo2: date = date(2026, 12, 10)
