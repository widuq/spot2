import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

# ─────────────────────────────────────────────────────────────────────────────
# Sin test doubles propios: TestClient de FastAPI actúa como cliente HTTP
# sin levantar servidor real. Las pruebas verifican el contrato de la API,
# no la implementación interna de los motores.
# ─────────────────────────────────────────────────────────────────────────────

client = TestClient(app)


# ── RF-04 — GET /search — Happy path ─────────────────────────────────────────

def test_deberia_retornar_200_cuando_query_es_valida():
    # GIVEN: cliente con query válida
    # WHEN
    respuesta = client.get("/search", params={"q": "coldplay"})

    # THEN
    assert respuesta.status_code == 200


def test_deberia_retornar_resultados_cuando_query_tiene_artista_conocido():
    # GIVEN: query con nombre de artista
    # WHEN
    respuesta = client.get("/search", params={"q": "yellow"})
    body = respuesta.json()

    # THEN: respuesta es un dict con los campos esperados
    assert respuesta.status_code == 200
    assert body is not None
    assert "results" in body
    assert "query" in body
    assert "total" in body


def test_deberia_retornar_campo_query_igual_al_termino_buscado():
    respuesta = client.get("/search", params={"q": "adele"})
    body = respuesta.json()

    assert body["query"] == "adele"


def test_deberia_retornar_campo_fallback_active_en_respuesta():
    respuesta = client.get("/search", params={"q": "coldplay"})
    body = respuesta.json()

    assert "fallback_active" in body
    assert isinstance(body["fallback_active"], bool)


# ── RF-04 — GET /search — Flujos de error ────────────────────────────────────

def test_deberia_retornar_422_cuando_query_esta_vacia():
    # GIVEN: query vacía
    # WHEN
    respuesta = client.get("/search", params={"q": ""})

    # THEN: FastAPI rechaza por min_length=1
    assert respuesta.status_code == 422


def test_deberia_retornar_422_cuando_no_se_pasa_parametro_q():
    respuesta = client.get("/search")

    assert respuesta.status_code == 422


# ── RF-04 — POST /search — Happy path ────────────────────────────────────────

def test_deberia_retornar_200_en_post_cuando_body_es_valido():
    respuesta = client.post("/search", json={"q": "coldplay"})

    assert respuesta.status_code == 200


def test_deberia_retornar_mismos_campos_en_post_que_en_get():
    get_resp = client.get("/search", params={"q": "adele"}).json()
    post_resp = client.post("/search", json={"q": "adele"}).json()

    # Mismos campos en la respuesta
    assert set(get_resp.keys()) == set(post_resp.keys())


def test_deberia_retornar_422_en_post_cuando_body_esta_vacio():
    respuesta = client.post("/search", json={})

    assert respuesta.status_code == 422


# ── Ruta raíz ─────────────────────────────────────────────────────────────────

def test_deberia_retornar_status_online_en_ruta_raiz():
    # GIVEN / WHEN
    respuesta = client.get("/")
    body = respuesta.json()

    # THEN
    assert respuesta.status_code == 200
    assert body["status"] == "Online"


# ── Health check ──────────────────────────────────────────────────────────────

def test_deberia_retornar_healthy_en_health_endpoint():
    respuesta = client.get("/health")
    body = respuesta.json()

    assert respuesta.status_code == 200
    assert body["status"] == "healthy"


# ── Caso límite — query sin resultados ───────────────────────────────────────

def test_deberia_retornar_200_con_lista_vacia_cuando_no_hay_coincidencias():
    respuesta = client.get("/search", params={"q": "xkzqwmvp_inexistente_999"})
    body = respuesta.json()

    assert respuesta.status_code == 200
    assert body["results"] == []
    assert body["total"] == 0
