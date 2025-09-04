Roadmap: Aplicação de Relatórios OpenStack

Este documento descreve o plano de trabalho para o desenvolvimento da nossa aplicação, dividido em fases lógicas e incrementais. Cada fase representa um marco funcional que nos aproxima do objetivo final.
Fase 1: "Hello, Worker!" - Validação da Arquitetura Assíncrona

Objetivo: Provar que a nossa arquitetura distribuída (API -> Redis -> Worker) está funcionando. É o "smoke test" do nosso sistema, garantindo que as peças se comunicam.

Passos:

    Ativar o Código: Descomentar as linhas relevantes em app/api/routes.py e app/tasks/report_tasks.py para habilitar a chamada de tarefas Celery.

    Criar Endpoint de Teste: Implementar uma rota POST /api/tasks/test que simplesmente enfileira nossa tarefa generate_scheduled_report.delay(...) com dados de exemplo.

    Executar o Ambiente: Subir todo o stack com docker-compose up --build.

    Disparar a Tarefa: Usar uma ferramenta como curl ou Postman para enviar uma requisição ao endpoint de teste.

    Verificar os Logs: Observar os logs do contêiner do worker e confirmar que a mensagem "WORKER: Executando relatório agendado..." aparece.

Resultado Esperado: A API responde imediatamente com um "OK", e o Worker executa a tarefa em background de forma independente.
Fase 2: Conectando com o Mundo Real - Integração com OpenStack

Objetivo: Estabelecer a comunicação real com a nuvem OpenStack, abstraindo essa complexidade na nossa camada de integração.

Passos:

    Configurar Credenciais: Preencher o arquivo .env com as credenciais reais de acesso ao OpenStack.

    Implementar o Cliente: Desenvolver a lógica em app/integrations/openstack_client.py usando o openstacksdk para autenticar e criar uma função inicial, como get_server_list(project_id).

    Testar a Conexão: Criar um pequeno script de teste (ou um teste unitário) que importa nosso cliente e executa a função, garantindo que a conexão é bem-sucedida e os dados são retornados corretamente.

Resultado Esperado: Somos capazes de buscar uma lista de VMs de um projeto específico do OpenStack de forma programática.
Fase 3: A Lógica do Negócio - Orquestrando o Relatório

Objetivo: Implementar o "cérebro" da aplicação no report_generator.py, que orquestra a busca e o processamento dos dados.

Passos:

    Desenvolver o Serviço: Criar a função create_vm_inventory_report em app/services/report_generator.py. Esta função deverá:

        Receber uma lista de IDs de projetos.

        Iterar sobre a lista, chamando o openstack_client para cada projeto.

        Agregar todos os dados em uma única estrutura Python (ex: uma lista de dicionários).

    Conectar com a API: Modificar o endpoint POST /api/reports/generate para chamar este novo serviço. Inicialmente, a rota pode retornar os dados agregados como um JSON para validação.

Resultado Esperado: Ao fazer uma requisição na API com uma lista de projetos, recebemos um JSON contendo os dados de todas as VMs desses projetos.
Fase 4: Do Dado ao Documento - Geração do PDF

Objetivo: Transformar a estrutura de dados validada na fase anterior em um arquivo PDF bem formatado.

Passos:

    Criar o Template HTML: Em app/templates/, criar um arquivo vm_report.html com uma estrutura de tabela, usando a sintaxe do Jinja2 para iterar sobre os dados das VMs.

    Implementar o Exportador: Desenvolver a lógica em app/services/pdf_exporter.py que utiliza a biblioteca WeasyPrint para:

        Renderizar o template HTML com os dados.

        Converter o HTML resultante em um fluxo de bytes de PDF.

    Integrar o Fluxo Completo: Alterar o report_generator para, em vez de retornar JSON, passar os dados para o pdf_exporter e obter o PDF. A rota na API deve ser ajustada para retornar o arquivo com o Content-Type: application/pdf.

Resultado Esperado: A mesma requisição da fase anterior agora retorna um arquivo PDF para download com os dados do inventário.
Fase 5: Ativando o Agendamento e Entrega

Objetivo: Implementar a funcionalidade principal de agendamento e definir o que fazer com o relatório gerado em background.

Passos:

    Endpoint de Agendamento: Criar a rota POST /api/reports/schedule que recebe os detalhes do agendamento (projetos, frequência, etc.).

    Configurar o Agendador (Celery Beat): Adicionar a configuração do Celery Beat para que ele possa disparar tarefas em intervalos programados.

    Implementar a Lógica de Entrega: Modificar a tarefa generate_scheduled_report em app/tasks/report_tasks.py para, após gerar o PDF, realizar uma ação:

        Opção 1: Salvar o arquivo em um volume persistente.

        Opção 2: Enviar o PDF por e-mail para uma lista de destinatários.

        Opção 3: Fazer upload para um serviço de Object Storage (como o OpenStack Swift).

Resultado Esperado: Uma aplicação completa capaz de gerar relatórios sob demanda ou de forma agendada, entregando o resultado de forma útil.