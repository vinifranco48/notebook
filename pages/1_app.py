import streamlit as st
import logging
from pathlib import Path
from typing import List, Optional
import tempfile
import os
from langchain_core.documents import Document
from datetime import datetime
import os
import sys
from pathlib import Path

# Obtém o diretório raiz do projeto (pasta notebook)
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))


import streamlit as st
import logging
from pathlib import Path
from typing import List
from datetime import datetime

# Imports locais
from src.text_processing.load_clear import TextProcessor, TextProcessingConfig
from store.vector_store import ChromaDBHandler

import streamlit as st
import logging
from pathlib import Path
from typing import List
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from spellchecker import SpellChecker

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatbotApp:
    """
    Aplicação Streamlit com interface de chatbot usando Groq LLM.
    """
    
    def __init__(self):
        """Inicializa a aplicação com as configurações padrão."""
        # Configurações de diretório
        self.data_dir = Path("./dados_vetoriais")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_dir = Path(r"C:\Users\Graúna Motos\Documents\notebook\data")
        
        # Configurações do processador de texto
        self.config = TextProcessingConfig(
            chunk_size=1000,
            overlap_size=200
        )
        
        # Inicializa componentes básicos
        self.text_processor = TextProcessor()
        self.vector_store = ChromaDBHandler(
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
        """Configura o LLM e a chain de QA."""
        try:
            # Inicializa o Groq LLM
            self.llm = ChatGroq(
                groq_api_key='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',
                model_name="llama3-70b-8192",  # Modelo poderoso com contexto longo
                temperature=0.4,
                max_tokens=1000
            )
            
            # Configura o retriever
            vectorstore_retriever = self.vector_store.get_retriever()
            
            # Template do prompt
            prompt_template = """
            Você é um assistente especializado em analisar documentos e responder perguntas.
            Por favor, evite especular se não tiver certeza. Simplesmente diga que você não sabe.
            As respostas devem ser concisas, em até 300 palavras detalhando e explicando os processos de maneira didática, sem erros de escrita e em português.

            Contexto dos documentos:
            {context}

            Pergunta: {question}

            Resposta:"""
            
            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            # Configura a chain de QA
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=vectorstore_retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": PROMPT}
            )
            
        except Exception as e:
            logger.error(f"Erro na configuração do LLM: {str(e)}")
            st.error("Erro na configuração do assistente. Por favor, verifique as credenciais da API.")

    def _process_documents(self):
        """Processa documentos em segundo plano."""
        try:
            pdf_files = list(self.pdf_dir.glob("*.pdf"))
            
            for file in pdf_files:
                if file.name not in st.session_state.processed_files:
                    documents = list(self.text_processor.process_documents([str(file)]))
                    self.vector_store.store_documents(documents)
                    st.session_state.processed_files.add(file.name)
                    
        except Exception as e:
            logger.error(f"Erro no processamento: {str(e)}")

    def get_llm_response(self, query: str) -> dict:
        """Obtém resposta do LLM com fontes."""
        try:
            response = self.qa_chain(query)
            
            result = {
                "answer": response["result"],
                "sources": []
            }
            
            # Adiciona as fontes se disponíveis
            if "source_documents" in response:
                for doc in response["source_documents"]:
                    source = doc.metadata.get("source", "documento não especificado")
                    result["sources"].append(source)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na consulta ao LLM: {str(e)}")
            return {
                "answer": "Desculpe, ocorreu um erro ao processar sua pergunta.",
                "sources": []
            }

    def run(self):
        """Executa a interface do chatbot."""
        st.title("Assistente de Documentos Inteligente 🤖")
        
        # Inicializa o estado da sessão para 'messages' e 'processed_files' se não existir
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
            # Adiciona mensagem do usuário
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Processa e mostra resposta
            with st.chat_message("assistant"):
                with st.spinner("Pensando..."):
                    response = self.get_llm_response(prompt)
                    
                    # Formata a resposta com as fontes
                    answer = response["answer"]
                    if response["sources"]:
                        sources_text = "\n\n📚 **Fontes consultadas:**\n" + "\n".join(f"- {source}" for source in set(response["sources"]))
                        full_response = f"{answer}\n{sources_text}"
                    else:
                        full_response = answer
                    
                    st.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

def main():
    """Função principal da aplicação."""
    app = ChatbotApp()
    app.run()

if __name__ == "__main__":
    main()