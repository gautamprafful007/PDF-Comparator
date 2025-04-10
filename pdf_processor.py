import PyPDF2
from io import StringIO
import re

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text content
    """
    text = ""
    
    try:
        # Try using PyPDF2 first
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Check if PDF is encrypted
            if pdf_reader.is_encrypted:
                try:
                    # Try with empty password
                    pdf_reader.decrypt('')
                except:
                    return "This PDF is encrypted and cannot be processed."
            
            # Extract text from each page
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                
                if page_text:
                    text += page_text + "\n\n"
        
        # Clean up the text
        text = clean_text(text)
        
        # If we couldn't extract any text, the PDF might be scanned
        if not text.strip():
            return "No text could be extracted. This might be a scanned document or image-based PDF."
            
        return text
        
    except Exception as e:
        # Handle the exception
        return f"Error extracting text: {str(e)}"

def clean_text(text):
    """
    Clean and normalize extracted text from PDF.
    
    Args:
        text (str): Raw text from PDF
        
    Returns:
        str: Cleaned text
    """
    # Remove excessive whitespace and normalize line breaks
    text = re.sub(r'\s+', ' ', text)
    
    # Normalize line breaks
    text = re.sub(r'(\n\s*){3,}', '\n\n', text)
    
    # Split text into paragraphs for better comparison
    paragraphs = text.split('\n\n')
    clean_paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    return '\n\n'.join(clean_paragraphs)
