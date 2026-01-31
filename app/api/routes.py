"""API routes for IRD Tax Assistant."""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import shutil
from pathlib import Path

from app.api.schemas import (
    QueryRequest, 
    QueryResponse, 
    SourceDocument, 
    UploadResponse,
    DocumentInfo
)
from app.services.loader import DocumentLoader
from app.services.chunker import TextChunker
from app.services.embeddings import EmbeddingService
from app.services.vector_db import VectorDBService
from app.services.rag_chain import RAGChain
from app.config import settings

router = APIRouter()

# Initialize services
vector_db = VectorDBService()
document_loader = DocumentLoader()
text_chunker = TextChunker()

# Try to load existing vector store
try:
    vector_db.load_vectorstore()
    print("✅ Existing vector store loaded")
except:
    print("⚠️ No existing vector store found")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    doc_info = document_loader.get_document_info()
    
    return {
        "status": "healthy",
        "documents": doc_info,
        "vector_store_initialized": vector_db.vectorstore is not None
    }


@router.get("/documents", response_model=DocumentInfo)
async def list_documents():
    """List all documents in the system."""
    info = document_loader.get_document_info()
    return DocumentInfo(**info)


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process an IRD PDF document.
    
    Only PDF files are accepted.
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are supported"
        )
    
    try:
        # Save file
        file_path = Path(settings.RAW_DATA_PATH) / file.filename
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"📄 Saved: {file.filename}")
        
        # Load and process
        documents = document_loader.load_pdf(str(file_path))
        
        if not documents:
            raise HTTPException(
                status_code=500,
                detail="Failed to load PDF content"
            )
        
        # Split into chunks
        chunks = text_chunker.split_documents(documents)
        print(f"✂️ Created {len(chunks)} chunks")
        
        # Add to vector store
        vector_db.add_documents(chunks)
        print(f"✅ Added to vector store")
        
        return UploadResponse(
            message="Document uploaded and processed successfully",
            filename=file.filename,
            pages_loaded=len(documents),
            chunks_created=len(chunks)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/initialize")
async def initialize_system():
    """
    Initialize the system by loading all PDFs from data/raw directory.
    
    This processes all existing PDFs and creates the vector store.
    """
    try:
        # Load all PDFs
        print("\n🚀 Initializing IRD Tax Assistant System...")
        documents = document_loader.load_all_pdfs()
        
        if not documents:
            return {
                "status": "no_documents",
                "message": "No PDF documents found in data/raw directory",
                "suggestion": "Upload IRD documents using the /upload endpoint"
            }
        
        # Split into chunks
        print("✂️ Splitting documents into chunks...")
        chunks = text_chunker.split_documents(documents)
        print(f"   Created {len(chunks)} chunks")
        
        # Create vector store
        print("🗄️ Creating vector store...")
        vector_db.create_vectorstore(chunks)
        print("   ✅ Vector store created")
        
        print("\n✅ System initialized successfully!\n")
        
        return {
            "status": "success",
            "documents_loaded": len(set(doc.metadata.get('source_file') for doc in documents)),
            "pages_loaded": len(documents),
            "chunks_created": len(chunks),
            "message": "System initialized and ready for queries"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the IRD tax knowledge base.
    
    Returns answers with citations from official IRD documents.
    """
    if vector_db.vectorstore is None:
        raise HTTPException(
            status_code=503,
            detail="System not initialized. Please call /initialize endpoint first or upload documents."
        )
    
    try:
        # Get retriever
        retriever = vector_db.get_retriever(k=request.k)
        
        # Create RAG chain
        rag = RAGChain(retriever)
        
        # Query
        result = rag.query(request.question)
        
        # Format sources
        sources = []
        for citation in result["citations"]:
            sources.append(SourceDocument(
                source=citation["document"],
                page=citation["page"],
                content=citation["content_preview"]
            ))
        
        return QueryResponse(
            answer=result["answer"],
            sources=sources,
            disclaimer="This response is based solely on IRD-published documents and is not professional tax advice."
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))