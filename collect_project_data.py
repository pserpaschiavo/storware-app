
import json
import argparse
import logging
import sys
from datetime import datetime, timedelta, timezone
from storware_api_client import StorwareAPIClient, format_bytes

# Configura o logger para este módulo
log = logging.getLogger(__name__)

def collect_data(client, from_date, to_date, include_vms):
    """
    Orquestra a coleta e combinação de dados da API do Storware.
    """
    log.info("Iniciando coleta de dados...")

    # --- PASSO 1 (Opcional): Obter a lista completa de todas as VMs ---
    all_vms = None
    if include_vms:
        log.info("Buscando inventário completo de VMs (solicitado via flag)...")
        all_vms = client.list_vms()
        if not all_vms:
            log.warning("Não foi possível obter a lista de VMs. O relatório não incluirá os detalhes das VMs.")
    
    # --- PASSO 2: Obter a volumetria total agrupada por projeto ---
    log.info(f"Buscando relatório de volumetria de {from_date.strftime('%Y-%m-%d %H:%M')} a {to_date.strftime('%Y-%m-%d %H:%M')}...")
    report_url = f"{client.host}{client.base_path}/chargeback-reporting/backup-size/vm"
    
    from_timestamp = int(from_date.timestamp() * 1000)
    to_timestamp = int(to_date.timestamp() * 1000)
    
    payload = {
        "groupBy": "project", "from": from_timestamp, "to": to_timestamp,
        "backupDestinationGuids": [], "backupPolicyGuids": [], "hypervisorClusterGuids": [],
        "hypervisorManagerGuids": [], "hypervisorGuids": [], "virtualMachineGuids": [], "projectGuids": []
    }

    try:
        response = client.session.post(report_url, json=payload)
        response.raise_for_status()
        volumetrics_by_project = response.json()
    except Exception as e:
        log.error(f"Erro ao buscar o relatório de volumetria por projeto: {e}")
        return None

    # --- PASSO 3: Combinar os dados ---
    log.info("Combinando e estruturando os dados...")
    
    projects_data = {
        project['guid']: {
            "project_name": project.get('name', 'N/A'),
            "project_guid": project.get('guid', 'N/A'),
            "total_backup_size_bytes": project.get('size', 0),
            "total_backup_size_readable": format_bytes(project.get('size', 0)),
            "vms": []
        }
        for project in volumetrics_by_project
    }

    if include_vms and all_vms:
        log.info("Alocando VMs aos seus respectivos projetos...")
        for vm in all_vms:
            project_info = vm.get('project')
            if project_info and project_info.get('guid') in projects_data:
                project_guid = project_info['guid']
                projects_data[project_guid]['vms'].append({
                    "vm_name": vm.get('name', 'N/A'),
                    "vm_guid": vm.get('guid', 'N/A')
                })

    final_report = list(projects_data.values())
    
    log.info("Coleta de dados concluída com sucesso.")
    return final_report


if __name__ == "__main__":
    # Configura o logging básico para imprimir no console (stderr)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stderr # Garante que os logs vão para o stderr
    )

    parser = argparse.ArgumentParser(description="Coletor de dados de volumetria por projeto do Storware.")
    parser.add_argument('--from-date', type=str, help='Data de início do relatório (formato: AAAA-MM-DD).')
    parser.add_argument('--to-date', type=str, help='Data de fim do relatório (formato: AAAA-MM-DD).')
    parser.add_argument('--include-vms', action='store_true', help='Inclui a lista detalhada de VMs em cada projeto.')
    
    args = parser.parse_args()

    # Lógica para definir o período de tempo
    try:
        to_date_obj = datetime.strptime(args.to_date, '%Y-%m-%d').replace(tzinfo=timezone.utc) if args.to_date else datetime.now(timezone.utc)
        if args.from_date:
            from_date_obj = datetime.strptime(args.from_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        else:
            from_date_obj = to_date_obj - timedelta(hours=1)
            
    except ValueError:
        log.critical("Erro: Formato de data inválido. Use AAAA-MM-DD.")
        sys.exit(1)

    client = StorwareAPIClient()

    # --- VERIFICAÇÃO EXPLÍCITA DA SESSÃO ---
    # Esta é a principal mudança para evitar falhas silenciosas.
    if not client.session:
        log.critical("Falha ao criar a sessão autenticada. Verifique os logs de erro acima e a sua configuração (variáveis de ambiente, .env).")
        sys.exit(1)

    # Se a sessão foi criada com sucesso, o script continua...
    report = collect_data(client, from_date=from_date_obj, to_date=to_date_obj, include_vms=args.include_vms)
    
    if report is not None:
        # A saída principal (o JSON) é impressa no stdout
        print(json.dumps(report, indent=4, ensure_ascii=False))
    else:
        log.error("O relatório final não pôde ser gerado.")
        sys.exit(1)