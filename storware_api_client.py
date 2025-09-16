#!/usr/bin/env python3
# storware_api_client.py
# Finalidade: Cliente Python para interagir com a API do Storware,
# utilizando práticas seguras de gerenciamento de segredos.

import requests
import os
import json
import urllib3
from dotenv import load_dotenv
from cryptography.fernet import Fernet, InvalidToken

# --- Inicialização e Configuração ---
# Carrega variáveis do arquivo .env para o ambiente de execução
load_dotenv()

# Desabilita avisos de SSL para ambientes de teste com certificados autoassinados
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Carrega as configurações do ambiente
STORWARE_HOST = os.getenv('STORWARE_HOST')
# Lemos o nome de usuário e a senha criptografados do .env
ENCRYPTED_USERNAME = os.getenv('STORWARE_ENCRYPTED_USERNAME')
ENCRYPTED_PASSWORD = os.getenv('STORWARE_ENCRYPTED_PASSWORD')
# Lemos a CHAVE MESTRA do ambiente do sistema
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

# Constantes da API
API_BASE_PATH = '/api'
LOGIN_ENDPOINT = '/session/login'
HEADERS = {'Content-Type': 'application/json', 'Accept': 'application/json'}

# --- Funções Auxiliares ---

def decrypt_value(key, encrypted_value):
    """Descriptografa um valor genérico usando a chave de ambiente."""
    if not key or not encrypted_value:
        return None  # Erro será tratado na lógica principal
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

# --- Funções Principais da API ---

def create_authenticated_session(host, username, password):
    """Cria e retorna uma sessão autenticada na API do Storware."""
    if not all([host, username, password]):
        print("❌ Erro de Configuração: Uma ou mais variáveis (HOST, USERNAME, PASSWORD) não foram definidas ou descriptografadas.")
        return None

    login_url = f"{host}{API_BASE_PATH}{LOGIN_ENDPOINT}"

    # Payload com as chaves corretas que descobrimos ('login' e 'password')
    payload = {
        "login": username,    # <-- CORREÇÃO: A chave correta é "login", conforme nossa investigação.
        "password": password
    }

    session = requests.Session()
    session.headers.update(HEADERS)
    session.verify = False  # Em produção, use um certificado válido: session.verify = '/path/to/cert.pem'

    print(f"Tentando autenticar o usuário '{username}' em '{login_url}'...")

    try:
        response = session.post(login_url, data=json.dumps(payload))
        response.raise_for_status()  # Lança exceção para códigos de erro (4xx/5xx)
        print("✅ Autenticação bem-sucedida! A sessão está pronta para ser usada.")
        return session

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ Erro HTTP: {http_err}")
        if response.status_code == 401:
            print("   Causa provável: Credenciais inválidas (usuário ou senha).")
        else:
            print(f"   Resposta do Servidor: {response.text}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"❌ Erro de Conexão: {req_err}")
        print("   Causa provável: O host está inacessível ou o nome/IP/porta está incorreto.")
        return None

# --- Bloco Principal de Execução ---

if __name__ == "__main__":
    print("🚀 Iniciando cliente da API Storware...")

    # 1. Descriptografar o nome de usuário e a senha
    api_username = decrypt_value(ENCRYPTION_KEY, ENCRYPTED_USERNAME)
    api_password = decrypt_value(ENCRYPTION_KEY, ENCRYPTED_PASSWORD)

    if api_username and api_password:
        # 2. Se ambos foram descriptografados, tentar criar a sessão
        authenticated_session = create_authenticated_session(STORWARE_HOST, api_username, api_password)

        if authenticated_session:
            # 3. Se a sessão foi criada, fazer uma chamada de teste
            print("\n--- Validando a Sessão Autenticada ---")
            vms_url = f"{STORWARE_HOST}{API_BASE_PATH}/virtual-machines"
            print(f"Buscando lista de VMs em '{vms_url}'...")

            try:
                vm_response = authenticated_session.get(vms_url)
                vm_response.raise_for_status()
                vms_data = vm_response.json()
                print(f"✅ Sucesso! Sessão válida. Encontradas {len(vms_data)} máquinas virtuais.")

            except requests.exceptions.RequestException as e:
                print(f"❌ Falha ao tentar usar a sessão autenticada: {e}")
    else:
        print("\n🛑 Processo interrompido. Verifique se as variáveis ENCRYPTION_KEY, STORWARE_ENCRYPTED_USERNAME e STORWARE_ENCRYPTED_PASSWORD estão configuradas corretamente.")
