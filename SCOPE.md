# SCOPE.md — Alcance Declarado

> **Proyecto:** Spotify Search 2.0 — Motor de búsqueda híbrida  
> **Equipo:** Yamis, Mariana Ramírez Colorado, Wison Delgado Viveros  
> **Curso:** Ingeniería de Software II — Universidad del Quindío  
> **Stack:** FastAPI / Python 3.12

Este documento especifica qué requisitos del TRD se implementaron y cuáles no,
con justificación explícita. Es el primer artefacto que lee el evaluador.

---

## Requisitos Funcionales (RF)

| RF    | Descripción                                                       | Estado                                   |
|-------|-------------------------------------------------------------------|------------------------------------------|
| RF-01 | Transformar consultas en embeddings vectoriales (SBERT)           | ✅ Implementado                          |
| RF-02 | Orquestación híbrida: priorizar coincidencia exacta               | ✅ Implementado                          |
| RF-03 | Fallback léxico ante fallo del motor semántico                    | ✅ Implementado                          |
| RF-04 | Endpoint `POST /search` que retorna resultados combinados         | ✅ Implementado (GET disponible también) |
| RF-05 | Ordenar resultados por score combinado (léxico + semántico 70/30) | ❌ No implementado — ver justificación   |

### RF-05 — Justificación de no implementación

El ordenamiento combinado 70/30 requiere que RF-01 y RF-02 estén completamente
integrados con el catálogo real de Spotify (>1M canciones). En el entorno académico
no tenemos acceso a la Spotify Audio Features API, por lo que se priorizó dejar
ambos motores funcionando de forma aislada y correctamente probados antes de
conectar el ranking final. **La lógica de combinación está diseñada en el
orquestador pero no conectada al endpoint final** — es trabajo pendiente que no
rompe los tests existentes.

---

## Criterios de aceptación técnicos implementados (TRD sección 15)

| Criterio TRD                                  | Estado       | Dónde verificarlo                        |
|-----------------------------------------------|--------------|------------------------------------------|
| Cobertura de tests unitarios ≥ 80%            | ✅ 94%       | CI job "Unit Tests (cobertura ≥ 80%)"   |
| Umbral similitud coseno ≥ 0.75                | ✅ Implementado | `vector_store.py` — `UMBRAL_SIMILITUD` |
| Fallback automático ante timeout              | ✅ Implementado | `orchestrator.py` — RF-03              |
| Logs estructurados en flujos críticos         | ✅ Implementado | Todos los módulos usan `logger` JSON    |
| Sin secretos hardcodeados                     | ✅ Verificado en CI | Step "Verificar secretos" en pipeline |
| Latencia p95 ≤ 300ms                          | ⚠️ No validable | Sin infraestructura cloud disponible   |
| Disponibilidad ≥ 99.9%                        | ⚠️ No validable | Sin infraestructura cloud disponible   |

---

## Decisiones de diseño (desviaciones documentadas)

| Decisión             | Design Doc original        | Implementado                      | Justificación                                                      |
|----------------------|----------------------------|-----------------------------------|--------------------------------------------------------------------|
| Arquitectura | Microservicios distribuidos (Design Doc) | **Arquitectura en capas (proceso único FastAPI/Python)** | El Design Doc define una arquitectura de microservicios con contenedores independientes (API Semántica, SBERT, FAISS) comunicándose por gRPC/REST. Por limitaciones de tiempo y recursos del entorno académico, se implementó una arquitectura en capas dentro de un único proceso Python, manteniendo la misma separación de responsabilidades: capa de presentación (api/), capa de aplicación (application/), capa de dominio (domain/) e infraestructura (infrastructure/). Los módulos están diseñados para extraerse a microservicios independientes con cambios mínimos. |                      |
| Motor vectorial      | FAISS IVF-Flat             | VectorLibrary en memoria (numpy)  | FAISS requiere compiladores C no disponibles en el entorno local.  |
| Comunicación interna | gRPC entre microservicios  | Llamadas directas (mismo proceso) | Módulos listos para extraerse a microservicios con mínimo cambio.  |
| Catálogo             | Spotify Audio Features API | JSON de 10 canciones              | Sin acceso a la API en entorno académico. Lógica idéntica a escala real. |


> **Nota sobre la arquitectura:** La decisión de usar capas en lugar de microservicios 
> no afecta la lógica de negocio implementada. RF-01, RF-02, RF-03 y RF-04 funcionan 
> de forma idéntica en ambas arquitecturas. La diferencia es únicamente de despliegue, 
> no de comportamiento.
---

## Lo que NO se implementó y por qué

| Ítem                            | Justificación                                                              |
|---------------------------------|----------------------------------------------------------------------------|
| RF-05 — Ranking 70/30           | Requiere RF-01 y RF-02 completamente integrados con catálogo real.         |
| Pruebas de performance (Locust) | Sin infraestructura cloud; el objetivo de 5.000 req/s no es validable en local. |
| Auto-scaling y feature flags    | Fuera del alcance del entorno académico. La arquitectura está preparada para agregarlo. |
| Catálogo real (>1M canciones)   | Se usa catálogo de prueba de 10 canciones. La lógica es idéntica a escala real. |
| TLS / JWT / autenticación       | Seguridad de red fuera del alcance del entorno académico local.            |
| FAISS IVF-Flat real             | Requiere compiladores C. Se sustituyó por VectorLibrary con interfaz idéntica. |

---

## Cobertura de pruebas

| Módulo          | Tipo        | Escenarios cubiertos                                                              |
|-----------------|-------------|-----------------------------------------------------------------------------------|
| `VectorLibrary` | Unitario    | happy path, umbral 0.75 (TRD), top_k, score descendente, inventario vacío        |
| `Orchestrator`  | Unitario    | RF-02 exacta, artista inexistente, RF-03 fallback, sin propagación de excepción, query vacía |
| `LexicalEngine` | Unitario    | happy path, query vacía, sin resultados, case-insensitive, score, search_type     |
| `OllamaClient`  | Unitario    | respuesta OK (mock HTTP), timeout, prompt vacío, variables de entorno             |
| `CatalogLoader` | Unitario    | 10 canciones, campos obligatorios, JSON inválido, env personalizado               |
| `POST /search`  | Integración | 200 válida, 422 vacía, sin parámetro, POST+GET mismos campos, health check        |

---

## Estructura del repositorio

spot2/
├── .github/workflows/ci.yml          # Pipeline CI: Build+Lint → Unit Tests → Integration
├── backend/
│   ├── api/main.py                   # FastAPI — POST /search + GET /search (RF-04)
│   ├── application/orchestrator.py   # RF-02 (exacta) + RF-03 (fallback)
│   ├── domain/semantic_engine.py     # RF-01 — Motor semántico SBERT
│   ├── infrastructure/
│   │   ├── vector_store.py           # VectorLibrary — similitud coseno + umbral 0.75
│   │   ├── lexical_engine.py         # Motor léxico — búsqueda por texto ponderada
│   │   ├── catalog_loader.py         # Carga data/catalog.json
│   │   └── ollama_client.py          # Cliente HTTP opcional para LLM
│   └── services/search_engine.py     # HybridSearchEngine — punto de entrada
├── data/catalog.json                 # 10 canciones de prueba
├── tests/
│   ├── unit/                         # 39 tests — cobertura 94%
│   └── integration/                  # 12 tests — contrato API completo
├── SCOPE.md                          # Este documento (obligatorio)
├── conftest.py
├── requirements.txt
├── pytest.ini
└── .env.example