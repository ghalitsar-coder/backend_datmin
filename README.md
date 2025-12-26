# Sistem Temu Balik Dokumen - Backend API

Backend API menggunakan FastAPI untuk Sistem Temu Balik Dokumen dengan TF-IDF dan Generalized Jaccard Similarity.

## Installation

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python main.py
```

atau

```bash
uvicorn main:app --reload
```

Server akan berjalan di `http://localhost:8000`

## API Documentation

Akses dokumentasi interaktif di:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### 1. Health Check

- **GET** `/`
- Response: Status server dan info indexing

### 2. Upload & Index Documents

- **POST** `/api/upload`
- Body: `{"folder_path": "path/to/folder"}`
- Response: List dokumen yang berhasil diindex

### 3. Search Documents

- **POST** `/api/search`
- Body: `{"query": "kata kunci", "top_k": 10}`
- Response: Ranking dokumen berdasarkan similarity

### 4. Get All Documents

- **GET** `/api/documents`
- Response: List semua dokumen terindex

### 5. Get Document Detail

- **GET** `/api/document/{doc_id}`
- Response: Detail dokumen dengan preprocessing steps

### 6. Get TF-IDF Matrix

- **GET** `/api/tfidf-matrix`
- Response: Matriks TF-IDF untuk visualisasi

### 7. Preprocess Text (Testing)

- **POST** `/api/preprocess`
- Body: Plain text
- Response: Tahapan preprocessing

## Tech Stack

- **FastAPI**: Modern Python web framework
- **Scikit-learn**: TF-IDF vectorization
- **Sastrawi**: Indonesian text processing (stemming & stopword removal)
- **PyPDF2**: PDF processing
- **python-docx**: DOCX processing
