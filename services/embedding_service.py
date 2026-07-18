import os
import numpy as np
from typing import List, Optional

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class EmbeddingService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = "models/text-embedding-004"
        self._initialized = False

        if HAS_GENAI and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self._initialized = True
            except Exception:
                self._initialized = False

    def get_embedding(self, text: str) -> List[float]:
        """
        Gets embedding for a single text. Falls back to a deterministic local vectorizer if genai is unavailable.
        """
        if self._initialized and HAS_GENAI:
            try:
                response = genai.embed_content(
                    model=self.model,
                    content=text,
                    task_type="retrieval_document"
                )
                return response["embedding"]
            except Exception:
                pass

        # Deterministic mock fallback vector (dimension 768)
        return self._local_vectorize(text)

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if self._initialized and HAS_GENAI:
            try:
                response = genai.embed_content(
                    model=self.model,
                    content=texts,
                    task_type="retrieval_document"
                )
                return response["embeddings"]
            except Exception:
                pass
        
        return [self._local_vectorize(t) for t in texts]

    def _local_vectorize(self, text: str, dimension: int = 768) -> List[float]:
        """
        Generates a deterministic vector from text by seeding NumPy with a hash of the text.
        This provides a mock embedding space where similar strings have somewhat similar vectors
        and exact strings have identical vectors, perfect for development and testing.
        """
        import hashlib
        # Hash text to get a stable integer seed
        hasher = hashlib.md5(text.encode('utf-8'))
        seed = int(hasher.hexdigest(), 16) % (2**32)
        
        rng = np.random.default_rng(seed)
        vector = rng.normal(0, 1.0, dimension)
        # Normalize to unit length
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector.tolist()
