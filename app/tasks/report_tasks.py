# app/tasks/report_tasks.py
# from .celery_app import celery_app
# from app.services.report_generator import report_service

# @celery_app.task(name="generate_scheduled_report")
def generate_scheduled_report(project_ids: list):
    """
    Tarefa Celery que gera o relatório, salva em algum lugar ou envia por e-mail.
    """
    print(f"WORKER: Executando relatório agendado para projetos: {project_ids}")
    # Chama o mesmo serviço usado pela API
    # report_service.create_vm_inventory_report(project_ids)
    # Lógica para salvar o PDF ou enviar por e-mail
    print("WORKER: Relatório concluído.")
    return "Relatório gerado com sucesso pelo worker."

