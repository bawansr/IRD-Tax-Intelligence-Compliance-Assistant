"""Vector database management."""
import shutil
import os
from typing import List, Optional
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from app.config import settings

# Import your new Embedding Service
from app.services.embeddings import EmbeddingService

class VectorDBService:
    """Manage vector database operations."""
    
    def __init__(self):
        """
        Initialize vector database service.
        We initialize the embedding model here automatically.
        """
        # 1. Initialize the Embedding Service we just created
        embedding_service = EmbeddingService()
        self.embedding_model = embedding_service.get_embedding_model()
        
        self.persist_directory = settings.VECTOR_DB_PATH
        self.vectorstore: Optional[Chroma] = None
        
        # Ensure directory structure exists
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
    
    def create_vectorstore(self, documents: List[Document], force_refresh: bool = False) -> Chroma:
        """
        Create vector store from documents.
        """
        # 1. Clear old data if requested
        if force_refresh and os.path.exists(self.persist_directory):
            print(f"Clearing existing database at {self.persist_directory}...")
            shutil.rmtree(self.persist_directory)
            os.makedirs(self.persist_directory) # Recreate empty folder

        print(f"Creating Vector Database with {len(documents)} chunks...")
        
        try:
            # 2. Create and Persist
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embedding_model,  # Use the model we loaded
                persist_directory=self.persist_directory
            )
            print(f"  Success! Database saved to {self.persist_directory}")
            return self.vectorstore
            
        except Exception as e:
            print(f"   Error creating vector store: {e}")
            raise e

    def load_vectorstore(self) -> Optional[Chroma]:
        """Load existing vector store."""
        print(f"Loading Vector Store from {self.persist_directory}...")
        try:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_model 
            )
            return self.vectorstore
        except Exception as e:
            print(f"  Error loading vector store: {e}")
            return None
    
    def get_retriever(self, k: int = 3):
        """Get retriever from vector store."""
        if self.vectorstore is None:
            self.load_vectorstore()
        
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized")
        
        return self.vectorstore.as_retriever(
            search_kwargs={"k": k}
        )
        
    def add_documents(self, documents: List[Document]):
        """
        Add new documents to the existing vector store.
        """
        if self.vectorstore is None:
            self.load_vectorstore()

        if self.vectorstore is None:
            # If DB doesn't exist yet, create it
            self.create_vectorstore(documents)
        else:
            print(f"Adding {len(documents)} new chunks to Vector Store...")
            self.vectorstore.add_documents(documents)
            print(" Added successfully.")