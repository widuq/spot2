"""Tests para backend/domain/semantic_engine.py."""
import pytest
import numpy as np
from unittest.mock import MagicMock, patch


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_engine(vector_store=None):
    if vector_store is None:
        vector_store = MagicMock()

    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([1.0, 0.0, 0.0])

    with patch("backend.domain.semantic_engine.SentenceTransformer", return_value=mock_model):
        from backend.domain.semantic_engine import SemanticEngine
        engine = SemanticEngine(vector_store)

    return engine, mock_model, vector_store


# ── Constructor ───────────────────────────────────────────────────────────────

def test_deberia_cargar_modelo_sbert_al_inicializar():
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([1.0])
    with patch("backend.domain.semantic_engine.SentenceTransformer", return_value=mock_model) as mock_cls:
        from backend.domain.semantic_engine import SemanticEngine
        SemanticEngine(MagicMock())
        mock_cls.assert_called_once()


def test_deberia_lanzar_excepcion_cuando_sbert_no_esta_disponible():
    with patch("backend.domain.semantic_engine.SentenceTransformer", side_effect=RuntimeError("sin modelo")):
        from backend.domain.semantic_engine import SemanticEngine
        with pytest.raises(Exception):
            SemanticEngine(MagicMock())


# ── generar_embedding ─────────────────────────────────────────────────────────

def test_deberia_retornar_numpy_array_para_query_valida():
    engine, _, _ = _make_engine()
    resultado = engine.generar_embedding("coldplay")
    assert isinstance(resultado, np.ndarray)


def test_deberia_lanzar_value_error_cuando_query_vacia():
    engine, _, _ = _make_engine()
    with pytest.raises(ValueError):
        engine.generar_embedding("")


def test_deberia_lanzar_value_error_cuando_query_es_solo_espacios():
    engine, _, _ = _make_engine()
    with pytest.raises(ValueError):
        engine.generar_embedding("   ")


def test_deberia_llamar_encode_del_modelo():
    engine, mock_model, _ = _make_engine()
    engine.generar_embedding("test query")
    mock_model.encode.assert_called_once()


# ── buscar ────────────────────────────────────────────────────────────────────

def test_deberia_retornar_lista_de_resultados():
    vector_store = MagicMock()
    vector_store.find_near.return_value = [{"id": "1", "title": "Yellow"}]
    engine, _, _ = _make_engine(vector_store)
    resultados = engine.buscar("coldplay")
    assert isinstance(resultados, list)


def test_deberia_agregar_search_type_semantic_a_resultados():
    vector_store = MagicMock()
    vector_store.find_near.return_value = [{"id": "1", "title": "Yellow"}]
    engine, _, _ = _make_engine(vector_store)
    resultados = engine.buscar("coldplay")
    assert resultados[0]["search_type"] == "semantic"


def test_deberia_retornar_lista_vacia_cuando_no_hay_coincidencias():
    vector_store = MagicMock()
    vector_store.find_near.return_value = []
    engine, _, _ = _make_engine(vector_store)
    assert engine.buscar("xyz123") == []


# ── indexar_catalogo ──────────────────────────────────────────────────────────

def test_deberia_indexar_todas_las_canciones_del_catalogo():
    vector_store = MagicMock()
    engine, _, _ = _make_engine(vector_store)
    catalogo = [
        {"id": "1", "title": "Yellow", "artist": "Coldplay",
         "genre": "rock", "mood": "sad", "description": ""},
        {"id": "2", "title": "Hello", "artist": "Adele",
         "genre": "pop", "mood": "sad", "description": ""},
    ]
    engine.indexar_catalogo(catalogo)
    assert vector_store.add_to_inventory.call_count == 2


def test_deberia_no_indexar_nada_con_catalogo_vacio():
    vector_store = MagicMock()
    engine, _, _ = _make_engine(vector_store)
    engine.indexar_catalogo([])
    vector_store.add_to_inventory.assert_not_called()