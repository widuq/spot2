import pytest
from unittest.mock import patch, MagicMock
from backend.infrastructure.ollama_client import OllamaClient


# ── Happy path con mock HTTP ───────────────────────────────────────────────────

def test_deberia_retornar_respuesta_cuando_ollama_responde_ok():
    # GIVEN: Ollama responde correctamente
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "resultado generado"}
    mock_response.raise_for_status = MagicMock()

    with patch("backend.infrastructure.ollama_client.requests.post", return_value=mock_response):
        cliente = OllamaClient()
        resultado = cliente.generar("Genera algo")

    assert resultado == "resultado generado"


# ── Timeout → debe lanzar TimeoutError ───────────────────────────────────────

def test_deberia_lanzar_timeout_error_cuando_ollama_no_responde():
    import requests as req
    with patch("backend.infrastructure.ollama_client.requests.post",
               side_effect=req.Timeout()):
        cliente = OllamaClient()
        with pytest.raises(TimeoutError):
            cliente.generar("Genera algo")


# ── Prompt vacío → ValueError antes de llamar al servidor ────────────────────

def test_deberia_lanzar_value_error_cuando_prompt_esta_vacio():
    cliente = OllamaClient()
    with pytest.raises(ValueError, match="vacío"):
        cliente.generar("")


def test_deberia_lanzar_value_error_cuando_prompt_es_solo_espacios():
    cliente = OllamaClient()
    with pytest.raises(ValueError):
        cliente.generar("   ")


# ── Configuración desde variables de entorno ─────────────────────────────────

def test_deberia_usar_url_y_modelo_de_variables_de_entorno(monkeypatch):
    monkeypatch.setenv("OLLAMA_URL", "http://mi-servidor:9999")
    monkeypatch.setenv("OLLAMA_MODEL", "mistral")
    monkeypatch.setenv("OLLAMA_TIMEOUT_MS", "500")

    cliente = OllamaClient()

    assert cliente.base_url == "http://mi-servidor:9999"
    assert cliente.modelo == "mistral"
    assert cliente.timeout == 0.5
