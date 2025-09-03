# app/api/routes.py
from fastapi import APIRouter, BackgroundTasks
from typing import List

router = APIRouter(
    prefix="/api/v1",
    tags=["Relatórios"]
)

@router.post("/reports/generate")
async def generate_report(project_ids: List[str]):
    """
    Gera um relatório sob demanda para uma lista de projetos.
    (Implementação pendente)
    """
    # Lógica para chamar o report_generator e retornar o PDF
    return {"message": f"Gerando relatório para os projetos: {project_ids}"}


@router.post("/reports/schedule")
async def schedule_report(project_ids: List[str], background_tasks: BackgroundTasks):
    """
    Agenda a geração de um relatório para uma lista de projetos.
    (Implementação pendente)
    """
    # Lógica para enfileirar a tarefa no Celery
    return {"message": f"Relatório para os projetos {project_ids} agendado com sucesso!"}
