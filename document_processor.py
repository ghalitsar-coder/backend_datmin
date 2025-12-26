"""
Document Processor untuk membaca file TXT, PDF, DOCX
"""

import os
from typing import List, Dict
import PyPDF2
from docx import Document


class DocumentProcessor:
    
    @staticmethod
    def read_txt(file_path: str) -> str:
        """Baca file TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            # Coba encoding lain
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                return ""
    
    @staticmethod
    def read_pdf(file_path: str) -> str:
        """Baca file PDF"""
        try:
            text = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
            return ""
    
    @staticmethod
    def read_docx(file_path: str) -> str:
        """Baca file DOCX"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {e}")
            return ""
    
    @staticmethod
    def read_document(file_path: str) -> str:
        """Baca dokumen berdasarkan ekstensi"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.txt':
            return DocumentProcessor.read_txt(file_path)
        elif ext == '.pdf':
            return DocumentProcessor.read_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return DocumentProcessor.read_docx(file_path)
        else:
            return ""
    
    @staticmethod
    def process_directory(directory_path: str) -> List[Dict]:
        """
        Baca semua dokumen di folder
        Returns: List of {filename, text, file_path}
        """
        documents = []
        
        if not os.path.exists(directory_path):
            return documents
        
        valid_extensions = ['.txt', '.pdf', '.docx', '.doc']
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            if os.path.isfile(file_path):
                ext = os.path.splitext(filename)[1].lower()
                
                if ext in valid_extensions:
                    text = DocumentProcessor.read_document(file_path)
                    
                    if text.strip():  # Hanya tambahkan jika ada text
                        documents.append({
                            'filename': filename,
                            'text': text,
                            'file_path': file_path
                        })
        
        return documents
