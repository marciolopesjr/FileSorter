<p align="center">
  <img src="https://raw.githubusercontent.com/marciolopesjr/FileSorter/main/FileSorter_logo.png" width="300" alt="FileSorter Logo">
</p>

<h1 align="center">FileSorter com IA</h1>

<p align="center">
  <strong>Uma ferramenta de organização de ficheiros inteligente que usa IA (OpenAI, Gemini, Groq, etc.) para criar regras de organização contextuais e granulares.</strong>
</p>

---

## Descrição

Cansado da sua pasta de "Downloads" parecer uma zona de desastre? O **FileSorter** é uma ferramenta com interface gráfica (GUI) que leva a organização de ficheiros para o próximo nível. Em vez de se basear apenas em extensões de ficheiro (`.jpg`, `.pdf`), ele utiliza o poder da IA generativa para **analisar os nomes dos seus ficheiros** e criar regras de organização inteligentes baseadas em palavras-chave e contexto.

Diga-lhe "separe faturas de relatórios de trabalho" e veja-o criar as regras por si. Ou seja vago e peça-lhe para "organizar esta confusão", e ele irá inferir categorias lógicas. No final de cada operação, é gerado um relatório HTML detalhado para que saiba exatamente o que foi alterado.

## Recursos Principais

*   🧠 **Organização Inteligente com IA:** Suporta múltiplos provedores (OpenAI, Gemini, Groq, LM Studio, Ollama, etc.) para analisar nomes de ficheiros e sugerir regras de organização contextuais.
*   ✍️ **Comandos em Linguagem Natural:** Dê instruções como "separe fotos de férias e documentos de impostos" e a IA cria as regras.
*   📂 **Organização Granular:** Move ficheiros com base em palavras-chave (`fatura`, `relatorio_q3`, `ferias_2025`) e não apenas em extensões.
*   📋 **Relatórios de Auditoria:** Gera automaticamente um relatório HTML detalhado após cada organização, mostrando cada ficheiro movido e cada pasta criada.
*   🖱️ **Interface Amigável:** Uma GUI simples com suporte para arrastar e largar (Drag and Drop), barra de progresso e log de atividades em tempo real.
*   🚫 **Operação Segura:** Nunca sobrescreve ficheiros. Se um ficheiro já existir no destino, ele é renomeado de forma inteligente (ex: `documento (1).pdf`).
*   🛑 **Controlo Total:** Inclui um botão de "Cancelar" para interromper operações longas de forma segura.
*   🔓 **Multi-Provedor:** Alterne entre OpenAI, Gemini, Groq, ou qualquer API compatível com OpenAI diretamente na interface.
*   ⏰ **Automação Completa:** Agende organizações periódicas, por horário específico, ou em tempo real (watch mode).
*   🚀 **Instalador Windows:** Crie um instalador profissional com Inno Setup para distribuição fácil.

## Instalação Rápida

### Opção 1: Usando o Instalador (Recomendado)

