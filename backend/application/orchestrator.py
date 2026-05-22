import logging
import os

logger = logging.getLogger(__name__)


class Orchestrator:
    """Orquestador de la búsqueda híbrida.

    Implementa la lógica central de routing entre motores:
    - RF-02: Si la query parece una búsqueda exacta (nombre de artista/canción),
             prioriza el motor léxico para máxima precisión.
    - RF-01 + RF-02: Para búsquedas semánticas, intenta primero el motor SBERT.
    - RF-03: Si el motor semántico falla por cualquier razón (timeout, modelo
             no disponible, etc.), activa el fallback al motor léxico sin
             propagar la excepción al cliente.

    El flag `fallback_activado` permite a la capa superior informar al cliente
    qué motor se usó realmente.
    """

    def __init__(self, motor_lexico, motor_semantico):
        self.motor_lexico = motor_lexico
        self.motor_semantico = motor_semantico
        self.fallback_activado = False

    def buscar(self, query: str) -> list:
        """Ejecuta la búsqueda aplicando las reglas RF-01, RF-02 y RF-03.

        Args:
            query: Texto de la consulta del usuario.

        Returns:
            Lista de resultados ordenada por relevancia.

        Raises:
            ValueError: Si la query está vacía o es solo espacios.
        """
        if not query or not query.strip():
            raise ValueError("La consulta no puede estar vacía")

        self.fallback_activado = False

        # RF-02 — si parece nombre exacto, prioriza motor léxico
        if self._es_busqueda_exacta(query):
            logger.info(f"Búsqueda exacta detectada | query={query!r}")
            return self.motor_lexico.buscar(query)

        # RF-01 + RF-02 — intenta motor semántico
        try:
            resultados = self.motor_semantico.buscar(query)
            logger.info(f"Motor semántico OK | query={query!r} | resultados={len(resultados)}")
            return resultados

        # RF-03 — fallback si el motor semántico falla
        except Exception as e:
            logger.warning(f"Fallback activado | query={query!r} | error={e}")
            self.fallback_activado = True
            return self.motor_lexico.buscar(query)

    def _es_busqueda_exacta(self, query: str) -> bool:
        """Heurística simple: query corta (≤2 palabras) = probable nombre exacto."""
        palabras = query.strip().split()
        return len(palabras) <= 2
