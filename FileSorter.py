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

from logic import FileSorterLogic, GeminiRuleSuggester

def get_config_path() -> Path:
    app_config_dir = Path(user_config_dir("FileSorter", "CurmudgeonApps"))
    return app_config_dir / "config.json"

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
        self.gemini_suggester = None
        self.ai_available = False
        try:
            self.gemini_suggester = GeminiRuleSuggester()
            self.ai_available = True
        except ValueError as e:
            # Não podemos usar messagebox aqui porque a janela pode não estar pronta
            # Escrevemos para o terminal se algo falhar na inicialização
            print(f"[AVISO] Configuração da IA falhou: {e}. A funcionalidade de IA estará desabilitada.")
            self.ai_error_message = str(e) # Guarda a mensagem para mostrar depois
        else:
            self.ai_error_message = None

        self.selected_folder = tk.StringVar(value="Arraste e largue uma pasta aqui ou selecione")
        self.queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.thread = None

        self.master.drop_target_register(DND_FILES)
        self.master.dnd_bind('<<Drop>>', self.on_drop)
        
        self._build_ui()

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
        rules = self.gemini_suggester.suggest_rules(folder, user_request)
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