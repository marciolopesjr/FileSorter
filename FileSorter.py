# Ficheiro: FileSorter.py

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import os
import threading
import queue
import logging
import json
import webbrowser
from pathlib import Path
from tkinterdnd2 import DND_FILES, TkinterDnD
from platformdirs import user_config_dir, user_log_dir

from logic import FileSorterLogic, create_ai_suggester, load_ai_config
from scheduler import FileSorterScheduler, register_startup_task, unregister_startup_task

def get_config_path() -> Path:
    app_config_dir = Path(user_config_dir("FileSorter", "CurmudgeonApps"))
    return app_config_dir / "config.json"

def get_ai_config_path() -> Path:
    app_config_dir = Path(user_config_dir("FileSorter", "CurmudgeonApps"))
    return app_config_dir / "ai_config.json"

def get_scheduler_config_path() -> Path:
    app_config_dir = Path(user_config_dir("FileSorter", "CurmudgeonApps"))
    return app_config_dir / "scheduler_config.json"

def setup_logging():
    log_dir = Path(user_log_dir("FileSorter", "CurmudgeonApps"))
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "file_sorter.log"
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler(log_file)]
    )

class FileSorterGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("FileSorter com IA e Relatórios")
        self.master.geometry("800x650")

        self.logic = FileSorterLogic(config_path=get_config_path())

        # Carregar configuração da IA
        self.ai_config_path = get_ai_config_path()
        self.ai_provider, self.ai_config = load_ai_config(self.ai_config_path)

        # Inicializar scheduler
        self.scheduler_config_path = get_scheduler_config_path()
        self.scheduler = FileSorterScheduler(self.config_path)
        self.scheduler.set_log_callback(self._update_log)
        self.scheduler.set_status_callback(self.status_label.config)

        self.ai_suggester = None
        self.ai_available = False
        self.ai_error_message = None

        self._initialize_ai()

        self.selected_folder = tk.StringVar(value="Arraste e largue uma pasta aqui ou selecione")
        self.queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.thread = None

        self.master.drop_target_register(DND_FILES)
        self.master.dnd_bind('<<Drop>>', self.on_drop)

        self._build_ui()

        # Mostrar mensagem de erro após a UI estar pronta
        if self.ai_error_message and not self.ai_available:
            self.master.after(100, lambda: messagebox.showwarning("Configuração da IA", f"{self.ai_error_message}\n\nA funcionalidade de IA estará desabilitada até que configure um provedor."))
        
        # Verificar se deve iniciar automação automaticamente
        self.master.after(500, self._check_auto_start)

    def _check_auto_start(self):
        """Verifica se deve iniciar automação automaticamente."""
        if self.scheduler.is_enabled():
            self.scheduler.start()
            self._update_log("Automação iniciada automaticamente")

    def _initialize_ai(self):
        """Inicializa o suggestor de IA baseado na configuração."""
        try:
            self.ai_suggester = create_ai_suggester(self.ai_provider, self.ai_config)
            if self.ai_suggester:
                self.ai_available = True
        except ValueError as e:
            print(f"[AVISO] Configuração da IA falhou: {e}. A funcionalidade de IA estará desabilitada.")
            self.ai_error_message = str(e)

    def _build_ui(self):
        """Constrói todos os widgets da interface gráfica."""
        main_frame = tk.Frame(self.master, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)
        self.select_button = tk.Button(top_frame, text="Selecionar Pasta", command=self.select_folder)
        self.select_button.pack(side=tk.LEFT, padx=(0, 10))
        folder_label = tk.Label(top_frame, textvariable=self.selected_folder, relief=tk.GROOVE, bd=2)
        folder_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.rules_button = tk.Button(top_frame, text="Gerenciar Regras", command=self.open_rules_window, state='disabled')
        self.rules_button.pack(side=tk.RIGHT, padx=(10, 0))
        self.automation_button = tk.Button(top_frame, text="🕐 Automação", command=self.open_automation_settings)
        self.automation_button.pack(side=tk.RIGHT, padx=(10, 0))
        self.settings_button = tk.Button(top_frame, text="⚙ Configurar IA", command=self.open_ai_settings)
        self.settings_button.pack(side=tk.RIGHT, padx=(0, 10))

        # Frame de seleção de provedor
        provider_frame = tk.Frame(main_frame)
        provider_frame.pack(fill=tk.X, pady=5)
        tk.Label(provider_frame, text="Provedor de IA:").pack(side=tk.LEFT, padx=(0, 10))
        self.provider_var = tk.StringVar(value=self.ai_provider)
        self.provider_combo = ttk.Combobox(provider_frame, textvariable=self.provider_var, values=["openai", "gemini"], state="readonly", width=20)
        self.provider_combo.pack(side=tk.LEFT)
        self.provider_combo.bind('<<ComboboxSelected>>', self.on_provider_changed)

        ai_frame = tk.LabelFrame(main_frame, text="Assistente de IA", padx=10, pady=10)
        ai_frame.pack(fill=tk.X, pady=10)
        self.ai_prompt_entry = tk.Entry(ai_frame, font=("Arial", 10))
        self.ai_prompt_entry.insert(0, "Ex: organize esta confusão")
        self.ai_prompt_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.ask_ai_button = tk.Button(ai_frame, text="Sugerir Novas Regras", command=self.start_ai_suggestion_thread)
        self.ask_ai_button.pack(side=tk.LEFT)
        if not self.ai_available:
            self.ask_ai_button.config(state='disabled')
            self.ai_prompt_entry.config(state='disabled')
            
        action_frame = tk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=5)
        self.organize_button = tk.Button(action_frame, text="Organizar Usando Regras Atuais", command=self.start_organization_thread, height=2)
        self.organize_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.cancel_button = tk.Button(action_frame, text="Cancelar", command=self.cancel_organization, height=2, state='disabled')
        self.cancel_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        progress_frame = tk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=100, mode="determinate")
        self.progress_bar.pack(fill=tk.X, expand=True)
        log_frame = tk.LabelFrame(main_frame, text="Log de Atividades")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state='disabled', bg='#f0f0f0')
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_label = tk.Label(self.master, text="Pronto", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        if self.ai_error_message:
            self.master.after(100, lambda: messagebox.showwarning("Configuração da IA", f"{self.ai_error_message}\nA funcionalidade de IA está desabilitada."))

    def on_drop(self, event):
        path = event.data.strip('{}')
        if os.path.isdir(path):
            self.selected_folder.set(path)
        else:
            messagebox.showwarning("Seleção Inválida", "Por favor, arraste e largue uma pasta, não um ficheiro.")

    def open_rules_window(self):
        messagebox.showinfo("Indisponível", "A gestão manual de regras de IA não é suportada. Use o assistente para gerar um novo conjunto de regras.")

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.selected_folder.set(folder_path)

    def start_organization_thread(self):
        folder = self.selected_folder.get()
        if not os.path.isdir(folder):
            messagebox.showerror("Erro", "Por favor, selecione ou arraste uma pasta válida primeiro.")
            return
        self.cancel_event.clear()
        self.toggle_ui_state(is_running=True)
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state='disabled')
        self.thread = threading.Thread(target=self.run_organization, args=(folder, self.cancel_event))
        self.thread.start()
        self.master.after(100, self.process_queue)

    def run_organization(self, folder, cancel_event):
        report_data = {}
        try:
            generator = self.logic.organize_files(folder, cancel_event)
            while True:
                try:
                    msg_type, msg_data = next(generator)
                    self.queue.put((msg_type, msg_data))
                except StopIteration as e:
                    report_data = e.value
                    break
            
            if report_data:
                report_path = self.logic.generate_html_report(report_data)
                if report_path:
                    self.queue.put(("report_generated", report_path))

        except Exception as e:
            logging.error(f"Erro inesperado na thread de organização: {e}")
            self.queue.put(("error", f"Ocorreu um erro fatal: {e}"))

    def start_ai_suggestion_thread(self):
        folder = self.selected_folder.get()
        user_request = self.ai_prompt_entry.get()
        if not os.path.isdir(folder):
            messagebox.showerror("Erro", "Selecione uma pasta para a IA analisar.")
            return
        if not user_request or "Ex:" in user_request:
            messagebox.showerror("Erro", "Escreva um pedido claro para a IA.")
            return
        self.status_label.config(text="Consultando a IA, por favor aguarde...")
        self.toggle_ui_state(is_running=True)
        self.thread = threading.Thread(target=self.run_ai_suggestion, args=(folder, user_request))
        self.thread.start()
        self.master.after(100, self.process_queue)

    def run_ai_suggestion(self, folder, user_request):
        rules = self.ai_suggester.suggest_rules(folder, user_request)
        self.queue.put(("ai_suggestion_result", rules))

    def cancel_organization(self):
        self.status_label.config(text="Cancelando...")
        self.cancel_event.set()
        self.cancel_button.config(state='disabled')

    def handle_ai_result(self, rules):
        if rules is None:
            messagebox.showerror("Erro da IA", "A IA não conseguiu gerar regras. Verifique o ficheiro de log para detalhes.")
            return
        if not rules:
            messagebox.showinfo("IA", "A IA não encontrou ficheiros ou não sugeriu nenhuma regra.")
            return
        rules_str = json.dumps(rules, indent=2, ensure_ascii=False)
        apply = messagebox.askyesno("Sugestão da IA", f"A IA sugeriu as seguintes regras:\n\n{rules_str}\n\nDeseja aplicá-las? (Isto irá sobrescrever as regras atuais)")
        if apply:
            self.logic.set_rules(rules)
            self.logic.save_rules()
            self.status_label.config(text="Regras da IA aplicadas e salvas!")
            self._update_log("Novas regras de IA baseadas em palavras-chave foram salvas.")

    def open_ai_settings(self):
        """Abre a janela de configurações da IA."""
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Configurar Provedor de IA")
        settings_window.geometry("500x400")
        settings_window.resizable(False, False)
        
        # Tornar modal
        settings_window.transient(self.master)
        settings_window.grab_set()
        
        frame = tk.Frame(settings_window, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Seleção de provedor
        provider_frame = tk.Frame(frame)
        provider_frame.pack(fill=tk.X, pady=10)
        tk.Label(provider_frame, text="Provedor:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        provider_var = tk.StringVar(value=self.ai_provider)
        provider_combo = ttk.Combobox(provider_frame, textvariable=provider_var, values=["openai", "gemini"], state="readonly", width=30)
        provider_combo.pack(fill=tk.X, pady=5)
        
        # Configurações OpenAI
        openai_frame = tk.LabelFrame(frame, text="Configurações OpenAI / Compatível")
        openai_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(openai_frame, text="Chave de API:").pack(anchor=tk.W)
        api_key_entry = tk.Entry(openai_frame, width=50, show="*")
        api_key_entry.pack(fill=tk.X, pady=5)
        api_key_entry.insert(0, self.ai_config.get("api_key", "") if self.ai_provider == "openai" else "")
        
        tk.Label(openai_frame, text="Base URL (opcional):").pack(anchor=tk.W)
        base_url_entry = tk.Entry(openai_frame, width=50)
        base_url_entry.pack(fill=tk.X, pady=5)
        base_url_entry.insert(0, self.ai_config.get("base_url", "") if self.ai_provider == "openai" else "")
        tk.Label(openai_frame, text="Ex: https://api.groq.com/openai/v1 ou https://localhost:1234/v1", font=("Arial", 8), fg="gray").pack(anchor=tk.W)
        
        tk.Label(openai_frame, text="Modelo:").pack(anchor=tk.W)
        model_entry = tk.Entry(openai_frame, width=50)
        model_entry.pack(fill=tk.X, pady=5)
        model_entry.insert(0, self.ai_config.get("model", "gpt-3.5-turbo") if self.ai_provider == "openai" else "gpt-3.5-turbo")
        tk.Label(openai_frame, text="Ex: gpt-4, llama-3, mixtral-8x7b", font=("Arial", 8), fg="gray").pack(anchor=tk.W)
        
        # Instruções
        info_label = tk.Label(frame, text="Para Gemini: deixe a chave vazia e certifique-se de ter GEMINI_API_KEY no .env", font=("Arial", 9), fg="blue", wraplength=450, justify=tk.LEFT)
        info_label.pack(fill=tk.X, pady=10)
        
        def save_settings():
            provider = provider_var.get()
            config = {
                "provider": provider,
                "openai": {
                    "api_key": api_key_entry.get(),
                    "base_url": base_url_entry.get() if base_url_entry.get() else None,
                    "model": model_entry.get()
                },
                "gemini": {}
            }
            self._save_ai_config(config)
            settings_window.destroy()
            messagebox.showinfo("Sucesso", "Configurações salvas! Reinicie a aplicação para aplicar as mudanças.")
        
        # Botões
        button_frame = tk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        tk.Button(button_frame, text="Cancelar", command=settings_window.destroy).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Salvar", command=save_settings, bg="#4CAF50", fg="white").pack(side=tk.RIGHT, padx=5)

    def _save_ai_config(self, config: dict):
        """Guarda as configurações da IA no ficheiro de configuração."""
        try:
            self.ai_config_path.parent.mkdir(parents=True, exist_ok=True)
            with self.ai_config_path.open('w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except IOError as e:
            logging.error(f"Erro ao salvar configuração da IA: {e}")
            messagebox.showerror("Erro", f"Não foi possível salvar as configurações: {e}")

    def on_provider_changed(self, event):
        """Atualiza o suggester quando o provedor é alterado."""
        new_provider = self.provider_var.get()
        # Recarregar configurações
        self.ai_provider = new_provider
        self.ai_config = load_ai_config(self.ai_config_path)[1]
        self._initialize_ai()

        if self.ai_available:
            self.ask_ai_button.config(state='normal')
            self.ai_prompt_entry.config(state='normal')
            self.status_label.config(text=f"Provedor alterado para {new_provider}")
        else:
            self.ask_ai_button.config(state='disabled')
            self.ai_prompt_entry.config(state='disabled')
            self.status_label.config(text=f"Provedor {new_provider} requer configuração")

    def open_automation_settings(self):
        """Abre a janela de configurações de automação."""
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Configurar Automação")
        settings_window.geometry("600x500")
        settings_window.resizable(False, False)
        
        settings_window.transient(self.master)
        settings_window.grab_set()
        
        frame = tk.Frame(settings_window, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(frame, text="Configuração de Automação", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Status atual
        scheduler_config = self.scheduler.get_config()
        is_running = self.scheduler.is_running
        
        status_frame = tk.LabelFrame(frame, text="Status")
        status_frame.pack(fill=tk.X, pady=10)
        
        status_text = "Ativo" if is_running else "Parado"
        status_color = "green" if is_running else "red"
        tk.Label(status_frame, text=f"Status: {status_text}", font=("Arial", 10, "bold"), fg=status_color).pack(anchor=tk.W, pady=5)
        tk.Label(status_frame, text=f"Modo: {scheduler_config.get('mode', 'interval')}", wraplength=500).pack(anchor=tk.W, pady=5)
        
        # Botões de controlo
        control_frame = tk.Frame(status_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        def start_scheduler():
            mode = mode_var.get()
            self.scheduler.update_config({"enabled": True})
            self.scheduler.start(mode)
            status_label.config(text="Status: Ativo", fg="green")
            start_btn.config(state='disabled')
            stop_btn.config(state='normal')
        
        def stop_scheduler():
            self.scheduler.stop()
            self.scheduler.update_config({"enabled": False})
            status_label.config(text="Status: Parado", fg="red")
            start_btn.config(state='normal')
            stop_btn.config(state='disabled')
        
        tk.Label(status_frame, text="Ações:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)
        mode_var = tk.StringVar(value=scheduler_config.get('mode', 'interval'))
        mode_frame = tk.Frame(status_frame)
        mode_frame.pack(fill=tk.X, pady=5)
        
        tk.Radiobutton(mode_frame, text="Por Intervalo", variable=mode_var, value="interval").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(mode_frame, text="Por Horário", variable=mode_var, value="schedule").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(mode_frame, text="Tempo Real (Watch)", variable=mode_var, value="watch").pack(side=tk.LEFT, padx=10)
        
        btn_frame = tk.Frame(status_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        start_btn = tk.Button(btn_frame, text="Iniciar Automação", command=start_scheduler, bg="#4CAF50", fg="white")
        start_btn.pack(side=tk.LEFT, padx=5)
        stop_btn = tk.Button(btn_frame, text="Parar Automação", command=stop_scheduler, bg="#f44336", fg="white")
        stop_btn.pack(side=tk.LEFT, padx=5)
        
        if is_running:
            start_btn.config(state='disabled')
            stop_btn.config(state='normal')
        else:
            start_btn.config(state='normal')
            stop_btn.config(state='disabled')
        
        status_label = tk.Label(status_frame, text=f"Status: {status_text}", fg=status_color)
        status_label.pack(anchor=tk.W, pady=5)
        
        # Pastas monitoradas
        folders_frame = tk.LabelFrame(frame, text="Pastas Monitoradas")
        folders_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Lista de pastas
        list_frame = tk.Frame(folders_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        folders_listbox = tk.Listbox(list_frame, height=8, yscrollcommand=scrollbar.set)
        folders_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=folders_listbox.yview)
        
        for folder in scheduler_config.get('watched_folders', []):
            folders_listbox.insert(tk.END, folder)
        
        def add_folder():
            folder = filedialog.askdirectory()
            if folder and folder not in scheduler_config.get('watched_folders', []):
                self.scheduler.add_watched_folder(folder)
                folders_listbox.insert(tk.END, folder)
        
        def remove_folder():
            selection = folders_listbox.curselection()
            if selection:
                folder = folders_listbox.get(selection[0])
                self.scheduler.remove_watched_folder(folder)
                folders_listbox.delete(selection)
        
        folders_btn_frame = tk.Frame(folders_frame)
        folders_btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(folders_btn_frame, text="Adicionar Pasta", command=add_folder).pack(side=tk.LEFT, padx=5)
        tk.Button(folders_btn_frame, text="Remover Selecionada", command=remove_folder).pack(side=tk.LEFT, padx=5)
        
        # Configurações de intervalo
        interval_frame = tk.LabelFrame(frame, text="Configurações de Intervalo (minutos)")
        interval_frame.pack(fill=tk.X, pady=10)
        
        interval_var = tk.IntVar(value=scheduler_config.get('interval_minutes', 30))
        interval_spinbox = tk.Spinbox(interval_frame, from_=1, to=1440, textvariable=interval_var, width=10)
        interval_spinbox.pack(pady=5)
        
        # Inicialização com Windows
        startup_frame = tk.LabelFrame(frame, text="Inicialização")
        startup_frame.pack(fill=tk.X, pady=10)
        
        startup_var = tk.BooleanVar(value=scheduler_config.get('run_on_startup', False))
        tk.Checkbutton(startup_frame, text="Iniciar com o Windows", variable=startup_var).pack(anchor=tk.W, pady=5)
        
        def save_and_close():
            # Atualizar configurações
            self.scheduler.update_config({
                "interval_minutes": interval_var.get(),
                "run_on_startup": startup_var.get()
            })
            
            # Registrar/remover tarefa de inicialização
            if startup_var.get():
                success, msg = register_startup_task()
                if success:
                    messagebox.showinfo("Sucesso", msg)
                else:
                    messagebox.showerror("Erro", msg)
            else:
                unregister_startup_task()
            
            settings_window.destroy()
        
        # Botões
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=10)
        tk.Button(btn_frame, text="Cancelar", command=settings_window.destroy).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="Salvar", command=save_and_close, bg="#4CAF50", fg="white").pack(side=tk.RIGHT, padx=5)

    def process_queue(self):
        try:
            while not self.queue.empty():
                msg_type, msg_data = self.queue.get_nowait()
                
                if msg_type == "ai_suggestion_result": self.handle_ai_result(msg_data); self.toggle_ui_state(is_running=False); return
                elif msg_type == "total_files": self.progress_bar['maximum'] = int(msg_data); self.status_label.config(text=f"Encontrados {msg_data} ficheiros...")
                elif msg_type == "progress": self.progress_bar['value'] = int(msg_data)
                elif msg_type == "log": self._update_log(msg_data)
                elif msg_type == "error": self.status_label.config(text=f"Erro: {msg_data}"); messagebox.showerror("Erro", msg_data)
                elif msg_type == "cancelled": self._update_log(msg_data); self.status_label.config(text="Operação cancelada."); self.toggle_ui_state(is_running=False); return
                elif msg_type == "done": self.status_label.config(text=msg_data)
                elif msg_type == "report_generated":
                    self.toggle_ui_state(is_running=False)
                    if messagebox.askyesno("Relatório Concluído", f"Relatório salvo em:\n{msg_data}\n\nDeseja abri-lo agora no seu browser?"):
                        try: webbrowser.open(Path(msg_data).as_uri())
                        except Exception as e: messagebox.showerror("Erro", f"Não foi possível abrir o relatório: {e}")
                    return

            if self.thread and self.thread.is_alive(): self.master.after(100, self.process_queue)
            else: self.toggle_ui_state(is_running=False)
        except queue.Empty:
            if self.thread and self.thread.is_alive(): self.master.after(100, self.process_queue)
            else: self.toggle_ui_state(is_running=False)

    def _update_log(self, message: str):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        
    def toggle_ui_state(self, is_running: bool):
        state = 'disabled' if is_running else 'normal'
        self.organize_button.config(state=state)
        self.select_button.config(state=state)
        if self.ai_available: self.ask_ai_button.config(state=state)
        self.cancel_button.config(state='normal' if is_running else 'disabled')

def main():
    setup_logging()
    
    try:
        root = TkinterDnD.Tk() 
        app = FileSorterGUI(root)
        
        # --- A MUDANÇA CRÍTICA ---
        # Força o Tkinter a processar todos os eventos pendentes e a desenhar a janela
        # antes de entrar no loop principal.
        root.update()
        root.deiconify() # Garante que a janela não está escondida/iconificada

        root.mainloop()
    except Exception as e:
        # Se algo falhar, mesmo com a nossa tentativa, mostramos um erro claro.
        print(f"ERRO FATAL DURANTE A INICIALIZAÇÃO DA GUI: {e}")
        logging.critical(f"ERRO FATAL DURANTE A INICIALIZAÇÃO DA GUI: {e}", exc_info=True)
        messagebox.showerror("Erro Crítico", f"Não foi possível iniciar a aplicação.\n\nVerifique o ficheiro 'file_sorter.log' para detalhes.\n\nErro: {e}")


if __name__ == "__main__":
    main()