#  IRD Tax Intelligence & Compliance Assistant

An AI-powered retrieval-augmented generation (RAG) system that enables users to ask natural language questions about Sri Lankan tax regulations and receive accurate, citation-backed answers extracted strictly from official Inland Revenue Department (IRD) documents.

## Overview

This system leverages Large Language Models (LLMs) and vector databases to provide intelligent tax guidance by:
- Ingesting official IRD tax documents (PDFs)
- Converting them into searchable embeddings
- Answering tax questions with precise document citations
- Preventing hallucinations through prompt engineering
- Maintaining full audit trails with source references

## Key Features

**Document Ingestion** - Upload and process IRD PDF documents
**Multi-Document Retrieval** - Search across multiple tax documents simultaneously  
**Citation-Backed Answers** - All responses include document, page, and section references  
**Safety Controls** - Responses restricted to source documents only  
**REST API** - Easy integration with frontend applications  
**Vector Database** - Fast semantic search using Chroma + HuggingFace embeddings  
**LLM Integration** - Groq API for fast inference without GPU requirements

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Framework** | FastAPI (Python) |
| **LLM** | Groq (llama-3.1-8b-instant) |
| **Embeddings** | HuggingFace (all-MiniLM-L6-v2) |
| **Vector Database** | Chroma + ChromaDB |
| **PDF Processing** | PyPDF, PyMuPDF |
| **Text Splitting** | LangChain RecursiveCharacterTextSplitter |
| **Server** | Uvicorn (ASGI) |
| **API Validation** | Pydantic |

## 📦 Installation & Setup

### Prerequisites
- Python 3.10+
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone & Navigate
```bash
cd d:\Tax_Ai
```

### Step 2: Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create a `.env` file in the root directory with:
```env
# API Keys (Required)
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Model Configuration
LLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
TEMPERATURE=0.0

# Chunking Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Vector Database
VECTOR_DB_TYPE=chroma
VECTOR_DB_PATH=data/vector_store

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Step 5: Prepare Data Directory
```bash
mkdir -p data/raw
mkdir -p data/vector_store
```

Add your IRD PDF documents to `data/raw/` folder.

### Step 6: Start the Server
```bash
python -m uvicorn app.main:app --reload
```

Server will run at: **http://127.0.0.1:8000**

## 📚 API Documentation

### 1. Health Check
```
GET /api/v1/health
```
**Response:**
```json
{
  "status": "healthy",
  "documents": {
    "status": "active",
    "count": 3,
    "files": ["Corporate_Income_Tax_Guide.pdf"]
  },
  "vector_store_initialized": true
}
```

---

### 2. List Documents
```
GET /api/v1/documents
```
**Response:**
```json
{
  "status": "active",
  "count": 3,
  "files": ["CIT_Guide_2022_2023.pdf", "PN_IT_2025_01.pdf", "SET_Guide_2025_26.pdf"],
  "path": "data/raw"
}
```

---

### 3. Initialize System
```
POST /api/v1/initialize
```
Loads all PDFs from `data/raw/`, creates embeddings, and builds vector store.

**Response:**
```json
{
  "status": "success",
  "documents_loaded": 3,
  "pages_loaded": 450,
  "chunks_created": 1523,
  "message": "System initialized and ready for queries"
}
```

---

### 4. Upload Document
```
POST /api/v1/upload
Content-Type: multipart/form-data

file: <PDF_FILE>
```

**Response:**
```json
{
  "message": "Document uploaded and processed successfully",
  "filename": "CIT_Assessment_Guide.pdf",
  "pages_loaded": 156,
  "chunks_created": 387
}
```

---

### 5. Query Tax Documents 
```
POST /api/v1/query
Content-Type: application/json

{
  "question": "What is the Corporate Income Tax rate for AY 2022/2023?",
  "k": 3
}
```

**Response:**
```json
{
  "answer": "According to the Corporate Income Tax Assessment Guide (AY 2022/2023), the standard Corporate Income Tax rate is 18% for resident companies and 28% for non-resident companies. However, certain categories may qualify for concessional rates as outlined in the Income Tax Act...",
  "sources": [
    {
      "source": "Corporate_Income_Tax_Guide.pdf",
      "page": 15,
      "content": "The standard rate of Corporate Income Tax for AY 2022/2023 is 18% on taxable income of resident companies..."
    },
    {
      "source": "Corporate_Income_Tax_Guide.pdf",
      "page": 47,
      "content": "Non-resident companies are subject to Corporate Income Tax at the rate of 28%..."
    }
  ],
  "disclaimer": "This response is based solely on IRD-published documents and is not professional tax advice."
}
```

---

## Usage Examples

### Example 1: Basic Tax Question
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How is Self Employment Tax calculated for 2025/2026?",
    "k": 5
  }'
```

### Example 2: Specific Public Notice Query
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What changes were introduced in Public Notice PN_IT_2025-01?",
    "k": 3
  }'
```

### Example 3: Using Swagger UI
1. Navigate to: `http://127.0.0.1:8000/docs`
2. Click on "POST /api/v1/query"
3. Click "Try it out"
4. Enter your question in the request body
5. Click "Execute"

---

##  Project Structure

```
d:\Tax_Ai\
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration & environment variables
│   ├── ingest.py               # Document ingestion script (standalone)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # API endpoints
│   │   └── schemas.py          # Pydantic request/response models
│   └── services/
│       ├── __init__.py
│       ├── loader.py           # PDF document loader & orchestrator
│       ├── preprocessor.py     # Text cleaning & normalization
│       ├── chunker.py          # Text splitting into chunks
│       ├── embeddings.py       # HuggingFace embedding service
│       ├── metadata_extractor.py # Document metadata enrichment
│       ├── vector_db.py        # Chroma vector database management
│       └── rag_chain.py        # RAG pipeline & LLM integration
├── data/
│   ├── raw/                    # PDF documents (input)
│   └── vector_store/           # Chroma database (auto-created)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create manually)
└── README.md                   # This file
```

