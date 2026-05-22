import logging

logger = logging.getLogger(__name__)


class LexicalEngine:
    """Motor de búsqueda léxica sobre el catálogo en memoria.

    Implementa búsqueda por coincidencia de texto sobre campos clave
    de cada canción. Se usa como motor primario para búsquedas exactas
    (RF-02) y como fallback cuando el motor semántico falla (RF-03).

    El score de cada campo está ponderado: título > artista > género > mood > descripción.
    """

    _PESOS = {
        "title": 1.0,
        "artist": 0.85,
        "genre": 0.55,
        "mood": 0.45,
        "description": 0.30,
    }

    def __init__(self, catalogo: list):
        if not catalogo:
            raise ValueError("El catálogo no puede estar vacío")
        self._catalogo = catalogo
        logger.info(f"LexicalEngine inicializado | canciones={len(catalogo)}")

    def buscar(self, query: str) -> list:
        """Busca canciones cuyo texto coincida con la query.

        Args:
            query: Texto de búsqueda (case-insensitive).

        Returns:
            Lista de canciones ordenadas por score descendente (máx. 5).
            Cada ítem incluye los campos de la canción + 'score' + 'search_type'.
        """
        if not query or not query.strip():
            raise ValueError("La consulta no puede estar vacía")

        q = query.strip().lower()
        resultados = []

        for cancion in self._catalogo:
            score = self._calcular_score(q, cancion)
            if score > 0:
                resultados.append({
                    **cancion,
                    "score": score,
                    "search_type": "lexical"
                })

        resultados.sort(key=lambda x: x["score"], reverse=True)
        top5 = resultados[:5]

        logger.info(f"Búsqueda léxica | query={query!r} | encontrados={len(top5)}")
        return top5

    # ─── helpers ─────────────────────────────────────────────────────────────

    def _calcular_score(self, query: str, cancion: dict) -> float:
        """Calcula un score numérico para una canción dada la query."""
        score = 0.0
        for campo, peso in self._PESOS.items():
            valor = cancion.get(campo, "").lower()
            if query in valor:
                score += peso
        return round(score * 100, 2)
