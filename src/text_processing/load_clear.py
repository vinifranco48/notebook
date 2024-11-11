"""
MÓDULO: Processador Avançado de Documentos Textuais

Este módulo implementa um sistema robusto para processamento de documentos,
com foco especial em PDFs. Demonstra conceitos avançados de:

1. Processamento Paralelo em Python
2. Manipulação de Arquivos PDF
3. Processamento de Texto
4. Clean Architecture

Conceitos Fundamentais:
    - Thread Pooling: Processamento paralelo para melhor performance
    - Text Chunking: Divisão inteligente de texto para processamento
    - Clean Code: Princípios SOLID e boas práticas
    - Error Handling: Tratamento robusto de exceções

Melhorias Propostas:
    1. Implementação de Design Patterns
    2. Melhor gerenciamento de recursos
    3. Validação mais robusta
    4. Tipagem mais precisa
"""

from langchain_community.document_loaders import TextLoader, UnstructuredPDFLoader, PyPDFLoader
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from typing import List, Dict, Optional, Union, Generator
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import logging
import fitz
import re
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Configuração de logging aprimorada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@dataclass
class TextProcessingConfig:
    """
    Configuração para processamento de texto usando dataclass.
    
    Attributes:
        chunk_size (int): Tamanho dos chunks de texto
        overlap_size (int): Tamanho da sobreposição entre chunks
        max_threads (int): Número máximo de threads
        remove_numbers (bool): Remove números do texto
        remove_punctuation (bool): Remove pontuação
        min_chunk_length (int): Tamanho mínimo do chunk
    """
    chunk_size: int = 1000
    overlap_size: int = 200
    max_threads: int = 4
    remove_numbers: bool = False
    remove_punctuation: bool = False
    min_chunk_length: int = 100

class DocumentProcessor(ABC):
    """
    Interface abstrata para processadores de documento.
    Implementa o padrão Strategy para diferentes tipos de documentos.
    """
    @abstractmethod
    def extract_text(self, file_path: Path) -> str:
        """Método abstrato para extração de texto."""
        pass

class PDFProcessor(DocumentProcessor):
    """
    Processador específico para documentos PDF.
    Implementa otimizações específicas para PDF.
    """
    def extract_text(self, file_path: Path) -> str:
        """
        Extrai texto de PDF com processamento paralelo otimizado.
        
        Args:
            file_path: Caminho do arquivo PDF
            
        Returns:
            str: Texto extraído e processado
            
        Raises:
            FileNotFoundError: Se o arquivo não existir
            PyMuPDFError: Se houver erro na extração
        """
        doc = fitz.open(str(file_path))
        
        def process_page(page: fitz.Page) -> str:
            """Processa uma página individual do PDF."""
            return page.get_text()
        
        with ThreadPoolExecutor() as executor:
            pages = list(executor.map(process_page, doc))
            
        doc.close()
        return "\n".join(pages)

class TextProcessor:
    """
    Classe principal para processamento de documentos textuais.
    Implementa o padrão Facade para simplificar operações complexas.
    """
    
    def __init__(self, pdf_dir: Path, config: Optional[TextProcessingConfig] = None):
        """
        Inicializa o processador com configurações customizáveis e um diretório de PDFs.
        
        Args:
            pdf_dir: Caminho do diretório contendo os PDFs a serem processados.
            config: Configurações de processamento (opcional)
        """
        self.config = config or TextProcessingConfig()
        self.logger = logging.getLogger(__name__)
        self.pdf_processor = PDFProcessor()
        self.pdf_dir = pdf_dir

    def load_pdfs_from_directory(self) -> List[Path]:
        """
        Carrega todos os arquivos PDF do diretório especificado.
        
        Returns:
            List[Path]: Lista de caminhos dos arquivos PDF.
        """
        pdf_files = list(self.pdf_dir.glob("*.pdf"))
        if not pdf_files:
            self.logger.warning("Nenhum PDF encontrado no diretório especificado.")
        return pdf_files

    def process_all_pdfs(self) -> Generator[Document, None, None]:
        """
        Processa todos os PDFs do diretório especificado.
        
        Yields:
            Document: Chunks dos documentos processados.
        """
        pdf_files = self.load_pdfs_from_directory()
        return self.process_documents(pdf_files)

def process_document_batch(
    file_paths: List[str],
    config: Optional[TextProcessingConfig] = None
) -> Generator[Document, None, None]:
    """
    Função helper para processar lote de documentos.
    
    Args:
        file_paths: Lista de arquivos para processar
        config: Configurações opcionais
        
    Yields:
        Document: Documentos processados
    """
    processor = TextProcessor(config)
    yield from processor.process_documents(file_paths)

# Exemplo de uso
if __name__ == "__main__":
    config = TextProcessingConfig(
        chunk_size=1500,
        overlap_size=150,
        max_threads=6
    )
    
    processor = TextProcessor(config)
    
    try:
        documents = list(processor.process_documents(["exemplo.pdf"]))
        print(f"Processados {len(documents)} chunks de documento")
        
    except Exception as e:
        logging.error(f"Erro no processamento: {str(e)}")
        