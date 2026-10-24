# Imagem base oficial leve e imutável
FROM python:3.11-slim

# Evita geração de arquivos .pyc e garante logs em tempo real no terminal
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Diretório de trabalho dentro do container
WORKDIR /app

# Instalação isolada das dependências autorizadas
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Cópia do código-fonte, especificações e suíte de testes
COPY src/ ./src/
COPY tests/ ./tests/
COPY specs/ ./specs/
COPY CONTEXT_RULES.md README.md ./

# Comando de entrada padrão: executa a suíte de validação do Test Harness
CMD ["pytest", "tests/test_harness.py", "-v"]