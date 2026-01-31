"""Document loader that orchestrates loading, cleaning, and metadata."""
import os
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

# Import your services
# Note: Ensure your file is named 'metadata_extractor.py' (lowercase)
from app.services.preprocessing import TextPreprocessor
from app.services.metadata_extractor import MetadataExtractor

class DocumentLoader:
    def __init__(self, data_path: str = "data/raw"):
        self.data_path = data_path
        # Initialize helper classes
        self.preprocessor = TextPreprocessor()
        self.meta_extractor = MetadataExtractor()

        if not os.path.exists(data_path):
            os.makedirs(data_path)

    def load_pdf(self, file_path: str) -> List[Document]:
        """
        Loads, cleans, and tags a single PDF file.
        """
        print(f"📄 Loading: {os.path.basename(file_path)}...")
        try:
            # 1. Load Raw PDF
            loader = PyPDFLoader(file_path)
            raw_docs = loader.load()
            
            # 2. Clean Text (Hyphens, Spaces)
            cleaned_docs = self.preprocessor.preprocess_documents(raw_docs)
            
            # 3. Enrich Metadata (Page Numbers, Citations)
            final_docs = self.meta_extractor.process_documents(cleaned_docs, file_path)
            
            print(f"   ✅ Successfully processed {len(final_docs)} pages.")
            return final_docs

        except Exception as e:
            print(f"   ❌ Error loading {file_path}: {e}")
            return []

    def load_all_pdfs(self) -> List[Document]:
        """Loads all PDFs in the data directory."""
        all_documents = []
        
        # Safe check for directory
        if not os.path.exists(self.data_path):
            print(f"⚠️ Directory {self.data_path} not found.")
            return []

        pdf_files = [f for f in os.listdir(self.data_path) if f.endswith('.pdf')]
        
        if not pdf_files:
            print(f"⚠️ No PDFs found in {self.data_path}")
            return []

        print(f"📂 Found {len(pdf_files)} PDF(s) to process.")
        for filename in pdf_files:
            file_path = os.path.join(self.data_path, filename)
            docs = self.load_pdf(file_path)
            all_documents.extend(docs)
            
        return all_documents

    def get_document_info(self) -> Dict[str, Any]:
        """
        Returns statistics about the loaded documents.
        Used by the API /health and /documents endpoints.
        """
        try:
            if not os.path.exists(self.data_path):
                return {"status": "empty", "count": 0, "files": [], "path": self.data_path}
                
            files = [f for f in os.listdir(self.data_path) if f.endswith('.pdf')]
            return {
                "status": "active",
                "count": len(files),
                "files": files,
                "path": self.data_path
            }
        except Exception as e:
            return {
                "status": "error",
                "count": 0,
                "files": [],
                "error": str(e)
            }