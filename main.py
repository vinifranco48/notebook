import streamlit as st
from typing import Annotated, Sequence, TypedDict, Union, List
from langgraph.graph import StateGraph
from langchain_core.messages import AIMessage, HumanMessage
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from PIL import Image
import os
from pathlib import Path

class AgentState(TypedDict):
    messages: Sequence[Union[HumanMessage, AIMessage]]
    next_step: str

def init_llm():
    return ChatGroq(
        temperature=0.1,
        model_name="llama3-70b-8192",
        api_key="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"
    )

class TutorialHandler:
    def __init__(self):
        self.texts, self.images = self.load_tutorial_content()
        self.llm = init_llm()
    
    def load_tutorial_content(self):
        texts = [
            "PARA LANÇAR UMA NOTA FISCAL DE IMOBILIZADO, PRIMEIRAMENTE DEVE-SE CRIAR O BEM DO ATIVO IMOBILIZADO",
            "PREENCHER TODOS OS CAMPOS SOLICITADOS,PRENCHER A DESCRIÇÃO COMPLETA DO ITEM E NA DESCRIÇÃO DETALHADA INCLUIR O NUMERO DA NOTAFISCAL DA COMPRA.",
            "NA ABA DEPRECIAÇÃO, COLOCAR A DATA DA ENTRADA DA NOTA FISCAL NO SISTEMA. \"SALVAR\"",
            "AGORA DAR ENTRADA NA NOTA FISCAL \"COMPRA DE IMOBILIZADO\" GESTÃO DE ENTRADAS/IMOBILIZADO/COMPRA IMOBILIZADO",
            "SE A MERCADORIA FOI COMPRADA DE FORA DO ESTADO E O CST FOR 00 OU 020, SERÁ COBRADO O ICMS DIFERENCIAL DE ALIQUOTA.",
            "CFOP DE COMPRA DE ATIVO IMOBILIZADO DE FORA DO ESTADO SERÁ 2551 OBS:ESSA REGRA DA ALÍQUOTA CONFORME A NOTA FISCAL E MARCAR AS OPÇÕES DE SOMAR FRETE E IPI(CASO TENHA)PARA CALCULAR O VALOR CORRETO DO ICMS DIFERENCIAL, VALE TAMBÉM PARA NOTAS DE COMPPRA DE MATERIAL DE USO E CONSUMO, MATERIAL DE INFORMÁTICA, QUANDO A MERCADORIA É COMPRADA FORA DO ESTADO E O CSTFOR 000,020...",
            "NA ABA IMPOSTOS MARCAR AS DUAS OPÇÕES CASO TENHA FRETE E IPI.VERIFICAR SE ABASE DO ICMS DIFERENCIAL DE ALÍQUOTA ESTÁ CORRETA(TEM QUE SER O VALOR TOTAL DANF)",
            "NA ABA CONTAS A PAGAR, EDITAR O VENCIMENTO DA DUPLICATA DO DIFERENCIAL SEMPRE PARAO DIA 20 DO MÊS SEGUINTE"
        ]
        
        images = []
        path = './image'
        for i in range(1, 9):
            image_path = os.path.join(path, f'image_{i}.png')
            if os.path.exists(image_path):
                image = Image.open(image_path)
                images.append(image)
        
        return texts, images
    
    def find_relevant_sections(self, query: str):
        # Check if query is related to fixed assets
        fixed_asset_keywords = {
            'imobilizado', 'ativo', 'nota fiscal', 'depreciação', 
            'icms', 'cfop', 'bem', 'patrimônio'
        }
        
        query_words = set(query.lower().split())
        is_fixed_asset_related = any(keyword in query.lower() for keyword in fixed_asset_keywords)
        
        if is_fixed_asset_related:
            # Return all sections if query is related to fixed assets
            return [(self.texts[i], self.images[i], i) for i in range(len(self.texts))]
        else:
            # For non-fixed asset queries, use keyword matching to find relevant sections
            keywords = {
                'imobilizado': 0.8,
                'lançar': 0.2
            }
            
            relevance_scores = []
            for i, texto in enumerate(self.texts):
                score = 0
                texto_lower = texto.lower()
                
                for keyword, weight in keywords.items():
                    if keyword in query.lower() and keyword in texto_lower:
                        score += weight
                
                if score > 0:
                    relevance_scores.append((score, i))
            
            relevance_scores.sort(reverse=True)
            return [(self.texts[i], self.images[i], i) for _, i in relevance_scores[:2]]
    
    def get_tutorial_response(self, query: str) -> dict:
        relevant_sections = self.find_relevant_sections(query)
        
        if not relevant_sections:
            return {
                "content": "Não encontrei informações específicas do tutorial relacionadas à sua pergunta. Poderia reformular ou ser mais específico?",
                "sections": []
            }
        
        context = "\n".join([text for text, _, _ in relevant_sections])
        
        prompt = f"""
        Com base no seguinte contexto do tutorial sobre lançamento de notas fiscais de imobilizado:
        {context}
        
        Responda à seguinte pergunta de forma clara e didática:
        {query}
        
        Se a pergunta for sobre imobilizado, certifique-se de mencionar que estou mostrando todos os passos do processo para melhor compreensão.
        """
        
        explanation = self.llm.predict(prompt)
        
        return {
            "content": explanation,
            "sections": relevant_sections
        }

class DocumentQAHandler:
    def __init__(self):
        self.vectorstore = self.init_vectorstore()
        self.qa_chain = self.setup_qa_chain()
    
    def init_vectorstore(self):
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
        
        if not Path("faiss_index").exists():
            raise FileNotFoundError("FAISS index not found")
        
        return FAISS.load_local(
            "faiss_index",
            embeddings,
            allow_dangerous_deserialization=True
        )
    
    def setup_qa_chain(self):
        prompt_template = PromptTemplate(
            template="""
            Você é um assistente especializado em documentação.
            
            Contexto do Documento:
            {context}
            
            Pergunta do Usuário:
            {question}
            
            Por favor, forneça uma resposta clara e objetiva:
            """,
            input_variables=["context", "question"]
        )
        
        return RetrievalQA.from_chain_type(
            llm=init_llm(),
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 4}),
            chain_type_kwargs={
                "prompt": prompt_template,
                "verbose": False
            }
        )
    
    def get_response(self, query: str) -> dict:
        response = self.qa_chain.invoke({"query": query})
        return {
            "content": response['result']
        }

def route_query(state: AgentState) -> dict:
    llm = init_llm()
    last_message = state["messages"][-1]
    
    prompt = f"""
    Analise se esta pergunta está relacionada ao tutorial de lançamento de notas fiscais de imobilizado 
    ou se é uma pergunta geral sobre outros documentos.
    
    Pergunta: {last_message.content}
    
    Considere que é sobre imobilizado se a pergunta mencionar:
    - Nota fiscal de imobilizado
    - Lançamento de imobilizados
    
    Retorne apenas 'tutorial' ou 'document':
    """
    
    response = llm.predict(prompt).strip().lower()
    return {"next_step": response}

def handle_tutorial(state: AgentState) -> AgentState:
    handler = TutorialHandler()
    last_message = state["messages"][-1]
    response = handler.get_tutorial_response(last_message.content)
    
    state["messages"].append(AIMessage(
        content=response["content"],
        additional_kwargs={"tutorial_sections": response["sections"]}
    ))
    return state

def handle_document_qa(state: AgentState) -> AgentState:
    handler = DocumentQAHandler()
    last_message = state["messages"][-1]
    response = handler.get_response(last_message.content)
    
    state["messages"].append(AIMessage(content=response["content"]))
    return state

def build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)
    
    workflow.add_node("route", route_query)
    workflow.add_node("tutorial", handle_tutorial)
    workflow.add_node("document_qa", handle_document_qa)
    
    workflow.set_entry_point("route")
    
    workflow.add_conditional_edges(
        "route",
        lambda x: x["next_step"],
        {
            "tutorial": "tutorial",
            "document": "document_qa"
        }
    )
    
    workflow.set_finish_point("tutorial")
    workflow.set_finish_point("document_qa")
    
    return workflow.compile()

def main():
    st.set_page_config(page_title="Sistema de Chat Unificado", layout="wide")
    st.title("💬 Assistente de Documentação e Tutorial")
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Initialize graph
    graph = build_graph()
    
    # Chat column
    chat_column = st.container()
    
    with chat_column:
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                
                # Se for resposta do tutorial, mostrar seções relevantes
                if message["role"] == "assistant" and "additional_kwargs" in message:
                    tutorial_sections = message.get("additional_kwargs", {}).get("tutorial_sections", [])
                    if tutorial_sections:
                        st.divider()
                        st.subheader("Seções Relevantes do Tutorial:")
                        for texto, imagem, idx in tutorial_sections:
                            with st.expander(f"Passo {idx + 1}", expanded=True):
                                st.write(texto)
                                st.image(imagem, caption=f"Ilustração do Passo {idx + 1}", use_column_width=True)
        
        # Chat input
        if prompt := st.chat_input("Como posso ajudar?"):
            user_message = HumanMessage(content=prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.spinner("Processando..."):
                result = graph.invoke({
                    "messages": [user_message],
                    "next_step": None
                })
                
                ai_message = result["messages"][-1]
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_message.content,
                    "additional_kwargs": ai_message.additional_kwargs
                })
                
                st.rerun()
        
        # Clear chat button
        if st.button("Limpar Chat"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main()