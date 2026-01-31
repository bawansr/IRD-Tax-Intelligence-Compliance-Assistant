import os
from typing import List, Dict, Any
from langchain_core.documents import Document

class MetadataExtractor:
    """
    Service to enrich document metadata for accurate citations.
    """
    
    def __init__(self):
        pass

    def _generate_citation_string(self, filename: str, page_num: int) -> str:
        """
        Creates the standardized citation format required by the LLM
        Format: "Corporate_Income_Tax_Guide_2023.pdf - Page 5"
        """
        return f"{filename} - Page {page_num}"

    def enrich_metadata(self, doc: Document, file_path: str) -> Dict[str, Any]:
        """
        Enhance specific document metadata.
        
        Args:
            doc: The raw document from the loader.
            file_path: The origin path of the file.
            
        Returns:
            A dictionary of enhanced metadata.
        """
        # Start with existing metadata
        meta = doc.metadata.copy()
        
        # Extract Filename
        filename = os.path.basename(file_path)
        
        
        # PyPDF starts at 0. Humans start at 1.
        raw_page = meta.get('page', 0)
        display_page = raw_page + 1
        
        # Add Core Fields
        meta['source_document'] = filename
        meta['file_path'] = file_path
        meta['page_number'] = display_page
        
        # Add 'Citation' Field
        # This is what we will feed into the LLM's context window later
        meta['citation'] = self._generate_citation_string(filename, display_page)
        
        return meta

    def process_documents(self, documents: List[Document], file_path: str) -> List[Document]:
        """
        Apply metadata enrichment to a batch of documents from the same file.
        """
        enriched_docs = []
        
        for doc in documents:
            # Generate new metadata
            new_metadata = self.enrich_metadata(doc, file_path)
            
            # Create new Document with updated metadata
            new_doc = Document(
                page_content=doc.page_content,
                metadata=new_metadata
            )
            enriched_docs.append(new_doc)
            
        return enriched_docs