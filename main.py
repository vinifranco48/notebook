import streamlit as st
import subprocess
from pathlib import Path

class TutorialSystem:
    def __init__(self):
        self.setup_page_config()
        self.load_styles()
        
    def setup_page_config(self):
        st.set_page_config(
            page_title="Sistema de Tutoriais",
            page_icon="📚",
            layout="wide"
        )

    def load_styles(self):
        st.markdown("""
            <style>
            .main-container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }
            .header {
                text-align: center;
                padding: 2rem 0;
                margin-bottom: 3rem;
                background-color: #f8f9fa;
                border-radius: 10px;
            }
            .header h1 {
                margin-bottom: 1rem;
                color: #1a1a1a;
            }
            .header p {
                color: #666;
                font-size: 1.1rem;
            }
            .tutorial-card {
                height: 100%;
                background-color: white;
                border-radius: 12px;
                padding: 1.5rem;
                border: 1px solid #e0e0e0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                transition: transform 0.2s ease-in-out;
                display: flex;
                flex-direction: column;
            }
            .tutorial-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .card-icon {
                font-size: 2rem;
                margin-bottom: 1rem;
                text-align: center;
            }
            .card-title {
                font-size: 1.3rem;
                font-weight: bold;
                margin-bottom: 1rem;
                color: #1a1a1a;
                text-align: center;
            }
            .card-content {
                flex-grow: 1;
            }
            .topic-list {
                list-style-type: none;
                padding-left: 0;
                margin-bottom: 1.5rem;
            }
            .topic-list li {
                padding: 0.5rem 0;
                color: #4a4a4a;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            .time-estimate {
                text-align: center;
                padding: 0.5rem;
                background-color: #f8f9fa;
                border-radius: 6px;
                margin: 1rem 0;
                color: #666;
            }
            .stButton button {
                width: 100%;
                background-color: #0066cc;
                color: white;
                border-radius: 6px;
                padding: 0.7rem 1rem;
                border: none;
                font-size: 1rem;
                cursor: pointer;
                transition: background-color 0.2s ease;
            }
            .stButton button:hover {
                background-color: #0052a3;
            }
            .footer {
                text-align: center;
                padding: 2rem 0;
                color: #666;
                font-size: 0.9rem;
            }
            </style>
        """, unsafe_allow_html=True)

    def create_tutorial_card(self, icon: str, title: str, topics: list, time: str, script_path: str):
        """
        Cria um card de tutorial com as informações fornecidas.
        
        Args:
            icon (str): Emoji ou ícone do tutorial
            title (str): Título do tutorial
            topics (list): Lista de tópicos abordados
            time (str): Tempo estimado do tutorial
            script_path (str): Caminho para o script do tutorial
        """
        st.markdown(f"""
            <div class="tutorial-card">
                <div class="card-icon">{icon}</div>
                <div class="card-title">{title}</div>
                <div class="card-content">
                    <ul class="topic-list">
                        {''.join(f'<li>→ {topic}</li>' for topic in topics)}
                    </ul>
                    <div class="time-estimate">⏱️ Tempo estimado: {time}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"Iniciar Tutorial", key=f"btn_{title}"):
            self.launch_tutorial(script_path)

    def launch_tutorial(self, script_path: str):
        """
        Inicia o tutorial verificando primeiro se o arquivo existe.
        
        Args:
            script_path (str): Caminho para o script do tutorial
        """
        script_file = Path(script_path)
        if not script_file.exists():
            st.error(f"Erro: O arquivo {script_path} não foi encontrado!")
            return
        
        try:
            subprocess.run(["streamlit", "run", str(script_file)], check=True)
        except subprocess.CalledProcessError as e:
            st.error(f"Erro ao iniciar o tutorial: {e}")
        except FileNotFoundError:
            st.error("Erro: Streamlit não está instalado ou não está disponível no PATH")

    def render_header(self):
        """Renderiza o cabeçalho da página"""
        st.markdown("""
            <div class="header">
                <h1>Sistema de Tutoriais</h1>
                <p>Selecione um dos tutoriais abaixo para começar seu aprendizado</p>
            </div>
        """, unsafe_allow_html=True)

    def render_footer(self):
        """Renderiza o rodapé da página"""
        st.markdown("""
            <div class="footer">
                Sistema de Tutoriais • Versão 1.0
            </div>
        """, unsafe_allow_html=True)

    def run(self):
        """Executa o sistema de tutoriais"""
        self.render_header()

        # Grid de tutoriais
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            self.create_tutorial_card(
                "💼",
                "Imobilizado",
                [
                    "Lançamento de notas fiscais",
                    "Validação de documentos",
                    "Controle de ativos",
                    "Chat para dúvidas"
                ],
                "30 minutos",
                "Imobilizado.py"
            )

        with col2:
            self.create_tutorial_card(
                "📄",
                "Documentos",
                [
                    "Gestão de documentos",
                    "Processo de aprovação",
                    "Organização de arquivos",
                    "Boas práticas"
                ],
                "20 minutos",
                "app.py"
            )

        self.render_footer()

def main():
    tutorial_system = TutorialSystem()
    tutorial_system.run()

if __name__ == "__main__":
    main()