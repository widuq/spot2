import logging
import os

logger = logging.getLogger(__name__)


class Orchestrator:

    def __init__(self, motor_lexico, motor_semantico):
        self.motor_lexico = motor_lexico
        self.motor_semantico = motor_semantico
        self.fallback_activado = False

    def buscar(self, query: str) -> list:
        if not query or not query.strip():
            raise ValueError("La consulta no puede estar vacía")

        self.fallback_activado = False

        # RF-02 — si parece nombre exacto, prioriza motor léxico
        if self._es_busqueda_exacta(query):
            logger.info(f"Búsqueda exacta detectada | query={query}")
            return self.motor_lexico.buscar(query)

        # RF-01 + RF-02 — intenta motor semántico
        try:
            resultados = self.motor_semantico.buscar(query)
            logger.info(f"Motor semántico OK | query={query} | resultados={len(resultados)}")
            return resultados

        # RF-03 — fallback si el motor semántico falla
        except Exception as e:
            logger.warning(f"Fallback activado | query={query} | error={e}")
            self.fallback_activado = True
            return self.motor_lexico.buscar(query)

    def _es_busqueda_exacta(self, query: str) -> bool:
        # Heurística simple: query corta sin espacios = probable nombre de artista
        palabras = query.strip().split()
        return len(palabras) <= 2