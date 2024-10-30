from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import HuggingFaceHub, HuggingFaceEndpoint
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain import HuggingFaceHub
from langchain_community.llms import HuggingFaceEndpoint
from langchain.document_loaders import UnstructuredPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
import re
import textwrap
import fitz
from tqdm import tqdm
import logging

class ProcessingConfig:
    chunk_size = 1000
    chunk_overlap = 200
    embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
    device = "cpu"
    cache_dir = None


class DocumentProcessor:
    def __init__(self, config: ProcessingConfig = ProcessingConfig()):
        self.logger = logging.getLogger(__name__)
    def _initialize_embeddings(self) -> HuggingFaceEmbeddings:
        return HuggingFaceEmbeddings(
            model_name.config.embedding_model,
            model_kwargs = {
                'device':self.config.device
            },
            cache_folder=self.config.cache_dir
        )
    def generate_embeddings(chunks, batch_size=32):
        embeddings = []
        for i in tqdm(range(0, len(chunks), batch_size), desc="Generating embeddings"):
            batch = chunks[i:i+batch_size]
            batch_embeddings = embeddings.embed_documents(batch)
            embeddings.extend(batch_embeddings)
        return embeddings



    
