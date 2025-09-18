#!/usr/bin/env python3

# consolidated_data_collector.py
# VERSÃO OTIMIZADA: Coleta a volumetria, com timeouts e retentativas
# para maior resiliência em ambientes de produção.

import requests
import os
import json
import urllib3
import logging
import sys
import time # Importado para a lógica de retentativa (retry)
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from cryptography.fernet import Fernet, InvalidToken

# --- MARCADOR DE VERSÃO ---
print("--- [ INFO ] Executando Coletor de Volumetria v1.2 (Otimizado com Retries e Timeouts) ---", file=sys.stderr)

# --- 1. CONSTANTES DE CONFIGURAÇÃO ---
# Mover configurações para o topo facilita a manutenção do script.
DEFAULT_TIME_DELTA_HOURS = 24
REQUEST_TIMEOUT_SECONDS = 30 # Timeout para as requisições de API em segundos
MAX_RETRIES = 3 # Número máximo de tentativas em caso de falha de rede
RETRY_DELAY_SECONDS = 5 # Tempo de espera entre as tentativas

# --- 2. Bloco de Utilitários e Configuração ---
load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
log = logging.getLogger(__name__)

def decrypt_value(key, encrypted_value):
    """Descriptografa um valor genérico usando a chave de ambiente."""
    if not key or not encrypted_value: return None
    try:
        f = Fernet(key.encode())
        decrypted_value = f.decrypt(encrypted_value.encode())
        return decrypted_value.decode()
    except (InvalidToken, TypeError):
        log.error("Falha ao descriptografar: A chave 'ENCRYPTION_KEY' está incorreta.")
        return None
    except Exception as e:
        log.error(f"Erro inesperado durante a descriptografia: {e}")
        return None

def format_bytes(size_in_bytes):
    """Converte bytes para um formato legível (KB, MB, GB, TB)."""
    if size_in_bytes is None or not isinstance(size_in_bytes, (int, float)): return "N/A"
    if size_in_bytes == 0: return "0.00 B"
    power = 1024
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size_in_bytes >= power and n < len(power_labels) -1 :
        size_in_bytes /= power
        n += 1
    return f"{size_in_bytes:.2f} {power_labels[n]}B"

# --- 3. "Motor" da API: A Classe StorwareAPIClient ---
class StorwareAPIClient:
    """Um cliente para interagir com a API do Storware."""
    def __init__(self):
        log.info("Iniciando cliente da API Storware...")
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
            log.critical("Processo interrompido. Verifique as variáveis de ambiente.")

    def _authenticate(self, username, password):
        if not self.host:
            log.error("Erro de Configuração: STORWARE_HOST não definido.")
            return
        login_url = f"{self.host}{self.base_path}/session/login"
        payload = {"login": username, "password": password}
        
        for attempt in range(MAX_RETRIES):
            try:
                session = requests.Session()
                session.headers.update(self.headers)
                session.verify = False
                log.info(f"Tentando autenticar o usuário '{username}' (tentativa {attempt + 1}/{MAX_RETRIES})...")
                response = session.post(login_url, data=json.dumps(payload), timeout=REQUEST_TIMEOUT_SECONDS)
                response.raise_for_status()
                log.info("Autenticação bem-sucedida! A sessão está pronta para ser usada.")
                self.session = session
                return # Sai do loop se a autenticação for bem-sucedida
            except requests.exceptions.RequestException as e:
                log.warning(f"Falha na tentativa de autenticação: {e}")
                if attempt < MAX_RETRIES - 1:
                    log.info(f"Aguardando {RETRY_DELAY_SECONDS} segundos antes da próxima tentativa...")
                    time.sleep(RETRY_DELAY_SECONDS)
                else:
                    log.error("Número máximo de tentativas de autenticação atingido. Abortando.")
                    self.session = None

# --- 4. Função de Coleta de Dados ---
def collect_data(client, from_date, to_date):
    """Coleta os dados de volumetria agrupados por projeto."""
    log.info(f"Buscando relatório de volumetria de {from_date.strftime('%Y-%m-%d %H:%M')} a {to_date.strftime('%Y-%m-%d %H:%M')}...")
    report_url = f"{client.host}{client.base_path}/chargeback-reporting/backup-size/vm"
    
    from_timestamp = int(from_date.timestamp() * 1000)
    to_timestamp = int(to_date.timestamp() * 1000)
    
    payload = {
        "groupBy": "project", "from": from_timestamp, "to": to_timestamp,
        "backupDestinationGuids": [], "backupPolicyGuids": [], "hypervisorClusterGuids": [],
        "hypervisorManagerGuids": [], "hypervisorGuids": [], "virtualMachineGuids": [], "projectGuids": []
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = client.session.post(report_url, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            volumetrics_by_project = response.json()
            log.info("Coleta de dados concluída com sucesso.")
            
            final_report = [
                {
                    "project_name": project.get('name', 'N/A'),
                    "project_guid": project.get('guid', 'N/A'),
                    "total_backup_size_bytes": project.get('size', 0),
                    "total_backup_size_readable": format_bytes(project.get('size', 0)),
                    "vms": []
                }
                for project in volumetrics_by_project
            ]
            return final_report
        except requests.exceptions.RequestException as e:
            log.warning(f"Falha ao buscar o relatório (tentativa {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                log.info(f"Aguardando {RETRY_DELAY_SECONDS} segundos antes da próxima tentativa...")
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                log.error("Número máximo de tentativas de busca ao relatório atingido.")
                return None

# --- 5. Bloco de Execução Principal ---
def main():
    """Função principal que orquestra a execução do script."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stderr)

    to_date_obj = datetime.now(timezone.utc)
    from_date_obj = to_date_obj - timedelta(hours=DEFAULT_TIME_DELTA_HOURS)
            
    client = StorwareAPIClient()

    if not client.session:
        log.critical("Falha ao criar a sessão autenticada. Verifique os logs e a sua configuração.")
        sys.exit(1)

    report = collect_data(client, from_date=from_date_obj, to_date=to_date_obj)
    
    if report is not None:
        filename = f"volumetria_{from_date_obj.strftime('%Y-%m-%d')}_-_{to_date_obj.strftime('%Y-%m-%d')}.json"
        
        log.info(f"Preparando para salvar o relatório com {len(report)} projetos no arquivo '{filename}'...")

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=4, ensure_ascii=False)
            log.info(f"Relatório salvo com sucesso em: {filename}")
        except IOError as e:
            log.error(f"Falha ao salvar o relatório no arquivo {filename}: {e}")
            log.error("Verifique as permissões de escrita no diretório atual.")
            sys.exit(1)
    else:
        log.error("O relatório final não pôde ser gerado.")
        sys.exit(1)

if __name__ == "__main__":
    main()

