import logging
import os
import numpy as np

logger = logging.getLogger(__name__)


class SearchEngine:

    def __init__(self, vector_store):
        self.vector_store = vector_store
        self._modelo = None
        self._cargar_modelo()

    def _cargar_modelo(self):
        try:
            from sentence_transformers import SentenceTransformer
            nombre_modelo = os.getenv(
                "SBERT_MODEL",
                "paraphrase-multilingual-MiniLM-L12-v2"
            )
            self._modelo = SentenceTransformer(nombre_modelo)
            logger.info(f"Modelo SBERT cargado | modelo={nombre_modelo}")
        except Exception as e:
            logger.error(f"Error cargando modelo SBERT | error={e}")
            raise

    def generar_embedding(self, query: str) -> np.ndarray:
        # RF-01 — transforma texto en vector de 384 dimensiones
        if not query or not query.strip():
            raise ValueError("La consulta no puede estar vacía")

        vector = self._modelo.encode(query, normalize_embeddings=True)
        logger.info(f"Embedding generado | query={query} | dims={len(vector)}")
        return vector

    def buscar(self, query: str) -> list:
        # RF-01 — genera embedding y busca en el índice vectorial
        vector =