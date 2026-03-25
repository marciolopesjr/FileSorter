# Guia Rápido - FileSorter com Automação

## 🚀 Início Rápido

### 1. Configurar API
- Clique em "⚙ Configurar IA"
- Escolha o provedor (OpenAI, Gemini, Groq, etc.)
- Insira sua chave de API
- Clique em "Salvar"

### 2. Obter Regras da IA
- Arraste uma pasta para a FileSorter
- Digite: "organize esta confusão"
- Clique em "Sugerir Novas Regras"
- Aceite as regras sugeridas

### 3. Organizar Manualmente
- Clique em "Organizar Usando Regras Atuais"

### 4. Configurar Automação
- Clique em "🕐 Automação"
- Adicione pastas para monitorar
- Escolha o modo (Intervalo, Horário, ou Tempo Real)
- Clique em "Iniciar Automação"

## 📌 Modos de Automação

| Modo | Uso |
|------|-----|
| **Por Intervalo** | A cada X minutos (ideal para pastas com fluxo constante) |
| **Por Horário** | Em horários específicos (ex: 09:00, 18:00) |
| **Tempo Real** | Detecta ficheiros instantaneamente (watch mode) |

## 🔧 Comandos Úteis

### Executar do código
```bash
python FileSorter.py
```

### Criar executável
```bash
python build.py
```

### Criar instalador completo
```bash
build_installer.bat
```

## 📁 Pastas de Configuração

- **Configurações da IA:** `%APPDATA%\FileSorter\ai_config.json`
- **Configurações do Scheduler:** `%APPDATA%\FileSorter\scheduler_config.json`
- **Regras:** `config.json` (na pasta da aplicação)
- **Logs:** `%LOCALAPPDATA%\FileSorter\logs\`

## ⚠️ Problemas Comuns

### IA não funciona
- Verifique se a chave de API está correta
- Para APIs locais (Ollama, LM Studio), verifique se o servidor está ativo

### Automação não inicia
- Verifique se as pastas monitoradas existem
- Reinicie a aplicação

### Erro na organização
- Verifique o log de atividades na aplicação
- Consulte `%LOCALAPPDATA%\FileSorter\logs\file_sorter.log`

## 📞 Suporte

- Documentação completa: `README.md`
- Issues: https://github.com/marciolopesjr/FileSorter/issues
