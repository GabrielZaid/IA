import os
import json
import pdfplumber
import chromadb
import requests

# Configuración de Ollama
OLLAMA_URL = "http://localhost:11434/api/embeddings"
OLLAMA_HEADERS = {"Content-Type": "application/json"}
OLLAMA_MODEL = "nomic-embed-text"

def get_embedding(text):
    data = {
        "model": OLLAMA_MODEL,
        "prompt": text
    }
    try:
        response = requests.post(OLLAMA_URL, headers=OLLAMA_HEADERS, data=json.dumps(data))
        response.raise_for_status()
        return response.json()["embedding"]
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con Ollama o al generar embedding: {e}")
        return None

def extraer_texto_pdf(pdf_path):
    texto = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                texto += page_text + "\n"
    return texto

def fragmentar_texto(texto, max_length=500):
    # Fragmenta el texto en párrafos o bloques de longitud máxima
    fragmentos = []
    actual = ""
    for linea in texto.split("\n"):
        if len(actual) + len(linea) < max_length:
            actual += " " + linea.strip()
        else:
            if actual.strip():
                fragmentos.append(actual.strip())
            actual = linea.strip()
    if actual.strip():
        fragmentos.append(actual.strip())
    return [f for f in fragmentos if len(f) > 50]  # descarta fragmentos muy cortos

def cargar_txt_json(data_dir):
    # Carga los archivos .txt en formato JSON pregunta/respuesta
    pares = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(data_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        pregunta = item.get("pregunta", "").strip()
                        respuesta = item.get("respuesta_ia", "").strip()
                        if pregunta and respuesta:
                            pares.append({"pregunta": pregunta, "respuesta": respuesta})
            except Exception as e:
                print(f"Error leyendo {filename}: {e}")
    return pares

def procesar_pdfs(pdf_dir):
    # Extrae fragmentos de todos los PDFs en el directorio
    fragmentos = []
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            filepath = os.path.join(pdf_dir, filename)
            print(f"Extrayendo texto de {filename}...")
            texto = extraer_texto_pdf(filepath)
            frags = fragmentar_texto(texto)
            for i, frag in enumerate(frags):
                fragmentos.append({
                    "id": f"{os.path.splitext(filename)[0]}_{i}",
                    "contenido": frag
                })
    return fragmentos

def generar_embeddings_y_ids(fragmentos, tipo="pdf"):
    embeddings = []
    ids = []
    contenidos = []
    preguntas = []
    for frag in fragmentos:
        if tipo == "pdf":
            texto = frag["contenido"]
            pregunta = f"Fragmento de {frag['id']}"
            doc_id = frag["id"]
        else:
            texto = frag["respuesta"]
            pregunta = frag["pregunta"]
            doc_id = pregunta[:40].replace(" ", "_")
        embedding = get_embedding(texto)
        if embedding:
            embeddings.append(embedding)
            ids.append(doc_id)
            contenidos.append(texto)
            preguntas.append(pregunta)
    return embeddings, ids, contenidos, preguntas

def crear_coleccion_chroma(nombre_coleccion, embeddings, ids, documentos):
    client = chromadb.Client()
    try:
        client.delete_collection(name=nombre_coleccion)
    except Exception:
        pass
    collection = client.create_collection(name=nombre_coleccion)
    collection.add(
        documents=documentos,
        embeddings=embeddings,
        ids=ids
    )
    print(f"Documentos añadidos a ChromaDB en la colección '{nombre_coleccion}'.")
    return collection

def guardar_jsonl_para_finetune(pares, fragmentos_pdf, output_path):
    # Guarda un archivo .jsonl para fine-tuning
    with open(output_path, "w", encoding="utf-8") as f:
        for par in pares:
            f.write(json.dumps({"input": par["pregunta"], "output": par["respuesta"]}, ensure_ascii=False) + "\n")
        for frag in fragmentos_pdf:
            # Puedes usar el fragmento como contexto y la siguiente línea como respuesta, o solo como contexto
            f.write(json.dumps({"input": frag["contenido"][:100], "output": frag["contenido"]}, ensure_ascii=False) + "\n")
    print(f"Archivo para fine-tuning guardado en {output_path}")

if __name__ == "__main__":
    # 1. Cargar pares pregunta/respuesta de los .txt
    data_dir = "."
    pares_txt = cargar_txt_json(data_dir)

    # 2. Procesar PDFs y fragmentar
    pdf_dir = "."
    fragmentos_pdf = procesar_pdfs(pdf_dir)

    # 3. Generar embeddings para ambos conjuntos
    print("Generando embeddings de textos...")
    emb_txt, ids_txt, cont_txt, preg_txt = generar_embeddings_y_ids(pares_txt, tipo="txt")
    print("Generando embeddings de PDFs...")
    emb_pdf, ids_pdf, cont_pdf, preg_pdf = generar_embeddings_y_ids(fragmentos_pdf, tipo="pdf")

    # 4. Unir todo y crear colección ChromaDB
    embeddings_data = emb_txt + emb_pdf
    document_ids = ids_txt + ids_pdf
    documents_content = cont_txt + cont_pdf
    document_questions = preg_txt + preg_pdf

    collection = crear_coleccion_chroma(
        nombre_coleccion="bioetica_total",
        embeddings=embeddings_data,
        ids=document_ids,
        documentos=documents_content
    )

    # 5. Guardar archivo para fine-tuning
    guardar_jsonl_para_finetune(pares_txt, fragmentos_pdf, "dataset_bioetica.jsonl")

    print("¡Listo! Ahora puedes usar la colección para RAG y el archivo .jsonl para fine-tuning.")