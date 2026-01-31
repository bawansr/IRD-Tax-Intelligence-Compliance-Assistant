import os
import sys

# Add the parent directory to Python path so we can find 'app'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.loader import DocumentLoader
from app.services.chunker import TextChunker
from app.services.vector_db import VectorDBService

# Define where your PDFs are
DATA_FOLDER = "data/raw"

def main():
    print("Starting ingestion process...")

    # 1. Load PDFs using DocumentLoader
    document_loader = DocumentLoader(data_path=DATA_FOLDER)
    documents = document_loader.load_all_pdfs()

    if not documents:
        print("No documents found to ingest.")
        return

    # 2. Split Text (Chunks)
    print("Splitting documents...")
    text_chunker = TextChunker()
    chunks = text_chunker.split_documents(documents)
    print(f" Generated {len(chunks)} chunks.")

    # 3. Save to Vector Database
    vector_db = VectorDBService() 
    vector_db.create_vectorstore(chunks, force_refresh=True)

    print("Ingestion complete")

if __name__ == "__main__":
    main()