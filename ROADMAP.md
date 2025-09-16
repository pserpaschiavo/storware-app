# 🚀 Roadmap: Desenvolvimento do Cliente Python para API Storware

**Autor:** Phil
**Data:** 16 de setembro de 2025
**Objetivo:** Desenvolver um cliente de linha de comando (CLI) em Python para consultar informações e monitorar o status de tarefas na API do Storware.

---

## ✅ Fase 1: Coleta de Dados de Inventário (Concluído)

O foco desta fase foi transformar o script em uma ferramenta útil de consulta de inventário, com funcionalidades de filtragem e busca.

### Tarefas Concluídas:

-   [x] **Implementada a função `list_vms()`** para listar todas as máquinas virtuais.
-   [x] **Adicionada a biblioteca `tabulate`** para exibição elegante dos dados em tabela.
-   [x] **Implementada a interface de linha de comando (CLI) com `argparse`**.
-   [x] **Adicionados os argumentos `--head`, `--tail` e `--filter-name`** para manipulação da lista.
-   [x] **Implementada a função `get_vm_details()`** e o argumento `--get-details` para inspecionar uma VM específica.

---

## ✅ Fase 2: Refatoração para Arquitetura Profissional (Concluído)

Nesta fase, reestruturamos o código para uma arquitetura orientada a objetos, tornando-o limpo, reutilizável e escalável.

### Tarefas Concluídas:

-   [x] **Criada a classe `StorwareAPIClient`** para encapsular toda a lógica da API.
-   [x] **Implementado o método construtor `__init__()`** que gerencia todo o fluxo de autenticação.
-   [x] **Migradas as funções (`list_vms`, `get_vm_details`)** para métodos da classe.
-   [x] **Simplificado o bloco de execução principal** para apenas instanciar e usar o cliente.

---

## 🎯 Fase 3: Monitoramento de Tarefas (Em Andamento)

O foco desta fase é adicionar a capacidade de visualizar e filtrar as tarefas (como backups, restores, etc.) que estão sendo executadas pelo Storware. Esta é uma funcionalidade "read-only" que não requer permissões elevadas.

### Tarefas:

-   [ ] **Implementar o método `list_tasks()` na classe:**
    -   O método fará uma chamada `GET` para o endpoint `/tasks`.
    -   Permitirá a passagem de filtros como parâmetros opcionais, que serão convertidos em "query parameters" na URL (ex: `?state=RUNNING`).

-   [ ] **Adicionar novos comandos à CLI para tarefas:**
    -   Criar o comando principal `--list-tasks` para exibir todas as tarefas recentes.
    -   Adicionar argumentos de filtro, como:
        -   `--filter-task-status [QUEUED|RUNNING|FINISHED|FAILED|CANCELLED]`
        -   `--filter-task-type [EXPORT|STORE|RESTORE|...]`
        -   `--filter-by-vm-guid [GUID]` (para ver todas as tarefas de uma VM específica)

-   [ ] **Exibir a lista de tarefas em uma tabela formatada:**
    -   A tabela mostrará informações cruciais como `Tipo da Tarefa`, `Status`, `VM Alvo (se aplicável)`, `Progresso %` e `GUID da Tarefa`.

**✅ Critério de Conclusão:** O script é capaz de listar e filtrar as tarefas em andamento ou concluídas, fornecendo uma visão clara do que o Storware está fazendo.

---

### Próximos Passos (Pós-Roadmap)

Se no futuro suas permissões forem expandidas, a base que estamos construindo nos permitirá implementar rapidamente:

-   **Ações de escrita:** `trigger_backup`, `restore_vm`, etc.
-   **Gerenciamento de políticas e schedules**.