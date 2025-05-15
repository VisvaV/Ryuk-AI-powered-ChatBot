from flask import Flask, request, jsonify, render_template
import os
import numpy as np
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from PyPDF2 import PdfReader
import docx
import logging

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini API
GEMINI_API_KEY = "AIzaSyAzbxmAPyzcR595QvjWsTHoIlprJmaKlJQ"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Initialize SentenceTransformer
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# In-memory storage for document chunks and embeddings
documents = []
embeddings = []

# Prompt engineering: System-level instruction (Prompt Before Prompt)
SYSTEM_PROMPT = """
You are an expert assistant designed to provide accurate and concise answers based on provided context. Follow these steps:
1. Analyze the provided context carefully.
2. If the context is relevant, use it to inform your answer.
3. If the context is insufficient or irrelevant, rely on your general knowledge but acknowledge limitations.
4. Avoid hallucinating information not present in the context or your knowledge.
5. Structure your response clearly and concisely.
6. If the question is ambiguous, ask for clarification.
"""

# Main prompt template
MAIN_PROMPT_TEMPLATE = """
{system_prompt}

**Context**:
{context}

**User Question**:
{question}

**Instructions**:
- Provide a concise and accurate answer based on the context if applicable.
- If the context is not relevant, answer using general knowledge and state that no specific context was used.
- Format the response in markdown for clarity.
"""

def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        return ""

def extract_text_from_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            if not text.strip():
                logger.warning(f"File {file_path} is empty.")
            return text
    except UnicodeDecodeError:
        logger.warning(f"UTF-8 decoding failed for {file_path}, trying latin-1")
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                text = file.read()
                if not text.strip():
                    logger.warning(f"File {file_path} is empty.")
                return text
        except Exception as e:
            logger.error(f"Error extracting text from TXT with latin-1: {e}")
            return ""
    except Exception as e:
        logger.error(f"Error extracting text from TXT: {e}")
        return ""

def process_document(file_path, filename):
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    
    if ext == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif ext == '.docx':
        text = extract_text_from_docx(file_path)
    elif ext == '.txt':
        text = extract_text_from_txt(file_path)
    else:
        return None
    
    # Debug: Log the extracted text
    logger.info(f"Extracted text from {filename}: {text[:100]}...")
    
    if not text.strip():
        logger.warning(f"No text extracted from {filename}. Cannot process.")
        return None
    
    # Split text into chunks (increased to 1000 characters)
    chunk_size = 1000
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    if not chunks:
        logger.warning(f"No chunks created for {filename}. Text too short.")
        chunks = [text]  # Use the whole text as a single chunk if too short
    
    # Debug: Log the number of chunks
    logger.info(f"Number of chunks for {filename}: {len(chunks)}")
    
    # Generate embeddings for each chunk
    chunk_embeddings = [embedding_model.encode(chunk) for chunk in chunks]
    
    # Debug: Log the number of embeddings
    logger.info(f"Number of embeddings for {filename}: {len(chunk_embeddings)}")
    
    return chunks, chunk_embeddings

def fetch_relevant_context(question):
    if not embeddings:
        logger.info("No embeddings available. Documents list empty.")
        return ""
    
    # Special case for summary-related questions
    summary_keywords = ["summary", "summarize", "overview"]
    is_summary_request = any(keyword in question.lower() for keyword in summary_keywords) and "upload" in question.lower()
    
    if is_summary_request:
        logger.info("Summary request detected. Using all document content as context.")
        context = "\n\n".join(documents)
        logger.info(f"Summary context: {context[:100]}...")
        return context
    
    try:
        question_embedding = embedding_model.encode(question)
        embeddings_matrix = np.vstack(embeddings)
        similarities = cosine_similarity([question_embedding], embeddings_matrix)[0]
        
        # Debug: Log similarity scores
        logger.info(f"Similarity scores: {similarities}")
        
        # Get top 3 most similar chunks
        top_indices = np.argsort(similarities)[-3:][::-1]
        max_similarity = max(similarities) if similarities.size > 0 else 0
        logger.info(f"Max similarity: {max_similarity}")
        
        if max_similarity < 0.1:  # Lowered threshold
            logger.info("Max similarity below threshold (0.1). No context returned.")
            return ""
        
        context = "\n\n".join([documents[i] for i in top_indices])
        logger.info(f"Retrieved context: {context[:100]}...")
        return context
    except Exception as e:
        logger.error(f"Error fetching context: {e}")
        return ""

def ask_bot(question):
    try:
        context = fetch_relevant_context(question)
        prompt = MAIN_PROMPT_TEMPLATE.format(
            system_prompt=SYSTEM_PROMPT,
            context=context if context else "No specific context provided.",
            question=question
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error contacting Gemini: {e}")
        return f"Error: Could not generate response. {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global documents, embeddings
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        chunks, chunk_embeddings = process_document(file_path, filename)
        if chunks is None:
            return jsonify({'error': 'Unsupported file format'}), 400
        
        documents.extend(chunks)
        embeddings.extend(chunk_embeddings)
        
        # Debug: Log total documents and embeddings after upload
        logger.info(f"Total documents after upload: {len(documents)}")
        logger.info(f"Total embeddings after upload: {len(embeddings)}")
        
        return jsonify({'message': f'File {filename} processed successfully'}), 200

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    question = data.get('question', '')
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    answer = ask_bot(question)
    return jsonify({'answer': answer})

@app.route('/clear', methods=['POST'])
def clear_chat():
    global documents, embeddings
    documents = []
    embeddings = []
    logger.info("Chat history and documents cleared.")
    return jsonify({'message': 'Chat history and documents cleared'}), 200

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)