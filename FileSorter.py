import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from logic import FileSorterLogic
import os

class RulesWindow(tk.Toplevel):
    def __init__(self, master, logic):
        super().__init__(master)
        self.title("Gerenciar Regras")
        self.geometry("600x400")
        self.logic = logic

        # Frame para a Treeview
        tree_frame = tk.Frame(self)
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=("Pasta", "Extensões"), show="headings")
        self.tree.heading("Pasta", text="Pasta")
        self.tree.heading("Extensões", text="Extensões (separadas por vírgula)")
        self.tree.pack(fill="both", expand=True)

        self.load_rules_to_tree()

        # Frame para adicionar/editar regras
        edit_frame = tk.Frame(self)
        edit_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(edit_frame, text="Pasta:").grid(row=0, column=0, padx=5, pady=5)
        self.folder_entry = tk.Entry(edit_frame, width=20)
        self.folder_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(edit_frame, text="Extensões:").grid(row=0, column=2, padx=5, pady=5)
        self.extensions_entry = tk.Entry(edit_frame, width=30)
        self.extensions_entry.grid(row=0, column=3, padx=5, pady=5)

        add_button = tk.Button(edit_frame, text="Adicionar/Atualizar", command=self.add_rule)
        add_button.grid(row=1, column=0, columnspan=2, pady=10)

        remove_button = tk.Button(edit_frame, text="Remover Selecionado", command=self.remove_rule)
        remove_button.grid(row=1, column=2, columnspan=2, pady=10)

        # Frame para salvar
        save_frame = tk.Frame(self)
        save_frame.pack(pady=10, padx=10)

        save_button = tk.Button(save_frame, text="Salvar e Fechar", command=self.save_and_close)
        save_button.pack()

    def load_rules_to_tree(self):
        self.tree.delete(*self.tree.get_children())
        for folder, extensions in self.logic.rules.items():
            self.tree.insert("", "end", values=(folder, ", ".join(extensions)))

    def add_rule(self):
        folder = self.folder_entry.get().strip()
        extensions_str = self.extensions_entry.get().strip()

        if not folder or not extensions_str:
            messagebox.showwarning("Entrada Inválida", "Ambos os campos de pasta e extensões devem ser preenchidos.")
            return

        extensions = [ext.strip().lower() for ext in extensions_str.split(',')]
        self.logic.rules[folder.upper()] = extensions
        self.load_rules_to_tree()
        self.folder_entry.delete(0, tk.END)
        self.extensions_entry.delete(0, tk.END)

    def remove_rule(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione uma regra para remover.")
            return

        item_values = self.tree.item(selected_item, "values")
        folder_to_remove = item_values[0]

        if folder_to_remove in self.logic.rules:
            del self.logic.rules[folder_to_remove]

        self.load_rules_to_tree()

    def save_and_close(self):
        self.logic.save_rules()
        messagebox.showinfo("Salvo", "Regras salvas com sucesso!")
        self.destroy()

class FileSorterGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("FileSorter")
        self.master.geometry("500x300")

        self.logic = FileSorterLogic()
        self.selected_folder = tk.StringVar()

        main_frame = tk.Frame(self.master, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Botão de regras
        rules_button = tk.Button(main_frame, text="Gerenciar Regras", command=self.open_rules_window)
        rules_button.pack(anchor="ne", pady=5)

        folder_frame = tk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=5)

        select_button = tk.Button(folder_frame, text="Selecionar Pasta", command=self.select_folder)
        select_button.pack(side=tk.LEFT, padx=(0, 10))

        folder_label = tk.Label(folder_frame, textvariable=self.selected_folder, relief=tk.GROOVE, bd=2)
        folder_label.pack(fill=tk.X, expand=True)
        self.selected_folder.set("Nenhuma pasta selecionada")

        organize_button = tk.Button(main_frame, text="Organizar Arquivos", command=self.organize_files, height=2)
        organize_button.pack(fill=tk.X, pady=10)

        self.status_label = tk.Label(self.master, text="Pronto", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def open_rules_window(self):
        rules_win = RulesWindow(self.master, self.logic)
        rules_win.transient(self.master)
        rules_win.grab_set()
        self.master.wait_window(rules_win)
        # Recarregar regras no caso de terem sido alteradas
        self.logic.load_rules()

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.selected_folder.set(folder_path)
            self.status_label.config(text=f"Pasta selecionada: {folder_path}")

    def organize_files(self):
        folder = self.selected_folder.get()
        if not os.path.isdir(folder):
            messagebox.showerror("Erro", "Por favor, selecione uma pasta válida primeiro.")
            return

        try:
            self.status_label.config(text="Organizando arquivos...")
            self.master.update_idletasks()
            self.logic.organizar_arquivos(folder)
            self.status_label.config(text="Organização concluída com sucesso!")
            messagebox.showinfo("Sucesso", "Arquivos organizados com sucesso!")
        except Exception as e:
            self.status_label.config(text="Erro durante a organização.")
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

def main():
    root = tk.Tk()
    app = FileSorterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
