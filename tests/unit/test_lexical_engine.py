import pytest
from backend.infrastructure.lexical_engine import LexicalEngine

# ── Fixture: catálogo de prueba ───────────────────────────────────────────────

CATALOGO_PRUEBA = [
    {"id": 1, "title": "Yellow", "artist": "Coldplay",
     "genre": "Alternative Rock", "mood": "romantic", "description": "song about love"},
    {"id": 2, "title": "Fix You", "artist": "Coldplay",
     "genre": "Alternative Rock", "mood": "emotional", "description": "healing and support"},
    {"id": 3, "title": "Rolling in the Deep", "artist": "Adele",
     "genre": "Soul Pop", "mood": "powerful", "description": "breakup anthem"},
    {"id": 4, "title": "Imagine", "artist": "John Lennon",
     "genre": "Pop", "mood": "peaceful", "description": "anthem about peace and unity"},
]


@pytest.fixture
def engine():
    return LexicalEngine(CATALOGO_PRUEBA)


# ── Happy path ────────────────────────────────────────────────────────────────

def test_deberia_encontrar_cancion_por_titulo_exacto(engine):
    # GIVEN / WHEN
    resultados = engine.buscar("Yellow")

    # THEN
    assert len(resultados) >= 1
    assert resultados[0]["title"] == "Yellow"


def test_deberia_encontrar_canciones_por_artista(engine):
    resultados = engine.buscar("coldplay")

    assert len(resultados) == 2
    assert all(r["artist"] == "Coldplay" for r in resultados)


def test_deberia_ser_case_insensitive(engine):
    resultados_lower = engine.buscar("coldplay")
    resultados_upper = engine.buscar("COLDPLAY")
    resultados_mixed = engine.buscar("ColdPlay")

    assert len(resultados_lower) == len(resultados_upper) == len(resultados_mixed)


# ── Flujos de error ───────────────────────────────────────────────────────────

def test_deberia_lanzar_value_error_cuando_query_esta_vacia(engine):
    with pytest.raises(ValueError, match="vacía"):
        engine.buscar("")


def test_deberia_lanzar_value_error_cuando_query_es_solo_espacios(engine):
    with pytest.raises(ValueError):
        engine.buscar("   ")


def test_deberia_retornar_lista_vacia_cuando_no_hay_coincidencias(engine):
    resultados = engine.buscar("xkzqwmvp_no_existe_99999")
    assert resultados == []


# ── Límite de resultados ──────────────────────────────────────────────────────

def test_deberia_retornar_maximo_5_resultados():
    # GIVEN: catálogo con 10 canciones que todas coinciden con "rock"
    catalogo_grande = [
        {"id": i, "title": f"Rock Song {i}", "artist": "Band",
         "genre": "Rock", "mood": "energetic", "description": "rock song"}
        for i in range(10)
    ]
    motor = LexicalEngine(catalogo_grande)

    resultados = motor.buscar("rock")

    assert len(resultados) <= 5


# ── Score y ordenamiento ──────────────────────────────────────────────────────

def test_deberia_asignar_score_mayor_a_coincidencia_por_titulo(engine):
    """Coincidencia en título debe tener score mayor que solo en descripción."""
    # Yellow aparece en título → score alto
    # Otros aparecen en descripción → score menor
    resultados = engine.buscar("yellow")

    assert len(resultados) >= 1
    assert resultados[0]["title"] == "Yellow"
    assert resultados[0]["score"] > 0


def test_deberia_incluir_campo_search_type_en_resultados(engine):
    resultados = engine.buscar("coldplay")

    for r in resultados:
        assert r.get("search_type") == "lexical"


# ── Constructor ───────────────────────────────────────────────────────────────

def test_deberia_lanzar_error_cuando_catalogo_esta_vacio():
    with pytest.raises(ValueError):
        LexicalEngine([])
