"""
FastAPI Backend untuk Sistem Temu Balik Dokumen
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import json
import asyncio

from document_processor import DocumentProcessor
from text_preprocessor import TextPreprocessor
from tfidf_processor import TFIDFProcessor
from jaccard_similarity import JaccardSimilarity


# Pydantic Models
class UploadRequest(BaseModel):
    folder_path: str


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 10


class PreprocessResponse(BaseModel):
    original: str
    case_folding: str
    tokenizing: str
    filtering: str
    stopword_removal: str
    stemming: str


# Initialize FastAPI
app = FastAPI(
    title="Sistem Temu Balik Dokumen API",
    description="Backend API untuk search engine lokal dengan TF-IDF dan Generalized Jaccard",
    version="2.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Untuk development, production gunakan domain spesifik
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (dalam production, gunakan database)
class AppState:
    documents = []  # List of raw documents
    processed_docs = []  # List of processed documents
    preprocessor = TextPreprocessor()
    tfidf_processor = TFIDFProcessor()
    is_indexed = False

state = AppState()


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "message": "Sistem Temu Balik Dokumen API is running",
        "version": "2.0",
        "status": "active",
        "indexed": state.is_indexed,
        "total_documents": len(state.documents)
    }


@app.post("/api/upload")
def upload_documents(request: UploadRequest):
    """
    Upload dan index dokumen dari folder
    
    Process:
    1. Baca semua file dari folder
    2. Preprocessing setiap dokumen
    3. Build TF-IDF matrix
    4. Return list dokumen
    """
    try:
        folder_path = request.folder_path
        
        if not os.path.exists(folder_path):
            raise HTTPException(status_code=404, detail="Folder tidak ditemukan")
        
        # 1. Baca dokumen
        documents = DocumentProcessor.process_directory(folder_path)
        
        if not documents:
            raise HTTPException(
                status_code=400, 
                detail="Tidak ada dokumen valid (.txt, .pdf, .docx) ditemukan"
            )
        
        state.documents = documents
        
        # 2. Preprocessing
        processed_docs = []
        for doc in documents:
            processed_text, tokens = state.preprocessor.preprocess(doc['text'])
            processed_docs.append({
                'filename': doc['filename'],
                'file_path': doc['file_path'],
                'original_text': doc['text'],
                'processed_text': processed_text,
                'tokens': tokens,
                'word_count': len(tokens)
            })
        
        state.processed_docs = processed_docs
        
        # 3. Build TF-IDF matrix
        texts = [doc['processed_text'] for doc in processed_docs]
        state.tfidf_processor.fit_transform(texts)
        state.is_indexed = True
        
        # 4. Return summary
        return {
            "status": "success",
            "message": f"Berhasil mengindex {len(documents)} dokumen",
            "total_documents": len(documents),
            "documents": [
                {
                    "id": idx,
                    "filename": doc['filename'],
                    "original_text_preview": doc['original_text'][:200] + "...",
                    "processed_text_preview": doc['processed_text'][:200] + "...",
                    "word_count": doc['word_count']
                }
                for idx, doc in enumerate(processed_docs)
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/api/upload-stream")
async def upload_documents_stream(request: UploadRequest):
    """
    Upload dan index dokumen dengan streaming progress
    """
    async def generate_progress():
        try:
            folder_path = request.folder_path
            
            if not os.path.exists(folder_path):
                yield f"data: {json.dumps({'error': 'Folder tidak ditemukan'})}\n\n"
                return
            
            # 1. Baca dokumen
            yield f"data: {json.dumps({'status': 'reading', 'message': 'Membaca dokumen dari folder...'})}\n\n"
            await asyncio.sleep(0.1)
            
            documents = DocumentProcessor.process_directory(folder_path)
            
            if not documents:
                yield f"data: {json.dumps({'error': 'Tidak ada dokumen valid ditemukan'})}\n\n"
                return
            
            total = len(documents)
            yield f"data: {json.dumps({'status': 'found', 'total': total, 'message': f'Menemukan {total} dokumen'})}\n\n"
            await asyncio.sleep(0.1)
            
            state.documents = documents
            
            # 2. Preprocessing dengan progress
            processed_docs = []
            for idx, doc in enumerate(documents):
                current = idx + 1
                progress = (current / total) * 100
                
                # Send progress update
                filename = doc['filename']
                message = f'Memproses: {filename} ({current}/{total})'
                progress_data = {
                    'status': 'processing',
                    'current': current,
                    'total': total,
                    'progress': progress,
                    'filename': filename,
                    'message': message
                }
                yield f"data: {json.dumps(progress_data)}\n\n"
                
                processed_text, tokens = state.preprocessor.preprocess(doc['text'])
                processed_docs.append({
                    'filename': doc['filename'],
                    'file_path': doc['file_path'],
                    'original_text': doc['text'],
                    'processed_text': processed_text,
                    'tokens': tokens,
                    'word_count': len(tokens)
                })
                
                await asyncio.sleep(0.05)  # Small delay untuk smooth progress
            
            state.processed_docs = processed_docs
            
            # 3. Build TF-IDF matrix
            yield f"data: {json.dumps({'status': 'tfidf', 'message': 'Membuat TF-IDF matrix...'})}\n\n"
            await asyncio.sleep(0.1)
            
            texts = [doc['processed_text'] for doc in processed_docs]
            state.tfidf_processor.fit_transform(texts)
            state.is_indexed = True
            
            # 4. Complete
            result = {
                "status": "complete",
                "message": f"Berhasil mengindex {len(documents)} dokumen",
                "total_documents": len(documents),
                "documents": [
                    {
                        "id": idx,
                        "filename": doc['filename'],
                        "original_text_preview": doc['original_text'][:200] + "...",
                        "processed_text_preview": doc['processed_text'][:200] + "...",
                        "word_count": doc['word_count']
                    }
                    for idx, doc in enumerate(processed_docs)
                ]
            }
            
            yield f"data: {json.dumps(result)}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_progress(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.post("/api/search")
def search_documents(request: SearchRequest):
    """
    Search dokumen berdasarkan query
    
    Process:
    1. Preprocess query
    2. Transform query ke TF-IDF vector
    3. Hitung similarity dengan semua dokumen
    4. Return ranking hasil
    """
    try:
        if not state.is_indexed:
            raise HTTPException(
                status_code=400, 
                detail="Belum ada dokumen yang diindex. Upload dokumen terlebih dahulu."
            )
        
        query = request.query
        
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query tidak boleh kosong")
        
        # 1. Preprocess query
        processed_query, query_tokens = state.preprocessor.preprocess(query)
        
        # 2. Transform ke TF-IDF
        query_vector = state.tfidf_processor.transform_query(processed_query).toarray()[0]
        
        # 3. Hitung similarity
        document_vectors = [
            state.tfidf_processor.get_document_vector(i)
            for i in range(len(state.processed_docs))
        ]
        
        document_info = [
            {
                'filename': doc['filename'],
                'original_text': doc['original_text'][:300] + "...",
                'processed_text': doc['processed_text'][:300] + "...",
                'word_count': doc['word_count']
            }
            for doc in state.processed_docs
        ]
        
        results = JaccardSimilarity.rank_documents(
            query_vector,
            document_vectors,
            document_info
        )
        
        # Limit hasil
        top_results = results[:request.top_k]
        
        return {
            "status": "success",
            "query_original": query,
            "query_processed": processed_query,
            "query_tokens": query_tokens,
            "total_results": len(results),
            "showing": len(top_results),
            "results": top_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during search: {str(e)}")


@app.get("/api/documents")
def get_all_documents():
    """Get list semua dokumen yang sudah diindex"""
    try:
        if not state.is_indexed:
            return {
                "status": "success",
                "total": 0,
                "documents": []
            }
        
        return {
            "status": "success",
            "total": len(state.processed_docs),
            "documents": [
                {
                    "id": idx,
                    "filename": doc['filename'],
                    "original_text_preview": doc['original_text'][:200] + "...",
                    "processed_text_preview": doc['processed_text'][:200] + "...",
                    "word_count": doc['word_count']
                }
                for idx, doc in enumerate(state.processed_docs)
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/document/{doc_id}")
def get_document_detail(doc_id: int):
    """Get detail dokumen tertentu"""
    try:
        if not state.is_indexed or doc_id >= len(state.processed_docs):
            raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")
        
        doc = state.processed_docs[doc_id]
        raw_doc = state.documents[doc_id]
        
        # Get preprocessing steps
        steps = state.preprocessor.get_preprocessing_steps(raw_doc['text'][:500])
        
        return {
            "status": "success",
            "document": {
                "id": doc_id,
                "filename": doc['filename'],
                "file_path": doc['file_path'],
                "original_text": doc['original_text'],
                "processed_text": doc['processed_text'],
                "tokens": doc['tokens'],
                "word_count": doc['word_count'],
                "preprocessing_steps": steps
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/tfidf-matrix")
def get_tfidf_matrix():
    """Get TF-IDF matrix untuk visualisasi"""
    try:
        if not state.is_indexed:
            raise HTTPException(
                status_code=400,
                detail="Belum ada dokumen yang diindex"
            )
        
        matrix_data = state.tfidf_processor.get_tfidf_matrix_dict()
        
        return {
            "status": "success",
            "matrix": matrix_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/api/preprocess")
def preprocess_text(text: str):
    """
    Endpoint untuk testing preprocessing
    Menampilkan setiap tahap preprocessing
    """
    try:
        steps = state.preprocessor.get_preprocessing_steps(text)
        
        return {
            "status": "success",
            "steps": steps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
