from typing import List, Optional, Dict, Union
import logging
from pathlib import Path
from langchain_chroma import Chroma  # Atualizado para a nova versão de LangChain Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from chromadb.config import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaDBHandler:
    """Classe Gerenciadora de Base de Dados Vetorial"""

    def __init__(
        self,
        embedding_model: Optional[HuggingFaceEmbeddings] = None,
        persist_directory: Union[str, Path] = "./dados",
        collection_name: str = "colecao_padrao"
    ):
        self.embedding_model = embedding_model or HuggingFaceEmbeddings()
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.vectordb = None

        # Garante que o diretório existe
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Inicializa a base vetorial
        self._initialize_vectordb()

    def _initialize_vectordb(self) -> None:
        """Inicializa a base de dados vetorial."""
        try:
            self.vectordb = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embedding_model,
                collection_name=self.collection_name,
                client_settings=Settings(
                    anonymized_telemetry=False
                )
            )
            logger.info(f"Base vetorial inicializada em {self.persist_directory} para a coleção {self.collection_name}")
        except Exception as e:
            logger.error(f"Falha na inicialização da base vetorial: {type(e).__name__} - {str(e)}")
            raise ValueError("Erro ao inicializar a base vetorial")

    def store_documents(self, documents: List[Document], batch_size: int = 100) -> Dict:
        """Armazena documentos na base vetorial."""
        if not documents:
            logger.error("Nenhum documento fornecido para armazenamento")
            return {"status": "erro", "mensagem": "Nenhum documento fornecido"}
        
        try:
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                if self.vectordb is None:
                    self._initialize_vectordb()  # Assegura que a base está inicializada
                
                self.vectordb.add_documents(batch)
                logger.info(f"Processado lote de {len(batch)} documentos na coleção {self.collection_name}")

            logger.info(f"Armazenados {len(documents)} documentos com sucesso na coleção {self.collection_name}")
            return {"status": "sucesso", "mensagem": f"Armazenados {len(documents)} documentos"}
        
        except Exception as e:
            logger.error(f"Erro no armazenamento de documentos: {type(e).__name__} - {str(e)}")
            return {"status": "erro", "mensagem": str(e)}

    def get_retriever(self, search_kwargs: Optional[Dict] = None) -> BaseRetriever:
        """Retorna um retriever para uso com LangChain."""
        if not self.vectordb:
            logger.error("Base vetorial não inicializada")
            raise ValueError("Base vetorial não inicializada")
        
        search_kwargs = search_kwargs or {"k": 4}
        return self.vectordb.as_retriever(**search_kwargs)

    def retrieve_similar(
        self,
        query: str,
        k: int = 1,
        filter_dict: Optional[Dict] = None
    ) -> Union[Dict, List[Document]]:
        """Recupera documentos similares à consulta."""
        if not self.vectordb:
            logger.error("Base vetorial não inicializada")
            return {"status": "erro", "mensagem": "Base vetorial não inicializada"}
        if not query.strip():
            logger.error("Consulta vazia fornecida")
            return {"status": "erro", "mensagem": "Consulta vazia fornecida"}

        try:
            similar_docs = self.vectordb.similarity_search(
                query,
                k=k,
                filter=filter_dict
            )
            logger.info(f"Recuperados {len(similar_docs)} documentos similares para a coleção {self.collection_name}")
            return similar_docs
            
        except Exception as e:
            logger.error(f"Erro na recuperação de documentos: {type(e).__name__} - {str(e)}")
            return {"status": "erro", "mensagem": str(e)}

    def get_collection_stats(self) -> Dict:
        """Retorna estatísticas da coleção."""
        if not self.vectordb:
            logger.error("Base vetorial não inicializada")
            return {"status": "erro", "mensagem": "Base vetorial não inicializada"}
        
        try:
            collection = self.vectordb._collection
            stats = {
                "nome_colecao": self.collection_name,
                "total_documentos": collection.count(),
                "diretorio_persistencia": str(self.persist_directory)
            }
            logger.info(f"Estatísticas da coleção {self.collection_name}: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {type(e).__name__} - {str(e)}")
            return {"status": "erro", "mensagem": str(e)}
