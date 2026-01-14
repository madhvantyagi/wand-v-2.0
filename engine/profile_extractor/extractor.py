"""
Profile Extractor - Single-file module for structured profile data extraction.

Extract structured data from HTML portfolios, PDF resumes, and PDF LinkedIn profiles
using DeepSeek-V3 for cost-effective, accurate parsing.
"""

import os
import fitz  # PyMuPDF
import trafilatura
from pydantic import BaseModel, Field
from typing import List, Optional
from engine.models import get_deepseek_client

# No need to load_dotenv - models module handles it


# ============================================================================
# PYDANTIC MODELS - Flexible Data Schema
# ============================================================================

class ProfileData(BaseModel):
    """
    Flexible profile data structure that captures ALL information.
    Uses a dynamic dict to store any and all extracted data.
    """
    class Config:
        extra = "allow"  # Allow any additional fields
    
    # Store all extracted data as a flexible dictionary
    data: dict = Field(
        default_factory=dict,
        description="All extracted information organized into logical sections"
    )
    
    def model_dump_json(self, **kwargs):
        """Override to return just the data dict as JSON."""
        import json
        return json.dumps(self.data, indent=2, ensure_ascii=False)


# ============================================================================
# CONTENT EXTRACTION - PDF and HTML
# ============================================================================

def extract_content(file_content: bytes, file_type: str) -> str:
    """
    Extract text content from PDF or HTML bytes.
    
    Args:
        file_content: Raw bytes of the file
        file_type: Either 'pdf' or 'html'
        
    Returns:
        Extracted text content with preserved structure
        
    Raises:
        ValueError: If file_type is not 'pdf' or 'html'
    """
    if file_type.lower() == 'pdf':
        return _extract_pdf(file_content)
    elif file_type.lower() == 'html':
        return _extract_html(file_content)
    else:
        raise ValueError(f"Unsupported file type: {file_type}. Use 'pdf' or 'html'.")


def _extract_pdf(file_content: bytes) -> str:
    """
    Extract content from PDF bytes preserving text structure.
    
    Args:
        file_content: Raw PDF bytes
        
    Returns:
        Extracted text content
    """
    text = ""
    doc = fitz.open(stream=file_content, filetype="pdf")
    for page in doc:
        text += page.get_text("text")
    doc.close()
    return text


def _extract_html(file_content: bytes) -> str:
    """
    Extract clean content from HTML bytes, removing navigation and ads.
    
    Args:
        file_content: Raw HTML bytes
        
    Returns:
        Extracted text content
        
    Uses Trafilatura for intelligent content extraction.
    """
    html_string = file_content.decode('utf-8')
    
    # Trafilatura extracts main content, discards boilerplate
    extracted = trafilatura.extract(html_string)
    
    if not extracted:
        raise ValueError("Could not extract content from HTML")
    
    return extracted


# ============================================================================
# LLM INTEGRATION - DeepSeek-V3
# ============================================================================

def parse_profile(file_content: bytes, file_type: str, api_key: str = None) -> str:
    """
    Parse profile bytes (PDF/HTML) into structured JSON.
    
    Args:
        file_content: Raw bytes of the profile file
        file_type: Either 'pdf' or 'html'
        api_key: Optional DeepSeek API key (defaults to DEEPSEEK_API_KEY env var)
        
    Returns:
        JSON string with structured profile data
        
    Example:
        >>> with open("resume.pdf", "rb") as f:
        ...     file_bytes = f.read()
        >>> result = parse_profile(file_bytes, "pdf")
        >>> print(result)
        {
          "name": "John Doe",
          "email": "john@example.com",
          ...
        }
    """
    # Get API key from parameter or environment
    api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError(
            "DeepSeek API key required. Set DEEPSEEK_API_KEY environment variable "
            "or pass api_key parameter."
        )
    
    # Extract content from bytes
    content = extract_content(file_content, file_type)
    
    # Get DeepSeek client from centralized models
    client = get_deepseek_client(api_key)
    
    # Extract structured data using LLM
    profile_data = client.chat.completions.create(
        model="deepseek-chat",  # DeepSeek-V3
        response_model=ProfileData,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a comprehensive data extraction assistant. "
                    "Extract ALL information from the provided document and organize it into a well-structured JSON format. "
                    "\n\nGuidelines:\n"
                    "1. Extract EVERY piece of information - don't skip anything\n"
                    "2. Organize data into logical sections (e.g., personal_info, work_experience, education, skills, projects, certifications, etc.)\n"
                    "3. Preserve all details: dates, descriptions, achievements, links, contact info, etc.\n"
                    "4. Use clear, descriptive keys for all fields\n"
                    "5. Maintain hierarchical structure where appropriate (nested objects/arrays)\n"
                    "6. Include sections like: awards, publications, languages, volunteer_work, hobbies, references, etc. if present\n"
                    "7. Be thorough and accurate - capture everything available in the document"
                )
            },
            {
                "role": "user",
                "content": content
            }
        ],
        temperature=0.0,  # Deterministic output
    )
    
    # Return as formatted JSON
    return profile_data.model_dump_json(indent=2)
