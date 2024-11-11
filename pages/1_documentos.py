import streamlit as st
from pathlib import Path
import asyncio
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os

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
Você é um tutor especializado em criar experiências de aprendizado personalizadas a partir de documentos. Sua missão é transformar o conteúdo técnico em explicações claras e envolventes.

Contexto do Documento:
{context}

Pergunta do Usuário:
{question}

Instruções de Resposta:


1. Explicação Didática
- Explique cada conceito usando linguagem clara e acessível
- Forneça exemplos práticos quando possível
- Use analogias para tornar conceitos complexos mais compreensíveis
- Inclua dicas e observações importantes
- Seja didatico porem direto.

Por favor, mantenha um tom amigável e encorajador, adequado para aprendizado.

Resposta:
"""

@st.cache_resource
def initialize_rag_system():
    """Inicializa o sistema RAG com cache para evitar recarregamento"""
    # Configurar Groq API key
    os.environ["GROQ_API_KEY"] = "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"
    
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )
    
    # Carregar o índice FAISS
    if not Path("faiss_index").exists():
        st.error("Índice FAISS não encontrado. Por favor, execute primeiro o script de processamento dos PDFs.")
        st.stop()
    
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
    
    # Configurar o modelo LLM
    llm = ChatGroq(
        temperature=0.1,
        model_name="llama3-70b-8192",
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

async def get_response(qa_chain, query):
    """Função assíncrona para obter resposta do sistema RAG"""
    response = await qa_chain.ainvoke({"query": query})
    return response['result']

def main():
    st.title("💬 Chat com Documentos")
    st.subheader("Faça perguntas sobre seus documentos")
    
    # Inicializar o histórico de chat na sessão se não existir
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Inicializar o sistema RAG
    qa_chain = initialize_rag_system()
    
    # Mostrar mensagens do histórico
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input do usuário
    if prompt := st.chat_input("Digite sua pergunta aqui"):
        # Adicionar mensagem do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Gerar e mostrar resposta do assistente
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response = asyncio.run(get_response(qa_chain, prompt))
                st.markdown(response)
                # Adicionar resposta ao histórico
                st.session_state.messages.append({"role": "assistant", "content": response})

    # Botão para limpar o histórico
    if st.sidebar.button("Limpar Conversa"):
        st.session_state.messages = []
        st.rerun()

if __name__ == "__main__":
    main()