1.  Baixe o instalador mais recente em [Releases](https://github.com/marciolopesjr/FileSorter/releases)
2.  Execute `FileSorter_Setup_x.x.x.exe`
3.  Siga as instruções do instalador
4.  O FileSorter será instalado em `C:\Program Files\FileSorter`

### Opção 2: Criar Instalador a Partir do Código

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/marciolopesjr/FileSorter.git
    cd FileSorter
    ```

2.  **Execute o script de build:**
    ```bash
    build_installer.bat
    ```
    
    Este script irá:
    - Instalar dependências
    - Criar o executável com PyInstaller
    - Gerar o instalador com Inno Setup (se instalado)

3.  **O instalador será criado em:** `installer\Output\FileSorter_Setup_x.x.x.exe`

### Opção 3: Executar Direto do Código

1.  **Instale Python 3.8+:** [python.org](https://www.python.org/downloads/)

2.  **Clone e instale dependências:**
    ```bash
    git clone https://github.com/marciolopesjr/FileSorter.git
    cd FileSorter
    pip install -r requirements.txt
    ```

3.  **Execute:**
    ```bash
    python FileSorter.py
    ```

### Pré-requisitos

1.  **Python 3.8+:** [Instale o Python](https://www.python.org/downloads/) se ainda não o tiver. **Importante:** Durante a instalação no Windows, certifique-se que a opção "Add Python to PATH" está marcada.
2.  **Chave de API:** A funcionalidade de IA requer uma chave de API de um dos provedores suportados:
    *   **OpenAI:** Obtenha em [OpenAI API Keys](https://platform.openai.com/api-keys)
    *   **Google Gemini:** Obtenha em [Google AI Studio](https://aistudio.google.com/app/apikey)
    *   **Groq:** Obtenha em [Groq Console](https://console.groq.com/keys)
    *   **Outros:** Qualquer API compatível com OpenAI (LM Studio, Ollama, etc.)

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

    **Opção A - Via Interface (Recomendado):**
    *   Execute a aplicação (veja abaixo)
    *   Clique em "⚙ Configurar IA"
    *   Selecione o provedor (OpenAI, Gemini, etc.)
    *   Preencha a chave de API e outras configurações
    *   Clique em "Salvar"

    **Opção B - Via Ficheiro `.env`:**
    *   Na pasta do projeto, crie um ficheiro chamado `.env`.
    *   Abra o ficheiro `.env` e adicione as seguintes linhas:
      ```
      # Para OpenAI ou compatíveis
      OPENAI_API_KEY="SUA_CHAVE_OPENAI_AQUI"
      
      # Para Gemini (alternativo)
      GEMINI_API_KEY="SUA_CHAVE_GEMINI_AQUI"
      ```
    *   **Nunca partilhe este ficheiro ou envie-o para um repositório público!**

### Executar a Aplicação

Com tudo instalado e configurado, execute o seguinte comando no seu terminal:
```bash
python FileSorter.py
```

## Guia Rápido de Utilização

1.  **Selecione uma Pasta:** Arraste e largue uma pasta para dentro da janela da aplicação ou use o botão "Selecionar Pasta".
2.  **Configure o Provedor de IA (se necessário):** Clique em "⚙ Configurar IA" para selecionar o provedor e inserir a chave de API.
3.  **Peça Sugestões à IA:** No campo "Assistente de IA", escreva o que deseja fazer (ex: "divida os meus ficheiros de trabalho e pessoais").
4.  **Gere as Regras:** Clique em "Sugerir Novas Regras". A IA irá analisar os nomes dos ficheiros na pasta e propor um conjunto de regras.
5.  **Aplique as Regras:** Uma janela de confirmação irá mostrar as regras sugeridas. Se concordar, clique em "Sim" para as salvar.
6.  **Organize!** Clique no botão "Organizar Usando Regras Atuais" para iniciar o processo.
7.  **Verifique o Relatório:** No final, será perguntado se deseja ver o relatório HTML. Ele também será guardado dentro da pasta que acabou de organizar.

## 🕐 Automação

O FileSorter oferece três modos de automação para organizar ficheiros automaticamente:

### Modos de Automação

| Modo | Descrição | Quando Usar |
|------|-----------|-------------|
| **Por Intervalo** | Organiza pastas a cada X minutos | Para pastas com fluxo constante de ficheiros |
| **Por Horário** | Organiza em horários específicos (ex: 09:00, 18:00) | Para organização no início/fim do dia |
| **Tempo Real (Watch)** | Organiza assim que ficheiros novos são detectados | Para pastas de downloads ou recebimento automático |

### Configurar Automação

1.  Clique em **"🕐 Automação"** na janela principal
2.  **Adicione pastas monitoradas:** Clique em "Adicionar Pasta" e selecione as pastas que deseja monitorar
3.  **Selecione o modo:**
    - **Por Intervalo:** Defina o intervalo em minutos (1-1440)
    - **Por Horário:** Adicione horários no formato HH:MM
    - **Tempo Real:** Detecta ficheiros instantaneamente
4.  **Iniciar com o Windows:** Marque para iniciar automaticamente
5.  Clique em **"Iniciar Automação"**

### Exemplo: Monitorar Pasta de Downloads

1.  Abra configurações de automação
2.  Adicione `C:\Users\SeuNome\Downloads`
3.  Selecione modo "Tempo Real (Watch)"
4.  Clique em "Iniciar Automação"

Agora, sempre que um ficheiro for adicionado à pasta Downloads, ele será automaticamente organizado!

### Inicialização Automática

Para iniciar o FileSorter automaticamente com o Windows:

**Via Instalador:**
- Marque a opção "Iniciar automaticamente com o Windows" durante a instalação

**Via Interface:**
- Em "🕐 Automação", marque "Iniciar com o Windows"
- Isso cria uma tarefa no Agendador de Tarefas do Windows

**Manualmente:**
- Pressione `Win + R`, digite `shell:startup`
- Crie um atalho para `FileSorter.exe` nesta pasta

## Provedores Suportados

| Provedor | URL Base (opcional) | Modelos Exemplo |
|----------|---------------------|-----------------|
| OpenAI | (padrão) | gpt-4, gpt-3.5-turbo |
| Groq | `https://api.groq.com/openai/v1` | llama-3, mixtral-8x7b |
| LM Studio | `http://localhost:1234/v1` | Qualquer modelo local |
| Ollama | `http://localhost:11434/v1` | llama2, mistral, etc. |
| Gemini | (nativo) | gemini-pro, gemini-1.5-flash |

## Troubleshooting

*   **A janela não abre ao executar `python FileSorter.py`:**
    *   Certifique-se de que está a executar o comando a partir de um terminal/linha de comandos, e não a dar um duplo clique no ficheiro.
    *   Tente reinstalar as dependências com `pip install -r requirements.txt`.
    *   Se o problema persistir, pode ser um problema com a sua instalação do Python/Tkinter. Tente reinstalar o Python.

*   **A funcionalidade de IA está desabilitada:**
    *   Verifique se configurou corretamente a chave de API nas configurações da aplicação ou no ficheiro `.env`.
    *   Confirme que a chave de API está correta e não contém espaços extra.
    *   Para APIs locais (LM Studio, Ollama), certifique-se de que o servidor está em execução.

*   **Erro ao comunicar com a API:**
    *   Verifique sua conexão com a internet.
    *   Para APIs locais, confirme que o servidor está acessível no endereço configurado.
    *   Verifique se há créditos/saldo na sua conta do provedor.

## 📁 Estrutura do Projeto

```
FileSorter/
├── FileSorter.py          # Interface gráfica principal
├── logic.py               # Lógica de organização e IA
├── scheduler.py           # Sistema de automação e agendamento
├── config.json            # Regras de organização
├── requirements.txt       # Dependências Python
├── build.py               # Script de build PyInstaller
├── build_installer.bat    # Script de build completo (Windows)
├── .env.example           # Modelo de configuração de API
├── installer/
│   └── create_installer.iss  # Script Inno Setup
└── dist/                  # Executáveis compilados (após build)
```

## 🔨 Build e Distribuição

### Criar Executável

```bash
# Windows
build_installer.bat

# Ou manualmente
pip install -r requirements.txt
python build.py
```

### Criar Instalador

1.  Instale [Inno Setup 6](https://jrsoftware.org/isdl.php)
2.  Execute `build_installer.bat`
3.  O instalador será criado em `installer\Output\FileSorter_Setup_x.x.x.exe`

### Requisitos para Build

- Python 3.8+
- PyInstaller (`pip install pyinstaller`)
- Inno Setup 6 (opcional, para criar instalador)

## Contribuindo

Contribuições são bem-vindas! Se encontrar um bug ou tiver uma ideia para uma nova funcionalidade, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto está licenciado sob a licença MIT. Consulte o ficheiro [LICENSE](LICENSE) para obter detalhes.