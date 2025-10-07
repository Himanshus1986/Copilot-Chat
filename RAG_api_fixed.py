"""
HR Policy RAG API - Fixed for Port 8001 with CORS Support
Handles document queries with proper CORS headers
"""

import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import shutil
import ollama
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings

# Initialize FastAPI app
app = FastAPI(title="HR Policy RAG API", version="1.0.0", description="HR Policy document query system")

# Add CORS middleware to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Configuration
EMBEDDING_MODEL_NAME = "nomic-embed-text"  # Ollama embedding model
LLM_MODEL_NAME = "gemma:2b"  # Local Llama model via Ollama
CHROMA_PERSIST_DIR = './hr_policy_chroma_db'
UPLOAD_DIR = './hr_policy_pdfs'

# Ensure directories exist
os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize embedding model
try:
    embedding = OllamaEmbeddings(model=EMBEDDING_MODEL_NAME)
    print(f"✅ Initialized embedding model: {EMBEDDING_MODEL_NAME}")
except Exception as e:
    print(f"❌ Failed to initialize embedding model: {e}")
    embedding = None

# Global variable for vectorstore
vectorstore = None

# Data models
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str] = []

def process_pdfs(pdf_filepaths: List[str]):
    """Process PDF files and create vector embeddings"""
    global vectorstore

    if not embedding:
        raise HTTPException(status_code=500, detail="Embedding model not available")

    all_docs = []

    for pdf_file in pdf_filepaths:
        try:
            loader = PyPDFLoader(pdf_file)
            documents = loader.load()
            all_docs.extend(documents)
            print(f"✅ Loaded {len(documents)} pages from {pdf_file}")
        except Exception as e:
            print(f"❌ Error loading {pdf_file}: {str(e)}")
            continue

    if not all_docs:
        raise HTTPException(status_code=400, detail="No documents could be processed")

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )

    docs_chunks = text_splitter.split_documents(all_docs)
    print(f"📄 Created {len(docs_chunks)} document chunks")

    # Create or update vectorstore
    try:
        if os.path.exists(CHROMA_PERSIST_DIR) and os.listdir(CHROMA_PERSIST_DIR):
            # Load existing vectorstore and add new documents
            vectorstore = Chroma(persist_directory=CHROMA_PERSIST_DIR, embedding_function=embedding)
            vectorstore.add_documents(docs_chunks)
        else:
            # Create new vectorstore
            vectorstore = Chroma.from_documents(
                docs_chunks,
                embedding,
                persist_directory=CHROMA_PERSIST_DIR
            )

        vectorstore.persist()
        print("✅ Vector database updated successfully")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating vector database: {str(e)}")

