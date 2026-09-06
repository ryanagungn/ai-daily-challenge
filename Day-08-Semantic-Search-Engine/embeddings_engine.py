"""
Day 08 - Semantic Search Engine with Vector Embeddings Core Module
Mengimplementasikan embedding generation (text-embedding-004), vector caching,
kalkulasi Cosine Similarity, keyword matching comparison, dan 2D PCA projection.
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

CACHE_FILE = Path(__file__).parent / "vector_cache.json"
KB_FILE = Path(__file__).parent / "knowledge_base.json"

class SearchResult(BaseModel):
    id: str
    title: str
    category: str
    content: str
    similarity_score: float = Field(description="Skor kemiripan semantik (0.0 - 1.0)")
    similarity_percentage: str
    match_type: str = Field(default="Semantic Vector")

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY tidak ditemukan! Pastikan sudah menyetelnya di file .env")
    
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except ImportError:
        raise ImportError("Package 'google-genai' belum terpasang. Jalankan: pip install google-genai")

def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Menghitung sudut kosinus (kemiripan arah) antara 2 vektor numerik."""
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))

def get_embedding(text: str, model_name: str = "text-embedding-004") -> List[float]:
    """Mengambil representasi vector embedding dari teks menggunakan Gemini Embedding API."""
    client = get_gemini_client()
    clean_text = text.strip()
    if not clean_text:
        return [0.0] * 768

    response = client.models.embed_content(
        model=model_name,
        contents=clean_text
    )
    # google-genai embedding response structure
    if hasattr(response, "embeddings") and response.embeddings:
        return response.embeddings[0].values
    elif hasattr(response, "embedding") and response.embedding:
        return response.embedding.values
    else:
        raise RuntimeError("Format respon embedding tidak dikenali.")

class VectorDatabase:
    def __init__(self, kb_path: Path = KB_FILE, cache_path: Path = CACHE_FILE):
        self.kb_path = kb_path
        self.cache_path = cache_path
        self.documents: List[Dict[str, Any]] = []
        self.vectors: Dict[str, List[float]] = {}
        self.load_or_build_index()

    def load_or_build_index(self):
        """Memuat dokumen dan vector embedding dari cache jika tersedia."""
        if self.kb_path.exists():
            self.documents = json.loads(self.kb_path.read_text(encoding="utf-8"))
        
        if self.cache_path.exists():
            try:
                self.vectors = json.loads(self.cache_path.read_text(encoding="utf-8"))
            except Exception:
                self.vectors = {}

    def ensure_indexed(self, model_name: str = "text-embedding-004") -> int:
        """Memastikan semua dokumen telah memiliki vector embedding dalam cache."""
        updated = 0
        for doc in self.documents:
            doc_id = doc["id"]
            if doc_id not in self.vectors:
                # Gabungkan title dan content untuk context embedding yang optimal
                text_to_embed = f"{doc['title']}\n{doc['content']}"
                vec = get_embedding(text_to_embed, model_name=model_name)
                self.vectors[doc_id] = vec
                updated += 1

        if updated > 0:
            self.cache_path.write_text(json.dumps(self.vectors), encoding="utf-8")
        return updated

    def add_document(self, title: str, category: str, content: str, model_name: str = "text-embedding-004") -> str:
        """Menambahkan dokumen baru ke knowledge base dan langsung meng-indeks vektornya."""
        new_id = f"doc_{len(self.documents) + 1:02d}"
        doc_entry = {
            "id": new_id,
            "title": title.strip(),
            "category": category.strip(),
            "content": content.strip()
        }
        self.documents.append(doc_entry)
        self.kb_path.write_text(json.dumps(self.documents, indent=2, ensure_ascii=False), encoding="utf-8")

        # Generate & simpan vector
        text_to_embed = f"{title}\n{content}"
        vec = get_embedding(text_to_embed, model_name=model_name)
        self.vectors[new_id] = vec
        self.cache_path.write_text(json.dumps(self.vectors), encoding="utf-8")
        return new_id

    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.4,
        model_name: str = "text-embedding-004"
    ) -> List[SearchResult]:
        """
        Melakukan pencarian semantik (Semantic Search) dengan menghitung Cosine Similarity
        antara Query Vector dan semua Dokumen Vektor di Vector Store.
        """
        self.ensure_indexed(model_name=model_name)
        query_vector = np.array(get_embedding(query, model_name=model_name))

        scored_results = []
        for doc in self.documents:
            doc_id = doc["id"]
            doc_vec = np.array(self.vectors.get(doc_id, []))
            if len(doc_vec) == 0:
                continue

            score = cosine_similarity(query_vector, doc_vec)
            if score >= threshold:
                scored_results.append((score, doc))

        # Urutkan berdasarkan similarity tertinggi (descending)
        scored_results.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, doc in scored_results[:top_k]:
            results.append(SearchResult(
                id=doc["id"],
                title=doc["title"],
                category=doc["category"],
                content=doc["content"],
                similarity_score=round(score, 4),
                similarity_percentage=f"{score * 100:.1f}%",
                match_type="Semantic Vector"
            ))
        return results

    def keyword_search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        Pencarian konvensional berbasis exact keyword match untuk perbandingan vs Semantic Search.
        """
        keywords = [k.lower() for k in query.split() if len(k) > 2]
        scored = []

        for doc in self.documents:
            full_text = f"{doc['title']} {doc['content']}".lower()
            matches = sum(full_text.count(kw) for kw in keywords)
            if matches > 0:
                scored.append((matches, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, doc in scored[:top_k]:
            results.append(SearchResult(
                id=doc["id"],
                title=doc["title"],
                category=doc["category"],
                content=doc["content"],
                similarity_score=float(score),
                similarity_percentage=f"{score} kata cocok",
                match_type="Exact Keyword Match"
            ))
        return results

    def compute_2d_projection(self) -> Tuple[List[Dict[str, Any]], List[float], List[float]]:
        """
        Melakukan reduksi dimensi PCA (dari 768 dimensi ke 2D) menggunakan SVD murni NumPy
        untuk visualisasi posisi vektor dokumen pada grafik 2D.
        """
        if not self.vectors:
            return [], [], []

        doc_ids = [d["id"] for d in self.documents if d["id"] in self.vectors]
        matrix = np.array([self.vectors[did] for did in doc_ids])

        if matrix.shape[0] < 2:
            return [], [], []

        # Mean centering
        mean = np.mean(matrix, axis=0)
        centered = matrix - mean

        # SVD PCA 2 Components
        _, _, vh = np.linalg.svd(centered, full_matrices=False)
        coords_2d = np.dot(centered, vh[:2].T)

        projected = []
        for i, did in enumerate(doc_ids):
            doc = next(d for d in self.documents if d["id"] == did)
            projected.append({
                "id": did,
                "title": doc["title"],
                "category": doc["category"],
                "x": float(coords_2d[i, 0]),
                "y": float(coords_2d[i, 1])
            })

        return projected, coords_2d[:, 0].tolist(), coords_2d[:, 1].tolist()
