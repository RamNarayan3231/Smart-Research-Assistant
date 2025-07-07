from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from backend.openrouter_llm import OpenRouterLLM
import re
import os
import io  # Import for io
from typing import Union, Optional
from fastapi import HTTPException

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            length_function=len
        )
        self.llm = OpenRouterLLM()
    
    def process_pdf(self, file_bytes: bytes) -> str:
        """Process PDF file content from bytes."""
        try:
            text = ""
            reader = PdfReader(io.BytesIO(file_bytes))  # Now properly imported
            
            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except:
                    raise HTTPException(
                        status_code=400,
                        detail="PDF is password protected and cannot be processed"
                    )

            for page in reader.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except:
                    continue

            if not text.strip():
                raise HTTPException(
                    status_code=422,
                    detail="PDF contains no extractable text (may be image-based)"
                )

            return self._clean_text(text)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing PDF: {str(e)}"
            )


    def process_text(self, file_bytes: bytes) -> str:
        """Process text file content from bytes."""
        try:
            # Try UTF-8 first, fall back to latin-1
            try:
                text = file_bytes.decode('utf-8')
            except UnicodeDecodeError:
                text = file_bytes.decode('latin-1')
            
            return self._clean_text(text)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing text file: {str(e)}"
            )

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Validate minimum length
        if len(text) < 10:
            raise HTTPException(
                status_code=422,
                detail="Document contains insufficient text for processing"
            )
            
        return text

    def generate_summary(self, text: str, max_words: int = 150) -> str:
        """Generate a concise summary of the text."""
        try:
            if not text.strip():
                raise ValueError("Empty text provided for summarization")
                
            # Split the document into chunks
            texts = self.text_splitter.split_text(text)
            docs = [Document(page_content=t) for t in texts]
            
            # Use map-reduce for summarization
            chain = load_summarize_chain(
                self.llm,
                chain_type="map_reduce",
                verbose=True
            )
            summary = chain.run(docs)
            
            # Ensure summary is within word limit
            words = summary.split()
            if len(words) > max_words:
                summary = ' '.join(words[:max_words]) + "..."
            
            return summary
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating summary: {str(e)}"
            )