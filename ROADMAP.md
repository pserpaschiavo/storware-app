# 🚀 Roadmap: Desenvolvimento do Cliente Python para API Storware
**Objetivo:** Desenvolver um cliente de linha de comando (CLI) completo para consulta, monitoramento e exportação de dados da API do Storware.

---

## ✅ Fases Anteriores (Concluídas)

Nosso trabalho até agora resultou em uma ferramenta CLI funcional e profissional. As seguintes fases foram concluídas com sucesso:

* **Fase 1: Coleta de Dados de Inventário:** Implementamos a listagem, filtragem (`--head`, `--tail`, `--filter-name`) e detalhamento de VMs (`--get-details`).
* **Fase 2: Refatoração para Arquitetura Profissional:** O código foi reestruturado em uma classe `StorwareAPIClient`, tornando-o modular e escalável.
* **Fase 3: Monitoramento de Tarefas:** Adicionamos a capacidade de listar e filtrar tarefas (`--list-tasks`, `--filter-task-status`, `--filter-by-vm-guid`).
* **Fase 4: Relatórios de Volumetria:** Implementamos o relatório de tamanho de backup (`--volumetrics`) com filtros de data e a consulta de histórico de backups (`--backup-history`).

---

## 🎯 Fase 5: Expansão da Coleta de Dados e Melhorias de Usabilidade (A Fazer)

O foco desta fase é enriquecer ainda mais nossa capacidade de extrair dados da API e melhorar a forma como interagimos e utilizamos a saída do script.

### Tarefas:

-   [ ] **Listar Agendamentos (Schedules):**
    -   Implementar o método `list_schedules()` na classe (`GET /schedules`).
    -   Criar o comando `--list-schedules` na CLI.
    -   Exibir os schedules em uma tabela, mostrando `Nome`, `Status (Ativo/Inativo)`, `Tipo de Backup` e `GUID`.

-   [ ] **Listar Destinos de Backup (Backup Destinations):**
    -   Investigar e encontrar o endpoint correto para listar os destinos de backup.
    -   Implementar o método `list_backup_destinations()` na classe.
    * Criar o comando `--list-destinations` na CLI.
    -   Exibir os destinos em uma tabela, mostrando `Nome`, `Tipo` e `GUID`.

-   [ ] **Detalhar Tarefa ou Backup Específico:**
    -   Adicionar o comando `--get-task-details <GUID>` para buscar e exibir o JSON completo de uma tarefa (`GET /tasks/{guid}`).
    -   Adicionar o comando `--get-backup-details <GUID>` para buscar e exibir o JSON completo de um backup (`GET /backups/{guid}`).

-   [ ] **Exportar Saída para Arquivo (CSV/JSON):**
    -   Adicionar um argumento global, como `--output [csv|json] <NOME_ARQUIVO>`.
    -   Modificar a lógica de exibição para, em vez de imprimir a tabela no console, salvar os dados no arquivo especificado no formato escolhido.

-   [ ] **Agrupar e Sumarizar Resultados (Requisitos a Definir):**
    -   Adicionar um argumento global, como `--group-by [CAMPO]`, que modifica a saída das listagens para um formato de resumo.
    -   *Exemplo 1:* `--list-vms --group-by protectionStatus` para mostrar a contagem de VMs por status.
    -   *Exemplo 2:* `--volumetrics --group-by policy` para mostrar a volumetria total por política de backup.
    -   *(Nota: Os campos exatos para agrupamento e o formato da saída serão definidos posteriormente, conforme a necessidade da equipe).*

**✅ Critério de Conclusão:** A ferramenta é capaz de consultar os principais objetos de configuração (Schedules, Destinations) e exportar qualquer