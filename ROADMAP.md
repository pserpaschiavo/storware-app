# 🚀 Roadmap: Desenvolvimento do Cliente Python para API Storware

**Autor:** Phil
**Data:** 16 de setembro de 2025
**Objetivo:** Delinear as próximas fases no desenvolvimento de um script Python robusto e modular para interagir com a API do Storware, focando primeiro na leitura de dados e depois na criação de uma arquitetura de software escalável.

---

## 🎯 Fase 1: Aprimoramento da Coleta de Dados (Leitura da API)

O foco desta fase é evoluir nosso script de uma simples prova de conceito para uma ferramenta útil de consulta de informações. Vamos extrair e apresentar os dados da API de forma clara e estruturada.

### Tarefas:

-   [ ] **Refatorar a listagem de VMs em uma função `list_vms()`:**
    -   A função deverá receber a `session` autenticada como argumento.
    -   Deverá processar a resposta JSON da API para extrair os dados de cada máquina virtual.
    -   O resultado final será uma tabela formatada no console, exibindo colunas essenciais como: `Nome da VM`, `GUID` e `Status de Proteção`.

-   [ ] **(Opcional) Adicionar biblioteca de formatação de tabelas:**
    -   Para uma saída "elegante", pesquisar e implementar a biblioteca `tabulate` ou `rich` para renderizar a tabela de VMs no terminal.

-   [ ] **Implementar a função `get_vm_details(vm_guid)`:**
    -   A função receberá a `session` e um `GUID` de uma VM como argumentos.
    -   Fará uma chamada para o endpoint `GET /virtual-machines/{guid}`.
    -   Exibirá os detalhes mais importantes da VM de forma legível.

**✅ Critério de Conclusão:** O script é capaz de listar todas as VMs de forma clara e buscar detalhes de qualquer VM específica usando seu GUID.

---

## 🏗️ Fase 2: Refatoração para Arquitetura Orientada a Objetos

Com as funcionalidades de leitura prontas, o foco agora é reestruturar nosso código. Vamos transformá-lo de um script linear para uma classe reutilizável, seguindo as melhores práticas de engenharia de software.

### Tarefas:

-   [ ] **Criar a classe `StorwareAPIClient`:**
    -   Esta classe encapsulará toda a lógica de comunicação com a API.

-   [ ] **Implementar o método construtor `__init__()`:**
    -   O construtor será responsável por todo o fluxo de autenticação:
        1.  Carregar as variáveis do `.env` e do ambiente.
        2.  Descriptografar o usuário e a senha.
        3.  Chamar o endpoint de login.
        4.  Armazenar o objeto `session` autenticado em um atributo da classe (ex: `self.session`).

-   [ ] **Migrar as funções para métodos da classe:**
    -   As funções `list_vms()` e `get_vm_details()` criadas na Fase 1 serão convertidas em métodos da classe (ex: `client.list_vms()`). Elas agora usarão `self.session` para fazer as requisições.

-   [ ] **Atualizar o bloco de execução principal (`if __name__ == "__main__":`)**
    -   O bloco principal se tornará muito mais limpo. Ele será responsável apenas por:
        1.  Instanciar o cliente: `client = StorwareAPIClient()`.
        2.  Chamar os métodos do cliente para executar as ações desejadas.

**✅ Critério de Conclusão:** Todo o código está encapsulado na classe `StorwareAPIClient`. O script principal é legível e simplesmente utiliza a classe para realizar as operações.

---

### Próximos Passos (Pós-Roadmap)

Uma vez que a Fase 2 esteja completa, teremos uma base sólida para implementar rapidamente qualquer outra funcionalidade, como:

-   Implementar ações de **escrita** (ex: `trigger_backup`, `restore_vm`).
-   Implementar o **monitoramento de tarefas** (ex: `get_task_status`).
-   Adicionar **argumentos de linha de comando** (com `argparse`) para transformar o script em uma ferramenta CLI completa.
