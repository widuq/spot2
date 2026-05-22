import json
import os
import pytest
from pathlib import Path
from backend.infrastructure.catalog_loader import CatalogLoader


# ── Happy path: carga catálogo real del proyecto ──────────────────────────────

def test_deberia_cargar_catalogo_con_10_canciones():
    """Verifica que el catálogo de data/catalog.json tenga exactamente 10 canciones."""
    catalogo = CatalogLoader.load()

    assert isinstance(catalogo, list)
    assert len(catalogo) == 10


def test_deberia_retornar_canciones_con_campos_obligatorios():
    """Cada canción debe tener los campos mínimos requeridos."""
    catalogo = CatalogLoader.load()

    campos_requeridos = {"id", "title", "artist", "genre", "mood", "description"}
    for cancion in catalogo:
        for campo in campos_requeridos:
            assert campo in cancion, f"Campo '{campo}' faltante en: {cancion}"


def test_deberia_incluir_coldplay_en_el_catalogo():
    catalogo = CatalogLoader.load()
    artistas = [c["artist"] for c in catalogo]
    assert "Coldplay" in artistas


# ── Caso de error: JSON malformado ────────────────────────────────────────────

def test_deberia_lanzar_error_cuando_json_es_invalido(tmp_path, monkeypatch):
    """Si el archivo tiene JSON inválido, debe lanzar json.JSONDecodeError."""
    archivo_malo = tmp_path / "catalog.json"
    archivo_malo.write_text("esto no es json válido {{{")

    monkeypatch.setenv("CATALOG_PATH", str(archivo_malo))

    with pytest.raises(json.JSONDecodeError):
        CatalogLoader.load()


# ── Carga desde variable de entorno personalizada ────────────────────────────

def test_deberia_cargar_catalogo_personalizado_desde_env(tmp_path, monkeypatch):
    """Debe respetar la variable CATALOG_PATH para el archivo del catálogo."""
    catalogo_prueba = [
        {"id": 1, "title": "Test Song", "artist": "Test Artist",
         "genre": "Pop", "mood": "happy", "description": "test"}
    ]
    archivo = tmp_path / "mi_catalogo.json"
    archivo.write_text(json.dumps(catalogo_prueba), encoding="utf-8")
    monkeypatch.setenv("CATALOG_PATH", str(archivo))

    resultado = CatalogLoader.load()

    assert len(resultado) == 1
    assert resultado[0]["title"] == "Test Song"


# ── Estructura del catálogo ────────────────────────────────────────────────────

def test_deberia_retornar_ids_unicos():
    """Los IDs del catálogo no deben repetirse."""
    catalogo = CatalogLoader.load()
    ids = [c["id"] for c in catalogo]
    assert len(ids) == len(set(ids))


def test_deberia_retornar_titulos_no_vacios():
    catalogo = CatalogLoader.load()
    for cancion in catalogo:
        assert cancion["title"].strip() != ""
