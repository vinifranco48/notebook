import streamlit as st
import logging
from pathlib import Path
from typing import List, Optional, Dict, Union
from datetime import datetime

# Importações específicas
from langchain_core.documents import Document
from src.text_processing.load_clear import TextProcessor, TextProcessingConfig
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from spellchecker import SpellChecker
from store.vector_store import FAISSDBHandler
from langchain import hub

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatbotApp:
    """
    Aplicação Streamlit com interface de chatbot usando um LLM.
    """
    
    def __init__(self):
        """Inicializa a aplicação com as configurações padrão."""
        # Configurações de diretório
        self.data_dir = Path("./dados_vetoriais")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        # Aqui e o local onde esta ps pdfs
        self.pdf_dir = Path(r"C:\Users\Graúna Motos\Documents\notebook\data")
        
        # Configurações do processador de texto
        self.config = TextProcessingConfig(
            chunk_size=1000,
            overlap_size=200
        )
        
        # Inicializa componentes básicos
        self.text_processor = TextProcessor()
        self.vector_store = FAISSDBHandler(
            embedding_model=HuggingFaceEmbeddings(),
            persist_directory=str(self.data_dir),
            collection_name="documentos_processados"
        )
        
        # Configuração do LLM e QA Chain
        self.setup_llm()
        
        # Inicializa estados da sessão
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'processed_files' not in st.session_state:
            st.session_state.processed_files = set()
            self._process_documents()

    def setup_llm(self):
        qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
        combine_dochs = create_stuff_documents_chain(
            
        )
    def _process_documents(self):
        """Processa documentos e os armazena na base FAISS."""
        try:
            # aqui eu pego todos os pdfs
            pdf_files = list(self.pdf_dir.glob("*.pdf"))
            
            for file in pdf_files:
                if file.name not in st.session_state.processed_files:
                    documents = list(self.text_processor.process_documents([str(file)]))
                    self.vector_store.store_documents(documents)
                    st.session_state.processed_files.add(file.name)
                    
        except Exception as e:
            logger.error(f"Erro no processamento: {str(e)}")

    def run(self):
        """Executa a interface do chatbot."""
        st.title("Assistente de Documentos Inteligente 🤖")
        
        # Inicializa o estado da sessão
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'processed_files' not in st.session_state:
            st.session_state.processed_files = set()

        # Mostra mensagem inicial
        if not st.session_state.messages:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Olá! Sou seu assistente especializado em documentos. Como posso ajudar você hoje?"
            })

        # Mostra histórico de mensagens
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Campo de input do usuário
        if prompt := st.chat_input("Digite sua pergunta..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Processa e mostra resposta
            with st.chat_message("assistant"):
                with st.spinner("Pensando..."):
                    # Insira a lógica de resposta aqui
                    response = {"answer": "Resposta simulada", "sources": []}  # Substitua pelo método de resposta
                    st.markdown(response["answer"])
                    st.session_state.messages.append({"role": "assistant", "content": response["answer"]})

def main():
    """Função principal da aplicação."""
    app = ChatbotApp()
    app.run()

if __name__ == "__main__":
    main()
