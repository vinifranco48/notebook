from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

class EmbeddingManager:
    def __init__(self, config):
        """
        Gerenciador de embeddings.
        
        Args:
            config (EmbeddingConfig): Configurações para o gerenciamento de embeddings
        """
        self.config = config
        # Usando o modelo multilingual da Sentence Transformers
        self.model = SentenceTransformer('distiluse-base-multilingual-cased-v1')
        
    def create_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """
        Cria embeddings para uma lista de textos.
        
        Args:
            texts (List[str]): Lista de textos para criar embeddings
            
        Returns:
            List[np.ndarray]: Lista de embeddings
        """
        return self.model.encode(texts, show_progress_bar=True)
