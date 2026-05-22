import pytest
from backend.application.orchestrator import Orchestrator


# ─────────────────────────────────────────────────────────────────
# TEST DOUBLES
#
# StubMotorSemantico → Stub: siempre devuelve resultado fijo.
#   No importa cómo ni cuántas veces se llame.
#
# StubMotorSemanticoConError → Stub que siempre lanza TimeoutError.
#   Simula fallo del motor semántico para probar RF-03.
#
# FakeMotorLexico → Fake: filtra de verdad sobre lista en memoria.
#   Cada test crea uno nuevo → empieza limpio.
# ─────────────────────────────────────────────────────────────────


class StubMotorSemantico:
    def buscar(self, query: str):
        return [{"title": "Yellow", "artist": "Coldplay", "score": 0.91}]


class StubMotorSemanticoConError:
    def buscar(self, query: str):
        raise TimeoutError("Motor semántico no respondió en 150 ms")


class FakeMotorLexico:
    def __init__(self):
        self._catalogo = [
            {"title": "Yellow",       "artist": "Coldplay"},
            {"title": "Fix You",      "artist": "Coldplay"},
            {"title": "The Scientist","artist": "Coldplay"},
        ]

    def buscar(self, query: str):
        q = query.lower()
        return [c for c in self._catalogo
                if q in c["title"].lower() or q in c["artist"].lower()]


# ── RF-02 ──────────────────────────────────────────────────────────

def test_deberia_retornar_resultados_cuando_query_coincide_con_artista_exacto():
    # GIVEN
    orquestador = Orchestrator(
        motor_lexico=FakeMotorLexico(),
        motor_semantico=StubMotorSemantico()
    )

    # WHEN
    resultados = orquestador.buscar("coldplay")

    # THEN
    assert len(resultados) > 0
    assert all(r["artist"] == "Coldplay" for r in resultados)


def test_deberia_retornar_lista_vacia_cuando_artista_no_existe():
    # GIVEN
    orquestador = Orchestrator(
        motor_lexico=FakeMotorLexico(),
        motor_semantico=StubMotorSemantico()
    )

    # WHEN
    resultados = orquestador.buscar("xkzqwmvp99999")

    # THEN
    assert resultados == []


# ── RF-03 ──────────────────────────────────────────────────────────

def test_deberia_activar_fallback_cuando_motor_semantico_lanza_timeout():
    # GIVEN
    orquestador = Orchestrator(
        motor_lexico=FakeMotorLexico(),
        motor_semantico=StubMotorSemanticoConError()
    )

    # WHEN — query larga para que llegue al motor semántico
    resultados = orquestador.buscar("música para estudiar concentrado")

    # THEN
    assert isinstance(resultados, list)
    assert orquestador.fallback_activado is True


def test_deberia_no_propagar_excepcion_cuando_motor_semantico_falla():
    # GIVEN
    orquestador = Orchestrator(
        motor_lexico=FakeMotorLexico(),
        motor_semantico=StubMotorSemanticoConError()
    )

    # WHEN / THEN
    try:
        orquestador.buscar("canciones para trabajar en casa")
    except Exception:
        pytest.fail("El orquestador propagó una excepción que no debe llegar al cliente")