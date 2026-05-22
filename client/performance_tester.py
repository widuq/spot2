import requests
import time

def test_busqueda(query_texto):
    url = "http://127.0.0.1:8000/search"
    payload = {"text": query_texto}
    
    start_time = time.time()
    response = requests.get(url, params={"q": "Canción de prueba"})
    end_time = time.time()
    
    if response.status_code == 200:
        latencia = (end_time - start_time) * 1000
        print(f"✅ Resultado recibido en {latencia:.2f} ms")
        print(response.json())
    else:
        print("❌ Error en la conexión")

if __name__ == "__main__":
    # Simulamos una consulta desde el cliente
    test_busqueda("Música relajante para estudiar en la Uniquindio")