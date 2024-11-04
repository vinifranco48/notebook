import streamlit as st
import os
from groq import Groq
from PIL import Image
import re

def initialize_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'tutorial_content' not in st.session_state:
        st.session_state.tutorial_content = []

def load_tutorial_content():
    # Texto do tutorial dividido em seções
    textos = [
        "PARA LANÇAR UMA NOTA FISCAL DE IMOBILIZADO, PRIMEIRAMENTE DEVE-SE CRIAR O BEM DO ATIVO IMOBILIZADO",
        "PREENCHER TODOS OS CAMPOS SOLICITADOS,PRENCHER A DESCRIÇÃO COMPLETA DO ITEM E NA DESCRIÇÃO DETALHADA INCLUIR O NUMERO DA NOTAFISCAL DA COMPRA.",
        "NA ABA DEPRECIAÇÃO, COLOCAR A DATA DA ENTRADA DA NOTA FISCAL NO SISTEMA. \"SALVAR\"",
        "AGORA DAR ENTRADA NA NOTA FISCAL \"COMPRA DE IMOBILIZADO\" GESTÃO DE ENTRADAS/IMOBILIZADO/COMPRA IMOBILIZADO",
        "SE A MERCADORIA FOI COMPRADA DE FORA DO ESTADO E O CST FOR 00 OU 020, SERÁ COBRADO O ICMS DIFERENCIAL DE ALIQUOTA.",
        "CFOP DE COMPRA DE ATIVO IMOBILIZADO DE FORA DO ESTADO SERÁ 2551 OBS:ESSA REGRA DA ALÍQUOTA CONFORME A NOTA FISCAL E MARCAR AS OPÇÕES DE SOMAR FRETE E IPI(CASO TENHA)PARA CALCULAR O VALOR CORRETO DO ICMS DIFERENCIAL, VALE TAMBÉM PARA NOTAS DE COMPPRA DE MATERIAL DE USO E CONSUMO, MATERIAL DE INFORMÁTICA, QUANDO A MERCADORIA É COMPRADA FORA DO ESTADO E O CSTFOR 000,020...",
        "NA ABA IMPOSTOS MARCAR AS DUAS OPÇÕES CASO TENHA FRETE E IPI.VERIFICAR SE ABASE DO ICMS DIFERENCIAL DE ALÍQUOTA ESTÁ CORRETA(TEM QUE SER O VALOR TOTAL DANF)",
        "NA ABA CONTAS A PAGAR, EDITAR O VENCIMENTO DA DUPLICATA DO DIFERENCIAL SEMPRE PARAO DIA 20 DO MÊS SEGUINTE"
    ]
    
    # Carrega imagens
    imagens = []
    path = './image'
    for i in range(1, 9):
        imagem_path = os.path.join(path, f'image_{i}.png')
        if os.path.exists(imagem_path):
            imagem = Image.open(imagem_path)
            imagens.append(imagem)
    
    return textos, imagens

def get_groq_explanation(texto):
    try:
        client = Groq(
            api_key="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"
        )
        
        prompt = f"Reescreva o seguinte texto de forma mais didática e clara em português, mantendo todas as informações importantes: {texto}"
        
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            model="llama3-70b-8192",
            temperature=0.5,
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro ao gerar explicação: {str(e)}")
        return texto

def find_relevant_context(pergunta, textos):
    # Palavras-chave importantes para o contexto
    keywords = {
        'como': 0.3,
        'imobilizado': 0.8,
        'nota': 0.7,
        'fiscal': 0.7,
        'lançar': 0.8,
        'aba': 0.6,
        'depreciação': 0.8,
        'icms': 0.8,
        'diferencial': 0.7,
        'alíquota': 0.7,
        'cfop': 0.8,
        'frete': 0.6,
        'ipi': 0.6,
        'duplicata': 0.7,
        'vencimento': 0.6,
        'compra': 0.7,
        'entrada': 0.7,
        'sistema': 0.6,
        'salvar': 0.5
    }
    
    # Normaliza a pergunta
    pergunta = pergunta.lower()
    
    # Encontra as seções mais relevantes
    relevance_scores = []
    for i, texto in enumerate(textos):
        score = 0
        texto_lower = texto.lower()
        
        # Verifica palavras-chave
        for keyword, weight in keywords.items():
            if keyword in pergunta:
                if keyword in texto_lower:
                    score += weight
        
        # Adiciona o score e índice
        relevance_scores.append((score, i))
    
    # Ordena por relevância
    relevance_scores.sort(reverse=True)
    
    # Retorna os contextos mais relevantes (top 2)
    relevant_contexts = []
    for score, idx in relevance_scores[:2]:
        if score > 0:  # Só inclui se houver alguma relevância
            relevant_contexts.append(textos[idx])
    
    return relevant_contexts

