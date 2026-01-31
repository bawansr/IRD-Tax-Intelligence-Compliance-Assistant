"""RAG chain with citations - LangChain v1.x compatible."""
import os
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from app.config import settings

class RAGChain:
    """RAG chain for tax questions using Groq."""
    
    def __init__(self, retriever):
        self.retriever = retriever
        self.llm = self._create_llm()
        self.prompt = self._create_prompt()
    
    def _create_llm(self):
        """Create LLM (Groq)."""
        # 1. Get API Key from Environment
        api_key = os.getenv("GROQ_API_KEY")
        
        # Fallback: Check settings if not in os.environ
        if not api_key and hasattr(settings, "GROQ_API_KEY"):
            api_key = settings.GROQ_API_KEY
            
        if not api_key:
            raise ValueError("Error: GROQ_API_KEY is missing. Check your .env file.")

        # 2. Return Groq LLM
        return ChatGroq(
            model_name="llama-3.1-8b-instant",  # Fast, free, and smart
            temperature=0,                # 0 for strict factual answers
            api_key=api_key
        )

    def _create_prompt(self):
        """Define the strict tax assistant prompt."""
        template = """You are an intelligent assistant for the Sri Lankan Inland Revenue Department (IRD).

STRICT RULES:
1. Answer ONLY using information from the provided IRD documents below.
2. If the answer is not in the documents, say: "This information is not available in the provided IRD documents."
3. NEVER make assumptions or use outside knowledge.
4. ALWAYS cite sources inline using this format: [Document Name - Page X].
5. Distinguish between assessment years (AY) clearly.

IMPORTANT DISCLAIMER:
All responses are based solely on IRD-published documents and should not be considered professional tax advice.

CONTEXT FROM IRD DOCUMENTS:
{context}

QUESTION: {question}

ANSWER (with citations):"""
        return ChatPromptTemplate.from_template(template)

    def _format_docs(self, docs: List[Document]) -> str:
        """
        Formats retrieved documents into a string with metadata citations.
        Matches keys from metadata_extractor.py ('source_document', 'page_number').
        """
        formatted_chunks = []
        for doc in docs:
            # Use .get() with defaults to prevent crashes if metadata is missing
            source = doc.metadata.get('source_document', 'Unknown Source')
            page = doc.metadata.get('page_number', '?')
            content = doc.page_content.replace('\n', ' ')
            
            chunk_str = f"[Source: {source} - Page {page}]\n{content}"
            formatted_chunks.append(chunk_str)
            
        return "\n\n".join(formatted_chunks)

    def get_chain(self):
        """
        Builds the LangChain Runnable.
        """
        # 1. Retrieve & Format
        retrieval_chain = (
            RunnablePassthrough() 
            | self.retriever 
            | self._format_docs
        )

        # 2. Main Chain
        chain = (
            RunnableParallel(
                {"context": retrieval_chain, "question": RunnablePassthrough()}
            )
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        return chain

    def query(self, question: str) -> Dict[str, Any]:
        """
        Public method to answer a question.
        Returns the Answer + The Source Documents used.
        """
        fallback_msg = "This information is not available in the provided IRD documents."
        # 1. Manually retrieve docs first so we can return them in the response
        docs = self.retriever.invoke(question)
        print(f"Retrieved {len(docs)} documents for question: '{question}'")
        
        # 2. Filter low-confidence results to improve precision
        # Keep only chunks that are likely relevant (avoid noisy citations)
        docs = [doc for doc in docs if self._is_relevant(doc, question)]
        print(f"After filtering: {len(docs)} relevant documents")
        
        # 3. Format context
        context_str = self._format_docs(docs)
        
        if not context_str.strip():
            print("No context found in retrieved documents")
            context_str = fallback_msg
        
        # 4. Generate Answer
        chain = (
            {"context": lambda x: context_str, "question": lambda x: question}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        answer = chain.invoke(question)
        
        # 5. Extract Clean Citations
        citations = self._extract_citations(docs)
        print(f"Extracted {len(citations)} citations")

        # If the model returns the fallback message, do not show unrelated citations
        if fallback_msg in answer:
            citations = []
        
        return {
            "answer": answer,
            "citations": citations,
        }
    
    def _is_relevant(self, doc: Document, question: str) -> bool:
        """
        Simple relevance check: filter out chunks with very short content
        or obvious mismatches (optional logic for better precision).
        You can extend this with semantic similarity checks if needed.
        """
        content = doc.page_content.strip()
        # Keep chunks with meaningful length to avoid noise
        return len(content) > 50
    
    def _extract_citations(self, source_docs: List[Document]) -> List[Dict[str, Any]]:
        """Extract unique citations to show in the UI."""
        unique_citations = {}
        
        for doc in source_docs:
            # Create a unique key (Source + Page) to avoid duplicate citations
            source = doc.metadata.get("source_document", "Unknown")
            page = doc.metadata.get("page_number", "?")
            key = f"{source}_{page}"
            
            if key not in unique_citations:
                unique_citations[key] = {
                    "document": source,
                    "page": page,
                    "content_preview": doc.page_content[:150] + "..."
                }
        
        return list(unique_citations.values())