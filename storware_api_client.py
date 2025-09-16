#!/usr/bin/env python3

# storware_api_client.py
# Finalidade: Cliente Python para interagir com a API do Storware,
# utilizando práticas seguras de gerenciamento de segredos.

import requests
import os
import json
import urllib3
import argparse  # <-- 1. Importamos a biblioteca para argumentos de CLI
from dotenv import load_dotenv
from cryptography.fernet import Fernet, InvalidToken
from tabulate import tabulate

# --- Bloco de Configuração e Funções (sem alterações) ---
load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
STORWARE_HOST = os.getenv('STORWARE_HOST')
ENCRYPTED_USERNAME = os.getenv('STORWARE_ENCRYPTED_USERNAME')
ENCRYPTED_PASSWORD = os.getenv('STORWARE_ENCRYPTED_PASSWORD')
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
API_BASE_PATH = '/api'
LOGIN_ENDPOINT = '/session/login'
HEADERS = {'Content-Type': 'application/json', 'Accept': 'application/json'}

def decrypt_value(key, encrypted_value):
    if not key or not encrypted_value: return None
    try:
        f = Fernet(key.encode())
        decrypted_value = f.decrypt(encrypted_value.encode())
        return decrypted_value.decode()
    except (InvalidToken, TypeError):
        print(f"❌ Falha ao descriptografar: A chave 'ENCRYPTION_KEY' está incorreta ou um valor criptografado está corrompido.")
        return None
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado durante a descriptografia: {e}")
        return None

def create_authenticated_session(host, username, password):
    if not all([host, username, password]):
        print("❌ Erro de Configuração: Variáveis essenciais não definidas.")
        return None
    login_url = f"{host}{API_BASE_PATH}{LOGIN_ENDPOINT}"
    payload = {"login": username, "password": password}
    session = requests.Session()
    session.headers.update(HEADERS)
    session.verify = False
    print(f"Tentando autenticar o usuário '{username}' em '{login_url}'...")
    try:
        response = session.post(login_url, data=json.dumps(payload))
        response.raise_for_status()
        print("✅ Autenticação bem-sucedida! A sessão está pronta para ser usada.")
        return session
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição de login: {e}")
        return None

def list_vms(session):
    """Busca a lista de todas as máquinas virtuais visíveis na API."""
    vms_url = f"{STORWARE_HOST}{API_BASE_PATH}/virtual-machines"
    print(f"\nBuscando lista de VMs em '{vms_url}'...")
    try:
        response = session.get(vms_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Falha ao buscar a lista de VMs: {e}")
        return None

# --- Bloco Principal de Execução (TOTALMENTE ATUALIZADO) ---
if __name__ == "__main__":
    # --- 2. Configuração do Parser de Argumentos ---
    parser = argparse.ArgumentParser(
        description="Cliente de linha de comando para a API do Storware.",
        formatter_class=argparse.RawTextHelpFormatter # Melhora a formatação da ajuda
    )
    parser.add_argument('--head', type=int, help='Exibe as N primeiras VMs da lista.')
    parser.add_argument('--tail', type=int, help='Exibe as N últimas VMs da lista.')
    parser.add_argument(
        '--filter-name', 
        type=str, 
        help='Filtra VMs cujo nome contém o texto fornecido (case-insensitive).'
    )
    # Adicione aqui outros filtros, ex: --filter-status
    
    args = parser.parse_args()

    # --- Lógica de Autenticação e Execução ---
    print("🚀 Iniciando cliente da API Storware...")
    
    api_username = decrypt_value(ENCRYPTION_KEY, ENCRYPTED_USERNAME)
    api_password = decrypt_value(ENCRYPTION_KEY, ENCRYPTED_PASSWORD)
    
    if api_username and api_password:
        authenticated_session = create_authenticated_session(STORWARE_HOST, api_username, api_password)
        
        if authenticated_session:
            vms_list = list_vms(authenticated_session)
            
            if vms_list:
                processed_list = vms_list
                
                # --- 3. Lógica de Filtragem e Seleção ---
                # Primeiro, aplica o filtro de nome, se existir
                if args.filter_name:
                    print(f"Filtrando VMs com o nome contendo: '{args.filter_name}'")
                    # List comprehension para filtrar a lista
                    processed_list = [
                        vm for vm in processed_list 
                        if args.filter_name.lower() in vm.get('name', '').lower()
                    ]

                # Depois, aplica head ou tail na lista já filtrada
                if args.head:
                    print(f"Exibindo as primeiras {args.head} VMs...")
                    processed_list = processed_list[:args.head]
                elif args.tail:
                    print(f"Exibindo as últimas {args.tail} VMs...")
                    processed_list = processed_list[-args.tail:]

                # --- 4. Preparação e Exibição da Tabela ---
                print(f"✅ Sucesso! Exibindo {len(processed_list)} de {len(vms_list)} máquinas virtuais encontradas.")
                
                if not processed_list:
                    print("Nenhuma VM encontrada com os filtros aplicados.")
                else:
                    headers = ["Nome da VM", "GUID", "Status de Proteção"]
                    table_data = []
                    for vm in processed_list:
                        vm_name = vm.get('name', 'N/A')
                        vm_guid = vm.get('guid', 'N/A')
                        protection_status = vm.get('protectionStatus', {}).get('name', 'N/A')
                        table_data.append([vm_name, vm_guid, protection_status])
                    
                    print("\n--- Inventário de Máquinas Virtuais ---")
                    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    else:
        print("\n🛑 Processo interrompido. Verifique as variáveis de ambiente.")