@app.get("/")
def read_root():
    return {
        "message": "HR Policy RAG API is running!",
        "status": "healthy",
        "port": 8001,
        "endpoints": {
            "query": "POST /query - Ask questions about HR policies",
            "upload": "POST /upload_pdfs - Upload policy documents",
            "health": "GET /health - Health check",
            "clear": "DELETE /clear_database - Clear all data"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test Ollama connection
        models = ollama.list()
        ollama_status = "connected"

        # Check if required model is available
        available_models = [model['name'] for model in models.get('models', [])]
        model_available = LLM_MODEL_NAME in available_models

        return {
            "status": "healthy",
            "ollama": ollama_status,
            "embedding_model": EMBEDDING_MODEL_NAME,
            "llm_model": LLM_MODEL_NAME,
            "model_available": model_available,
            "vectorstore_ready": vectorstore is not None
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "vectorstore_ready": vectorstore is not None
        }

@app.post("/upload_pdfs")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    """Upload and process HR policy PDF files"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    uploaded_paths = []

    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            uploaded_paths.append(file_path)
            print(f"📤 Uploaded: {file.filename}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving {file.filename}: {str(e)}")

    # Process the uploaded PDFs
    try:
        process_pdfs(uploaded_paths)
        return {
            "message": f"Successfully processed {len(uploaded_paths)} HR policy PDF files",
            "files": [os.path.basename(path) for path in uploaded_paths]
        }

    except Exception as e:
        # Clean up uploaded files if processing fails
        for path in uploaded_paths:
            if os.path.exists(path):
                os.remove(path)
        raise HTTPException(status_code=500, detail=f"Error processing PDFs: {str(e)}")

@app.post("/query", response_model=QueryResponse)
def query_pdf(request: QueryRequest):
    """Query the HR policy documents"""
    global vectorstore

    if vectorstore is None:
        # Try to load existing vectorstore
        if os.path.exists(CHROMA_PERSIST_DIR) and os.listdir(CHROMA_PERSIST_DIR):
            try:
                vectorstore = Chroma(persist_directory=CHROMA_PERSIST_DIR, embedding_function=embedding)
                print("📚 Loaded existing vectorstore")
            except Exception as e:
                print(f"❌ Error loading vectorstore: {e}")
                raise HTTPException(status_code=400, detail="No documents loaded. Please upload HR policy PDFs first.")
        else:
            raise HTTPException(status_code=400, detail="No documents loaded. Please upload HR policy PDFs first.")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        print(f"🔍 Processing query: {request.question}")

        # Retrieve relevant chunks using vectorstore
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )

        relevant_docs = retriever.get_relevant_documents(request.question)

        if not relevant_docs:
            return QueryResponse(
                answer="I couldn't find relevant information in the HR policy documents to answer your question. Please try rephrasing your question or check if the relevant policies have been uploaded.",
                sources=[]
            )

        # Prepare context from retrieved documents
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        sources = [f"Page {doc.metadata.get('page', 'Unknown')} from {os.path.basename(doc.metadata.get('source', 'Unknown'))}"
                  for doc in relevant_docs]

        # Format prompt for the LLM
        prompt = f"""You are an HR Policy Assistant. Based on the following HR policy documents, please answer the question clearly and professionally.

Context from HR Policy Documents:
{context}

Question: {request.question}

Please provide a comprehensive answer based only on the information provided in the HR policy documents above. If the documents don't contain enough information to fully answer the question, please say so and suggest what additional information might be needed.

Answer:"""

        # Get completion from Ollama chat model locally
        try:
            response = ollama.chat(
                model=LLM_MODEL_NAME,
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response['message']['content']

            print(f"✅ Generated answer for: {request.question[:50]}...")

            return QueryResponse(answer=answer, sources=sources)

        except Exception as ollama_error:
            print(f"❌ Ollama error: {ollama_error}")
            # Fallback response if Ollama fails
            return QueryResponse(
                answer=f"Based on the HR policy documents, I found relevant information but encountered an issue generating the response. Please try again. Error: {str(ollama_error)}",
                sources=sources
            )

    except Exception as e:
        print(f"❌ Query processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.delete("/clear_database")
def clear_database():
    """Clear the vector database and uploaded files"""
    global vectorstore

    try:
        # Clear vectorstore
        if vectorstore:
            vectorstore = None

        # Remove database directory
        if os.path.exists(CHROMA_PERSIST_DIR):
            shutil.rmtree(CHROMA_PERSIST_DIR)
        os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

        # Clear uploaded files
        if os.path.exists(UPLOAD_DIR):
            shutil.rmtree(UPLOAD_DIR)
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        print("🧹 Database and files cleared")
        return {"message": "HR policy database and uploaded files cleared successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing database: {str(e)}")

# Add a simple test endpoint for connectivity
@app.get("/test")
def test_endpoint():
    """Simple test endpoint to verify API is working"""
    return {
        "message": "HR Policy RAG API is working!",
        "timestamp": os.popen('date').read().strip(),
        "status": "ok"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting HR Policy RAG API on port 8001...")
    print("📚 Make sure to upload HR policy PDFs using POST /upload_pdfs before querying")
    print("🔍 Use POST /query to ask questions about HR policies")

    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,  # Changed to port 8001 to avoid conflict with timesheet API
        log_level="info"
    )
