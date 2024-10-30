"""
Projeto principal para processamento de texto e gerenciamento de embeddings.
Fornece funcionalidades para processamento de documentos e armazenamento vetorial.
"""

from text_processing import TextProcessingConfig, TextProcessor
from vector_store import EmbeddingConfig, EmbeddingManager, VectorStoreManager

__version__ = '0.1.0'

__all__ = [
    'TextProcessingConfig',
    'TextProcessor',
    'EmbeddingConfig',
    'EmbeddingManager',
    'VectorStoreManager',
] 