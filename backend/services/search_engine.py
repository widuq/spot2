import logging

from backend.application.orchestrator import Orchestrator
from backend.domain.semantic_engine import SemanticEngine
from backend.infrastructure.catalog_loader import CatalogLoader
from backend.infrastructure.lexical_engine import LexicalEngine
from backend.infrastructure.vector_store import VectorLibrary

logger = logging.getLogger(__name__)


class _FallbackSemanticEngine:
    """Stub que siempre falla — activa RF-03 cuando SBERT no está disponible.

    Permite que el sistema arranque incluso sin el modelo descargado.
    """
    def buscar(self, query: str) -> list:
        raise RuntimeError("Motor semántico no disponible — usando fallback léxico")


class HybridSearchEngine:
    """Punto de entrada principal del sistema de búsqueda.

    Capa de servicio que:
    1. Carga el catálogo de canciones.
    2. Inicializa el motor léxico (siempre disponible).
    3. Intenta inicializar el motor semántico SBERT.
       Si falla, instala un stub que activa RF-03 automáticamente.
    4. Crea el orquestador y expone execute_search().

    Esta separación garantiza que la API siempre responde, incluso en
    entornos académicos sin modelo SBERT descargado.
    """

    def __init__(self):
        catalogo = CatalogLoader.load()
        vector_store = VectorLibrary()

        motor_lexico = LexicalEngine(catalogo)
        motor_semantico = self._init_motor_semantico(vector_store, catalogo)

        self._orchestrator = Orchestrator(motor_lexico, motor_semantico)
        logger.info("HybridSearchEngine listo")

    def execute_search(self, query: str) -> dict:
        """Ejecuta la búsqueda y retorna el resultado formateado para la API.

        Args:
            query: Texto de la consulta del usuario.

        Returns:
            Dict con claves: query, results, fallback_active, total, search_type.
        """
        resultados = self._orchestrator.buscar(query)

        # Determinar qué motor se usó (para observabilidad)
        search_type = "lexical" if self._orchestrator.fallback_activado else "hybrid"

        return {
            "query": query,
            "results": resultados,
            "total": len(resultados),
            "fallback_active": self._orchestrator.fallback_activado,
            "search_type": search_type,
        }

    # ─── helpers ─────────────────────────────────────────────────────────────

    @staticmethod
    def _init_motor_semantico(vector_store, catalogo: list):
        """Intenta crear SemanticEngine; devuelve stub si no está disponible."""
        try:
            motor = SemanticEngine(vector_store)
            motor.indexar_catalogo(catalogo)
            logger.info("Motor semántico SBERT inicializado y catálogo indexado")
            return motor
        except Exception as e:
            logger.warning(
                f"Motor semántico no disponible — RF-03 activo | error={e}"
            )
            return _FallbackSemanticEngine()
