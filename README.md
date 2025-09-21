<p align="center">
  <img src="https://raw.githubusercontent.com/marciolopesjr/FileSorter/main/FileSorter_logo.png" width="300" alt="FileSorter Logo">
</p>

<h1 align="center">FileSorter com IA</h1>

<p align="center">
  <strong>Uma ferramenta de organização de ficheiros inteligente que usa a IA do Google Gemini para criar regras de organização contextuais e granulares.</strong>
</p>

---

## Descrição

Cansado da sua pasta de "Downloads" parecer uma zona de desastre? O **FileSorter** é uma ferramenta com interface gráfica (GUI) que leva a organização de ficheiros para o próximo nível. Em vez de se basear apenas em extensões de ficheiro (`.jpg`, `.pdf`), ele utiliza o poder da IA generativa para **analisar os nomes dos seus ficheiros** e criar regras de organização inteligentes baseadas em palavras-chave e contexto.

Diga-lhe "separe faturas de relatórios de trabalho" e veja-o criar as regras por si. Ou seja vago e peça-lhe para "organizar esta confusão", e ele irá inferir categorias lógicas. No final de cada operação, é gerado um relatório HTML detalhado para que saiba exatamente o que foi alterado.

## Recursos Principais

*   🧠 **Organização Inteligente com IA:** Utiliza a API do Google Gemini para analisar nomes de ficheiros e sugerir regras de organização contextuais.
*   ✍️ **Comandos em Linguagem Natural:** Dê instruções como "separe fotos de férias e documentos de impostos" e a IA cria as regras.
*   📂 **Organização Granular:** Move ficheiros com base em palavras-chave (`fatura`, `relatorio_q3`, `ferias_2025`) e não apenas em extensões.
*   📋 **Relatórios de Auditoria:** Gera automaticamente um relatório HTML detalhado após cada organização, mostrando cada ficheiro movido e cada pasta criada.
*   🖱️ **Interface Amigável:** Uma GUI simples com suporte para arrastar e largar (Drag and Drop), barra de progresso e log de atividades em tempo real.
*   🚫 **Operação Segura:** Nunca sobrescreve ficheiros. Se um ficheiro já existir no destino, ele é renomeado de forma inteligente (ex: `documento (1).pdf`).
*   🛑 **Controlo Total:** Inclui um botão de "Cancelar" para interromper operações longas de forma segura.

## Como Usar

### Pré-requisitos

1.  **Python 3.8+:** [Instale o Python](https://www.python.org/downloads/) se ainda não o tiver. **Importante:** Durante a instalação no Windows, certifique-se que a opção "Add Python to PATH" está marcada.
2.  **Chave de API do Google Gemini:** A funcionalidade de IA requer uma chave de API.
    *   Vá para o [Google AI Studio](https://aistudio.google.com/app/apikey).
    *   Clique em "Create API key" e copie a chave gerada.

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/marciolopesjr/FileSorter.git
    cd FileSorter
    ```

2.  **Instale as dependências:**
    A aplicação utiliza algumas bibliotecas externas. Instale-as facilmente com o seguinte comando:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure a sua chave de API:**
    *   Na pasta do projeto, crie um ficheiro chamado `.env`.
    *   Abra o ficheiro `.env` e adicione a seguinte linha, substituindo com a sua chave real:
      ```
      GEMINI_API_KEY="SUA_CHAVE_DE_API_VEM_AQUI"
      ```
    *   **Nunca partilhe este ficheiro ou envie-o para um repositório público!**

### Executar a Aplicação

Com tudo instalado e configurado, execute o seguinte comando no seu terminal:
```bash
python FileSorter.py
```

## Guia Rápido de Utilização

1.  **Selecione uma Pasta:** Arraste e largue uma pasta para dentro da janela da aplicação ou use o botão "Selecionar Pasta".
2.  **Peça Sugestões à IA:** No campo "Assistente de IA", escreva o que deseja fazer (ex: "divida os meus ficheiros de trabalho e pessoais").
3.  **Gere as Regras:** Clique em "Sugerir Novas Regras". A IA irá analisar os nomes dos ficheiros na pasta e propor um conjunto de regras.
4.  **Aplique as Regras:** Uma janela de confirmação irá mostrar as regras sugeridas. Se concordar, clique em "Sim" para as salvar.
5.  **Organize!** Clique no botão "Organizar Usando Regras Atuais" para iniciar o processo.
6.  **Verifique o Relatório:** No final, será perguntado se deseja ver o relatório HTML. Ele também será guardado dentro da pasta que acabou de organizar.

## Troubleshooting

*   **A janela não abre ao executar `python FileSorter.py`:**
    *   Certifique-se de que está a executar o comando a partir de um terminal/linha de comandos, e não a dar um duplo clique no ficheiro.
    *   Tente reinstalar as dependências com `pip install -r requirements.txt`.
    *   Se o problema persistir, pode ser um problema com a sua instalação do Python/Tkinter. Tente reinstalar o Python.

*   **A funcionalidade de IA está desabilitada:**
    *   Verifique se o seu ficheiro `.env` está na pasta correta e se o nome está exatamente `.env` (e não `.env.txt`).
    *   Confirme que a sua chave de API dentro do ficheiro `.env` está correta e não contém espaços extra.

## Contribuindo

Contribuições são bem-vindas! Se encontrar um bug ou tiver uma ideia para uma nova funcionalidade, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto está licenciado sob a licença MIT. Consulte o ficheiro [LICENSE](LICENSE) para obter detalhes.