---

## Processing Pipeline

```
1. INGESTION (app/services/loader.py)
   ↓
   PDF → Load raw pages
   
2. PREPROCESSING (app/services/preprocessing.py)
   ↓
   Raw text → Fix hyphenation, normalize spaces
   
3. CHUNKING (app/services/chunker.py)
   ↓
   Clean text → Split into 1000-char chunks (200 overlap)
   
4. METADATA ENRICHMENT (app/services/metadata_extractor.py)
   ↓
   Chunks → Add document name, page number, citation format
   
5. EMBEDDING (app/services/embeddings.py)
   ↓
   Chunks → Convert to vector embeddings
   
6. VECTOR DB STORAGE (app/services/vector_db.py)
   ↓
   Embeddings → Store in Chroma database
   
7. RETRIEVAL & ANSWERING (app/services/rag_chain.py)
   ↓
   Question → Search similar chunks → LLM → Cite sources
```

---

## Safety & Accuracy Features

### Hallucination Prevention
-  **Prompt engineering** restricts answers to source documents
-  **Strict retrieval** only uses chunks found in vector database
-  **No external knowledge** - LLM cannot invent tax rules
-  **Fallback message** - "This information is not available in the provided IRD documents"

### Citation Accuracy
-  **Metadata tracking** - Document name, page number, section stored with each chunk
-  **Source attribution** - Every answer includes precise source references
-  **Audit trail** - Citation format: "Document Name – Page X"

### Compliance Controls
-  **Legal disclaimer** - All responses include non-professional-advice notice
-  **Temperature = 0.0** - Deterministic responses, no creativity
-  **No speculative answers** - System clearly states when info is unavailable

---

##  Configuration Parameters

### Chunking Strategy
```python
CHUNK_SIZE = 1000        # Characters per chunk
CHUNK_OVERLAP = 200      # Overlap between chunks (context preservation)
```
**Why?** Tax documents often contain multi-line rules. Overlap prevents cutting sentences.

### Vector Retrieval
```python
k = 3 (default)          # Number of similar chunks retrieved
```
**Why?** Balances retrieval time vs answer completeness.

### LLM Settings
```python
MODEL = "llama-3.1-8b-instant"
TEMPERATURE = 0.0        # Strict factual mode, no creativity
```
**Why?** Tax guidance requires 100% accuracy, no hallucinations.

---

##  Troubleshooting

### Issue: "Vector store not initialized"
**Solution:**
```bash
POST http://127.0.0.1:8000/api/v1/initialize
```

### Issue: "ModuleNotFoundError: langchain_chroma"
**Solution:**
```bash
pip install langchain-community chromadb
```

### Issue: "GROQ_API_KEY missing"
**Solution:**
- Add `GROQ_API_KEY=...` to `.env` file
- Restart the server

### Issue: "No PDF files found"
**Solution:**
- Ensure PDFs are in `data/raw/` folder
- Check file extensions are `.pdf` (lowercase)

---

##  Official IRD Documents

The system is designed to ingest these documents:

1. **Corporate Income Tax Assessment Guide (AY 2022/2023)**
   - https://www.ird.gov.lk/en/Downloads/IT_Corporate_Doc/Asmt_CIT_003_2022_2023_E.pdf

2. **Public Notice – Income Tax (PN_IT_2025-01)**
   - https://www.ird.gov.lk/en/Lists/Latest%20News%20%20Notices/Attachments/666/PN_IT_2025-01_26032025_E.pdf

3. **Self Employment Tax (SET) Detailed Guide (AY 2025/2026)**
   - https://www.ird.gov.lk/ta/Downloads/IT_SET_Doc/SET_25_26_Detail_Guide_E.pdf

**Optional Enhancements:**
- Inland Revenue Act No. 24 of 2017
- VAT Act & VAT guides
- PAYE and WHT circulars
- Tax filing deadline notices

---

##  Testing the System

### 1. Upload a Document
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/upload" \
  -F "file=@data/raw/CIT_Guide.pdf"
```

### 2. Initialize Vector Store
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/initialize"
```

### 3. Ask a Question
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the Corporate Income Tax rate?",
    "k": 3
  }'
```

### 4. Check Health
```bash
curl "http://127.0.0.1:8000/api/v1/health"
```

---

##  Key Assumptions

1. **PDF Quality** - Documents are text-based PDFs (not scanned images)
2. **Language** - All documents are in English
3. **Chunking** - 1000 characters is optimal for tax document structures
4. **Retrieval** - Top-3 chunks provide sufficient context for accurate answers
5. **API Keys** - Groq and OpenAI API keys are valid and have sufficient quota
6. **Disclaimer** - Users understand this is not professional tax advice
7. **Source Authority** - Only official IRD documents are used (no third-party sources)

---

##  License

This project is designed for educational and compliance assistance purposes.

---

##  Support & Feedback

For issues or feature requests:
1. Check the Troubleshooting section above
2. Verify all `.env` variables are correctly set
3. Ensure PDFs are in the correct folder
4. Check server logs for detailed error messages

---

##  Next Steps

1. **Add IRD Documents** - Download and place PDFs in `data/raw/`
2. **Initialize System** - Run `/api/v1/initialize`
3. **Test Queries** - Use Swagger UI or curl commands
4. **Monitor Citations** - Verify sources are accurate and helpful

---

**Version:** 1.0.0  
**Last Updated:** January 27, 2026  
**Status:** Production Ready ✅
