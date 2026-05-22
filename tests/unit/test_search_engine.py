"""Tests para backend/services/search_engine.py — HybridSearchEngine."""
import pytest
from unittest.mock import MagicMock, patch


# ── Helpers ───────────────────────────────────────────────────────────────────

CATALOGO_MOCK = [
    {"id": "1", "title": "Yellow", "artist": "Coldplay", "genre": "rock", "mood": "sad", "description": ""},
]

RESULTADO_MOCK = [{"id": "1", "title": "Yellow", "artist": "Coldplay", "score": 95, "search_type": "lexical"}]


def _make_hybrid_engine():
    """Instancia HybridSearchEngine con todas las dependencias mockeadas."""
    with patch("backend.services.search_engine.CatalogLoader") as mock_loader, \
         patch("backend.services.search_engine.VectorLibrary") as mock_vl, \
         patch("backend.services.search_engine.LexicalEngine") as mock_lex, \
         patch("backend.services.search_engine.SemanticEngine") as mock_sem, \
         patch("backend.services.search_engine.Orchestrator") as mock_orch:

        mock_loader.load.return_value = CATALOGO_MOCK
        mock_orchestrator = MagicMock()
        mock_orchestrator.buscar.return_value = RESULTADO_MOCK
        mock_orchestrator.fallback_activado = False
        mock_orch.return_value = mock_orchestrator

        from backend.services.search_engine import HybridSearchEngine
        engine = HybridSearchEngine()
        engine._orchestrator = mock_orchestrator
        return engine, mock_orchestrator


# ── Constructor ───────────────────────────────────────────────────────────────

def test_deberia_inicializar_sin_excepciones():
    engine, _ = _make_hybrid_engine()
    assert engine is not None


def test_deberia_usar_fallback_cuando_sbert_no_esta_disponible():
    with patch("backend.services.search_engine.CatalogLoader") as mock_loader, \
         patch("backend.services.search_engine.VectorLibrary"), \
         patch("backend.services.search_engine.LexicalEngine"), \
         patch("backend.services.search_engine.SemanticEngine", side_effect=RuntimeError("sin SBERT")), \
         patch("backend.services.search_engine.Orchestrator") as mock_orch:

        mock_loader.load.return_value = CATALOGO_MOCK
        mock_orch.return_value = MagicMock()
        mock_orch.return_value.buscar.return_value = []
        mock_orch.return_value.fallback_activado = True

        from backend.services.search_engine import HybridSearchEngine
        engine = HybridSearchEngine()
        assert engine is not None


# ── execute_search ────────────────────────────────────────────────────────────

def test_deberia_retornar_dict_con_claves_requeridas():
    engine, _ = _make_hybrid_engine()
    resultado = engine.execute_search("coldplay")
    assert all(k in resultado for k in ["query", "results", "total", "fallback_active", "search_type"])


def test_deberia_retornar_la_query_en_respuesta():
    engine, _ = _make_hybrid_engine()
    resultado = engine.execute_search("adele")
    assert resultado["query"] == "adele"


def test_deberia_retornar_total_correcto():
    engine, _ = _make_hybrid_engine()
    resultado = engine.execute_search("coldplay")
    assert resultado["total"] == len(resultado["results"])


def test_deberia_retornar_search_type_hybrid_cuando_no_hay_fallback():
    engine, mock_orch = _make_hybrid_engine()
    mock_orch.fallback_activado = False
    resultado = engine.execute_search("coldplay")
    assert resultado["search_type"] == "hybrid"


def test_deberia_retornar_search_type_lexical_cuando_hay_fallback():
    engine, mock_orch = _make_hybrid_engine()
    mock_orch.fallback_activado = True
    resultado = engine.execute_search("coldplay")
    assert resultado["search_type"] == "lexical"


def test_deberia_retornar_fallback_active_false_cuando_no_hay_fallback():
    engine, mock_orch = _make_hybrid_engine()
    mock_orch.fallback_activado = False
    resultado = engine.execute_search("coldplay")
    assert resultado["fallback_active"] is False


def test_deberia_llamar_orchestrator_buscar_con_la_query():
    engine, mock_orch = _make_hybrid_engine()
    engine.execute_search("test query")
    mock_orch.buscar.assert_called_once_with("test query")


def test_deberia_propagar_value_error_del_orchestrator():
    engine, mock_orch = _make_hybrid_engine()
    mock_orch.buscar.side_effect = ValueError("query vacía")
    with pytest.raises(ValueError):
        engine.execute_search("")