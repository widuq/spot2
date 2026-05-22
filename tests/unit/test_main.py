"""Tests para backend/api/main.py — cubre endpoints REST."""
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    """Cliente de prueba con motor mockeado."""
    with patch("backend.api.main.HybridSearchEngine") as mock_engine_cls:
        mock_engine = MagicMock()
        mock_engine_cls.return_value = mock_engine
        mock_engine.execute_search.return_value = {
            "query": "test",
            "results": [],
            "total": 0,
            "fallback_active": False,
            "search_type": "hybrid",
        }
        from backend.api.main import app
        with TestClient(app) as c:
            c.app_engine = mock_engine
            yield c


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

def test_search_get_deberia_retornar_200_con_query_valida(client):
    response = client.get("/search?q=coldplay")
    assert response.status_code == 200


def test_search_get_deberia_llamar_execute_search(client):
    client.get("/search?q=coldplay")
    client.app_engine.execute_search.assert_called_once_with("coldplay")


def test_search_get_deberia_retornar_422_cuando_query_vacia(client):
    response = client.get("/search?q=")
    assert response.status_code == 422


def test_search_get_deberia_retornar_422_cuando_engine_lanza_value_error(client):
    client.app_engine.execute_search.side_effect = ValueError("query inválida")
    response = client.get("/search?q=test")
    assert response.status_code == 422


def test_search_get_deberia_retornar_500_cuando_engine_lanza_excepcion(client):
    client.app_engine.execute_search.side_effect = RuntimeError("fallo interno")
    response = client.get("/search?q=test")
    assert response.status_code == 500


# ── POST /search ──────────────────────────────────────────────────────────────

def test_search_post_deberia_retornar_200_con_body_valido(client):
    response = client.post("/search", json={"q": "coldplay"})
    assert response.status_code == 200


def test_search_post_deberia_llamar_execute_search(client):
    client.post("/search", json={"q": "adele"})
    client.app_engine.execute_search.assert_called_once_with("adele")


def test_search_post_deberia_retornar_422_cuando_engine_lanza_value_error(client):
    client.app_engine.execute_search.side_effect = ValueError("query inválida")
    response = client.post("/search", json={"q": "test"})
    assert response.status_code == 422


def test_search_post_deberia_retornar_500_cuando_engine_lanza_excepcion(client):
    client.app_engine.execute_search.side_effect = RuntimeError("fallo")
    response = client.post("/search", json={"q": "test"})
    assert response.status_code == 500


def test_search_post_deberia_retornar_422_cuando_falta_campo_q(client):
    response = client.post("/search", json={})
    assert response.status_code == 422