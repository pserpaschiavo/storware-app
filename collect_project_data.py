#!/usr/bin/env python3

# collect_project_data.py
# Finalidade: Coletar dados de volumetria de backup por projeto e listar
# as VMs de cada um, gerando uma saída em JSON para ingestão em banco de dados.
# - Execução padrão: últimos 24h, sem lista de VMs.
# - Flags para customizar período e inclusão de VMs.

import json
import argparse
from datetime import datetime, timedelta, timezone
from storware_api_client import StorwareAPIClient, format_bytes

def collect_data(client, from_date, to_date, include_vms):
    """
    Orquestra a coleta e combinação de dados da API do Storware.
    """
    print("Iniciando coleta de dados...")

    # --- PASSO 1 (Opcional): Obter a lista completa de todas as VMs ---
    all_vms = None
    if include_vms:
        print("Buscando inventário completo de VMs (solicitado via flag)...")
        all_vms = client.list_vms()
        if not all_vms:
            print("Aviso: Não foi possível obter a lista de VMs. O relatório não incluirá os detalhes das VMs.")
    
    # --- PASSO 2: Obter a volumetria total agrupada por projeto ---
    print(f"Buscando relatório de volumetria de {from_date.strftime('%Y-%m-%d %H:%M')} a {to_date.strftime('%Y-%m-%d %H:%M')}...")
    report_url = f"{client.host}{client.base_path}/chargeback-reporting/backup-size/vm"
    
    from_timestamp = int(from_date.timestamp() * 1000)
    to_timestamp = int(to_date.timestamp() * 1000)
    
    payload = {
        "groupBy": "project",
        "from": from_timestamp,
        "to": to_timestamp,
        # Mantemos os outros filtros vazios para abranger tudo
        "backupDestinationGuids": [], "backupPolicyGuids": [], "hypervisorClusterGuids": [],
        "hypervisorManagerGuids": [], "hypervisorGuids": [], "virtualMachineGuids": [], "projectGuids": []
    }

    try:
        response = client.session.post(report_url, json=payload)
        response.raise_for_status()
        volumetrics_by_project = response.json()
    except Exception as e:
        print(f"Erro ao buscar o relatório de volumetria por projeto: {e}")
        return None

    # --- PASSO 3: Combinar os dados ---
    print("Combinando e estruturando os dados...")
    
    # Estrutura base do relatório a partir dos dados de volumetria
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

    # Se a inclusão de VMs foi solicitada e os dados foram obtidos com sucesso,
    # iteramos sobre a lista de VMs e as alocamos em seus respectivos projetos.
    if include_vms and all_vms:
        print("Alocando VMs aos seus respectivos projetos...")
        for vm in all_vms:
            project_info = vm.get('project')
            if project_info and project_info.get('guid') in projects_data:
                project_guid = project_info['guid']
                projects_data[project_guid]['vms'].append({
                    "vm_name": vm.get('name', 'N/A'),
                    "vm_guid": vm.get('guid', 'N/A')
                })

    # Converte o dicionário de volta para uma lista, que é um formato JSON mais padrão
    final_report = list(projects_data.values())
    
    print("Coleta de dados concluída com sucesso.")
    return final_report


if __name__ == "__main__":
    # Configuração da interface de linha de comando
    parser = argparse.ArgumentParser(description="Coletor de dados de volumetria por projeto do Storware.")
    parser.add_argument('--from-date', type=str, help='Data de início do relatório (formato: AAAA-MM-DD).')
    parser.add_argument('--to-date', type=str, help='Data de fim do relatório (formato: AAAA-MM-DD).')
    parser.add_argument('--include-vms', action='store_true', help='Inclui a lista detalhada de VMs em cada projeto.')
    
    args = parser.parse_args()

    # Lógica para definir o período de tempo
    try:
        to_date_obj = datetime.strptime(args.to_date, '%Y-%m-%d').replace(tzinfo=timezone.utc) if args.to_date else datetime.now(timezone.utc)
        
        # O padrão é últimas 24h SE a data de início não for fornecida
        if args.from_date:
            from_date_obj = datetime.strptime(args.from_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        else:
            from_date_obj = to_date_obj - timedelta(hours=24)
            
    except ValueError:
        print("Erro: Formato de data inválido. Use AAAA-MM-DD.")
        exit()

    # Instancia nosso cliente. O __init__ cuida de todo o login.
    client = StorwareAPIClient()

    if client.session:
        # Chama a função principal de coleta e processamento com os argumentos da CLI
        report = collect_data(client, from_date=from_date_obj, to_date=to_date_obj, include_vms=args.include_vms)
        
        if report:
            # Imprime o resultado final em formato JSON formatado
            print(json.dumps(report, indent=4, ensure_ascii=False))
