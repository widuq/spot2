try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None
import logging
import os
import numpy as np

logger = logging.getLogger(__name__)


class SemanticEngine:
    """Motor de búsqueda semántica usando SBERT + VectorLibrary.

    Implementa RF-01: transforma consultas en embeddings vectoriales de
    384 dimensiones y recupera canciones similares por similitud coseno.

    Si el modelo SBERT no está disponible (sin conexión a internet o sin
    instalación), el constructor lanza una excepción. El orquestador captura
    esto y activa el fallback léxico (RF-03) de forma transparente.
    """

    def __init__(self, vector_store):
        self.vector_store = vector_store
        self._modelo = None
        self._cargar_modelo()

    def _cargar_modelo(self):
        try:
            if SentenceTransformer is None:
                raise ImportError("sentence_transformers no está instalado")
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
        """RF-01 — transforma texto en vector de 384 dimensiones.

        Args:
            query: Texto de la consulta del usuario.

        Returns:
            Vector numpy normalizado de 384 dimensiones.
        """
        if not query or not query.strip():
            raise ValueError("La consulta no puede estar vacía")

        vector = self._modelo.encode(query, normalize_embeddings=True)
        logger.info(f"Embedding generado | query={query!r} | dims={len(vector)}")
        return vector

    def buscar(self, query: str) -> list:
        """RF-01 — genera embedding y busca en el índice vectorial.

        Args:
            query: Texto de la consulta.

        Returns:
            Lista de canciones similares ordenadas por score (max 5).
            Cada ítem incluye los campos de la canción + 'score' + 'search_type'.
        """
        vector = self.generar_embedding(query)
        resultados_raw = self.vector_store.find_near(vector.tolist())

        # Enriquecer con tipo de búsqueda para trazabilidad
        for r in resultados_raw:
            r["search_type"] = "semantic"

        logger.info(f"Búsqueda semántica OK | query={query!r} | encontrados={len(resultados_raw)}")
        return resultados_raw

    def indexar_catalogo(self, catalogo: list) -> None:
        """Pre-indexa el catálogo completo en el vector store.

        Genera un embedding para cada canción usando su descripción,
        título, artista y mood como texto representativo.

        Args:
            catalogo: Lista de dicts con campos de canciones.
        """
        for cancion in catalogo:
            texto = (
                f"{cancion.get('title', '')} "
                f"{cancion.get('artist', '')} "
                f"{cancion.get('genre', '')} "
                f"{cancion.get('mood', '')} "
                f"{cancion.get('description', '')}"
            )
            vector = self.generar_embedding(texto)
            self.vector_store.add_to_inventory(cancion, vector.tolist())

        logger.info(f"Catálogo indexado | total={len(catalogo)} canciones")
