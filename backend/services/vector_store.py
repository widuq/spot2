import numpy as np

class VectorLibrary:
    def __init__(self):
        # Este es nuestro "Diccionario de ADN"
        # En un sistema real, esto vendría de una base de datos como PostgreSQL o ChromaDB
        self.inventory = []

    def add_to_inventory(self, song_data, vector):
        """Asocia la info de la canción con su ADN matemático"""
        self.inventory.append({
            "metadata": song_data,  # Título, artista, género
            "vector": np.array(vector) # El 'ADN' de 384 dimensiones
        })

    def find_near(self, query_vector, limit=3):
        """Compara el ADN de la búsqueda contra todo el inventario"""
        query_vec = np.array(query_vector)
        results = []

        for item in self.inventory:
            # Fórmula de Similitud de Coseno: mide el ángulo entre los dos ADN
            dot_product = np.dot(query_vec, item["vector"])
            norm_q = np.linalg.norm(query_vec)
            norm_i = np.linalg.norm(item["vector"])
            
            similarity = dot_product / (norm_q * norm_i)
            
            results.append({
                "song": item["metadata"],
                "score": round(float(similarity) * 100, 2) # Porcentaje de parecido
            })

        # Ordenamos: la que tenga mayor score (más parecida) va primero
        return sorted(results, key=lambda x: x["score"], reverse=True)[:limit]