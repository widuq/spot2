import pytest
import numpy as np
from backend.services.vector_store import VectorLibrary

def test_vector_similarity_exact_match():
    """✅ PRUEBA: Si buscamos la misma canción, el score debe ser 100%"""
    store = VectorLibrary()
    cancion = {"title": "Yellow", "artist": "Coldplay"}
    adn_ficticio = [0.1] * 384 
    
    # Usamos los nombres reales de sus métodos
    store.add_to_inventory(cancion, adn_ficticio)
    
    # Buscamos con el mismo ADN exacto usando 'find_near'
    resultados = store.find_near(adn_ficticio)
    
    # Ajustamos al formato de respuesta: 'song' en lugar de 'cancion'
    assert resultados[0]["song"]["title"] == "Yellow"
    assert resultados[0]["score"] == 100.0

def test_vector_similarity_different_songs():
    """✅ PRUEBA: Canciones con ADN opuesto deben tener score 0%"""
    store = VectorLibrary() # Cambiado de VectorStore a VectorLibrary
    
    # Vector Eje X
    vec_a = [1.0] + [0.0] * 383
    # Vector Eje Y (Perpendicular)
    vec_b = [0.0, 1.0] + [0.0] * 382
    
    store.add_to_inventory({"title": "Canción A"}, vec_a)
    store.add_to_inventory({"title": "Canción B"}, vec_b)
    
    resultados = store.find_near(vec_a)
    
    assert resultados[0]["song"]["title"] == "Canción A"
    assert resultados[0]["score"] == 100.0
    # La Canción B debe tener 0.0 de score por ser perpendicular
    assert resultados[1]["score"] == 0.0

def test_empty_results():
    """✅ PRUEBA: El sistema no debe romperse si el inventario está vacío"""
    store = VectorLibrary() # Cambiado de VectorStore a VectorLibrary
    resultados = store.find_near([0.1] * 384)
    assert len(resultados) == 0