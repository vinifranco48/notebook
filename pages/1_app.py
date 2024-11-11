import streamlit as st
from pathlib import Path
import asyncio
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da página Streamlit
st.set_page_config(
    page_title="Chat com Documentos",
    page_icon="📚",
    layout="centered"
)

# Estilização CSS personalizada
st.markdown("""
    <style>
    .stTextInput {
        padding: 10px;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e6f3ff;
    }
    .assistant-message {
        background-color: #f0f2f6;
    }
    </style>
""", unsafe_allow_html=True)

# Prompt personalizado
CUSTOM_PROMPT = """
Você é um assistente especializado em analisar e explicar documentos.

Contexto dos documentos:
{context}

Pergunta do usuário:
{question}

Instrução: Responda sobre os documentos com precisão e didaticamente, explicando o que está no documento de acordo com o contexto da pergunta. Se a informação não estiver nos documentos, indique claramente.

Resposta:
"""

@st.cache_resource
def initialize_rag_system():
    """Inicializa o sistema RAG com cache para evitar recarregamento"""
    try:
        # Inicializar embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
        
        # Verificar se o índice FAISS existe
        if not Path("faiss_index").exists():
            st.error("Índice FAISS não encontrado. Execute primeiro o script de processamento dos PDFs.")
            st.stop()
        
        # Carregar o índice FAISS
        vectorstore = FAISS.load_local(
            "faiss_index",
            embeddings,
            allow_dangerous_deserialization=True
        )
        
        # Criar o template do prompt
        prompt_template = PromptTemplate(
            template=CUSTOM_PROMPT,
            input_variables=["context", "question"]
        )
        
        # Verificar API key do Groq
        if not os.getenv("GROQ_API_KEY"):
            st.error("API Key do Groq não encontrada. Configure a variável de ambiente GROQ_API_KEY.")
            st.stop()
        
        # Configurar o modelo LLM
        llm = ChatGroq(
            temperature=0.1,
            model_name="mixtral-8x7b-32768",
            max_tokens=1024
        )
        
        # Criar a chain de QA
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
            chain_type_kwargs={
                "prompt": prompt_template,
                "verbose": False
            }
        )
        
        return qa_chain
    
    except Exception as e:
        st.error(f"Erro ao inicializar o sistema: {str(e)}")
        st.stop()

async def get_response(qa_chain, query):
    """Função assíncrona para obter resposta do sistema RAG"""
    try:
        response = await qa_chain.ainvoke({"query": query})
        return response['result']
    except Exception as e:
        return f"Erro ao processar a pergunta: {str(e)}"

def main():
    st.title("💬 Chat com Documentos")
    st.subheader("Faça perguntas sobre seus documentos")
    
    # Inicializar o histórico de chat na sessão
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Status na sidebar
    st.sidebar.title("Status do Sistema")
    st.sidebar.info("Sistema inicializado e pronto para uso")
    
    try:
        # Inicializar o sistema RAG
        qa_chain = initialize_rag_system()
        
        # Mostrar histórico de mensagens
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Input do usuário
        if prompt := st.chat_input("Digite sua pergunta aqui"):
            # Adicionar mensagem do usuário
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Gerar e mostrar resposta
            with st.chat_message("assistant"):
                with st.spinner("Processando sua pergunta..."):
                    response = asyncio.run(get_response(qa_chain, prompt))
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

        # Botão para limpar conversa
        if st.sidebar.button("Limpar Conversa"):
            st.session_state.messages = []
            st.rerun()
            
    except Exception as e:
        st.error(f"Erro no sistema: {str(e)}")

if __name__ == "__main__":
    main()