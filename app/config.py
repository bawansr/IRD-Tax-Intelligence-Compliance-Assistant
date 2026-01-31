import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Settings:
    # --- Application Configuration ---
    APP_NAME: str = "IRD Tax Assistant"
    
    # --- API KEYS (Keep these null in code!) ---
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    
    # --- Model Configuration ---
    # Using 'gpt-4o' or 'gpt-3.5-turbo' for the brain
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")
    # Using 'text-embedding-3-small' for the memory (cheap & fast)
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.0"))
    
    # --- Chunking Configuration ---
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # --- Vector DB Configuration ---
    VECTOR_DB_TYPE: str = os.getenv("VECTOR_DB_TYPE", "chroma")
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "data/vector_store")
    
    # --- API Configuration ---
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # --- Data paths ---
    RAW_DATA_PATH: str = "data/raw"

settings = Settings()