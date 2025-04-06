# services/rag_service.py

import numpy as np
from typing import List

class RAGService:
    def __init__(self, embedding_model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        """
        Service for Retrieval-Augmented Generation (RAG) via similarity search.
        Uses a SentenceTransformer to embed text and FAISS for similarity search.
        :param embedding_model_name: Name of the embedding model for SentenceTransformer.
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError("sentence-transformers library is required for RAGService.")
        self.embedder = SentenceTransformer(embedding_model_name)
        self.index = None
        self.documents: List[str] = []

def build_index(self, texts: List[str]):
        """
        Build a FAISS index from a list of text documents or tokens.
        :param texts: List of text strings to index.
        """
        if not texts:
            raise ValueError("No texts provided to build the index.")
        embeddings = self.embedder.encode(texts, show_progress_bar=False)
        embeddings = np.array(embeddings, dtype='float32')
        # Normalize embeddings for cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1e-9
        embeddings_norm = embeddings / norms
        dim = embeddings_norm.shape[1]
        try:
            import faiss
        except ImportError:
            raise ImportError("faiss library is required for similarity search.")
        self.index = faiss.IndexFlatIP(dim)  # inner product index on normalized vectors = cosine similarity
        self.index.add(embeddings_norm)
        self.documents = list(texts)

def search(self, query: str, k: int = 5) -> List[str]:
        """
        Search the index for texts similar to the query.
        :param query: Query string to search for.
        :param k: Number of top similar results to return.
        :return: List of text strings corresponding to the most similar entries.
        """
        if self.index is None:
            raise RuntimeError("The index has not been built. Call build_index() first.")
        if k <= 0:
            return []
        # Embed and normalize the query
        query_vec = self.embedder.encode([query], show_progress_bar=False)
        query_vec = np.array(query_vec, dtype='float32')
        norm = np.linalg.norm(query_vec)
        if norm == 0:
            norm = 1e-9
        query_vec = query_vec / norm
        try:
            import faiss
        except ImportError:
            raise ImportError("faiss library is required for similarity search.")
        k_eff = min(k, len(self.documents))
        D, I = self.index.search(query_vec, k_eff)
        results = []
        for idx in I[0]:
            if idx < 0 or idx >= len(self.documents):
                continue
            results.append(self.documents[idx])
        return results
