import logging
import numpy as np

logger = logging.getLogger(__name__)

UMBRAL_SIMILITUD = 0.75


class VectorLibrary:
    """Almacén vectorial en memoria — sustituye a FAISS en entorno académico.

    Aplica el umbral de similitud coseno >= 0.75 definido en el TRD
    (criterio de aceptación técnico, sección 15) y en el Design Doc
    (sección 5.1 y 8.1): los resultados con score inferior se descartan.
    """

    def __init__(self, umbral: float = UMBRAL_SIMILITUD):
        self._inventario = []
        self.umbral = umbral

    def add_to_inventory(self, cancion: dict, vector: list) -> None:
        vector_np = np.array(vector, dtype=np.float32)
        self._inventario.append({"song": cancion, "vector": vector_np})
        logger.info(f"Canción indexada | titulo={cancion.get('title')} | dims={len(vector_np)}")

    def find_near(self, vector_query: list, top_k: int = 5) -> list:
        """Busca top_k vectores más cercanos, filtrando por umbral >= 0.75 (TRD)."""
        if not self._inventario:
            return []

        query_np = np.array(vector_query, dtype=np.float32)
        resultados = []

        for item in self._inventario:
            score = self._similitud_coseno(query_np, item["vector"])
            if score >= self.umbral:
                resultados.append({
                    "song": item["song"],
                    "score": round(score * 100, 2)
                })

        resultados.sort(key=lambda x: x["score"], reverse=True)
        logger.info(
            f"Búsqueda vectorial | candidatos={len(self._inventario)} "
            f"| sobre_umbral={len(resultados)} | umbral={self.umbral}"
        )
        return resultados[:top_k]

    def _similitud_coseno(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        norma_a = np.linalg.norm(vec_a)
        norma_b = np.linalg.norm(vec_b)
        if norma_a == 0 or norma_b == 0:
            return 0.0
        return float(np.dot(vec_a, vec_b) / (norma_a * norma_b))

    @property
    def size(self) -> int:
        return len(self._inventario)