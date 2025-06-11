# Imagem base com Python
FROM python:3.12-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Diretório de trabalho no container
WORKDIR /app

# Atualiza os pacotes e instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de dependências
COPY requirements.txt .

# Instala dependências do projeto
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia o restante dos arquivos do projeto
COPY . .

# Comando para rodar as migrações e iniciar o servidor (substitua conforme necessário)
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
