# Ficheiro: logic.py

import json
import logging
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union, Generator, Tuple, Optional, Any
from threading import Event

import google.generativeai as genai
from dotenv import load_dotenv

class GeminiRuleSuggester:
    """Gera regras de organização contextuais, agora com melhor manuseamento de pedidos vagos."""

    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Chave de API do Gemini não encontrada. Verifique o seu ficheiro .env.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def _build_prompt(self, filenames: List[str], user_request: str) -> str:
        system_instruction = """
        Você é um especialista em organização de ficheiros extremamente meticuloso. A sua tarefa é criar um conjunto de regras de organização analisando uma lista de nomes de ficheiros e um pedido do utilizador.

        As regras devem ser fornecidas num formato JSON estrito, que será uma LISTA de objetos.
        Cada objeto na lista representa UMA regra e deve conter DUAS chaves:
        1. "folder": O nome da pasta de destino (em MAIÚSCULAS e descritivo).
        2. "keywords": UMA LISTA de palavras-chave em minúsculas que, se encontradas no nome de um ficheiro, o moverão para esta pasta.

        Exemplo de resposta JSON válida:
        [
          { "folder": "RELATORIOS_VENDAS", "keywords": ["vendas", "relatorio_q3"] },
          { "folder": "FATURAS_CLIENTES", "keywords": ["fatura", "invoice", "recibo"] }
        ]

        INSTRUÇÕES IMPORTANTES:
        - Se o pedido do utilizador for VAGO ou GENÉRICO (ex: "organize isto", "arrume a confusão"), a sua tarefa é inferir categorias lógicas a partir dos nomes dos ficheiros. Crie pastas como DOCUMENTOS, IMAGENS, TRABALHO, PESSOAL, etc., e atribua palavras-chave apropriadas.
        - Crie regras específicas primeiro, e depois uma regra mais genérica no final para apanhar ficheiros comuns (como por extensão, ex: [".pdf", ".docx"]) se nenhuma palavra-chave específica corresponder.
        - A sua resposta deve ser APENAS o array JSON. Sem explicações, sem markdown, apenas o JSON.
        """
        file_list_str = ", ".join(filenames)[:4000]
        prompt = (f"{system_instruction}\n\n"
                  f"--- INÍCIO DOS DADOS ---\n"
                  f"Lista de nomes de ficheiros a analisar: {file_list_str}\n"
                  f"Pedido do utilizador: \"{user_request}\"\n"
                  f"--- FIM DOS DADOS ---\n\n"
                  f"Gere o array JSON com as regras de organização:")
        return prompt

    def suggest_rules(self, folder_path: Union[str, Path], user_request: str) -> Optional[List[Dict[str, Any]]]:
        source_path = Path(folder_path)
        if not source_path.is_dir():
            logging.error(f"O caminho fornecido '{folder_path}' não é um diretório válido.")
            return None
        
        filenames = [f.name for f in source_path.iterdir() if f.is_file()][:150]
        if not filenames:
            return []

        prompt = self._build_prompt(filenames, user_request)
        try:
            response = self.model.generate_content(prompt)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
            
            rules = json.loads(cleaned_response)
            if isinstance(rules, list) and all(isinstance(r, dict) and 'folder' in r and 'keywords' in r for r in rules):
                return rules
            else:
                logging.error(f"Resposta da IA não está no formato esperado: {rules}")
                return None
        except Exception as e:
            logging.error(f"Erro ao comunicar com a API do Gemini: {e}")
            return None

