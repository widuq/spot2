import logging
import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.services.search_engine import HybridSearchEngine

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Spotify Search 2.0 - Armenia Project",
    description=(
        "API de búsqueda híbrida (semántica + léxica). "
        "Implementa RF-01, RF-02, RF-03, RF-04 del TRD. "
        "Ver SCOPE.md para el alcance declarado completo."
    ),
    version="1.0.0",
)

# ── CORS — seguridad: permite HTML local hablar con el backend ────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ── Motor de búsqueda (singleton) ─────────────────────────────────────────────
engine = HybridSearchEngine()


# ── Schemas ───────────────────────────────────────────────────────────────────
class SearchRequest(BaseModel):
    q: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def read_root():
    """Health check — verifica que el servicio está en línea."""
    return {
        "message": "⚓ Bienvenido al sistema de búsqueda de Spotify v2",
        "location": "Armenia, Quindío",
        "status": "Online",
        "docs": "/docs",
    }


@app.get("/search")
async def search_get(q: str = Query(..., min_length=1, description="Texto de búsqueda")):
    """RF-04 — Búsqueda vía GET (conveniente para pruebas manuales).

    Retorna canciones que coincidan semánticamente o léxicamente con la query.
    """
    try:
        return engine.execute_search(q)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error en búsqueda GET | query={q!r} | error={e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@app.post("/search")
async def search_post(body: SearchRequest):
    """RF-04 — Búsqueda vía POST (endpoint declarado en el TRD).

    Acepta JSON con campo `q`. Retorna las mismas canciones que GET /search.
    """
    try:
        return engine.execute_search(body.q)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error en búsqueda POST | query={body.q!r} | error={e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@app.get("/health")
def health():
    """Endpoint de health check para el pipeline de CI."""
    return {"status": "healthy", "engine": "HybridSearchEngine"}
