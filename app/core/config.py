# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Classe de configurações da aplicação.
    Lê as variáveis de ambiente e as valida usando Pydantic.
    """
    # Configurações do OpenStack
    # Estas variáveis precisam ser definidas no seu ambiente
    # (por exemplo, em um arquivo .env)
    OS_AUTH_URL: str
    OS_PROJECT_NAME: str
    OS_USERNAME: str
    OS_PASSWORD: str
    OS_USER_DOMAIN_NAME: str = "Default"
    OS_PROJECT_DOMAIN_NAME: str = "Default"

    # Configurações do Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # Carrega as variáveis de um arquivo .env se ele existir.
    # O nome do arquivo pode ser alterado aqui.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

# Instancia as configurações para serem importadas em outros módulos
settings = Settings()

