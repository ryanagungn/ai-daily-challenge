"""
Day 11 - Hybrid Search & Re-ranking Engine Core Module
Menggabungkan Sparse Retrieval (BM25) dan Dense Vector Retrieval (text-embedding-004)
menggunakan Reciprocal Rank Fusion (RRF), serta Cross-Encoder Re-ranking dengan Gemini.
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from bm25 import BM25Index

load_dotenv()

CORPUS_PATH = Path(__file__).parent / "knowledge_corpus.json"
CACHE_PATH = Path(__file__).parent / "hybrid_vector_cache.json"

class RankedItem(BaseModel):
    id: str
    title: str
    category: str
    content: str
    bm25_rank: Optional[int] = None
    bm25_score: Optional[float] = None
    dense_rank: Optional[int] = None
    dense_score: Optional[float] = None
    rrf_score: float = 0.0

class ReRankedItem(BaseModel):
    id: str
    title: str
    category: str
    content: str
    relevance_score: int = Field(description="Skor relevansi final dari 0 sampai 100")
    reasoning: str = Field(description="Alasan konkret mengapa dokumen ini relevan dengan kueri pengguna")

class ReRankerResponse(BaseModel):
    items: List[ReRankedItem] = Field(description="Daftar dokumen setelah di-rerank dari yang paling relevan")

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
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))

def get_embedding(text: str, model_name: str = "text-embedding-004") -> List[float]:
    client = get_gemini_client()
    clean = text.strip()
    if not clean:
        return [0.0] * 768
    
    response = client.models.embed_content(
        model=model_name,
        contents=clean
    )
    if hasattr(response, "embeddings") and response.embeddings:
        return response.embeddings[0].values
    elif hasattr(response, "embedding") and response.embedding:
        return response.embedding.values
    return [0.0] * 768

class HybridSearchEngine:
    def __init__(self, corpus_path: Path = CORPUS_PATH, cache_path: Path = CACHE_PATH):
        self.corpus_path = corpus_path
        self.cache_path = cache_path
        self.corpus: List[Dict[str, Any]] = []
        self.vectors: Dict[str, List[float]] = {}
        self.bm25 = BM25Index()
        self.load_and_index()

    def load_and_index(self, force_reindex: bool = False, model_name: str = "text-embedding-004"):
        if self.corpus_path.exists():
            self.corpus = json.loads(self.corpus_path.read_text(encoding="utf-8"))
        
        # 1. Index BM25 (Sparse)
        self.bm25.fit(self.corpus, text_key="content")

        # 2. Index Dense Vectors
        if not force_reindex and self.cache_path.exists():
            try:
                self.vectors = json.loads(self.cache_path.read_text(encoding="utf-8"))
            except Exception:
                self.vectors = {}

        updated = False
        for doc in self.corpus:
            doc_id = doc["id"]
            if doc_id not in self.vectors or force_reindex:
                embed_text = f"{doc['title']}\n{doc['content']}"
                vec = get_embedding(embed_text, model_name=model_name)
                self.vectors[doc_id] = vec
                updated = True

        if updated:
            self.cache_path.write_text(json.dumps(self.vectors), encoding="utf-8")

    def search_bm25_only(self, query: str, top_k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        return self.bm25.search(query, top_k=top_k)

    def search_dense_only(self, query: str, top_k: int = 5, model_name: str = "text-embedding-004") -> List[Tuple[float, Dict[str, Any]]]:
        query_vec = np.array(get_embedding(query, model_name=model_name))
        scored = []
        for doc in self.corpus:
            doc_id = doc["id"]
            vec = np.array(self.vectors.get(doc_id, []))
            if len(vec) == 0:
                continue
            sim = cosine_similarity(query_vec, vec)
            scored.append((sim, doc))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]

    def hybrid_search_rrf(
        self,
        query: str,
        top_k: int = 5,
        bm25_weight: float = 0.5,
        dense_weight: float = 0.5,
        rrf_k: int = 60,
        model_name: str = "text-embedding-004"
    ) -> List[RankedItem]:
        """
        Reciprocal Rank Fusion (RRF):
        RRF_Score(d) = w_bm25 * 1/(k + rank_bm25) + w_dense * 1/(k + rank_dense)
        """
        # 1. Jalankan kedua pencarian secara independen (ambil top 10 masing-masing)
        pool_size = max(top_k * 2, 10)
        bm25_results = self.search_bm25_only(query, top_k=pool_size)
        dense_results = self.search_dense_only(query, top_k=pool_size, model_name=model_name)

        doc_dict: Dict[str, RankedItem] = {}

        # 2. Skor BM25
        for rank, (score, doc) in enumerate(bm25_results, 1):
            did = doc["id"]
            item = RankedItem(
                id=did,
                title=doc["title"],
                category=doc["category"],
                content=doc["content"],
                bm25_rank=rank,
                bm25_score=round(score, 3)
            )
            item.rrf_score += bm25_weight * (1.0 / (rrf_k + rank))
            doc_dict[did] = item

        # 3. Skor Dense
        for rank, (score, doc) in enumerate(dense_results, 1):
            did = doc["id"]
            if did in doc_dict:
                item = doc_dict[did]
                item.dense_rank = rank
                item.dense_score = round(score, 4)
                item.rrf_score += dense_weight * (1.0 / (rrf_k + rank))
            else:
                item = RankedItem(
                    id=did,
                    title=doc["title"],
                    category=doc["category"],
                    content=doc["content"],
                    dense_rank=rank,
                    dense_score=round(score, 4)
                )
                item.rrf_score += dense_weight * (1.0 / (rrf_k + rank))
                doc_dict[did] = item

        # 4. Urutkan berdasarkan gabungan RRF Score
        fused_results = list(doc_dict.values())
        fused_results.sort(key=lambda x: x.rrf_score, reverse=True)
        return fused_results[:top_k]

    def rerank_with_llm(
        self,
        query: str,
        candidates: List[RankedItem],
        model_name: str = "gemini-2.5-flash"
    ) -> List[ReRankedItem]:
        """
        Cross-Encoder LLM Re-ranker:
        Mengevaluasi kembali kandidat hasil Hybrid RRF menggunakan pemahaman semantik LLM tingkat tinggi.
        """
        if not candidates:
            return []

        client = get_gemini_client()

        candidates_text = []
        for i, c in enumerate(candidates, 1):
            candidates_text.append(f"[{i}] ID: {c.id}\nJudul: {c.title}\nKonten: {c.content}")
        
        candidates_formatted = "\n\n".join(candidates_text)

        prompt = f"""
        Kamu adalah Expert Retrieval Cross-Encoder & Search Quality Evaluator.
        Tugasmu adalah mereview daftar kandidat dokumen berikut dan mengurutkan kembali (re-rank)
        berdasarkan seberapa presisi dokumen tersebut menjawab/berkaitan dengan pertanyaan pengguna.

        KUERI PENGGUNA: "{query}"

        DAFTAR KANDIDAT DOKUMEN:
        {candidates_formatted}

        Instruksi Re-ranking:
        1. Berikan skor relevansi (relevance_score) dari 0 sampai 100 untuk setiap dokumen.
        2. Tuliskan 'reasoning' (alasan 1 kalimat) mengapa dokumen ini relevan atau tidak relevan.
        3. Urutkan dari yang paling relevan (skor tertinggi).
        """

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": ReRankerResponse,
                "temperature": 0.1,
            }
        )

        parsed = json.loads(response.text)
        return parsed.get("items", [])
