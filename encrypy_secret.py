#!/usr/bin/env python3

# encrypt_secret.py
# Finalidade: Gerar uma chave de criptografia e criptografar o USUÁRIO e a SENHA.
# Execução: Rode este script uma única vez para configurar seu ambiente.

from cryptography.fernet import Fernet
import getpass

print("--- Utilitário de Criptografia de Segredos ---")
print("Este script irá gerar uma chave e criptografar o usuário e a senha que você digitar.")

# 1. Gerar uma única chave de criptografia para ambos os segredos
key = Fernet.generate_key()
f = Fernet(key)

# 2. Capturar o nome de usuário de forma segura
try:
    plain_text_username = getpass.getpass(
        "Digite o NOME DE USUÁRIO do Storware (a digitação ficará oculta): "
    ).encode()
except Exception as error:
    print(f'\nERRO: Não foi possível ler o nome de usuário. {error}')
    exit()

# 3. Capturar a senha de forma segura
try:
    plain_text_password = getpass.getpass(
        "Digite a SENHA do Storware (a digitação ficará oculta): "
    ).encode()
except Exception as error:
    print(f'\nERRO: Não foi possível ler a senha. {error}')
    exit()

# 4. Criptografar ambos os valores
encrypted_username = f.encrypt(plain_text_username)
encrypted_password = f.encrypt(plain_text_password)

# 5. Imprimir os valores para configuração
print("\n" + "="*50)
print("✅ AÇÕES NECESSÁRIAS ✅")
print("Por favor, siga os dois passos abaixo:")
print("\n1. DEFINA A VARIÁVEL DE AMBIENTE 'ENCRYPTION_KEY':")
print("   - Esta é sua chave mestra. NÃO a salve em arquivos de texto.")
print("   - Execute no seu terminal (Linux/macOS):")
print(f'     export ENCRYPTION_KEY="{key.decode()}"')
print("   - Execute no seu terminal (Windows PowerShell):")
print(f'     $env:ENCRYPTION_KEY="{key.decode()}"')

print("\n2. ATUALIZE SEU ARQUIVO .env:")
print("   - Copie as DUAS linhas abaixo e cole no seu arquivo .env:")
print(f'   STORWARE_ENCRYPTED_USERNAME="{encrypted_username.decode()}"')
print(f'   STORWARE_ENCRYPTED_PASSWORD="{encrypted_password.decode()}"')
print("="*50)
