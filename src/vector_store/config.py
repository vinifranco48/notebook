from dataclasses import dataclass
from typing import Optional
import torch

@dataclass
class EmbeddingConfig:
    """Configurações para embeddings e vector store"""
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    cache_dir: Optional[str] = None
    batch_size: int = 32
    vector_store_path: Optional[str] = "./vector_store"
