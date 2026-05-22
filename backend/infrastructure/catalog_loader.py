import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class CatalogLoader:

    @staticmethod
    def load() -> list:
        ruta = os.getenv("CATALOG_PATH", "data/catalog.json")

        if not Path(ruta).exists():
            raiz = Path(__file__).resolve().parent.parent.parent
            ruta = str(raiz / "data" / "catalog.json")

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                catalogo = json.load(f)
            logger.info(f"Catálogo cargado | canciones={len(catalogo)} | ruta={ruta}")
            return catalogo
        except FileNotFoundError:
            logger.error(f"Catálogo no encontrado | ruta={ruta}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando catálogo | error={e}")
            raise