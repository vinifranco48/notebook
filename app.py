import os
import sys
from pathlib import Path
import logging
from typing import List
import streamlit as st
from langchain_core.documents import Document
from groq import Groq

# Configuração do PYTHONPATH
current_dir = Path(__file__).resolve().parent
src_dir = current_dir / 'src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from text_processing.config import TextProcessingConfig
from text_processing.load_clear import TextProcessor
from vector_store.config import EmbeddingConfig
from vector_store.vector_store_manager import VectorStoreManager

# Configuração do cliente Groq
groq_client = Groq(api_key="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")

def setup_logging():
    """Configura o sistema de logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

def process_documents(text_processor: TextProcessor, file_paths: List[str]) -> List[Document]:
    """Processa os documentos usando o TextProcessor."""
    documents = text_processor.process_documents(file_paths)
    if not documents:
        raise ValueError("Nenhum documento foi processado")
    return documents

def create_vector_store(vector_store_manager: VectorStoreManager, 
                       documents: List[Document], 
                       store_name: str):
    """Cria o armazenamento vetorial."""
    return vector_store_manager.create_vector_store(documents, store_name)

def process_with_llama(text: str) -> str:
    """Processa o texto usando o modelo LLaMA."""
    try:
        prompt = f"""Você é um assistente especializado em documentos e sua tarefa é:
        1. Analisar cuidadosamente o conteúdo fornecido
        2. Responder perguntas sobre o documento de forma clara e objetiva
        3. Citar trechos relevantes do documento quando necessário
        4. Ensinar aos usuários como usar o sistema
        
        Conteúdo para análise: {text}
        """
        
        response = groq_client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt
            }],
            model="llama3-70b-8192",
            temperature=0.5,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Erro ao processar texto com LLaMA: {e}")
        return text

def initialize_chat_history():
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def main():
    """Interface principal do chatbot."""
    st.set_page_config(page_title="Assistente de Documentos", layout="wide")
    st.title("Assistente de Documentos 📚")
    
    initialize_chat_history()
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Configurações
        text_config = TextProcessingConfig(chunk_size=500, overlap_size=50)
        embedding_config = EmbeddingConfig(vector_store_path=str(current_dir / 'vector_stores'))

        # Inicialização dos processadores
        text_processor = TextProcessor(text_config)
        vector_store_manager = VectorStoreManager(embedding_config)

        # Caminho do arquivo
        data_path = current_dir / 'data' / 'despesas.pdf'
        if not data_path.exists():
            st.error("Arquivo de documentos não encontrado!")
            return

        # Processa os documentos (apenas na primeira execução)
        if 'processed_store' not in st.session_state:
            documents = process_documents(text_processor, [str(data_path)])
            processed_documents = []
            
            with st.spinner('Processando documentos...'):
                for doc in documents:
                    doc.page_content = process_with_llama(doc.page_content)
                    processed_documents.append(doc)
                
                vector_store = create_vector_store(
                    vector_store_manager,
                    processed_documents,
                    store_name='despesas'
                )
                st.session_state.processed_store = True

        # Interface do chat
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Faça uma pergunta sobre o documento..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            results = vector_store_manager.query_vector_store(
                query=prompt,
                store_name='despesas',
                k=1
            )

            if results:
                response = process_with_llama(f"Com base no seguinte trecho do documento: {results[0].page_content}, responda: {prompt}")
                
                with st.chat_message("assistant"):
                    st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

    except Exception as e:
        st.error(f"Ocorreu um erro: {str(e)}")
        logger.exception("Detalhes do erro:")

if __name__ == '__main__':
    main()
