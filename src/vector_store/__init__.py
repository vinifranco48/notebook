"""
Módulo vector_store para gerenciamento de embeddings e armazenamento vetorial.
"""

from .config import EmbeddingConfig
from .embedding_manager import EmbeddingManager
from .vector_store_manager import VectorStoreManager

__all__ = ['EmbeddingConfig', 'EmbeddingManager', 'VectorStoreManager'] 