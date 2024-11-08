from typing import List, Optional, Dict, Union
import logging
from pathlib import Path
import faiss  # Import FAISS para manipulação direta do índice
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FAISSDBHandler:
    """Classe Gerenciadora de Base de Dados Vetorial utilizando FAISS"""

    def __init__(
        self,
        embedding_model: Optional[HuggingFaceEmbeddings] = None,
        persist_directory: Union[str, Path] = "./dados",
        collection_name: str = "colecao_padrao"
    ):
        self.embedding_model = embedding_model or HuggingFaceEmbeddings()
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.index = None

        # Garante que o diretório existe
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Inicializa a base vetorial
        self._initialize_vectordb()

    def _initialize_vectordb(self) -> None:
        """Inicializa a base de dados vetorial usando FAISS."""
        index_path = self.persist_directory / "faiss_index.idx"
        try:
            if index_path.exists():
                self.index = faiss.read_index(str(index_path))
                logger.info(f"Índice FAISS carregado de {index_path}")
            else:
                # Obter dimensão dos embeddings diretamente
                d = self.embedding_model.dimension  # Ajuste se a dimensão do modelo for acessível
                if not d:
                    d = 768  # Valor padrão; altere conforme necessário
                self.index = faiss.IndexFlatL2(d)
                logger.info("Novo índice FAISS criado")
        except Exception as e:
            logger.error(f"Falha na inicialização da base vetorial FAISS: {type(e).__name__} - {str(e)}")
            raise ValueError("Erro ao inicializar a base vetorial FAISS")

    def store_documents(self, documents: List[Document], batch_size: int = 100) -> Dict:
        """Armazena documentos na base vetorial FAISS."""
        if not documents:
            logger.error("Nenhum documento fornecido para armazenamento")
            return {"status": "erro", "mensagem": "Nenhum documento fornecido"}
        
        try:
            embeddings = []
            for doc in documents:
                embedding = self.embedding_model.embed_text(doc.page_content)
                if embedding is None or len(embedding) == 0:
                    logger.warning(f"Documento '{doc}' não gerou embedding. Verifique o conteúdo.")
                    continue  # Ignora documentos com embeddings inválidos
                embeddings.append(embedding)
            
            if not embeddings:
                logger.error("Nenhum embedding válido foi gerado.")
                return {"status": "erro", "mensagem": "Nenhum embedding válido foi gerado."}
            
            embeddings_array = np.array(embeddings).astype('float32')
            self.index.add(embeddings_array)
            logger.info(f"Armazenados {len(embeddings)} documentos com sucesso na coleção {self.collection_name}")

            # Salva o índice
            index_path = self.persist_directory / "faiss_index.idx"
            faiss.write_index(self.index, str(index_path))
            logger.info(f"Índice FAISS salvo em {index_path}")
            
            return {"status": "sucesso", "mensagem": f"Armazenados {len(embeddings)} documentos"}
        
        except Exception as e:
            logger.error(f"Erro no armazenamento de documentos: {type(e).__name__} - {str(e)}")
            return {"status": "erro", "mensagem": str(e)}
