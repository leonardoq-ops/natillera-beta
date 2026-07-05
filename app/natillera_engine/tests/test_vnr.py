from decimal import Decimal

from natillera_engine.vnr import liquidacion_grupo


def test_vnr_suma_exacta():
    capitales = {
        "M01": Decimal("1000000"),
        "M02": Decimal("2500000"),
        "M03": Decimal("750000"),
    }
    rg, gmfg, rfg = Decimal("300000"), Decimal("12000"), Decimal("21000")
    resultados = liquidacion_grupo(capitales, rg, gmfg, rfg)
    cg = sum(capitales.values())
    total_vnr = sum(r["vnr"] for r in resultados.values())
    assert total_vnr == cg + rg - gmfg - rfg


def test_capital_protegido():
    capitales = {
        "M01": Decimal("1000000"),
        "M02": Decimal("2500000"),
        "M03": Decimal("750000"),
    }
    rg, gmfg, rfg = Decimal("300000"), Decimal("12000"), Decimal("21000")
    assert gmfg + rfg <= rg
    resultados = liquidacion_grupo(capitales, rg, gmfg, rfg)
    for code, ci in capitales.items():
        assert resultados[code]["vnr"] >= ci
