"""Central Spanish terminology per CALC_ENGINE_SPEC instruction 6.

Every page must pull labels from here rather than hardcoding its own
wording, so terms like "Niebla"/"Viva" never drift between pages.
"""
from natillera_engine.mora import EstadoPago

ESTADO_LABEL = {
    EstadoPago.VIVA: "Viva",
    EstadoPago.NIEBLA_AUTO: "Niebla",
    EstadoPago.NIEBLA_COMUNICADA: "Niebla (comunicada)",
    EstadoPago.NOTIFICADO_GRUPO: "Niebla — notificado al grupo",
    EstadoPago.PLAN_PAGO: "Plan de pago",
    EstadoPago.RETIRO_FORZOSO: "Retiro forzoso",
}

ESTADO_COLOR = {
    EstadoPago.VIVA: "green",
    EstadoPago.NIEBLA_AUTO: "orange",
    EstadoPago.NIEBLA_COMUNICADA: "orange",
    EstadoPago.NOTIFICADO_GRUPO: "red",
    EstadoPago.PLAN_PAGO: "blue",
    EstadoPago.RETIRO_FORZOSO: "red",
}

THE_NUMBER_LABEL = "THE NUMBER"
LA_COSECHA_LABEL = "La Cosecha"
HUELLA_LABEL = "Huella Financiera"
