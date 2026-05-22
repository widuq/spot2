# SCOPE.md — Alcance Declarado

> **Proyecto:** Spotify Search 2.0 — Motor de búsqueda híbrida  
> **Equipo:** Yamis, Mariana Ramírez Colorado, Wison Delgado Viveros  
> **Curso:** Ingeniería de Software II — Universidad del Quindío  
> **Stack:** FastAPI / Python 3.12

Este documento especifica qué requisitos del TRD se implementaron y cuáles no,
con justificación explícita. Es el primer artefacto que lee el evaluador.

---

## Requisitos Funcionales (RF)

| RF    | Descripción                                              | Estado           |
|-------|----------------------------------------------------------|------------------|
| RF-01 | Transformar consultas en embeddings vectoriales (SBERT) | ✅ Implementado  |
| RF-02 | Orquestación híbrida: priorizar coincidencia exacta      | ✅ Implementado  |
| RF-03 | Fallback léxico ante fallo del motor semántico           | ✅ Implementado  |
| RF-04 | Endpoint `GET /search` que retorna resultados combinados | ✅ Implementado  |
| RF-05 | Ordenar resultados por score combinado (léxico + semántico 70/30) | ❌ No implementado — ver justificación |

### RF-05 — Justificación de no implementación

El ordenamiento combinado 70/30 requiere que RF-01 y RF-02 estén completamente
integrados con el catálogo real de Spotify (>1M canciones). En el entorno académico
no tenemos acceso a la Spotify Audio Features API, por lo que se priorizó dejar
ambos motores funcionando de forma aislada y correctamente probados antes de
conectar el ranking final. **La lógica de combinación está diseñada en el
orquestador pero no conectada al endpoint final** — es trabajo pendiente que no
rompe los tests existentes.

---

## Decisiones de Diseño (desviaciones del TRD original)

| Decisión          | TRD original        | Implementado                  | Justificación                                                     |
|-------------------|---------------------|-------------------------------|-------------------------------------------------------------------|
| Stack API         | Java / Spring Boot  | **FastAPI / Python**          | Mismo ecosistema que SBERT; menor fricción para el equipo.        |
| Catálogo          | Spotify real        | **JSON de 10 canciones**      | Sin acceso a Spotify Audio Features API en entorno académico.     |
| Comunicación interna | gRPC             | **Llamadas directas (mismo proceso)** | Módulos preparados para extraerse a microservicios con mínimo cambio. |
| Motor LLM         | Ollama integrado    | **Cliente HTTP opcional**     | Ollama no disponible en entorno local; el cliente está aislado con timeout configurable. |

---

## Lo que NO se implementó y por qué

| Ítem                          | Justificación                                                            |
|-------------------------------|--------------------------------------------------------------------------|
| RF-05 — Ranking 70/30         | Requiere RF-01 y RF-02 completamente integrados con catálogo real.       |
| Pruebas de performance (Locust) | Sin infraestructura cloud; el objetivo de 5.000 req/s no es validable en local. |
| Auto-scaling y feature flags  | Fuera del alcance del entorno académico. La arquitectura está preparada para agregarlo. |
| Catálogo real (>1M canciones) | Se usa catálogo de prueba de 10 canciones. La lógica es idéntica a escala real. |

---

## Cobertura de pruebas

| Módulo                          | Tipo          | Tests                          |
|---------------------------------|---------------|--------------------------------|
| `VectorLibrary`                 | Unitario      | happy path, vectores perpendiculares, inventario vacío |
| `Orchestrator`                  | Unitario      | RF-02 exacta, artista inexistente, RF-03 fallback, sin propagación de excepción |
| `LexicalEngine`                 | Unitario      | happy path, query vacía, sin resultados, case-insensitive |
| `SemanticEngine`                | Unitario      | error sin modelo, embedding con mock |
| `GET /search` (API)             | Integración   | 200 válida, 422 vacía, ruta raíz |

---

## Estructura del repositorio

```
spotify-search/
├── .github/workflows/ci.yml     # Pipeline CI completo
├── backend/
│   ├── api/main.py              # FastAPI — endpoint /search
│   ├── application/orchestrator.py   # RF-01, RF-02, RF-03
│   ├── domain/semantic_engine.py     # Motor semántico SBERT
│   ├── infrastructure/
│   │   ├── vector_store.py      # VectorLibrary (similitud coseno)
│   │   ├── lexical_engine.py    # Motor léxico (búsqueda por texto)
│   │   ├── catalog_loader.py    # Carga catalog.json
│   │   └── ollama_client.py     # Cliente HTTP opcional para LLM
│   └── services/search_engine.py    # HybridSearchEngine (punto de entrada)
├── data/catalog.json            # 10 canciones de prueba
├── tests/
│   ├── unit/                    # Pruebas unitarias (mocks/stubs/fakes)
│   └── integration/             # Pruebas de integración con TestClient
├── SCOPE.md                     # Este documento (obligatorio)
├── requirements.txt
├── pytest.ini
└── .env.example
```
