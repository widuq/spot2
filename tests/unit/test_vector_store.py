import pytest
import numpy as np
from backend.infrastructure.vector_store import VectorLibrary


def test_deberia_retornar_score_100_cuando_se_busca_la_misma_cancion():
    store = VectorLibrary()
    cancion = {"title": "Yellow", "artist": "Coldplay"}
    adn_ficticio = [0.1] * 384
    store.add_to_inventory(cancion, adn_ficticio)
    resultados = store.find_near(adn_ficticio)
    assert resultados[0]["song"]["title"] == "Yellow"
    assert resultados[0]["score"] == 100.0


def test_deberia_descartar_resultados_con_score_menor_al_umbral():
    """TRD sección 15 y Design Doc 8.1: similitud < 0.75 se descarta."""
    store = VectorLibrary(umbral=0.75)
    vec_a = [1.0] + [0.0] * 383
    vec_b = [0.0, 1.0] + [0.0] * 382
    store.add_to_inventory({"title": "Canción B (score 0)"}, vec_b)
    resultados = store.find_near(vec_a)
    assert resultados == []


def test_deberia_retornar_solo_resultados_sobre_el_umbral():
    store = VectorLibrary(umbral=0.75)
    vec_alta = [1.0] * 384
    vec_baja = [1.0, -1.0] + [0.0] * 382
    store.add_to_inventory({"title": "Alta similitud"}, vec_alta)
    store.add_to_inventory({"title": "Baja similitud"}, vec_baja)
    resultados = store.find_near([1.0] * 384)
    assert len(resultados) == 1
    assert resultados[0]["song"]["title"] == "Alta similitud"


def test_umbral_por_defecto_es_0_75():
    store = VectorLibrary()
    assert store.umbral == 0.75


def test_deberia_retornar_lista_vacia_cuando_inventario_esta_vacio():
    store = VectorLibrary()
    assert store.find_near([0.1] * 384) == []


def test_deberia_retornar_maximo_top_k_resultados():
    store = VectorLibrary()
    for i in range(10):
        store.add_to_inventory({"title": f"Canción {i}"}, [1.0] * 384)
    resultados = store.find_near([1.0] * 384, top_k=3)
    assert len(resultados) <= 3


def test_deberia_retornar_resultados_ordenados_por_score_descendente():
    store = VectorLibrary(umbral=0.0)
    vec_cercano = [1.0] * 384
    vec_lejano = [1.0, -1.0] + [0.0] * 382
    store.add_to_inventory({"title": "Lejos"}, vec_lejano)
    store.add_to_inventory({"title": "Cercano"}, vec_cercano)
    resultados = store.find_near([1.0] * 384)
    assert resultados[0]["song"]["title"] == "Cercano"


def test_size_deberia_incrementar_con_cada_cancion_indexada():
    store = VectorLibrary()
    assert store.size == 0
    store.add_to_inventory({"title": "A"}, [0.1] * 384)
    assert store.size == 1


def test_deberia_filtrar_vector_cero_por_umbral():
    """Vector cero produce similitud 0.0 — descartado por umbral 0.75."""
    store = VectorLibrary()
    store.add_to_inventory({"title": "Silencio"}, [0.0] * 384)
    assert store.find_near([1.0] * 384) == []