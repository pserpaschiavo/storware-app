#!/usr/bin/env python3

# storware_api_client.py
# Módulo simplificado com as funcionalidades essenciais e logging.

import requests
import os
import json
import urllib3
import logging
from dotenv import load_dotenv
from cryptography.fernet import Fernet, InvalidToken

# --- Bloco de Configuração e Utilitários ---
load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configura o logger para este módulo
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

# --- CLASSE PRINCIPAL DA API ---
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
        session = requests.Session()
        session.headers.update(self.headers)
        session.verify = False
        log.info(f"Tentando autenticar o usuário '{username}' em '{login_url}'...")
        try:
            response = session.post(login_url, data=json.dumps(payload))
            response.raise_for_status()
            log.info("Autenticação bem-sucedida! A sessão está pronta para ser usada.")
            self.session = session
        except requests.exceptions.RequestException as e:
            log.error(f"Erro na requisição de login: {e}")
            self.session = None

    def list_vms(self):
        """Busca a lista de todas as máquinas virtuais visíveis na API."""
        if not self.session: return None
        vms_url = f"{self.host}{self.base_path}/virtual-machines"
        log.info(f"Buscando lista de VMs em '{vms_url}'...")
        try:
            response = self.session.get(vms_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log.error(f"Erro ao buscar a lista de VMs: {e}")
            return None

