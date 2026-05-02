FROM python:3.10-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório de dados
RUN mkdir -p data

# Expor portas
EXPOSE 8000 8501

# Comando padrão (será sobrescrito pelo docker-compose)
CMD ["sh", "-c", "python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 & sleep 5 && streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0"]
