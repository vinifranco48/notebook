from typing import List, Optional
import logging
from pathlib import Path
import pickle
import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class VectorStoreManager:
    def __init__(self, config):
        self.config = config
        self.embeddings = HuggingFaceEmbeddings(
            model_name="distiluse-base-multilingual-cased-v1",
            model_kwargs={'device': 'cpu'}
        )
        self._vector_store = None
        
        # Diretório para salvar os pickles
        self.store_dir = Path('data/embeddings')
        self.store_dir.mkdir(parents=True, exist_ok=True)
        
    def _save_pickle(self, obj, filename: str):
        """Salva objeto como pickle"""
        path = self.store_dir / filename
        with open(path, 'wb') as f:
            pickle.dump(obj, f)
            
    def _load_pickle(self, filename: str):
        """Carrega objeto do pickle"""
        path = self.store_dir / filename
        if path.exists():
            with open(path, 'rb') as f:
                return pickle.load(f)
        return None
        
    def create_vector_store(self, documents: List[Document], store_name: str) -> FAISS:
        """Cria e salva embeddings dos documentos"""
        try:
            logger.info(f"Processando {len(documents)} documentos")
            
            # Cria embeddings
            texts = [doc.page_content for doc in documents]
            embeddings = self.embeddings.embed_documents(texts)
            
            # Salva dados
            self._save_pickle({
                'embeddings': embeddings,
                'texts': texts,
                'documents': documents
            }, f"{store_name}.pkl")
            
            logger.info(f"Embeddings salvos para {store_name}")
            
            # Cria vector store em memória
            self._vector_store = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )
            
            return self._vector_store
            
        except Exception as e:
            logger.error(f"Erro ao criar embeddings: {str(e)}")
            raise
            
    def query_vector_store(self, query: str, store_name: str, k: int = 3) -> List[Document]:
        """Busca documentos similares"""
        try:
            # Carrega dados se necessário
            if self._vector_store is None:
                data = self._load_pickle(f"{store_name}.pkl")
                if data is None:
                    raise FileNotFoundError(f"Dados não encontrados para {store_name}")
                    
                # Recria vector store
                self._vector_store = FAISS.from_documents(
                    documents=data['documents'],
                    embedding=self.embeddings
                )
            
            # Realiza busca
            logger.info(f"Buscando: '{query}'")
            results = self._vector_store.similarity_search(query, k=k)
            logger.info(f"Encontrados {len(results)} resultados")
            
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca: {str(e)}")
            raise