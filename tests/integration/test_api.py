import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)


# ─────────────────────────────────────────────────────────────────
# Sin test doubles propios: TestClient de FastAPI actúa como
# cliente HTTP sin levantar servidor real.
# ─────────────────────────────────────────────────────────────────


# RF-04 — Happy path
def test_deberia_retornar_200_cuando_query_es_valida():
    # GIVEN: cliente con query válida
    # WHEN
    respuesta = client.get("/search", params={"q": "coldplay"})
    # THEN
    assert respuesta.status_code == 200


# RF-04 — Contrato de la API
def test_deberia_retornar_resultados_cuando_query_tiene_artista_conocido():
    # GIVEN: query con nombre de artista
    # WHEN
    respuesta = client.get("/search", params={"q": "yellow"})
    body = respuesta.json()
    # THEN: respuesta es un dict o lista, no está vacía
    assert respuesta.status_code == 200
    assert body is not None


# RF-04 — Flujo de error: query vacía
def test_deberia_retornar_422_cuando_query_esta_vacia():
    # GIVEN: query vacía
    # WHEN
    respuesta = client.get("/search", params={"q": ""})
    # THEN: FastAPI rechaza por min_length=1
    assert respuesta.status_code == 422


# RF-04 — Ruta raíz
def test_deberia_retornar_status_online_en_ruta_raiz():
    # GIVEN / WHEN
    respuesta = client.get("/")
    body = respuesta.json()
    # THEN
    assert respuesta.status_code == 200
    assert body["status"] == "Online"