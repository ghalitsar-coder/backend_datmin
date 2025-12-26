"""
Text Preprocessor untuk Bahasa Indonesia
Menggunakan Sastrawi untuk stemming
"""

import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory


class TextPreprocessor:
    def __init__(self):
        # Initialize Sastrawi
        self.stemmer = StemmerFactory().create_stemmer()
        self.stopword_remover = StopWordRemoverFactory().create_stop_word_remover()
        
    def case_folding(self, text: str) -> str:
        """Ubah ke lowercase"""
        return text.lower()
    
    def tokenizing(self, text: str) -> list:
        """Pecah text menjadi kata-kata"""
        # Hapus karakter non-alphanumeric kecuali spasi
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        # Split berdasarkan whitespace
        tokens = text.split()
        return tokens
    
    def filtering(self, tokens: list) -> list:
        """Hapus token yang tidak valid (angka, terlalu pendek)"""
        filtered = []
        for token in tokens:
            # Hapus angka dan kata dengan panjang < 2
            if not token.isdigit() and len(token) > 1:
                filtered.append(token)
        return filtered
    
    def stopword_removal(self, text: str) -> str:
        """Hapus stopwords menggunakan Sastrawi"""
        return self.stopword_remover.remove(text)
    
    def stemming(self, text: str) -> str:
        """Stemming menggunakan Sastrawi"""
        return self.stemmer.stem(text)
    
    def preprocess(self, text: str) -> tuple:
        """
        Pipeline preprocessing lengkap
        Returns: (processed_text, tokens)
        """
        # 1. Case Folding
        text = self.case_folding(text)
        
        # 2. Tokenizing
        tokens = self.tokenizing(text)
        
        # 3. Filtering
        tokens = self.filtering(tokens)
        
        # 4. Join untuk stopword removal
        text = ' '.join(tokens)
        
        # 5. Stopword Removal
        text = self.stopword_removal(text)
        
        # 6. Stemming
        text = self.stemming(text)
        
        # 7. Final tokenization
        final_tokens = text.split()
        
        return text, final_tokens
    
    def get_preprocessing_steps(self, text: str) -> dict:
        """
        Untuk debugging - tampilkan setiap tahap preprocessing
        """
        steps = {}
        
        steps['original'] = text
        
        # Case Folding
        text_cf = self.case_folding(text)
        steps['case_folding'] = text_cf
        
        # Tokenizing
        tokens = self.tokenizing(text_cf)
        steps['tokenizing'] = ' '.join(tokens)
        
        # Filtering
        tokens_filtered = self.filtering(tokens)
        steps['filtering'] = ' '.join(tokens_filtered)
        
        # Stopword Removal
        text_joined = ' '.join(tokens_filtered)
        text_stopword = self.stopword_removal(text_joined)
        steps['stopword_removal'] = text_stopword
        
        # Stemming
        text_stemmed = self.stemming(text_stopword)
        steps['stemming'] = text_stemmed
        
        return steps
