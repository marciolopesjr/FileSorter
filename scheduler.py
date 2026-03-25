# Ficheiro: scheduler.py

import json
import logging
import os
import sys
import time
import threading
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from threading import Event, Thread
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent
from platformdirs import user_config_dir, user_log_dir

from logic import FileSorterLogic, create_ai_suggester, load_ai_config


class AutoOrganizationHandler(FileSystemEventHandler):
    """Manipula eventos de sistema de ficheiros para organização automática."""
    
    def __init__(self, organizer_callback: Callable, extensions_filter: Optional[List[str]] = None):
        super().__init__()
        self.organizer_callback = organizer_callback
        self.extensions_filter = extensions_filter
        self._debounce_timer: Optional[threading.Timer] = None
        self._pending_files: set = set()
        self._debounce_seconds = 2
    
    def _should_process_file(self, file_path: str) -> bool:
        """Verifica se o ficheiro deve ser processado baseado na extensão."""
        if not self.extensions_filter:
            return True
        ext = Path(file_path).suffix.lower().lstrip('.')
        return ext in self.extensions_filter
    
    def _trigger_organization(self):
        """Aciona a organização após debounce."""
        if self._pending_files:
            files_to_process = list(self._pending_files)
            self._pending_files.clear()
            self.organizer_callback(files_to_process)
    
    def _schedule_organization(self):
        """Agenda organização com debounce para evitar múltiplas execuções rápidas."""
        if self._debounce_timer:
            self._debounce_timer.cancel()
        self._debounce_timer = threading.Timer(self._debounce_seconds, self._trigger_organization)
        self._debounce_timer.start()
    
    def on_created(self, event):
        if not event.is_directory and self._should_process_file(event.src_path):
            logging.info(f"Ficheiro criado detectado: {event.src_path}")
            self._pending_files.add(event.src_path)
            self._schedule_organization()
    
    def on_moved(self, event):
        if not event.is_directory and self._should_process_file(event.dest_path):
            logging.info(f"Ficheiro movido detectado: {event.dest_path}")
            self._pending_files.add(event.dest_path)
            self._schedule_organization()


