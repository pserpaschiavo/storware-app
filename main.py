# main.py
from fastapi import FastAPI
from app.api import routes

# Cria a instância principal da aplicação FastAPI
app = FastAPI(
    title="API de Relatórios OpenStack",
    description="Uma API para gerar e agendar relatórios de recursos do OpenStack.",
    version="0.1.0",
)

# Inclui as rotas definidas no módulo de API
app.include_router(routes.router)

@app.get("/", tags=["Root"])
def read_root():
    """
    Endpoint raiz para verificar se a API está funcionando.
    """
    return {"message": "Bem-vindo à API de Relatórios OpenStack!"}
