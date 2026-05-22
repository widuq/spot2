import logging
import numpy as np

logger = logging.getLogger(__name__)


class VectorLibrary:

    def __init__(self):
        # Fake en memoria — no requiere FAISS real
        self._inventario = []  # lista de {"song": {...}, "vector": [...]}

    def add_to_inventory(self, cancion: dict, vector: list) -> None:
        vector_np = np.array(vector, dtype=np.float32)
        self._inventario.append({
            "song": cancion,
            "vector": vector_np
        })
        logger.info(f"Canción indexada | titulo={cancion.get('title')} | dims={len(vector_np)}")

    def find_near(self, vector_query: list, top_k: int = 5) -> list:
        if not self._inventario:
            return []

        query_np = np.array(vector_query, dtype=np.float32)
        resultados = []

        for item in self._inventario:
            score = self._similitud_coseno(query_np, item["vector"])
            resultados.append({
                "song": item["song"],
                "score": round(score * 100, 2)  # 0.0 a 100.0
            })

        # Ordenar de mayor a menor score
        resultados.sort(key=lambda x: x["score"], reverse=True)
        return resultados[:top_k]

    def _similitud_coseno(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        norma_a = np.linalg.norm(vec_a)
        norma_b = np.linalg.norm(vec_b)

        if norma_a == 0 or norma_b == 0:
            return 0.0

        return float(np.dot(vec_a, vec_b) / (norma_a * norma_b))