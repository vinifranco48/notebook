from typing import List, Union
import logging
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .config import TextProcessingConfig

logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self, config: TextProcessingConfig):
        """
        Inicializa o processador de texto.
        
        Args:
            config (TextProcessingConfig): Configurações para processamento
        """
        self.config = config
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.overlap_size,
            length_function=len,
            is_separator_regex=False
        )
    
    def load_pdf(self, file_path: Union[str, Path]) -> List[Document]:
        """
        Carrega um arquivo PDF e retorna seus documentos.
        
        Args:
            file_path (Union[str, Path]): Caminho para o arquivo PDF
            
        Returns:
            List[Document]: Lista de documentos carregados
        """
        try:
            loader = PyPDFLoader(str(file_path))
            documents = loader.load()
            logger.info(f"PDF carregado com sucesso: {file_path}")
            return documents
        except Exception as e:
            logger.error(f"Erro ao carregar PDF {file_path}: {e}")
            raise

    def process_documents(self, file_paths: List[str]) -> List[Document]:
        """
        Processa uma lista de documentos e retorna chunks.
        
        Args:
            file_paths (List[str]): Lista de caminhos para os arquivos
            
        Returns:
            List[Document]: Lista de documentos processados
        """
        documents = []
        
        for file_path in file_paths:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"Arquivo não encontrado: {file_path}")
                continue
                
            if path.suffix.lower() == '.pdf':
                try:
                    docs = self.load_pdf(path)
                    documents.extend(docs)
                    logger.debug(f"Processado arquivo: {path}")
                except Exception as e:
                    logger.error(f"Erro ao processar {path}: {e}")
                    continue
            else:
                logger.warning(f"Formato de arquivo não suportado: {path.suffix}")
                
        if not documents:
            raise ValueError("Nenhum documento válido para processamento")
            
        try:
            # Divide os documentos em chunks
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Gerados {len(chunks)} chunks de texto")
            
            # Validação dos chunks
            for chunk in chunks:
                if not isinstance(chunk, Document):
                    logger.warning(f"Chunk inválido detectado: {type(chunk)}")
                if not chunk.page_content:
                    logger.warning("Chunk vazio detectado")
                    
            return chunks
        except Exception as e:
            logger.error(f"Erro ao dividir documentos em chunks: {e}")
            raise

