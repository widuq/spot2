"""Tests para backend/api/main.py — cubre endpoints REST."""
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


RESULTADO_MOCK = {
    "query": "test",
    "results": [],
    "total": 0,
    "fallback_active": False,
    "search_type": "hybrid",
}


@pytest.fixture
def mock_engine():
    """Motor mockeado inyectado directamente en el módulo main."""
    engine = MagicMock()
    engine.execute_search.return_value = RESULTADO_MOCK
    return engine


@pytest.fixture
def client(mock_engine):
    """TestClient con engine parcheado a nivel de módulo (no constructor)."""
    import backend.api.main as main_module
    original = main_module.engine
    main_module.engine = mock_engine
    from backend.api.main import app
    with TestClient(app) as c:
        yield c
    main_module.engine = original


# ── GET / ─────────────────────────────────────────────────────────────────────

def test_root_deberia_retornar_status_online(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "Online"


def test_root_deberia_retornar_mensaje_bienvenida(client):
    response = client.get("/")
    data = response.json()
    assert "message" in data
    assert "docs" in data


# ── GET /health ───────────────────────────────────────────────────────────────

def test_health_deberia_retornar_healthy(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_deberia_incluir_nombre_engine(client):
    response = client.get("/health")
    assert "engine" in response.json()


# ── GET /search ───────────────────────────────────────────────────────────────

def test_search_get_deberia_retornar_200_con_query_valida(client, mock_engine):
    response = client.get("/search?q=coldplay")
    assert response.status_code == 200


def test_search_get_deberia_llamar_execute_search(client, mock_engine):
    client.get("/search?q=coldplay")
    mock_engine.execute_search.assert_called_once_with("coldplay")


def test_search_get_deberia_retornar_422_cuando_query_vacia(client):
    response = client.get("/search?q=")
    assert response.status_code == 422


def test_search_get_deberia_retornar_422_cuando_engine_lanza_value_error(client, mock_engine):
    mock_engine.execute_search.side_effect = ValueError("query inválida")
    response = client.get("/search?q=test")
    assert response.status_code == 422


def test_search_get_deberia_retornar_500_cuando_engine_lanza_excepcion(client, mock_engine):
    mock_engine.execute_search.side_effect = RuntimeError("fallo interno")
    response = client.get("/search?q=test")
    assert response.status_code == 500


# ── POST /search ──────────────────────────────────────────────────────────────

def test_search_post_deberia_retornar_200_con_body_valido(client):
    response = client.post("/search", json={"q": "coldplay"})
    assert response.status_code == 200


def test_search_post_deberia_llamar_execute_search(client, mock_engine):
    client.post("/search", json={"q": "adele"})
    mock_engine.execute_search.assert_called_once_with("adele")


def test_search_post_deberia_retornar_422_cuando_engine_lanza_value_error(client, mock_engine):
    mock_engine.execute_search.side_effect = ValueError("query inválida")
    response = client.post("/search", json={"q": "test"})
    assert response.status_code == 422


def test_search_post_deberia_retornar_500_cuando_engine_lanza_excepcion(client, mock_engine):
    mock_engine.execute_search.side_effect = RuntimeError("fallo")
    response = client.post("/search", json={"q": "test"})
    assert response.status_code == 500


def test_search_post_deberia_retornar_422_cuando_falta_campo_q(client):
    response = client.post("/search", json={})
    assert response.status_code == 422