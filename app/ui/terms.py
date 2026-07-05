"""Central Spanish terminology per CALC_ENGINE_SPEC instruction 6.

Every page must pull labels from here rather than hardcoding its own
wording, so terms like "Niebla"/"Viva" never drift between pages.
"""
from natillera_engine.mora import EstadoPago
from natillera_engine.proof_status import EstadoVerificacion

ESTADO_LABEL = {
    EstadoPago.VIVA: "Viva",
    EstadoPago.NIEBLA_AUTO: "Niebla",
    EstadoPago.NIEBLA_COMUNICADA: "Niebla (comunicada)",
    EstadoPago.NOTIFICADO_GRUPO: "Niebla — notificado al grupo",
    EstadoPago.PLAN_PAGO: "Plan de pago",
    EstadoPago.RETIRO_FORZOSO: "Retiro forzoso",
}

VERIFICACION_LABEL = {
    EstadoVerificacion.NINGUNO: "Sin comprobante",
    EstadoVerificacion.PENDIENTE_VERIFICACION: "Pendiente de verificación",
    EstadoVerificacion.VERIFICADO: "Verificado",
    EstadoVerificacion.RECHAZADO: "Rechazado",
}

# Maps both enums to the badge CSS classes in ui/theme.py (Aesthetics Guide
# palette) - estado_badge() in ui/components.py is polymorphic over both.
BADGE_CLASS = {
    EstadoPago.VIVA: "nat-badge-teal",
    EstadoPago.NIEBLA_AUTO: "nat-badge-red",
    EstadoPago.NIEBLA_COMUNICADA: "nat-badge-red",
    EstadoPago.NOTIFICADO_GRUPO: "nat-badge-red",
    EstadoPago.PLAN_PAGO: "nat-badge-teal",
    EstadoPago.RETIRO_FORZOSO: "nat-badge-red",
    EstadoVerificacion.NINGUNO: "nat-badge-teal",
    EstadoVerificacion.PENDIENTE_VERIFICACION: "nat-badge-teal",
    EstadoVerificacion.VERIFICADO: "nat-badge-green",
    EstadoVerificacion.RECHAZADO: "nat-badge-red",
}

THE_NUMBER_LABEL = "THE NUMBER"
LA_COSECHA_LABEL = "La Cosecha"
HUELLA_LABEL = "Huella Financiera"
