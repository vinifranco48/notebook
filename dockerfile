# Use uma imagem base com Python e com acesso à atualização do SQLite
FROM python:3.11-slim

# Instale as dependências do sistema
RUN apt-get update && \
    apt-get install -y sqlite3 && \
    rm -rf /var/lib/apt/lists/*

# Verifique se o SQLite está na versão correta
RUN sqlite3 --version

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de requisitos e instale as dependências do Python
COPY requirements.txt .

# Instale as dependências do Python no ambiente do sistema
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copie o restante do código para o contêiner
COPY . .

# Defina a variável de ambiente para garantir que o Streamlit escute todas as interfaces
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Exponha a porta do Streamlit
EXPOSE 8501

# Comando para rodar a aplicação
CMD ["streamlit", "run", "main.py"]
