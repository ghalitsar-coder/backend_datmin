"""
TF-IDF Processor menggunakan scikit-learn
"""

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from typing import List, Dict


class TFIDFProcessor:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = None
        self.feature_names = None
        self.documents = []
        
    def fit_transform(self, documents: List[str]):
        """
        Fit dan transform dokumen menjadi TF-IDF matrix
        documents: List of preprocessed text
        """
        self.documents = documents
        self.tfidf_matrix = self.vectorizer.fit_transform(documents)
        self.feature_names = self.vectorizer.get_feature_names_out()
        
    def transform_query(self, query: str):
        """Transform query menggunakan vectorizer yang sudah di-fit"""
        return self.vectorizer.transform([query])
    
    def get_tfidf_matrix_dict(self) -> Dict:
        """
        Konversi TF-IDF matrix ke format dictionary untuk JSON response
        Returns: {
            'documents': [...],
            'terms': [...],
            'matrix': [[...]]
        }
        """
        if self.tfidf_matrix is None:
            return None
        
        # Konversi sparse matrix ke dense
        dense_matrix = self.tfidf_matrix.toarray()
        
        # Ambil top N terms dengan bobot tertinggi untuk setiap dokumen
        top_n = min(50, len(self.feature_names))  # Limit untuk performa
        
        result = {
            'num_documents': dense_matrix.shape[0],
            'num_terms': len(self.feature_names),
            'documents': [],
            'terms': list(self.feature_names[:top_n]),
            'matrix': []
        }
        
        for doc_idx, doc_vector in enumerate(dense_matrix):
            # Ambil top N terms untuk dokumen ini
            top_indices = np.argsort(doc_vector)[-top_n:][::-1]
            
            doc_data = {
                'doc_index': doc_idx,
                'top_terms': [
                    {
                        'term': self.feature_names[idx],
                        'tfidf': float(doc_vector[idx])
                    }
                    for idx in top_indices if doc_vector[idx] > 0
                ]
            }
            
            result['documents'].append(doc_data)
            result['matrix'].append([float(x) for x in doc_vector[:top_n]])
        
        return result
    
    def get_document_vector(self, doc_index: int):
        """Ambil TF-IDF vector untuk dokumen tertentu"""
        if self.tfidf_matrix is None:
            return None
        return self.tfidf_matrix[doc_index].toarray()[0]
    
    def get_feature_names(self) -> List[str]:
        """Ambil nama-nama fitur (terms)"""
        return list(self.feature_names) if self.feature_names is not None else []
