import os
import shutil
import json

class FileSorterLogic:
    def __init__(self, config_path='config.json'):
        """Inicializa a lógica de ordenação e carrega as regras."""
        self.config_path = config_path
        self.rules = {}
        self.load_rules()

    def load_rules(self):
        """Carrega as regras de ordenação do arquivo de configuração."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.rules = json.load(f)
            else:
                self.rules = {} # Inicia com regras vazias se o arquivo não existir
        except (json.JSONDecodeError, IOError) as e:
            print(f"Erro ao carregar o arquivo de configuração: {e}")
            self.rules = {}

    def save_rules(self):
        """Salva as regras de ordenação atuais no arquivo de configuração."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.rules, f, indent=2)
        except IOError as e:
            print(f"Erro ao salvar o arquivo de configuração: {e}")

    def set_rules(self, rules):
        """Define regras de ordenação personalizadas."""
        self.rules = rules

    def organizar_arquivos(self, pasta_origem):
        """
        Organiza os arquivos em uma pasta com base em suas extensões,
        usando as regras carregadas.
        """
        if not os.path.isdir(pasta_origem):
            print(f"Erro: A pasta de origem '{pasta_origem}' não foi encontrada.")
            return

        for filename in os.listdir(pasta_origem):
            caminho_origem = os.path.join(pasta_origem, filename)
            if os.path.isfile(caminho_origem):
                extensao = os.path.splitext(filename)[1].lower()

                if not extensao:
                    continue

                nome_pasta_destino = self.get_pasta_destino(extensao)

                caminho_pasta_destino = os.path.join(pasta_origem, nome_pasta_destino)
                os.makedirs(caminho_pasta_destino, exist_ok=True)

                shutil.move(caminho_origem, os.path.join(caminho_pasta_destino, filename))

    def get_pasta_destino(self, extensao):
        """Determina a pasta de destino para uma dada extensão."""
        ext_sem_ponto = extensao[1:]

        for pasta, extensoes in self.rules.items():
            if ext_sem_ponto in extensoes:
                return pasta

        return ext_sem_ponto.upper()
