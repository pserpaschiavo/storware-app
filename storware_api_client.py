#!/usr/bin/env python3

# storware_api_client.py
# Finalidade: Cliente Python para interagir com a API do Storware,
# utilizando práticas seguras de gerenciamento de segredos.

import requests
import os
import json
import urllib3
import argparse
from dotenv import load_dotenv
from cryptography.fernet import Fernet, InvalidToken
from tabulate import tabulate

# --- Bloco de Configuração e Classe (sem alterações) ---
load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def decrypt_value(key, encrypted_value):
    if not key or not encrypted_value: return None
    try:
        f = Fernet(key.encode())
        decrypted_value = f.decrypt(encrypted_value.encode())
        return decrypted_value.decode()
    except (InvalidToken, TypeError):
        print(f"❌ Falha ao descriptografar: A chave 'ENCRYPTION_KEY' está incorreta.")
        return None
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado durante a descriptografia: {e}")
        return None

class StorwareAPIClient:
    def __init__(self):
        print("🚀 Iniciando cliente da API Storware...")
        self.host = os.getenv('STORWARE_HOST')
        self.base_path = '/api'
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        self.session = None
        encryption_key = os.getenv('ENCRYPTION_KEY')
        encrypted_username = os.getenv('STORWARE_ENCRYPTED_USERNAME')
        encrypted_password = os.getenv('STORWARE_ENCRYPTED_PASSWORD')
        username = decrypt_value(encryption_key, encrypted_username)
        password = decrypt_value(encryption_key, encrypted_password)
        if username and password:
            self._authenticate(username, password)
        else:
            print("\n🛑 Processo interrompido. Verifique as variáveis de ambiente.")

    def _authenticate(self, username, password):
        if not self.host:
            print("❌ Erro de Configuração: STORWARE_HOST não definido.")
            return
        login_url = f"{self.host}{self.base_path}/session/login"
        payload = {"login": username, "password": password}
        session = requests.Session()
        session.headers.update(self.headers)
        session.verify = False
        print(f"Tentando autenticar o usuário '{username}' em '{login_url}'...")
        try:
            response = session.post(login_url, data=json.dumps(payload))
            response.raise_for_status()
            print("✅ Autenticação bem-sucedida! A sessão está pronta para ser usada.")
            self.session = session
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição de login: {e}")
            self.session = None

    def list_vms(self):
        if not self.session: return None
        vms_url = f"{self.host}{self.base_path}/virtual-machines"
        print(f"\nBuscando lista de VMs em '{vms_url}'...")
        try:
            response = self.session.get(vms_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Falha ao buscar a lista de VMs: {e}")
            return None

    def get_vm_details(self, vm_guid):
        if not self.session: return None
        details_url = f"{self.host}{self.base_path}/virtual-machines/{vm_guid}"
        print(f"\nBuscando detalhes da VM em '{details_url}'...")
        try:
            response = self.session.get(details_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404: print(f"❌ Erro: Nenhuma VM encontrada com o GUID '{vm_guid}'.")
            else: print(f"❌ Falha ao buscar detalhes da VM: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Falha na conexão ao buscar detalhes da VM: {e}")
            return None

    def list_tasks(self):
        """Busca a lista de tarefas recentes executadas pelo Storware."""
        if not self.session: return None
        tasks_url = f"{self.host}{self.base_path}/tasks"
        print(f"\nBuscando lista de tarefas em '{tasks_url}'...")
        try:
            response = self.session.get(tasks_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Falha ao buscar a lista de tarefas: {e}")
            return None

# --- Bloco Principal de Execução (com a mudança no print) ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente de linha de comando para a API do Storware.", formatter_class=argparse.RawTextHelpFormatter)
    
    # --- GRUPO DE AÇÕES PRINCIPAIS ---
    main_action = parser.add_mutually_exclusive_group()
    main_action.add_argument('--get-details', type=str, metavar='GUID', help='Busca e exibe os detalhes de uma VM específica.')
    main_action.add_argument('--list-tasks', action='store_true', help='Lista as tarefas recentes executadas pelo Storware.')
    
    # --- GRUPO DE FILTROS PARA LISTAGEM DE VMS ---
    vm_filters = parser.add_argument_group('Filtros para Listagem de VMs (ação padrão)')
    vm_filters.add_argument('--head', type=int, help='Exibe as N primeiras VMs.')
    vm_filters.add_argument('--tail', type=int, help='Exibe as N últimas VMs.')
    vm_filters.add_argument('--filter-name', type=str, help='Filtra VMs cujo nome contém o texto.')
    
    # --- GRUPO DE FILTROS PARA LISTAGEM DE TAREFAS ---
    task_filters = parser.add_argument_group('Filtros para --list-tasks')
    task_filters.add_argument('--filter-task-status', type=str.upper, choices=['QUEUED', 'RUNNING', 'FINISHED', 'FAILED', 'CANCELLED'], help='Filtra tarefas por status.')
    task_filters.add_argument('--filter-by-vm-guid', type=str, metavar='GUID', help='Filtra tarefas de uma VM específica.')

    args = parser.parse_args()

    client = StorwareAPIClient()

    if client.session:
        if args.get_details:
            vm_details = client.get_vm_details(args.get_details)
            if vm_details:
                print(f"\n--- Detalhes da VM (GUID: {args.get_details}) ---")
                print(json.dumps(vm_details, indent=2, ensure_ascii=False))
        
        elif args.list_tasks:
            tasks_list = client.list_tasks()
            if tasks_list:
                processed_list = tasks_list
                
                # --- APLICANDO OS NOVOS FILTROS DE TAREFAS ---
                if args.filter_task_status:
                    processed_list = [t for t in processed_list if t.get('state', {}).get('name') == args.filter_task_status]
                
                if args.filter_by_vm_guid:
                    processed_list = [t for t in processed_list if t.get('protectedEntity', {}).get('guid') == args.filter_by_vm_guid]

                print("\n--- Monitor de Tarefas ---")
                if not processed_list:
                    print("Nenhuma tarefa encontrada com os filtros aplicados.")
                else:
                    headers = ["GUID da Tarefa", "Tipo", "Status", "Progresso %", "VM Alvo"]
                    table_data = []
                    for task in processed_list:
                        target_vm = task.get('protectedEntity', {}).get('name', 'N/A')
                        table_data.append([
                            task.get('guid', 'N/A'),
                            task.get('type', {}).get('name', 'N/A'),
                            task.get('state', {}).get('name', 'N/A'),
                            task.get('progress', 'N/A'),
                            target_vm
                        ])
                    print(tabulate(table_data, headers=headers, tablefmt="grid"))
                
                print(f"\nExibindo {len(processed_list)} de {len(tasks_list)} tarefas totais encontradas.")

        else:
            # Ação Padrão: Listar VMs
            vms_list = client.list_vms()
            if vms_list:
                processed_list = vms_list
                if args.filter_name: processed_list = [vm for vm in processed_list if args.filter_name.lower() in vm.get('name', '').lower()]
                if args.head: processed_list = processed_list[:args.head]
                elif args.tail: processed_list = processed_list[-args.tail:]
                
                print("\n--- Inventário de Máquinas Virtuais ---")
                if not processed_list:
                    print("Nenhuma VM encontrada com os filtros aplicados.")
                else:
                    headers = ["Nome da VM", "GUID", "Status de Proteção"]
                    table_data = [[vm.get('name', 'N/A'), vm.get('guid', 'N/A'), vm.get('protectionStatus', {}).get('name', 'N/A')] for vm in processed_list]
                    print(tabulate(table_data, headers=headers, tablefmt="grid"))

                print(f"\nExibindo {len(processed_list)} de {len(vms_list)} VMs totais encontradas.")