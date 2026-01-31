import re 
from typing import List
from langchain_core.documents import Document

class TextPreprocessor:
    """Clean and preprocess text extracted from PDFs."""
    
    def __init__(self):
        """Initialize text preprocessor."""
        pass
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        
        if not text:
            return ""
        
        #Fix Hyphenated Words
       
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

        # Fix Line Breaks 
        # PDFs often wrap sentences with a newline. We want to turn those into spaces,
        # but keep Double Newlines (\n\n) as paragraph breaks.
        
        # Replace paragraph breaks (\n\n) with a temporary placeholder
        text = re.sub(r'\n\s*\n', '||PARAGRAPH||', text)
        
        # Replace single newlines with a space (joining the sentence)
        text = re.sub(r'\n', ' ', text)
        
        # Restore paragraph breaks
        text = text.replace('||PARAGRAPH||', '\n\n')
        
        # --- CHANGE 3: Standard Cleanup ---
        # Remove extra whitespace 
        text = re.sub(r'[ \t]+', ' ', text)
        
        return text.strip()

    # --- CHANGE 4: Fixed Indentation Error ---
    def preprocess_documents(self, documents: List[Document]) -> List[Document]:
        """Preprocess a list of Document objects."""
        cleaned_docs = []
        for doc in documents:
            # We process the content but KEEP the original metadata
            cleaned_content = self.clean_text(doc.page_content)
            
            # Only keep pages that actually have text after cleaning
            if len(cleaned_content) > 10:
                cleaned_doc = Document(
                    page_content=cleaned_content,
                    metadata=doc.metadata
                )
                cleaned_docs.append(cleaned_doc)
                
        return cleaned_docs