import streamlit as st
import subprocess

def set_custom_style():
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

def create_tutorial_card(icon, title, topics, time, script_path):
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
        subprocess.run(["streamlit", "run", script_path])

def main():
    st.set_page_config(
        page_title="Sistema de Tutoriais",
        page_icon="📚",
        layout="wide"
    )
    
    set_custom_style()

    st.markdown("""
        <div class="header">
            <h1>Sistema de Tutoriais</h1>
            <p>Selecione um dos tutoriais abaixo para começar seu aprendizado</p>
        </div>
    """, unsafe_allow_html=True)

    # Tutoriais em grid simétrico
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        create_tutorial_card(
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
        create_tutorial_card(
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

    st.markdown("""
        <div class="footer">
            Sistema de Tutoriais • Versão 1.0
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()