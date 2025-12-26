"""
Generalized Jaccard Similarity Calculator
"""

import numpy as np
from typing import List, Dict


class JaccardSimilarity:
    
    @staticmethod
    def calculate(vector1: np.ndarray, vector2: np.ndarray) -> float:
        """
        Hitung Generalized Jaccard Similarity antara 2 vektor TF-IDF
        
        Formula: J(Q, D) = sum(min(Wq, Wd)) / sum(max(Wq, Wd))
        
        Args:
            vector1: TF-IDF vector pertama (query)
            vector2: TF-IDF vector kedua (document)
            
        Returns:
            float: Skor similarity antara 0 dan 1
        """
        # Pastikan array 1D
        v1 = vector1.flatten()
        v2 = vector2.flatten()
        
        # Hitung min dan max element-wise
        min_values = np.minimum(v1, v2)
        max_values = np.maximum(v1, v2)
        
        # Sum
        numerator = np.sum(min_values)
        denominator = np.sum(max_values)
        
        # Avoid division by zero
        if denominator == 0:
            return 0.0
        
        return float(numerator / denominator)
    
    @staticmethod
    def rank_documents(query_vector: np.ndarray, 
                      document_vectors: List[np.ndarray],
                      document_info: List[Dict]) -> List[Dict]:
        """
        Ranking dokumen berdasarkan similarity dengan query
        
        Args:
            query_vector: TF-IDF vector dari query
            document_vectors: List of TF-IDF vectors untuk setiap dokumen
            document_info: List of document metadata
            
        Returns:
            List of documents sorted by similarity (highest first)
        """
        results = []
        
        for idx, doc_vector in enumerate(document_vectors):
            similarity = JaccardSimilarity.calculate(query_vector, doc_vector)
            
            result = {
                'rank': 0,  # Will be set after sorting
                'doc_index': idx,
                'similarity': similarity,
                **document_info[idx]  # Merge document info
            }
            
            results.append(result)
        
        # Sort by similarity (descending)
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Set rank
        for rank, result in enumerate(results, 1):
            result['rank'] = rank
        
        return results
