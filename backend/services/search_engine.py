from backend.services.ollama_client import OllamaClient

class HybridSearchEngine:
    def __init__(self):
        self.ai_client = OllamaClient()
        
        # MOTOR LÉXICO: Base de datos de prueba
        self.tracks_db = [
            {"id": 1, "title": "Yellow", "artist": "Coldplay", "genre": "Rock"},
            {"id": 2, "title": "Rainy Days", "artist": "V", "genre": "K-Pop"},
            {"id": 3, "title": "Bohemian Rhapsody", "artist": "Queen", "genre": "Rock"},
            {"id": 4, "title": "Triste Recuerdo", "artist": "Antonio Aguilar", "genre": "Ranchera"},
            {"id": 5, "title": "Fix You", "artist": "Coldplay", "genre": "Rock"},
        ]

    def execute_search(self, query: str):
        query_lower = query.lower()

        # 1. Búsqueda Léxica
        lexical_results = [
            track for track in self.tracks_db 
            if query_lower in track['title'].lower() or query_lower in track['artist'].lower()
        ]

        # 2. Búsqueda Semántica
        vector = self.ai_client.get_embedding(query)
        
        return {
            "query": query,
            "results": {
                "lexical_hits": lexical_results,
                "semantic_info": {
                    "vector_size": len(vector),
                    "vector_preview": vector[:5] if vector else "Motor Offline",
                    "status": "✅ GPU Active" if vector else "❌ Using Lexical Only"
                }
            },
            "total_lexical": len(lexical_results)
        }