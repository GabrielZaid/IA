import chromadb
import requests
import json
import os
import pdfplumber

# Configuración de Ollama
OLLAMA_URL = "http://localhost:11434/api/embeddings"
OLLAMA_HEADERS = {"Content-Type": "application/json"}
OLLAMA_MODEL = "nomic-embed-text"

def get_embedding(text):
    """Genera el embedding para un texto dado usando Ollama."""
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
        print(f"Asegúrate de que Ollama está corriendo y el modelo '{OLLAMA_MODEL}' está descargado.")
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
    return [f for f in fragmentos if len(f) > 50]

def procesar_pdfs(pdf_dir):
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

def cargar_documentos_y_embeddings_json(data_dir="."):
    """
    Lee archivos .txt que contienen datos JSON de preguntas/respuestas,
    genera embeddings para cada respuesta_ia y retorna listas.
    Cada elemento en el JSON se tratará como un documento individual.
    """
    embeddings_data = []
    document_ids = []
    documents_content = [] # Contendrá solo la respuesta_ia
    # Para el RAG, también podemos almacenar la pregunta original para referencia si es necesario
    document_questions = [] 

    for filename in os.listdir(data_dir):
        if filename.endswith(".txt"): # Asumimos que tus .txt ahora contienen JSON
            filepath = os.path.join(data_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    # Carga el contenido como JSON
                    data = json.load(f) 
                    
                    # Itera sobre cada objeto en el JSON
                    for i, item in enumerate(data):
                        # Usamos la 'respuesta_ia' como el contenido principal para el embedding
                        content_for_embedding = item.get("respuesta_ia", "")
                        # Usamos la 'pregunta' para el ID o referencia
                        original_question = item.get("pregunta", f"pregunta_desconocida_{filename}_{i}")
                        
                        # Genera un ID único para cada fragmento
                        doc_id = f"{os.path.splitext(filename)[0]}_{i}" 
                        
                        # print(f"Generando embedding para: {original_question[:50]}...") # Imprime la pregunta para seguimiento
                        embedding = get_embedding(content_for_embedding)
                        
                        if embedding:
                            embeddings_data.append(embedding)
                            document_ids.append(doc_id)
                            documents_content.append(content_for_embedding)
                            document_questions.append(original_question)
                        else:
                            print(f"No se pudo generar embedding para el item {doc_id}. Ignorando.")
            except json.JSONDecodeError as e:
                print(f"Error al parsear JSON en {filename}: {e}. Asegúrate de que el archivo es un JSON válido.")
            except Exception as e:
                print(f"Error inesperado al procesar {filename}: {e}")
    return embeddings_data, document_ids, documents_content, document_questions # Retornamos la lista de preguntas también

# El resto de tus funciones pueden permanecer igual
def crear_coleccion_chroma(nombre_coleccion, embeddings, ids, documentos):
    """Crea una colección en ChromaDB y añade los documentos y embeddings."""
    client = chromadb.Client()
    try:
        client.delete_collection(name=nombre_coleccion)
    except Exception:
        pass # No hacer nada si la colección no existe
    collection = client.create_collection(name=nombre_coleccion)
    collection.add(
        documents=documentos, # Asegúrate de que esto es solo el texto de la respuesta
        embeddings=embeddings,
        ids=ids
    )
    print(f"Documentos añadidos a ChromaDB en la colección '{nombre_coleccion}'.")
    return collection

def buscar_y_responder(collection, query_text, n_results=1, similarity_threshold=250):
    """Realiza una búsqueda semántica y muestra la pregunta y la respuesta más relevante."""
    print(f"\nPregunta: {query_text}")
    query_embedding = get_embedding(query_text)
    if not query_embedding:
        print("No se pudo generar el embedding para la consulta. Verifique la conexión con Ollama.")
        return

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=['documents', 'distances']  # <-- Solo estos
    )

    if results and results['documents'] and results['documents'][0]:
        distance = results['distances'][0][0]
        # retrieved_id = results['ids'][0][0]  # Ya no disponible aquí

        print(f"Distancia de similitud para el resultado más relevante: {distance:.4f}")

        if distance < similarity_threshold:
            respuesta = results['documents'][0][0]
            print(f"Respuesta-embedding: {respuesta[:500]}{'...' if len(respuesta) > 500 else ''}")
        else:
            print(f"No se encontraron resultados relevantes (distancia {distance:.4f} excede el umbral {similarity_threshold}).")
    else:
        print("No se encontraron resultados relevantes.")

def guardar_embeddings_en_txt(embeddings, ids, filepath):
    """Guarda los embeddings y sus IDs en un archivo .txt para reutilización."""
    with open(filepath, "w", encoding="utf-8") as f:
        for i, embedding in enumerate(embeddings):
            f.write(json.dumps({"id": ids[i], "embedding": embedding}, ensure_ascii=False) + "\n")
    print(f"Embeddings guardados en {filepath}")

def cargar_embeddings_de_txt(filepath):
    """Carga embeddings y sus IDs desde un archivo .txt."""
    embeddings = []
    ids = []
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line.strip())
                ids.append(data["id"])
                embeddings.append(data["embedding"])
        print(f"Embeddings cargados desde {filepath}")
    return embeddings, ids

