import requests

class OllamaClient:
    def __init__(self):
        # Usamos IP directa para asegurar conexión en Ubuntu
        self.url = "http://127.0.0.1:11434/api/embeddings"
        self.model = "paraphrase-multilingual"

    def get_embedding(self, text: str):
        """Obtiene el vector de la GPU usando Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": text
            }
            response = requests.post(self.url, json=payload, timeout=5)
            response.raise_for_status()
            return response.json().get('embedding', [])
        except Exception as e:
            print(f"⚓ Error conectando con el motor de IA: {e}")
            return []