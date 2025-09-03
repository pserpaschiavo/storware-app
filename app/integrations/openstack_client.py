# app/integrations/openstack_client.py
# import openstack

class OpenStackClient:
    def __init__(self, cloud_config):
        """
        Inicializa o cliente OpenStack usando a configuração da nuvem.
        """
        # try:
        #     self.conn = openstack.connect(cloud=cloud_config)
        #     print("Conexão com OpenStack estabelecida com sucesso.")
        # except Exception as e:
        #     print(f"Erro ao conectar com OpenStack: {e}")
        #     self.conn = None
        pass

    def get_servers_from_project(self, project_id: str) -> list:
        """
        Busca todas as instâncias (servidores) de um determinado projeto.
        """
        # if not self.conn:
        #     return []
        # servers = self.conn.compute.servers(project_id=project_id)
        # return list(servers)
        print(f"Simulando busca de VMs para o projeto {project_id}")
        return [
            {"id": "uuid-vm-1", "name": "vm-teste-01", "status": "ACTIVE"},
            {"id": "uuid-vm-2", "name": "vm-teste-02", "status": "SHUTOFF"},
        ]


# Exemplo de como seria instanciado com a configuração do ambiente
# openstack_client = OpenStackClient(cloud_config="my_cloud")
