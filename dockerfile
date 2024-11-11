FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Atualizar o pip para a versão mais recente
RUN pip install --upgrade pip

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    zlib1g-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiar os arquivos de dependências para o contêiner
COPY requirements.txt .

# Instalar as dependências do projeto
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Copiar o restante do código da aplicação
COPY . .

# Expor a porta utilizada pelo Streamlit
EXPOSE 8501

# Definir a variável de ambiente para a porta do Streamlit
ENV STREAMLIT_SERVER_PORT=8501

# Comando de inicialização do Streamlit
CMD ["streamlit", "run", "main.py"]
