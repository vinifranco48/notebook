from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain import hub

# Carregar os documentos
pdf_loader = PyPDFLoader("C:\\Users\\Graúna Motos\\Documents\\notebook\\data\\MANUAL PRÁTICO PARA ENTRADA DE NOTAS FISCAIS (1).pdf")
documents = pdf_loader.load_clear()  # Carrega e limpa o texto dos PDFs

# Dividir documentos em partes menores
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
split_documents = text_splitter.split_documents(documents)

# Substituir OpenAIEmbeddings por HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings()

# Criar o vector store FAISS e adicionar os documentos
vectorstore = FAISS.from_documents(split_documents, embeddings)

# Salvar o vector store FAISS
vectorstore.save("faiss_index")

# Carregar o vector store FAISS salvo
new_vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

# Configurar a chain de recuperação com prompt de chat
retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")

# Configurar o chain de combinação de documentos
combine_docs_chain = create_stuff_documents_chain(
    llm=hub.load("huggingface/gpt2"),  # Substituir OpenAI() por modelo open-source
    prompt=retrieval_qa_chat_prompt
)

# Configurar o retrieval chain usando o vector store
retrieval_chain = create_retrieval_chain(
    retriever=new_vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3}),
    combine_docs_chain=combine_docs_chain
)

# Fazer uma pergunta ao chatbot
res = retrieval_chain.invoke({"input": "Give me the gist of Retrieval-Augmented Generation (RAG) in 3 sentences"})
print(res["answer"])
