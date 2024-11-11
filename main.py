import streamlit as st
from pathlib import Path

class TutorialSystem:
    def __init__(self):
        self.setup_page_config()
        self.load_styles()
        
    def setup_page_config(self):
        st.set_page_config(page_title="Sistema de Tutoriais", page_icon="📚", layout="wide")

    def load_styles(self):
        st.markdown("""
            <style>
            .main-container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
            .header { text-align: center; padding: 2rem 0; background-color: #f8f9fa; border-radius: 10px; }
            .header h1 { color: #1a1a1a; }
            .tutorial-card { background-color: white; border-radius: 12px; padding: 1.5rem; border: 1px solid #e0e0e0; }
            .stButton button { width: 100%; background-color: #0066cc; color: white; border-radius: 6px; padding: 0.7rem 1rem; }
            .stButton button:hover { background-color: #0052a3; }
            </style>
        """, unsafe_allow_html=True)

    def create_tutorial_card(self, icon: str, title: str, topics: list, time: str):
        st.markdown(f"""
            <div class="tutorial-card">
                <div class="card-icon">{icon}</div>
                <div class="card-title"><h3>{title}</h3></div>
                <ul>
                    {''.join(f'<li>{topic}</li>' for topic in topics)}
                </ul>
                <div>⏱️ Tempo estimado: {time}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Botão para selecionar o tutorial
        if st.button(f"Iniciar {title}", key=f"btn_{title}"):
            st.session_state["current_tutorial"] = title

    def render_header(self):
        st.markdown("""
            <div class="header">
                <h1>Tutoriais</h1>
                <p>Selecione um tutorial abaixo para começar</p>
            </div>
        """, unsafe_allow_html=True)

    def render_footer(self):
        st.markdown("""
            <div class="footer">
                Sistema de Tutoriais • Versão 1.0
            </div>
        """, unsafe_allow_html=True)

    def render_main_page(self):
        """Renderiza a página principal com os tutoriais"""
        col1, col2 = st.columns(2)
        
        with col1:
            self.create_tutorial_card(
                "💼", "Imobilizado", ["Lançamento de notas fiscais Imobilizados", "Inserir documentos imobilizados no sistema"], "30 minutos"
            )
        
        with col2:
            self.create_tutorial_card(
                "📄", "Documentos", ["Tutoriais gerais", "CFOP, DESPESAS "], "20 minutos"
            )

    def render_tutorial(self, tutorial_title):
        """Renderiza o conteúdo do tutorial selecionado"""
        if tutorial_title == "Imobilizado":
            st.title("Tutorial: Imobilizado")
            st.write("Conteúdo detalhado sobre o tutorial Imobilizado.")
            st.write("Inclui tópicos como Lançamento de notas fiscais, Validação de documentos, etc.")
        
        elif tutorial_title == "Documentos":
            st.title("Tutorial: Documentos")
            st.write("Conteúdo detalhado sobre o tutorial de Documentos.")
            st.write("Inclui tópicos como Gestão de documentos, Processo de aprovação, etc.")
        
        st.button("Voltar", on_click=lambda: st.session_state.update({"current_tutorial": None}))

    def run(self):
        """Executa o sistema de tutoriais"""
        self.render_header()
        
        # Verifica se algum tutorial foi selecionado e renderiza o conteúdo apropriado
        if "current_tutorial" not in st.session_state:
            st.session_state["current_tutorial"] = None

        if st.session_state["current_tutorial"] is None:
            self.render_main_page()  # Renderiza a página principal
        else:
            self.render_tutorial(st.session_state["current_tutorial"])  # Renderiza o tutorial selecionado

        self.render_footer()

def main():
    tutorial_system = TutorialSystem()
    tutorial_system.run()

if __name__ == "__main__":
    main()
