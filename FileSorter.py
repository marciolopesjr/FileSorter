import os
import shutil

def mostrar_nome_script():
  """Exibe o nome do script em ASCII art."""
  print("""
  ______ _ _       _____            _            
 |  ____(_) |     / ____|          | |           
 | |__   _| | ___| (___   ___  _ __| |_ ___ _ __ 
 |  __| | | |/ _ \\___ \ / _ \| '__| __/ _ \ '__|
 | |    | | |  __/____) | (_) | |  | ||  __/ |   
 |_|    |_|_|\___|_____/ \___/|_|   \__\___|_|   
                                                 
""")

def organizar_arquivos(pasta_origem):
  """
  Organiza os arquivos em uma pasta com base em suas extensões, 
  criando pastas com nomes em letras maiúsculas.

  Args:
    pasta_origem: O caminho para a pasta que contém os arquivos a serem organizados.
  """

  for filename in os.listdir(pasta_origem):
    if os.path.isfile(os.path.join(pasta_origem, filename)):
      # Obter a extensão do arquivo
      extension = os.path.splitext(filename)[1].lower()

      # Ignorar arquivos sem extensão
      if extension:
        # Criar a pasta de destino com nome em maiúsculo se ela não existir
        pasta_destino = os.path.join(pasta_origem, extension[1:].upper())
        os.makedirs(pasta_destino, exist_ok=True)

        # Mover o arquivo para a pasta de destino
        shutil.move(os.path.join(pasta_origem, filename), os.path.join(pasta_destino, filename))

def listar_e_selecionar_pasta():
  """Lista as pastas do usuário e permite a seleção."""
  pastas_usuario = [
    nome for nome in os.listdir(os.path.expanduser("~")) 
    if os.path.isdir(os.path.join(os.path.expanduser("~"), nome))
  ]

  print("Pastas disponíveis:")
  for i, pasta in enumerate(pastas_usuario):
    print(f"{i+1}. {pasta}")

  while True:
    try:
      escolha = int(input("Selecione a pasta pelo número: "))
      if 1 <= escolha <= len(pastas_usuario):
        return os.path.join(os.path.expanduser("~"), pastas_usuario[escolha - 1])
      else:
        print("Opção inválida. Escolha um número da lista.")
    except ValueError:
      print("Entrada inválida. Digite um número.")

if __name__ == "__main__":
  mostrar_nome_script()
  pasta_origem = listar_e_selecionar_pasta()
  if pasta_origem:
    organizar_arquivos(pasta_origem)
    print("Arquivos organizados com sucesso!")
