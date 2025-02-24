# Usa uma imagem Python oficial
FROM python:3.10

# Define o diretório de trabalho
WORKDIR /app

# Copia todos os arquivos da API
COPY . /app

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta que a FastAPI usará
EXPOSE 8080

# Comando para rodar a API no Cloud Run
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
