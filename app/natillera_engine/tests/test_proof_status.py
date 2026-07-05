from natillera_engine.proof_status import EstadoVerificacion, estado_verificacion_actual


def test_sin_entradas_es_ninguno():
    assert estado_verificacion_actual([]) == EstadoVerificacion.NINGUNO


def test_aporte_pendiente():
    entries = [
        {"seq": 0, "event": "APORTE", "detail": {"status": "PENDIENTE_VERIFICACION"}},
    ]
    assert estado_verificacion_actual(entries) == EstadoVerificacion.PENDIENTE_VERIFICACION


def test_aporte_manual_es_verificado_por_defecto():
    entries = [
        {"seq": 0, "event": "APORTE", "detail": {"status": "VERIFICADO"}},
    ]
    assert estado_verificacion_actual(entries) == EstadoVerificacion.VERIFICADO


def test_verificacion_sobreescribe_aporte_pendiente():
    entries = [
        {"seq": 0, "event": "APORTE", "detail": {"status": "PENDIENTE_VERIFICACION"}},
        {"seq": 1, "event": "VERIFICACION", "detail": {"accion": "VERIFICADO"}},
    ]
    assert estado_verificacion_actual(entries) == EstadoVerificacion.VERIFICADO


def test_rechazo_sobreescribe_aporte_pendiente():
    entries = [
        {"seq": 0, "event": "APORTE", "detail": {"status": "PENDIENTE_VERIFICACION"}},
        {"seq": 1, "event": "VERIFICACION", "detail": {"accion": "RECHAZADO"}},
    ]
    assert estado_verificacion_actual(entries) == EstadoVerificacion.RECHAZADO


def test_orden_no_importa_se_usa_seq():
    entries = [
        {"seq": 1, "event": "VERIFICACION", "detail": {"accion": "VERIFICADO"}},
        {"seq": 0, "event": "APORTE", "detail": {"status": "PENDIENTE_VERIFICACION"}},
    ]
    assert estado_verificacion_actual(entries) == EstadoVerificacion.VERIFICADO