def generar_embeddings_y_ids(fragmentos, tipo="pdf", embedding_file=None):
    embeddings = []
    ids = []
    contenidos = []
    preguntas = []

    # Cargar embeddings existentes si el archivo está disponible
    if embedding_file:
        embeddings, ids = cargar_embeddings_de_txt(embedding_file)

    for frag in fragmentos:
        if tipo == "pdf":
            texto = frag["contenido"]
            pregunta = f"Fragmento de {frag['id']}"
            doc_id = f"pdf_{frag['id']}"
        else:
            texto = frag["respuesta"]
            pregunta = frag["pregunta"]
            doc_id = f"txt_{pregunta[:40].replace(' ', '_')}"

        # Evitar duplicados si ya existe el ID
        if doc_id in ids:
            continue

        embedding = get_embedding(texto)
        if embedding:
            embeddings.append(embedding)
            ids.append(doc_id)
            contenidos.append(texto)
            preguntas.append(pregunta)

    # Guardar nuevos embeddings en el archivo
    if embedding_file:
        guardar_embeddings_en_txt(embeddings, ids, embedding_file)

    return embeddings, ids, contenidos, preguntas

def cargar_txt_json(data_dir):
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

def guardar_jsonl_para_finetune(pares, fragmentos_pdf, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for par in pares:
            f.write(json.dumps({"input": par["pregunta"], "output": par["respuesta"]}, ensure_ascii=False) + "\n")
        for frag in fragmentos_pdf:
            f.write(json.dumps({"input": frag["contenido"][:100], "output": frag["contenido"]}, ensure_ascii=False) + "\n")
    print(f"Archivo para fine-tuning guardado en {output_path}")

if __name__ == "__main__":
    data_dir = "."
    pares_txt = cargar_txt_json(data_dir)
    pdf_dir = "."
    fragmentos_pdf = procesar_pdfs(pdf_dir)

    # Archivos para guardar/cargar embeddings
    embedding_file_txt = "embeddings_txt.jsonl"
    embedding_file_pdf = "embeddings_pdf.jsonl"

    print("Generando embeddings de textos...")
    emb_txt, ids_txt, cont_txt, preg_txt = generar_embeddings_y_ids(pares_txt, tipo="txt", embedding_file=embedding_file_txt)

    print("Generando embeddings de PDFs...")
    emb_pdf, ids_pdf, cont_pdf, preg_pdf = generar_embeddings_y_ids(fragmentos_pdf, tipo="pdf", embedding_file=embedding_file_pdf)

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

    guardar_jsonl_para_finetune(pares_txt, fragmentos_pdf, "dataset_bioetica.jsonl")
    print("¡Listo! Ahora puedes usar la colección para RAG y el archivo .jsonl para fine-tuning.")

    # Tus preguntas de prueba
    print("\n----------------------------------------------------- Preguntas sobre Aborto ----------------------------------------------------")
    buscar_y_responder(collection, "¿Tiene una persona el derecho exclusivo a decidir sobre su cuerpo cuando hay otra vida en desarrollo?", similarity_threshold=250)
    buscar_y_responder(collection, "¿Hasta qué punto el lenguaje utilizado (“interrupción” vs. “terminación”) influye en la percepción ética del aborto?", similarity_threshold=250)
    buscar_y_responder(collection, "¿Qué principios éticos (utilitarismo, deontología, ética del cuidado) pueden respaldar o rechazar el aborto inducido?", similarity_threshold=250)
    buscar_y_responder(collection, "¿Puede una inteligencia artificial participar de forma ética en decisiones sobre aborto?", similarity_threshold=250)
    buscar_y_responder(collection, "¿Qué riesgos éticos implica delegar información médica sensible a sistemas automatizados?", similarity_threshold=250)

    print("\n----------------------------------------------------- Preguntas sobre Eutanasia ----------------------------------------------------")
    buscar_y_responder(collection, "¿Es éticamente válido que una persona decida poner fin a su vida en situaciones de sufrimiento irreversible?", similarity_threshold=250)
    buscar_y_responder(collection, "¿Cuál es la diferencia entre eutanasia activa, pasiva y el suicidio asistido? ¿Importa éticamente?", similarity_threshold=250)
    buscar_y_responder(collection, "¿Qué papel podrían (o no deberían) tener los sistemas de inteligencia artificial en este tipo de decisiones?", similarity_threshold=250)
    buscar_y_responder(collection, "¿Qué sucede cuando el deseo de morir entra en conflicto con creencias religiosas, leyes o protocolos médicos?", similarity_threshold=250)
    buscar_y_responder(collection, "¿Se puede hablar de una “muerte digna” sin considerar el contexto emocional y humano?", similarity_threshold=250)

    print("\n----------------------------------------------------- Pregunta fuera de contexto ----------------------------------------------------")
    buscar_y_responder(collection, "¿Cómo puedo mejorar la eficiencia de la generación de embeddings si tengo muchos documentos?", similarity_threshold=250)