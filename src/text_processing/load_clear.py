from dataclasses import dataclass
from pathlib import Path
from typing import List, Generator, Optional
from abc import ABC, abstractmethod
import logging
from concurrent.futures import ThreadPoolExecutor
import fitz
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document

# Configuração de logging aprimorada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@dataclass
class TextProcessingConfig:
    """
    Configuração para processamento de texto usando dataclass.
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
    """
    @abstractmethod
    def extract_text(self, file_path: Path) -> str:
        """Método abstrato para extração de texto."""
        pass

class PDFProcessor(DocumentProcessor):
    """
    Processador específico para documentos PDF.
    """
    def extract_text(self, file_path: Path) -> str:
        if not file_path.exists():
            raise FileNotFoundError(f"O arquivo {file_path} não foi encontrado.")
        
        try:
            doc = fitz.open(str(file_path))
            def process_page(page: fitz.Page) -> str:
                return page.get_text()

            with ThreadPoolExecutor() as executor:
                pages = list(executor.map(process_page, doc))
            doc.close()
            return "\n".join(pages)
        except Exception as e:
            raise Exception(f"Erro ao processar o PDF {file_path}: {str(e)}")

class TextProcessor:
    """
    Classe principal para processamento de documentos textuais.
    """
    def __init__(self, pdf_dir: Path, config: Optional[TextProcessingConfig] = None):
        self.config = config or TextProcessingConfig()
        self.logger = logging.getLogger(__name__)
        self.pdf_processor = PDFProcessor()
        self.pdf_dir = pdf_dir

    def load_pdfs_from_directory(self) -> List[Path]:
        pdf_files = list(self.pdf_dir.glob("*.pdf"))
        if not pdf_files:
            self.logger.warning("Nenhum PDF encontrado no diretório especificado.")
        return pdf_files

    def _process_document(self, pdf_path: Path) -> List[Document]:
        """
        Processa um único documento PDF.
        """
        try:
            text = self.pdf_processor.extract_text(pdf_path)
            splitter = CharacterTextSplitter(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.overlap_size
            )
            chunks = splitter.split_text(text)
            return [Document(page_content=chunk) for chunk in chunks]
        except Exception as e:
            self.logger.error(f"Erro ao processar {pdf_path}: {str(e)}")
            return []

    def process_documents(self, pdf_files: List[Path]) -> Generator[Document, None, None]:
        """
        Processa uma lista de arquivos PDF e gera documentos divididos em chunks.
        """
        for pdf_path in pdf_files:
            self.logger.info(f"Processando arquivo: {pdf_path}")
            for doc in self._process_document(pdf_path):
                yield doc

    def process_all_pdfs(self) -> Generator[Document, None, None]:
        """
        Processa todos os PDFs do diretório especificado.
        """
        pdf_files = self.load_pdfs_from_directory()
        yield from self.process_documents(pdf_files)

def process_document_batch(
    file_paths: List[Path],
    config: Optional[TextProcessingConfig] = None
) -> Generator[Document, None, None]:
    """
    Função helper para processar lote de documentos.
    """
    processor = TextProcessor(Path("."), config)
    yield from processor.process_documents(file_paths)