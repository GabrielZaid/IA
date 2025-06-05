# Proyecto: Generación de Embeddings y Fine-Tuning para Chatbot

Este proyecto tiene como objetivo procesar información proveniente de archivos `.txt` y PDFs para generar embeddings y preparar un dataset para fine-tuning de un modelo de lenguaje. El resultado final es un chatbot capaz de responder preguntas basadas en el conocimiento extraído de los documentos.

## Funcionalidades Principales

1. **Extracción de Texto de PDFs:**
   - Se utiliza `pdfplumber` para extraer texto de archivos PDF.
   - El texto extraído se fragmenta en bloques manejables para generar embeddings.

2. **Procesamiento de Archivos `.txt`:**
   - Los archivos `.txt` deben estar en formato JSON con pares `pregunta` y `respuesta`.
   - Estos pares se procesan para generar embeddings y preparar un dataset para fine-tuning.

3. **Generación de Embeddings:**
   - Se utiliza el modelo Ollama para generar embeddings de los fragmentos de texto.
   - Los embeddings se guardan en archivos `.jsonl` (`embeddings_txt.jsonl` y `embeddings_pdf.jsonl`) para evitar recalcularlos en futuras ejecuciones.

4. **Creación de Colección en ChromaDB:**
   - Los embeddings generados se almacenan en una colección de ChromaDB para realizar búsquedas semánticas.

5. **Preparación de Dataset para Fine-Tuning:**
   - Se genera un archivo `dataset_bioetica.jsonl` que contiene pares `input` y `output` para entrenar un modelo de lenguaje.

6. **Chatbot Basado en RAG (Retrieval-Augmented Generation):**
   - El chatbot utiliza los embeddings almacenados en ChromaDB para encontrar fragmentos relevantes.
   - Los fragmentos relevantes se utilizan como contexto para generar respuestas lógicas y explicativas.

## Estructura del Proyecto

```
Practica3/
│
├── generacion_embeddings/
│   ├── aborto.txt
│   ├── aborto en méxico.pdf
│   ├── aborto1.pdf
│   ├── Eutanasia .txt
│   ├── EUTANASIA.pdf
│   ├── Eutanasia2.pdf
│   ├── embeddings_pdf.jsonl
│   ├── embeddings_txt.jsonl
│   ├── dataset_bioetica.jsonl
│   ├── usar_chroma.py
│   └── main.py
│
├── finturing/
│   ├── train.py
│   └── test.py
│
└── readm.md
```

## Requisitos

- Python 3.8+
- Librerías necesarias (instalar con `pip install -r requirements.txt`):
  - `pdfplumber`
  - `chromadb`
  - `requests`

## Cómo Ejecutar

1. **Preparar el Entorno:**
   - Asegúrate de que los archivos `.txt` y PDFs estén en el directorio `generacion_embeddings/`.
   - Instala las dependencias necesarias.

2. **Generar Embeddings y Dataset:**
   - Ejecuta el script `usar_chroma.py`:
     ```bash
     python usar_chroma.py
     ```
   - Esto generará los archivos `embeddings_pdf.jsonl`, `embeddings_txt.jsonl` y `dataset_bioetica.jsonl`.

3. **Entrenar el Modelo (Fine-Tuning):**
   - Usa el archivo `dataset_bioetica.jsonl` para entrenar tu modelo de lenguaje.

4. **Ejecutar el Chatbot:**
   - Integra el modelo fine-tuned con el pipeline de RAG para responder preguntas.

## Notas

- Los embeddings se guardan en archivos `.jsonl` para evitar recalcularlos en futuras ejecuciones.
- Asegúrate de que los IDs generados para los documentos sean únicos para evitar conflictos en ChromaDB.
- El enlace al video explicativo: https://youtu.be/TGvgD-VYMNo
