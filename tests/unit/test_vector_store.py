import pytest
import numpy as np
from backend.infrastructure.vector_store import VectorLibrary


# ── RF-01 — Happy path ────────────────────────────────────────────────────────

def test_deberia_retornar_score_100_cuando_se_busca_la_misma_cancion():
    # GIVEN: una canción indexada con un vector conocido
    store = VectorLibrary()
    cancion = {"title": "Yellow", "artist": "Coldplay"}
    adn_ficticio = [0.1] * 384
    store.add_to_inventory(cancion, adn_ficticio)

    # WHEN: se busca con el mismo vector
    resultados = store.find_near(adn_ficticio)

    # THEN: score perfecto y canción correcta
    assert resultados[0]["song"]["title"] == "Yellow"
    assert resultados[0]["score"] == 100.0


# ── RF-01 — Caso límite: vectores perpendiculares (score=0) ───────────────────

def test_deberia_retornar_score_0_cuando_canciones_tienen_vectores_perpendiculares():
    # GIVEN: dos canciones con vectores ortogonales
    store = VectorLibrary()
    vec_a = [1.0] + [0.0] * 383
    vec_b = [0.0, 1.0] + [0.0] * 382
    store.add_to_inventory({"title": "Canción A"}, vec_a)
    store.add_to_inventory({"title": "Canción B"}, vec_b)

    # WHEN
    resultados = store.find_near(vec_a)

    # THEN: A tiene score 100, B tiene score 0
    assert resultados[0]["song"]["title"] == "Canción A"
    assert resultados[0]["score"] == 100.0
    assert resultados[1]["score"] == 0.0


# ── RF-01 — Caso límite: inventario vacío ────────────────────────────────────

def test_deberia_retornar_lista_vacia_cuando_inventario_esta_vacio():
    store = VectorLibrary()
    resultados = store.find_near([0.1] * 384)
    assert resultados == []


# ── RF-01 — top_k limita resultados ──────────────────────────────────────────

def test_deberia_retornar_maximo_top_k_resultados():
    # GIVEN: 10 canciones indexadas
    store = VectorLibrary()
    for i in range(10):
        store.add_to_inventory({"title": f"Canción {i}"}, [float(i)] * 384)

    # WHEN: top_k=3
    resultados = store.find_near([1.0] * 384, top_k=3)

    # THEN
    assert len(resultados) <= 3


# ── RF-01 — resultados ordenados descendente ──────────────────────────────────

def test_deberia_retornar_resultados_ordenados_por_score_descendente():
    # GIVEN: dos canciones con distintos vectores
    store = VectorLibrary()
    vec_query = [1.0] * 384
    vec_cercano = [1.0] * 384          # idéntico → score 100
    vec_lejano = [1.0, -1.0] + [0.0] * 382  # ortogonal parcial

    store.add_to_inventory({"title": "Lejos"}, vec_lejano)
    store.add_to_inventory({"title": "Cercano"}, vec_cercano)

    # WHEN
    resultados = store.find_near(vec_query)

    # THEN: primero el más cercano
    assert resultados[0]["song"]["title"] == "Cercano"


# ── Propiedad size ─────────────────────────────────────────────────────────────

def test_size_deberia_incrementar_con_cada_cancion_indexada():
    store = VectorLibrary()
    assert store.size == 0
    store.add_to_inventory({"title": "A"}, [0.1] * 384)
    assert store.size == 1
    store.add_to_inventory({"title": "B"}, [0.2] * 384)
    assert store.size == 2


# ── Vector cero — similitud cero ─────────────────────────────────────────────

def test_deberia_retornar_score_0_cuando_vector_es_cero():
    store = VectorLibrary()
    vec_cero = [0.0] * 384
    store.add_to_inventory({"title": "Silencio"}, vec_cero)

    resultados = store.find_near([1.0] * 384)
    assert resultados[0]["score"] == 0.0