class FileSorterLogic:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.rules: List[Dict[str, Any]] = []
        self.load_rules()

    def load_rules(self) -> None:
        try:
            if self.config_path.exists():
                with self.config_path.open('r', encoding='utf-8') as f:
                    self.rules = json.load(f)
            else:
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                self.rules = []
                self.save_rules()
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Erro ao carregar o arquivo de configuração '{self.config_path}': {e}")
            self.rules = []

    def save_rules(self) -> None:
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with self.config_path.open('w', encoding='utf-8') as f:
                json.dump(self.rules, f, indent=4)
        except IOError as e:
            logging.error(f"Erro ao salvar o arquivo de configuração '{self.config_path}': {e}")

    def set_rules(self, rules: List[Dict[str, Any]]) -> None:
        self.rules = rules

    def _get_safe_destination_path(self, destination_path: Path, source_file: Path) -> Path:
        final_destination = destination_path / source_file.name
        counter = 1
        while final_destination.exists():
            final_destination = destination_path / f"{source_file.stem} ({counter}){source_file.suffix}"
            counter += 1
        return final_destination

    def organize_files(self, source_folder: Union[str, Path], cancel_event: Event) -> Generator[Tuple[str, str], None, Dict[str, Any]]:
        """Organiza ficheiros e, no final, retorna um dicionário com os dados para o relatório."""
        source_path = Path(source_folder)
        if not source_path.is_dir():
            yield ("error", f"Diretório '{source_path}' não encontrado.")
            return {}
        
        files_to_move = [f for f in source_path.iterdir() if f.is_file()]
        total_files = len(files_to_move)
        yield ("total_files", str(total_files))

        moved_count = 0
        created_folders = set()
        move_log = []

        for i, file_path in enumerate(files_to_move):
            if cancel_event.is_set():
                yield ("cancelled", "Operação cancelada pelo utilizador.")
                return {}

            destination_folder_name = self._get_destination_folder(file_path)
            destination_path = source_path / destination_folder_name
            
            if not destination_path.exists():
                created_folders.add(destination_folder_name)
            destination_path.mkdir(exist_ok=True)
            
            safe_path = self._get_safe_destination_path(destination_path, file_path)
            try:
                shutil.move(str(file_path), str(safe_path))
                moved_count += 1
                move_log.append({"from": file_path.name, "to_folder": destination_folder_name, "to_filename": safe_path.name})
                yield ("log", f"Movido '{file_path.name}' para '{destination_folder_name}'.")
            except Exception as e:
                logging.error(f"Falha ao mover '{file_path.name}': {e}")
                yield ("error", f"Falha ao mover '{file_path.name}': {e}")
            yield ("progress", str(i + 1))

        yield ("done", "Organização concluída! A gerar relatório...")
        
        return {
            "source_folder": str(source_path),
            "moved_count": moved_count,
            "total_files_scanned": total_files,
            "created_folders": sorted(list(created_folders)),
            "move_log": move_log
        }

    def _get_destination_folder(self, file_path: Path) -> str:
        filename_lower = file_path.name.lower()
        for rule in self.rules:
            for keyword in rule.get("keywords", []):
                if keyword.startswith('.') and filename_lower.endswith(keyword):
                    return rule["folder"]
                elif not keyword.startswith('.') and keyword in filename_lower:
                    return rule["folder"]
        extension = file_path.suffix.lower().replace('.', '')
        return extension.upper() if extension else "SEM_EXTENSAO"

    def generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Gera um ficheiro HTML com o resumo da organização e retorna o seu caminho."""
        timestamp = datetime.now()
        report_path = Path(report_data["source_folder"]) / f"_Relatorio_Organizacao_{timestamp.strftime('%Y-%m-%d_%H%M%S')}.html"

        summary_html = (f"<li><strong>Ficheiros analisados:</strong> {report_data['total_files_scanned']}</li>"
                        f"<li><strong>Ficheiros movidos:</strong> {report_data['moved_count']}</li>"
                        f"<li><strong>Pastas criadas:</strong> {len(report_data['created_folders'])} ({', '.join(report_data['created_folders']) if report_data['created_folders'] else 'Nenhuma'})</li>")

        log_rows_html = "".join([
            f"<tr><td>{item['from']}</td><td>{item['to_folder']}</td><td>{item['to_filename']}</td></tr>"
            for item in report_data["move_log"]
        ])

        html_template = f"""
        <!DOCTYPE html>
        <html lang="pt">
        <head>
            <meta charset="UTF-8">
            <title>Relatório de Organização</title>
            <style>
                body {{ font-family: sans-serif; margin: 2em; background-color: #fdfdfd; color: #333; }}
                h1, h2 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 5px;}}
                ul {{ list-style-type: none; padding: 0; }}
                li {{ background: #f4f4f4; margin: 5px 0; padding: 10px; border-left: 5px solid #007bff; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                th, td {{ padding: 12px; border: 1px solid #ddd; text-align: left; }}
                th {{ background-color: #007bff; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Relatório de Organização</h1>
            <p><strong>Pasta de Origem:</strong> {report_data['source_folder']}</p>
            <p><strong>Data e Hora:</strong> {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <h2>Resumo</h2>
            <ul>{summary_html}</ul>
            <h2>Registo Detalhado de Movimentos</h2>
            <table>
                <tr><th>Ficheiro Original</th><th>Pasta de Destino</th><th>Novo Nome (se alterado)</th></tr>
                {log_rows_html}
            </table>
        </body>
        </html>
        """
        try:
            with report_path.open('w', encoding='utf-8') as f:
                f.write(html_template)
            return str(report_path)
        except IOError as e:
            logging.error(f"Não foi possível escrever o relatório em '{report_path}': {e}")
            return ""