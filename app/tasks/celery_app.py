# app/tasks/celery_app.py
from celery import Celery
from app.core.config import settings

# Cria a instância da aplicação Celery
# O primeiro argumento 'tasks' é o nome do módulo principal das tarefas.
celery_app = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.report_tasks"]  # Módulos onde as tarefas estão definidas
)

celery_app.conf.update(
    task_track_started=True,
)


