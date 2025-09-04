# Roadmap: API de Relatórios OpenStack

Este documento descreve o plano de trabalho otimizado para o desenvolvimento da aplicação de relatórios OpenStack, dividido em fases lógicas e incrementais. Cada fase representa um marco funcional que nos aproxima do objetivo final de gerar relatórios detalhados sobre a utilização de recursos no OpenStack.

## Fase 1: Fundação Sólida (1-2 semanas)

### Ambiente de Desenvolvimento Completo
- **Completar o arquivo `requirements.txt`** com todas as dependências:
  ```
  fastapi>=0.103.0
  uvicorn>=0.23.0
  celery>=5.3.0
  redis>=4.6.0
  pydantic>=2.3.0
  pydantic-settings>=2.0.0
  openstacksdk>=1.0.0
  weasyprint>=60.0
  jinja2>=3.1.0
  httpx>=0.24.0
  ```
- **Criar o `docker-compose.yaml` completo** com serviços para API, worker, e Redis
- **Implementar testes automatizados básicos** para validar a infraestrutura

### Modelos e Schemas
- Criar módulo `app/models/` para definir schemas Pydantic:
  - `Project`: Modelo para representar projetos OpenStack
  - `Server`: Modelo para representar instâncias VM
  - `Report`: Modelo para representar configurações de relatórios

### Rota de Diagnóstico
- Implementar rota `/api/v1/system/health` para verificar conexão com Redis e OpenStack
- Adicionar logs detalhados para facilitar diagnóstico de problemas

## Fase 2: Integração OpenStack (1 semana)

### Cliente OpenStack Funcional
- **Implementar `openstack_client.py` com autenticação real**
- Adicionar métodos para:
  - Listar projetos disponíveis
  - Obter detalhes de um projeto
  - Listar VMs de um projeto com informações detalhadas (CPU, RAM, disco, IP)
  - Obter estatísticas de uso

### Cache Inteligente
- Implementar cache Redis para resultados do OpenStack para melhorar performance
- Configurar tempo de expiração adequado para diferentes tipos de dados

## Fase 3: Motor de Relatórios (1-2 semanas)

### Gerador de Relatórios Avançado
- **Implementar diferentes tipos de relatórios:**
  - Inventário básico de VMs
  - Relatório detalhado de recursos (com gráficos de utilização)
  - Relatório de custos estimados

### Templates HTML Responsivos
- Criar templates em Jinja2 com estilos modernos
- Implementar componentes reutilizáveis para tabelas, gráficos, etc.
- Adicionar suporte para temas e personalização

### Exportador PDF Robusto
- **Implementar geração de PDF com WeasyPrint**
- Adicionar cabeçalhos, rodapés, paginação
- Suporte para marcas d'água e estilos personalizados

## Fase 4: API e Sistema de Agendamento (1 semana)

### API RESTful Completa
- **Implementar CRUD para configurações de relatórios**
- Adicionar autenticação JWT para acesso à API
- Documentação automática com Swagger UI

### Sistema de Agendamento Flexível
- **Implementar Celery Beat para agendamento periódico**
- Suporte para expressões cron para maior flexibilidade
- Interface para gerenciar agendamentos

## Fase 5: Entrega e Notificações (1 semana)

### Múltiplos Métodos de Entrega
- **Email** (com SMTP configurável)
- **Armazenamento em disco persistente**
- **Integração com serviços de armazenamento em nuvem** (S3, Swift)

### Sistema de Notificações
- Notificações de conclusão por email
- Webhook para integração com outros sistemas
- Logs detalhados e rastreamento de estado

## Fase 6: Recursos Adicionais (2 semanas)

### Dashboard de Monitoramento
- Interface web simples para visualizar relatórios gerados
- Estatísticas de execução e performance

### Personalização Avançada
- Temas visuais para os relatórios
- Filtros e ordenação customizáveis
- Campos personalizados

### Melhorias de Performance
- Otimização de consultas ao OpenStack
- Processamento paralelo para múltiplos projetos
- Compressão de PDFs grandes

## Melhorias na Arquitetura

### Separação em Microserviços
- **API Gateway**: Para gerenciar autenticação e rotas
- **Serviço de Relatórios**: Para geração de conteúdo
- **Serviço de Entrega**: Para distribuição de relatórios

### Observabilidade
- Implementar logging estruturado
- Métricas de performance com Prometheus
- Rastreamento distribuído com OpenTelemetry

### Segurança
- Gerenciamento seguro de credenciais (HashiCorp Vault)
- Rate limiting para evitar abusos
- Análise estática de código no CI/CD

## Próximos Passos Imediatos

1. Completar `requirements.txt` com todas as dependências necessárias
2. Implementar o arquivo `docker-compose.yaml` funcional
3. Finalizar a configuração do Celery e validar a comunicação com Redis
4. Implementar o cliente OpenStack real e testar a conexão
5. Criar um relatório HTML básico e converter para PDF

---

Este roadmap foi desenhado para permitir entregas incrementais de valor, priorizando a funcionalidade básica e depois expandindo para recursos mais avançados. Cada fase constrói sobre a anterior, mantendo a arquitetura coesa e escalável.
