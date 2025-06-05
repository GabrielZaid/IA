import requests
import json
import os

# Configuración de Ollama
url = "http://localhost:11434/api/embeddings"
headers = {"Content-Type": "application/json"}
model_name = "nomic-embed-text"

def get_embedding(text):
    """Genera el embedding para un texto dado usando Ollama."""
    data = {
        "model": model_name,
        "prompt": text
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status() # Lanza un error para códigos de estado HTTP 4xx/5xx
        return response.json()["embedding"]
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con Ollama o al generar embedding: {e}")
        print(f"Asegúrate de que Ollama está corriendo y el modelo '{model_name}' está descargado.")
        return None

# Directorio donde se encuentran tus archivos de texto
data_dir = "." # Asume que tus .txt están en el mismo directorio que este script

embeddings_data = []
document_ids = []
documents_content = []

# Leer cada archivo .txt y generar su embedding
for filename in os.listdir(data_dir):
    if filename.endswith(".txt"):
        filepath = os.path.join(data_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            print(f"Generando embedding para: {filename}...")
            embedding = get_embedding(content)
            if embedding:
                embeddings_data.append(embedding)
                document_ids.append(os.path.splitext(filename)[0]) # Usa el nombre del archivo sin extensión como ID
                documents_content.append(content)
            else:
                print(f"No se pudo generar embedding para {filename}. Ignorando este documento.")

print("\nEmbeddings generados exitosamente para los siguientes documentos:")
for i, doc_id in enumerate(document_ids):
    print(f"- {doc_id}: {embeddings_data[i][:5]}...") # Muestra las primeras 5 dimensiones