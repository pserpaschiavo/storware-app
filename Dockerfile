# Usar uma imagem base oficial do Python
FROM python:3.11-slim

# Definir o diretório de trabalho no container
WORKDIR /code

# Copiar o arquivo de dependências
COPY requirements.txt .

# Instalar as dependências
# --no-cache-dir: não armazena o cache do pip, reduzindo o tamanho da imagem
# --trusted-host pypi.python.org: pode ser necessário em redes com restrições
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Copiar todo o código da aplicação para o diretório de trabalho
COPY ./app /code/app
COPY ./main.py /code/

# Expor a porta que a aplicação vai rodar
EXPOSE 8000

# Comando para iniciar a aplicação (será sobrescrito pelo docker-compose para o worker)
# O --host 0.0.0.0 é essencial para que a aplicação seja acessível de fora do container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


