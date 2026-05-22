from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from backend.services.search_engine import HybridSearchEngine

app = FastAPI(
    title="Spotify Search 2.0 - Armenia Project",
    description="API de búsqueda híbrida para la Guía 8"
)

# Configuración de seguridad para que el HTML pueda hablar con el Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializamos el motor de búsqueda
engine = HybridSearchEngine()

@app.get("/")
def read_root():
    return {
        "message": "⚓ Bienvenido al sistema de búsqueda de Spotify v2",
        "location": "Armenia, Quindío",
        "status": "Online"
    }

@app.get("/search")
async def search(q: str = Query(..., min_length=1)):
    results = engine.execute_search(q)
    return results