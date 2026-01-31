import sys
import traceback

try:
    print("Step 1: Importing langchain_openai...")
    from langchain_openai import OpenAIEmbeddings
    print("✓ langchain_openai imported")
    
    print("\nStep 2: Importing app.config...")
    from app.config import settings
    print("✓ app.config imported")
    print(f"  Settings: {settings}")
    
    print("\nStep 3: Defining EmbeddingService...")
    class EmbeddingService:
        """Manage embedding models."""
        
        def __init__(self):
            """Initialize embedding service."""
            self.embeddings = self._create_embeddings()
        
        def _create_embeddings(self):
            """Create embedding model instance."""
            return OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                openai_api_key=settings.OPENAI_API_KEY
            )
        
        def get_embeddings(self):
            """Get the embeddings instance."""
            return self.embeddings
    
    print("✓ EmbeddingService class defined")
    
    print("\nStep 4: Now trying to import from embeddings.py...")
    from app.services.embeddings import EmbeddingService as ES
    print("✓ EmbeddingService imported successfully")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    traceback.print_exc()
