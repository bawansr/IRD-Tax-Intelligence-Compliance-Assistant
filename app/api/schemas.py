"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    """Schema for query requests."""
    question: str = Field(..., description="Tax-related question")
    k: int = Field(default=3, ge=1, le=10, description="Number of relevant chunks to retrieve")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the Corporate Income Tax rate for AY 2022/2023?",
                "k": 3
            }
        }


class SourceDocument(BaseModel):
    """Schema for source document citation."""
    source: str = Field(..., description="Source document filename")
    page: int | str = Field(..., description="Page number")
    content: str = Field(..., description="Relevant text excerpt")


class QueryResponse(BaseModel):
    """Schema for query responses with citations."""
    answer: str = Field(..., description="The generated answer")
    sources: List[SourceDocument] = Field(default_factory=list, description="Source citations")
    disclaimer: str = Field(..., description="Legal disclaimer")


class UploadResponse(BaseModel):
    """Schema for document upload responses."""
    message: str
    filename: str
    pages_loaded: int
    chunks_created: int


class DocumentInfo(BaseModel):
    """Schema for document information."""
    status: str
    count: int
    files: List[str]
    path: Optional[str] = None