"""Text chunking utilities for document processing."""
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.config import settings

class TextChunker:
    """Split documents into chunks for processing."""
    
    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ):
        """
        Initialize text chunker.
        """
        # Prioritize arguments -> Settings -> Defaults
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks with logging.
        """
        # 1. Safety Check: Handle empty input
        if not documents:
            print("⚠️  Warning: No documents provided to chunker.")
            return []

        print(f"✂️  Splitting {len(documents)} pages...")
        
        # 2. Split
        try:
            chunks = self.text_splitter.split_documents(documents)
            
            # 3. Logging: Critical for debugging ingestion
            print(f"   ✅ Success: Created {len(chunks)} chunks from {len(documents)} pages.")
            return chunks
            
        except Exception as e:
            print(f"   ❌ Error during chunking: {e}")
            return []
    
    def split_text(self, text: str) -> List[str]:
        """
        Split raw text into chunks.
        """
        if not text:
            return []
        return self.text_splitter.split_text(text)