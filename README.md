<img src="https://raw.githubusercontent.com/marciolopesjr/FileSorter/main/FileSorter_logo.png" width="400" height="400">

# FileSorter

## Descrição

O FileSorter é uma ferramenta com interface gráfica (GUI) que organiza automaticamente os arquivos em uma pasta com base em suas extensões. Ele permite que os usuários definam regras de organização personalizadas para agrupar diferentes tipos de arquivo em pastas específicas.

## Recursos

* **Interface Gráfica Amigável:** Fácil de usar, com botões para selecionar pastas e organizar arquivos.
* **Organização Personalizável:** Defina suas próprias regras para agrupar arquivos (por exemplo, colocar `.jpg` e `.png` na pasta "IMAGENS").
* **Regras Persistentes:** Suas regras de organização são salvas em um arquivo `config.json` e carregadas automaticamente sempre que você usa a ferramenta.
* **Criação Automática de Pastas:** As pastas de destino são criadas automaticamente se não existirem.

## Como usar

1. **Clone o repositório:** `git clone https://github.com/seu-usuario/FileSorter.git`
2. **Navegue até o diretório:** `cd FileSorter`
3. **Execute a aplicação:** `python FileSorter.py`
4. **Selecione uma Pasta:** Clique no botão "Selecionar Pasta" para escolher o diretório que você deseja organizar.
5. **Gerencie as Regras (Opcional):**
   - Clique em "Gerenciar Regras" para abrir a janela de regras.
   - Adicione, atualize ou remova regras de organização conforme necessário.
   - Clique em "Salvar e Fechar" para salvar suas alterações.
6. **Organize os Arquivos:** Clique no botão "Organizar Arquivos" para iniciar o processo. Os arquivos serão movidos para as pastas de acordo com suas regras.

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir um problema ou enviar um pull request.

## Licença

Este projeto está licenciado sob a licença MIT - consulte o arquivo [LICENSE](LICENSE) para obter detalhes.