class FileSorterScheduler:
    """
    Sistema de automação para organização de ficheiros.
    Suporta:
    - Agendamento por intervalo de tempo
    - Monitorização em tempo real (watch mode)
    - Execução em horários específicos
    """
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load_config()
        self.logic = FileSorterLogic(config_path)
        self.observer: Optional[Observer] = None
        self.scheduler_thread: Optional[Thread] = None
        self.stop_event = Event()
        self.is_running = False
        self.status_callback: Optional[Callable[[str], None]] = None
        self.log_callback: Optional[Callable[[str], None]] = None
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração de automação."""
        default_config = {
            "enabled": False,
            "mode": "interval",  # "interval", "schedule", "watch"
            "watched_folders": [],
            "interval_minutes": 30,
            "schedule_times": ["09:00", "18:00"],
            "extensions_filter": [],
            "ai_prompt": "organize automaticamente",
            "run_on_startup": False,
            "minimize_to_tray": True
        }
        
        scheduler_config_path = self.config_path.parent / "scheduler_config.json"
        if scheduler_config_path.exists():
            try:
                with scheduler_config_path.open('r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
            except (json.JSONDecodeError, IOError) as e:
                logging.error(f"Erro ao carregar config do scheduler: {e}")
        
        return default_config
    
    def _save_config(self):
        """Guarda configuração de automação."""
        scheduler_config_path = self.config_path.parent / "scheduler_config.json"
        try:
            scheduler_config_path.parent.mkdir(parents=True, exist_ok=True)
            with scheduler_config_path.open('w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except IOError as e:
            logging.error(f"Erro ao salvar config do scheduler: {e}")
    
    def set_status_callback(self, callback: Callable[[str], None]):
        """Define callback para atualizações de status."""
        self.status_callback = callback
    
    def set_log_callback(self, callback: Callable[[str], None]):
        """Define callback para logs."""
        self.log_callback = callback
    
    def _log(self, message: str):
        """Envia log para o callback se disponível."""
        logging.info(message)
        if self.log_callback:
            self.log_callback(message)
    
    def _set_status(self, status: str):
        """Envia status para o callback se disponível."""
        if self.status_callback:
            self.status_callback(status)
    
    def organize_folder(self, folder_path: str) -> Dict[str, Any]:
        """Organiza uma pasta usando as regras atuais."""
        folder = Path(folder_path)
        if not folder.exists():
            self._log(f"Pasta não encontrada: {folder_path}")
            return {"success": False, "error": "Pasta não encontrada"}
        
        self._log(f"Iniciando organização de: {folder_path}")
        self._set_status(f"Organizando {folder_path}...")
        
        try:
            cancel_event = Event()
            report_data = {}
            
            generator = self.logic.organize_files(folder, cancel_event)
            while True:
                try:
                    msg_type, msg_data = next(generator)
                    if msg_type == "log":
                        self._log(msg_data)
                    elif msg_type == "progress":
                        self._set_status(f"Progresso: {msg_data}%")
                except StopIteration as e:
                    report_data = e.value
                    break
            
            # Gerar relatório
            if report_data:
                report_path = self.logic.generate_html_report(report_data)
                self._log(f"Relatório gerado: {report_path}")
            
            self._set_status(f"Organização concluída: {folder_path}")
            return {
                "success": True,
                "moved_count": report_data.get("moved_count", 0),
                "report_path": report_path
            }
            
        except Exception as e:
            logging.error(f"Erro ao organizar {folder_path}: {e}")
            self._log(f"Erro: {str(e)}")
            self._set_status(f"Erro na organização: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _run_scheduled_organization(self):
        """Executa organização agendada em todas as pastas monitoradas."""
        for watched_folder in self.config.get("watched_folders", []):
            if Path(watched_folder).exists():
                self.organize_folder(watched_folder)
            else:
                self._log(f"Pasta monitorada não existe: {watched_folder}")
    
    def _interval_scheduler_loop(self):
        """Loop de agendamento por intervalo."""
        interval_minutes = self.config.get("interval_minutes", 30)
        interval_seconds = interval_minutes * 60
        
        self._log(f"Agendamento por intervalo iniciado: {interval_minutes} minutos")
        
        while not self.stop_event.is_set():
            self._run_scheduled_organization()
            
            # Aguarda próximo intervalo, verificando stop_event periodicamente
            for _ in range(interval_seconds):
                if self.stop_event.is_set():
                    break
                time.sleep(1)
    
    def _schedule_times_loop(self):
        """Loop de agendamento por horários específicos."""
        schedule_times = self.config.get("schedule_times", ["09:00", "18:00"])
        
        self._log(f"Agendamento por horários: {', '.join(schedule_times)}")
        
        while not self.stop_event.is_set():
            now = datetime.now()
            current_time = f"{now.hour:02d}:{now.minute:02d}"
            
            if current_time in schedule_times:
                self._run_scheduled_organization()
                # Aguarda 61 segundos para não executar múltiplas vezes no mesmo minuto
                time.sleep(61)
            else:
                time.sleep(30)  # Verifica a cada 30 segundos
    
    def _start_watch_mode(self):
        """Inicia monitorização em tempo real."""
        watched_folders = self.config.get("watched_folders", [])
        extensions_filter = self.config.get("extensions_filter", None)
        
        if not watched_folders:
            self._log("Nenhuma pasta configurada para monitorização")
            return
        
        def on_files_detected(files):
            """Callback quando ficheiros são detectados."""
            # Agrupar ficheiros por pasta pai
            folders_to_organize = set()
            for file_path in files:
                folders_to_organize.add(str(Path(file_path).parent))
            
            for folder in folders_to_organize:
                self._log(f"Ficheiros novos detectados em: {folder}")
                self.organize_folder(folder)
        
        # Usar PollingObserver para melhor compatibilidade com Windows
        self.observer = PollingObserver() if os.name == 'nt' else Observer()
        
        for folder_path in watched_folders:
            if Path(folder_path).exists():
                event_handler = AutoOrganizationHandler(on_files_detected, extensions_filter)
                self.observer.schedule(event_handler, folder_path, recursive=False)
                self._log(f"Monitorando pasta: {folder_path}")
            else:
                self._log(f"Pasta não existe para monitorização: {folder_path}")
        
        self.observer.start()
        self._log("Monitorização em tempo real iniciada")
        
        # Manter thread ativa
        while not self.stop_event.is_set():
            time.sleep(1)
        
        self.observer.stop()
        self.observer.join()
        self._log("Monitorização em tempo real parada")
    
    def start(self, mode: Optional[str] = None):
        """Inicia o scheduler."""
        if self.is_running:
            self._log("Scheduler já está em execução")
            return
        
        mode = mode or self.config.get("mode", "interval")
        self.config["mode"] = mode
        self._save_config()
        
        self.stop_event.clear()
        self.is_running = True
        
        if mode == "watch":
            self.scheduler_thread = Thread(target=self._start_watch_mode, daemon=True)
        elif mode == "schedule":
            self.scheduler_thread = Thread(target=self._schedule_times_loop, daemon=True)
        else:  # interval
            self.scheduler_thread = Thread(target=self._interval_scheduler_loop, daemon=True)
        
        self.scheduler_thread.start()
        self._log(f"Scheduler iniciado no modo: {mode}")
        self._set_status(f"Automação ativa: {mode}")
    
    def stop(self):
        """Para o scheduler."""
        if not self.is_running:
            return
        
        self._log("Parando scheduler...")
        self.stop_event.set()
        
        if self.observer:
            self.observer.stop()
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        self.is_running = False
        self._log("Scheduler parado")
        self._set_status("Automação desativada")
    
    def add_watched_folder(self, folder_path: str):
        """Adiciona pasta à lista de monitorização."""
        if folder_path not in self.config["watched_folders"]:
            self.config["watched_folders"].append(folder_path)
            self._save_config()
            self._log(f"Pasta adicionada: {folder_path}")
    
    def remove_watched_folder(self, folder_path: str):
        """Remove pasta da lista de monitorização."""
        if folder_path in self.config["watched_folders"]:
            self.config["watched_folders"].remove(folder_path)
            self._save_config()
            self._log(f"Pasta removida: {folder_path}")
    
    def update_config(self, new_config: Dict[str, Any]):
        """Atualiza configuração do scheduler."""
        self.config.update(new_config)
        self._save_config()
        self._log("Configuração do scheduler atualizada")
    
    def get_config(self) -> Dict[str, Any]:
        """Retorna configuração atual do scheduler."""
        return self.config.copy()
    
    def is_enabled(self) -> bool:
        """Verifica se automação está habilitada."""
        return self.config.get("enabled", False)


def register_startup_task():
    """
    Registra o FileSorter para iniciar com o Windows.
    Cria uma tarefa no Agendador de Tarefas do Windows.
    """
    import subprocess
    
    script_path = Path(__file__).resolve()
    project_dir = script_path.parent
    python_path = sys.executable
    
    task_name = "FileSorter_AutoOrganization"
    
    # Comando para executar o scheduler em modo background
    command = f'"{python_path}" "{project_dir}\\FileSorter.py" --minimized --auto-start'
    
    try:
        # Usar schtasks para criar tarefa agendada
        subprocess.run([
            'schtasks', '/Create',
            '/TN', task_name,
            '/TR', command,
            '/SC', 'ONLOGON',
            '/RL', 'HIGHEST',
            '/F'
        ], check=True, capture_output=True)
        
        logging.info(f"Tarefa '{task_name}' criada com sucesso")
        return True, f"Tarefa '{task_name}' criada com sucesso"
    except subprocess.CalledProcessError as e:
        error_msg = f"Erro ao criar tarefa: {e.stderr.decode() if e.stderr else str(e)}"
        logging.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Erro inesperado: {str(e)}"
        logging.error(error_msg)
        return False, error_msg


def unregister_startup_task():
    """
    Remove a tarefa de inicialização do Windows.
    """
    import subprocess
    
    task_name = "FileSorter_AutoOrganization"
    
    try:
        subprocess.run([
            'schtasks', '/Delete',
            '/TN', task_name,
            '/F'
        ], check=True, capture_output=True)
        
        logging.info(f"Tarefa '{task_name}' removida com sucesso")
        return True, f"Tarefa '{task_name}' removida com sucesso"
    except subprocess.CalledProcessError:
        # Tarefa não existe, ignorar
        return True, "Tarefa não existia"
    except Exception as e:
        error_msg = f"Erro ao remover tarefa: {str(e)}"
        logging.error(error_msg)
        return False, error_msg


# Função para execução em linha de comando (modo background)
def run_scheduler_cli():
    """Executa o scheduler em modo CLI para tarefas agendadas."""
    import argparse
    
    parser = argparse.ArgumentParser(description='FileSorter Scheduler CLI')
    parser.add_argument('--mode', choices=['interval', 'schedule', 'watch'], default='interval')
    parser.add_argument('--config', type=str, help='Caminho para o arquivo de configuração')
    args = parser.parse_args()
    
    config_dir = Path(user_config_dir("FileSorter", "CurmudgeonApps"))
    config_path = config_dir / "config.json" if not args.config else Path(args.config)
    
    scheduler = FileSorterScheduler(config_path)
    
    # Configurar logging para arquivo
    log_dir = Path(user_log_dir("FileSorter", "CurmudgeonApps"))
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "scheduler.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logging.info(f"FileSorter Scheduler iniciado - Modo: {args.mode}")
    
    try:
        scheduler.start(args.mode)
    except KeyboardInterrupt:
        logging.info("Interruptido pelo usuário")
    finally:
        scheduler.stop()
        logging.info("Scheduler encerrado")


if __name__ == "__main__":
    run_scheduler_cli()
