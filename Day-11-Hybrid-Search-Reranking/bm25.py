"""
Day 11 - Pure Python BM25 (Okapi BM25) Sparse Retrieval Engine
Implementasi algoritma pencarian leksikal BM25 standar industri tanpa dependensi pihak ketiga.
"""

import math
import re
from typing import List, Dict, Any, Tuple

def tokenize(text: str) -> List[str]:
    """Tokenisasi teks menjadi kata/token alfanumerik huruf kecil."""
    return re.findall(r"\b[a-zA-Z0-9_\-]+\b", text.lower())

class BM25Index:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avgdl = 0.0
        self.doc_lengths: List[int] = []
        self.doc_token_freqs: List[Dict[str, int]] = []
        self.idf: Dict[str, float] = {}
        self.documents: List[Dict[str, Any]] = []

    def fit(self, documents: List[Dict[str, Any]], text_key: str = "content"):
        """Membangun indeks BM25 dari kumpulan dokumen."""
        self.documents = documents
        self.corpus_size = len(documents)
        self.doc_lengths = []
        self.doc_token_freqs = []
        self.idf = {}

        if self.corpus_size == 0:
            self.avgdl = 0.0
            return

        df: Dict[str, int] = {}
        total_len = 0

        for doc in documents:
            text = f"{doc.get('title', '')} {doc.get(text_key, '')}"
            tokens = tokenize(text)
            doc_len = len(tokens)
            total_len += doc_len
            self.doc_lengths.append(doc_len)

            freqs: Dict[str, int] = {}
            seen_in_doc = set()
            for token in tokens:
                freqs[token] = freqs.get(token, 0) + 1
                if token not in seen_in_doc:
                    df[token] = df.get(token, 0) + 1
                    seen_in_doc.add(token)

            self.doc_token_freqs.append(freqs)

        self.avgdl = total_len / self.corpus_size

        # Hitung IDF (Inverse Document Frequency)
        for token, freq in df.items():
            # Okapi BM25 standard IDF with smoothing (+1)
            idf_val = math.log(1.0 + (self.corpus_size - freq + 0.5) / (freq + 0.5))
            self.idf[token] = max(0.0, idf_val)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        """Menghitung skor BM25 untuk kueri terhadap semua dokumen."""
        tokens = tokenize(query)
        if not tokens or self.corpus_size == 0:
            return []

        scores: List[float] = [0.0] * self.corpus_size

        for token in tokens:
            if token not in self.idf:
                continue

            idf_val = self.idf[token]
            for idx in range(self.corpus_size):
                tf = self.doc_token_freqs[idx].get(token, 0)
                if tf == 0:
                    continue

                doc_len = self.doc_lengths[idx]
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avgdl))
                scores[idx] += idf_val * (numerator / denominator)

        # Pasangkan dengan dokumen dan urutkan
        results = [(scores[i], self.documents[i]) for i in range(self.corpus_size) if scores[i] > 0]
        results.sort(key=lambda x: x[0], reverse=True)
        return results[:top_k]
