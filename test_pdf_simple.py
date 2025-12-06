#!/usr/bin/env python3
"""
Test PDF text extraction without Ollama
"""

import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.pdf import get_pdf_analysis

def test_pdf_text_extraction():
    """Test PDF text extraction"""
    try:
        pdf_service = get_pdf_analysis()
        
        # Test with a sample PDF path (you can replace this with an actual PDF)
        pdf_path = "sample.pdf"  # Replace with actual PDF path
        
        print("Testing PDF text extraction...")
        print("=" * 50)
        
        # Test text extraction
        text = pdf_service.get_text(pdf_path)
        print(f"Extracted text length: {len(text)} characters")
        print(f"First 200 characters: {text[:200]}...")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_text_extraction()
