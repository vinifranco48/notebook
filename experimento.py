from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
from pathlib import Path
import os

# Configure Groq API key
os.environ["GROQ_API_KEY"] = "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"

# Define o prompt personalizado
CUSTOM_PROMPT = """
Você é um assistente especializado em analisar e explicar documentos.

Contexto dos documentos:
{context}

Pergunta do usuário:
{question}

Instrução: Responda sobre os documentos com precisão e didaticamente, explicando o que está no documento de acordo com o contexto da pergunta. Se a informação não estiver nos documentos, indique claramente.

Resposta:
"""

def verify_pdf_directory(pdf_dir):
    """Verifica se o diretório existe e lista os PDFs encontrados"""
    pdf_dir = Path(pdf_dir)
    
    if not pdf_dir.exists():
        raise FileNotFoundError(f"Diretório não encontrado: {pdf_dir}")
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"\nDiretório de PDFs: {pdf_dir.absolute()}")
    print(f"PDFs encontrados: {len(pdf_files)}")
    for pdf in pdf_files:
        print(f"- {pdf.name}")
    
    return pdf_files

def process_pdfs(pdf_files):
    """Processa os PDFs e retorna os documentos"""
    documents = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )
    
    for pdf_path in pdf_files:
        try:
            print(f"\nProcessando: {pdf_path.name}")
            loader = PyPDFLoader(str(pdf_path))
            pdf_documents = loader.load()
            split_documents = text_splitter.split_documents(pdf_documents)
            documents.extend(split_documents)
            print(f"Páginas processadas: {len(pdf_documents)}")
        except Exception as e:
            print(f"Erro ao processar {pdf_path.name}: {e}")
    
    return documents

def create_rag_system():
    # Definir o caminho correto para o diretório de PDFs
    pdf_dir = Path('./pdfs')  # Ajuste o caminho conforme necessário
    
    # Verifica o diretório de PDFs
    pdf_files = verify_pdf_directory(pdf_dir)
    
    if not pdf_files:
        raise ValueError("Nenhum PDF encontrado no diretório")
    
    print("\nProcessando PDFs...")
    documents = process_pdfs(pdf_files)
    print(f"Total de chunks processados: {len(documents)}")
    
    if documents:
        print("\nAmostra do primeiro chunk:")
        print(documents[0].page_content[:200] + "...")
    
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )
    
    print("\nCriando índice FAISS...")
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local("faiss_index")
    
    return vectorstore

def load_rag_system(embeddings):
    if not Path("faiss_index").exists():
        raise FileNotFoundError("Índice FAISS não encontrado")
    
    return FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )

def create_qa_chain(vectorstore):
    # Cria o template do prompt personalizado
    prompt_template = PromptTemplate(
        template=CUSTOM_PROMPT,
        input_variables=["context", "question"]
    )
    
    llm = ChatGroq(
        temperature=0.1,
        model_name="mixtral-8x7b-32768",
        max_tokens=1024  # Aumentado para respostas mais detalhadas
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_kwargs={"k": 4}  # Aumentado para buscar mais contexto
        ),
        chain_type_kwargs={
            "prompt": prompt_template,
            "verbose": True  # Permite ver o processo de geração da resposta
        }
    )
    
    return qa_chain

async def query_rag_system(qa_chain, query):
    print(f"\nBuscando resposta para: {query}")
    response = await qa_chain.ainvoke({"query": query})
    return response

def main():
    print("Iniciando sistema RAG...")
    
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )
    
    try:
        print("\nTentando carregar índice FAISS existente...")
        vectorstore = load_rag_system(embeddings)
        print("Índice FAISS carregado com sucesso!")
    except Exception as e:
        print(f"\nErro ao carregar índice existente: {e}")
        print("Criando novo índice FAISS...")
        vectorstore = create_rag_system()
    
    qa_chain = create_qa_chain(vectorstore)
    
    # Loop para fazer perguntas
    import asyncio
    while True:
        query = input("\nDigite sua pergunta (ou 'sair' para encerrar): ")
        if query.lower() == 'sair':
            break
            
        response = asyncio.run(query_rag_system(qa_chain, query))
        print("\nResposta:", response['result'])

if __name__ == "__main__":
    main()