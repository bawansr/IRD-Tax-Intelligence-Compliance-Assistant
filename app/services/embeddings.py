"""
Embedding service using local HuggingFace model 
"""
from langchain_community.embeddings import HuggingFaceEmbeddings

class EmbeddingService:
    def get_embedding_model(self):
        """
        Returns a local embedding model.
        Model: all-MiniLM-L6-v2 (Standard for RAG, fast on CPU)
        """
        # This runs locally on computer.
        return HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )