import os
from typing import Dict, List, Tuple, TypedDict
from datetime import datetime
from langgraph.graph import Graph, END
from groq import Groq
import operator

# Definição dos tipos de dados
class AgentState(TypedDict):
    messages: List[Dict[str, str]]
    customer_id: str
    issue_type: str | None
    sentiment: str | None
    escalated: bool
    resolved: bool

# Configuração do cliente Groq
client = "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"

def call_groq(messages: List[Dict[str, str]]) -> str:
    """Função auxiliar para chamar a API da Groq"""
    try:
        response = client.chat.completions.create(
            messages=messages,
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro ao chamar Groq API: {e}")
        return "Desculpe, houve um erro no processamento."

# Funções auxiliares
def format_message(role: str, content: str) -> Dict[str, str]:
    return {"role": role, "content": content}

# Nós do grafo
def classify_issue(state: AgentState) -> AgentState:
    """Classifica o tipo de problema do cliente"""
    messages = state["messages"]
    last_message = messages[-1]["content"]
    
    classification_prompt = f"""
    Classifique o problema do cliente em uma das seguintes categorias:
    - TECHNICAL (problemas técnicos)
    - BILLING (problemas de cobrança)
    - ACCOUNT (problemas de conta)
    - INFO (pedidos de informação)
    
    Mensagem do cliente: {last_message}
    
    Responda apenas com a categoria.
    """
    
    response = call_groq([
        format_message("system", classification_prompt),
        format_message("user", last_message)
    ])
    
    state["issue_type"] = response.strip()
    return state

def analyze_sentiment(state: AgentState) -> AgentState:
    """Analisa o sentimento do cliente"""
    messages = state["messages"]
    last_message = messages[-1]["content"]
    
    sentiment_prompt = """
    Analise o sentimento desta mensagem e classifique como:
    POSITIVE, NEGATIVE, ou NEUTRAL.
    Responda apenas com a classificação.
    """
    
    response = call_groq([
        format_message("system", sentiment_prompt),
        format_message("user", last_message)
    ])
    
    state["sentiment"] = response.strip()
    return state

def should_escalate(state: AgentState) -> Tuple[str, AgentState]:
    """Decide se deve escalar para um humano"""
    if (state["sentiment"] == "NEGATIVE" and 
        state["issue_type"] in ["TECHNICAL", "BILLING"]):
        state["escalated"] = True
        return "escalate", state
    return "handle", state

def handle_customer_query(state: AgentState) -> AgentState:
    """Processa a consulta do cliente"""
    messages = state["messages"]
    issue_type = state["issue_type"]
    
    system_prompt = f"""
    Você é um agente de atendimento ao cliente profissional.
    O tipo de problema é: {issue_type}
    
    Diretrizes:
    - Seja empático e profissional
    - Forneça soluções práticas
    - Confirme entendimento
    - Pergunte se há mais alguma dúvida
    """
    
    conversation = [format_message("system", system_prompt)]
    conversation.extend(messages)
    
    response = call_groq(conversation)
    
    state["messages"].append(format_message("assistant", response))
    return state

def escalate_to_human(state: AgentState) -> AgentState:
    """Prepara escalonamento para atendente humano"""
    escalation_message = f"""
    Este caso será encaminhado para um atendente humano devido à sua complexidade.
    
    Detalhes do caso:
    - ID do Cliente: {state['customer_id']}
    - Tipo de Problema: {state['issue_type']}
    - Sentimento: {state['sentiment']}
    
    Um especialista entrará em contato em breve.
    """
    
    state["messages"].append(format_message("assistant", escalation_message))
    return state

def check_resolution(state: AgentState) -> Tuple[str, AgentState]:
    """Verifica se o problema foi resolvido"""
    if state["escalated"]:
        state["resolved"] = True
        return "end", state
        
    last_message = state["messages"][-1]["content"].lower()
    if "mais alguma dúvida" in last_message:
        state["resolved"] = True
        return "end", state
    return "continue", state

# Construção do grafo
def build_customer_service_graph() -> Graph:
    workflow = Graph()
    
    # Define o fluxo do grafo
    workflow.add_node("classify_issue", classify_issue)
    workflow.add_node("analyze_sentiment", analyze_sentiment)
    workflow.add_node("should_escalate", should_escalate)
    workflow.add_node("handle_customer_query", handle_customer_query)
    workflow.add_node("escalate_to_human", escalate_to_human)
    workflow.add_node("check_resolution", check_resolution)
    
    # Define as conexões
    workflow.set_entry_point("classify_issue")
    workflow.add_edge("classify_issue", "analyze_sentiment")
    workflow.add_edge("analyze_sentiment", "should_escalate")
    
    workflow.add_conditional_edges(
        "should_escalate",
        {
            "handle": "handle_customer_query",
            "escalate": "escalate_to_human"
        }
    )
    
    workflow.add_edge("handle_customer_query", "check_resolution")
    workflow.add_edge("escalate_to_human", "check_resolution")
    
    workflow.add_conditional_edges(
        "check_resolution",
        {
            "continue": "handle_customer_query",
            "end": END
        }
    )
    
    return workflow.compile()

# Classe principal do agente
class CustomerServiceAgent:
    def __init__(self):
        self.graph = build_customer_service_graph()
        
    def handle_message(self, customer_id: str, message: str) -> List[Dict[str, str]]:
        """Processa uma nova mensagem do cliente"""
        initial_state = AgentState(
            messages=[format_message("user", message)],
            customer_id=customer_id,
            issue_type=None,
            sentiment=None,
            escalated=False,
            resolved=False
        )
        
        # Executa o fluxo
        final_state = self.graph.invoke(initial_state)
        
        # Registra a interação
        self._log_interaction(final_state)
        
        return final_state["messages"]
    
    def _log_interaction(self, state: AgentState):
        """Registra a interação para análise"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "customer_id": state["customer_id"],
            "issue_type": state["issue_type"],
            "sentiment": state["sentiment"],
            "escalated": state["escalated"],
            "resolved": state["resolved"],
            "messages": state["messages"]
        }
        print(f"Log da interação: {log_entry}")

def main():
    # Verifica se a API key está configurada
    if not os.getenv("GROQ_API_KEY"):
        print("Erro: GROQ_API_KEY não está configurada!")
        return
        
    agent = CustomerServiceAgent()
    
    # Exemplo de interação
    customer_id = "CUST123"
    message = "Estou muito irritado! Minha conta foi cobrada duas vezes este mês!"
    
    print("\nProcessando mensagem do cliente...")
    responses = agent.handle_message(customer_id, message)
    
    print("\nConversa:")
    for msg in responses:
        print(f"{msg['role'].upper()}: {msg['content']}\n")

if __name__ == "__main__":
    main()