def get_groq_response(pergunta, contextos):
    try:
        client = Groq(
            api_key="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"
        )
        
        # Prepara o contexto para a resposta
        contexto_str = "\n".join(contextos) if contextos else "Informações gerais sobre lançamento de notas fiscais de imobilizado"
        
        prompt = f"""
        Contexto relevante do tutorial: {contexto_str}
        
        Pergunta do usuário: {pergunta}
        
        Por favor, forneça uma resposta clara e objetiva, baseada no contexto fornecido.
        Se a pergunta não puder ser respondida completamente com o contexto disponível, 
        indique isso e forneça informações gerais sobre o processo de lançamento de notas fiscais de imobilizado.
        A resposta deve ser em português e de forma didática, seja um pouco mais objetivo, tente retorna a resposta com menos linhas.
        """
        
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            model="llama3-70b-8192",
            temperature=0.5,
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro ao gerar resposta: {str(e)}")
        return "Desculpe, houve um erro ao gerar a resposta. Por favor, tente novamente."

def main():
    st.set_page_config(layout="wide")
    st.title("Tutorial: Lançamento de Nota Fiscal de Imobilizado")
    
    # Inicializa o estado da sessão
    initialize_session_state()
    
    # Carrega o conteúdo do tutorial
    textos, imagens = load_tutorial_content()
    
    # Criar duas colunas: uma para o tutorial e outra para o chat
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Área do Tutorial
        st.header("Tutorial Completo")
        
        # Processa e exibe todo o tutorial em sequência
        for i, (texto, imagem) in enumerate(zip(textos, imagens)):
            with st.container():
                st.subheader(f"Passo {i + 1}")
                
                # Exibe o texto original e explicação
                with st.expander(f"Texto Original - Passo {i + 1}", expanded=True):
                    st.write(texto)
                    st.write("**Explicação Detalhada:**")
                    explicacao = get_groq_explanation(texto)
                    st.write(explicacao)
                
                # Exibe a imagem
                st.image(imagem, caption=f"Ilustração do Passo {i + 1}", use_column_width=True)
                
                st.divider()
    
    with col2:
        # Área de Chat para Dúvidas
        st.header("Tire suas Dúvidas")
        
        # Container para o histórico do chat com altura fixa e scroll
        chat_container = st.container()
        with chat_container:
            # Exibe histórico do chat
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    if "image_index" in msg:
                        st.image(imagens[msg["image_index"]], 
                                caption=f"Ilustração relacionada",
                                use_column_width=True)
        
        # Campo para perguntas
        if pergunta := st.chat_input("Digite sua dúvida sobre o tutorial..."):
            # Adiciona pergunta ao histórico
            st.session_state.chat_history.append({"role": "user", "content": pergunta})
            
            # Encontra contextos relevantes
            contextos_relevantes = find_relevant_context(pergunta, textos)
            
            # Gera resposta baseada nos contextos relevantes
            with st.spinner("Gerando resposta..."):
                resposta = get_groq_response(pergunta, contextos_relevantes)
                
                # Encontra o índice da imagem mais relevante (se houver contexto)
                image_index = None
                if contextos_relevantes:
                    image_index = textos.index(contextos_relevantes[0])
                
                # Adiciona resposta ao histórico
                response_data = {
                    "role": "assistant",
                    "content": resposta
                }
                if image_index is not None:
                    response_data["image_index"] = image_index
                
                st.session_state.chat_history.append(response_data)
            
            # Recarrega a página
            st.rerun()
        
        # Botão para limpar o chat
        if st.button("Limpar Chat"):
            st.session_state.chat_history = []
            st.rerun()

if __name__ == "__main__":
    main()