import logging
import os
import requests

logger = logging.getLogger(__name__)


class OllamaClient:
    """Cliente HTTP para el servicio Ollama (LLM local opcional).

    Sin hardcoding de credenciales — toda configuración viene de variables
    de entorno. El timeout corto garantiza que un Ollama caído no bloquee
    el flujo principal: el orquestador captura el TimeoutError y activa
    el fallback léxico (RF-03).
    """

    def __init__(self):
        # Sin hardcoding — cubre criterio de seguridad de la guía
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.modelo = os.getenv("OLLAMA_MODEL", "llama3")
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT_MS", "150")) / 1000

    def generar(self, prompt: str) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("El prompt no puede estar vacío")

        try:
            respuesta = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.modelo,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=self.timeout
            )
            respuesta.raise_for_status()
            resultado = respuesta.json().get("response", "")
            logger.info(f"Ollama OK | modelo={self.modelo} | chars={len(resultado)}")
            return resultado

        except requests.Timeout:
            logger.warning(f"Ollama timeout | url={self.base_url} | timeout={self.timeout}s")
            raise TimeoutError(f"Ollama no respondió en {self.timeout}s")

        except requests.RequestException as e:
            logger.error(f"Ollama error | error={e}")
            raise
