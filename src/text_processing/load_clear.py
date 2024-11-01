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
    
    def __init__(self, config: Optional[TextProcessingConfig] = None):
        """
        Inicializa o processador com configurações customizáveis.
        
        Args:
            config: Configurações de processamento (opcional)
        """
        self.config = config or TextProcessingConfig()
        self.logger = logging.getLogger(__name__)
        self.pdf_processor = PDFProcessor()

    def process_documents(self, file_paths: Union[List[str], List[Path]]) -> Generator[Document, None, None]:
        """
        Processa documentos de forma otimizada usando generator.
        
        Args:
            file_paths: Lista de caminhos de arquivo
            
        Yields:
            Document: Documentos processados
            
        Raises:
            FileNotFoundError: Se algum arquivo não existir
        """
        for file_path in file_paths:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
            
            try:
                raw_text = self.pdf_processor.extract_text(path)
                clean_text = self._clean_text(raw_text)
                
                yield from self._create_chunks(clean_text, path.name)
                
            except Exception as e:
                self.logger.error(f"Erro processando {path}: {str(e)}")
                raise

    def _clean_text(self, text: str) -> str:
        """
        Limpa e normaliza o texto usando expressões regulares otimizadas.
        
        Args:
            text: Texto para limpar
            
        Returns:
            str: Texto limpo e normalizado
        """
        # Compilação prévia das regex para melhor performance
        space_pattern = re.compile(r'\s+')
        ascii_pattern = re.compile(r'[^\x00-\x7F]+')
        number_pattern = re.compile(r'\d+')
        punct_pattern = re.compile(r'[^\w\s]')

        text = space_pattern.sub(' ', text)
        text = ascii_pattern.sub('', text)

        if self.config.remove_numbers:
            text = number_pattern.sub('', text)
        if self.config.remove_punctuation:
            text = punct_pattern.sub('', text)

        return "\n".join(
            line.strip() for line in text.split('\n')
            if len(line.strip()) >= self.config.min_chunk_length
        )

    def _create_chunks(self, text: str, source: str) -> Generator[Document, None, None]:
        """
        Cria chunks de documento com metadata.
        
        Args:
            text: Texto para dividir
            source: Nome do arquivo fonte
            
        Yields:
            Document: Chunks de documento com metadata
        """
        splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.overlap_size,
            length_function=len
        )

        for chunk in splitter.split_text(text):
            yield Document(
                page_content=chunk,
                metadata={
                    "source": source,
                    "chunk_size": len(chunk),
                    "has_numbers": bool(re.search(r'\d', chunk))
                }
            )

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