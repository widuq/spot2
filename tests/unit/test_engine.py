import pytest
import numpy as np
from backend.infrastructure.vector_store import VectorLibrary  # ← única línea que cambia


# RF-01 — Happy path
def test_deberia_retornar_score_100_cuando_se_busca_la_misma_cancion():
    store = VectorLibrary()
    cancion = {"title": "Yellow", "artist": "Coldplay"}
    adn_ficticio = [0.1] * 384
    store.add_to_inventory(cancion, adn_ficticio)

    resultados = store.find_near(adn_ficticio)

    assert resultados[0]["song"]["title"] == "Yellow"
    assert resultados[0]["score"] == 100.0


# RF-01 — Caso límite: vectores perpendiculares
def test_deberia_retornar_score_0_cuando_canciones_tienen_vectores_perpendiculares():
    store = VectorLibrary()
    vec_a = [1.0] + [0.0] * 383
    vec_b = [0.0, 1.0] + [0.0] * 382
    store.add_to_inventory({"title": "Canción A"}, vec_a)
    store.add_to_inventory({"title": "Canción B"}, vec_b)

    resultados = store.find_near(vec_a)

    assert resultados[0]["song"]["title"] == "Canción A"
    assert resultados[0]["score"] == 100.0
    assert resultados[1]["score"] == 0.0


# RF-01 — Caso límite: inventario vacío
def test_deberia_retornar_lista_vacia_cuando_inventario_esta_vacio():
    store = VectorLibrary()

    resultados = store.find_near([0.1] * 384)

    assert len(resultados) == 0