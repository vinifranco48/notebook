import streamlit as st
import subprocess
import os

def main():
    st.set_page_config(layout="wide")
    st.title("Sistema de Tutoriais")

    # Criar container central para o menu
    menu_container = st.container()
    
    with menu_container:
        st.header("Escolha o Tutorial Desejado")
        
        # Container para os tutoriais
        tutorial_container = st.container()
        
        with tutorial_container:
            # Tutorial de Imobilizado
            col1, col2 = st.columns([1, 2])
            with col1:
                if st.button("Tutorial de Imobilizado", use_container_width=True):
                    subprocess.run(["streamlit", "run", "Imobilizado.py"])
            with col2:
                st.markdown("""
                **Descrição:**
                - Guia completo para lançamento de notas fiscais de imobilizado
                - Inclui explicações detalhadas e imagens
                - Sistema de chat para tirar dúvidas
                """)
            
            st.divider()
            
            # Tutorial 2
            col1, col2 = st.columns([1, 2])
            with col1:
                if st.button("Tutorial de Documentos", use_container_width=True):
                    subprocess.run(["streamlit", "run", "app.py"])
            with col2:
                st.markdown("**Descrição:** Em desenvolvimento")
            
            st.divider()
            
            # Tutorial 3    
            col1, col2 = st.columns([1, 2])
            with col1:
                if st.button("Tutorial 3 (Em breve)", use_container_width=True, disabled=True):
                    pass
            with col2:
                st.markdown("**Descrição:** Em desenvolvimento")

if __name__ == "__main__":
    main()
