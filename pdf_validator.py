import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import PyPDF2
import os
import json
from datetime import datetime
import threading

class PDFValidator:
    def __init__(self, root):
        self.root = root
        self.root.title("Validador de PDF - Desktop App")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variáveis
        self.current_pdf_path = None
        self.pdf_info = {}
        self.validation_results = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="🔍 Validador de PDF", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Botão para selecionar PDF
        self.select_btn = ttk.Button(main_frame, text="Selecionar PDF", 
                                    command=self.select_pdf)
        self.select_btn.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        # Label para mostrar arquivo selecionado
        self.file_label = ttk.Label(main_frame, text="Nenhum arquivo selecionado", 
                                   foreground='gray')
        self.file_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 10))
        
        # Botão para validar
        self.validate_btn = ttk.Button(main_frame, text="Validar PDF", 
                                      command=self.validate_pdf, state='disabled')
        self.validate_btn.grid(row=1, column=2, sticky=tk.E, pady=(0, 10))
        
        # Barra de progresso
        self.progress_var = tk.StringVar()
        self.progress_var.set("")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=2, column=0, columnspan=3, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Notebook para abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Aba de informações básicas
        self.info_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text="Informações Básicas")
        
        # Aba de validação
        self.validation_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.validation_frame, text="Validação")
        
        # Aba de conteúdo
        self.content_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.content_frame, text="Conteúdo")
        
        # Aba de relatório
        self.report_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.report_frame, text="Relatório")
        
        self.setup_info_tab()
        self.setup_validation_tab()
        self.setup_content_tab()
        self.setup_report_tab()
        
        # Barra de status
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto para validar")
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                                   relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def setup_info_tab(self):
        # Frame com scroll
        canvas = tk.Canvas(self.info_frame)
        scrollbar = ttk.Scrollbar(self.info_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Informações do PDF
        self.info_text = scrolledtext.ScrolledText(scrollable_frame, height=20, width=80)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def setup_validation_tab(self):
        # Frame para resultados de validação
        self.validation_canvas = tk.Canvas(self.validation_frame)
        self.validation_scrollbar = ttk.Scrollbar(self.validation_frame, orient="vertical", 
                                                 command=self.validation_canvas.yview)
        self.validation_scrollable_frame = ttk.Frame(self.validation_canvas)
        
        self.validation_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.validation_canvas.configure(scrollregion=self.validation_canvas.bbox("all"))
        )
        
        self.validation_canvas.create_window((0, 0), window=self.validation_scrollable_frame, anchor="nw")
        self.validation_canvas.configure(yscrollcommand=self.validation_scrollbar.set)
        
        # Área para mostrar resultados
        self.validation_results_text = scrolledtext.ScrolledText(self.validation_scrollable_frame, 
                                                                height=20, width=80)
        self.validation_results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.validation_canvas.pack(side="left", fill="both", expand=True)
        self.validation_scrollbar.pack(side="right", fill="y")
        
    def setup_content_tab(self):
        # Frame para conteúdo do PDF
        self.content_canvas = tk.Canvas(self.content_frame)
        self.content_scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", 
                                              command=self.content_canvas.yview)
        self.content_scrollable_frame = ttk.Frame(self.content_canvas)
        
        self.content_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all"))
        )
        
        self.content_canvas.create_window((0, 0), window=self.content_scrollable_frame, anchor="nw")
        self.content_canvas.configure(yscrollcommand=self.content_scrollbar.set)
        
        # Área para mostrar conteúdo
        self.content_text = scrolledtext.ScrolledText(self.content_scrollable_frame, 
                                                     height=20, width=80)
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.content_canvas.pack(side="left", fill="both", expand=True)
        self.content_scrollbar.pack(side="right", fill="y")
        
    def setup_report_tab(self):
        # Frame para relatório
        self.report_canvas = tk.Canvas(self.report_frame)
        self.report_scrollbar = ttk.Scrollbar(self.report_frame, orient="vertical", 
                                             command=self.report_canvas.yview)
        self.report_scrollable_frame = ttk.Frame(self.report_canvas)
        
        self.report_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.report_canvas.configure(scrollregion=self.report_canvas.bbox("all"))
        )
        
        self.report_canvas.create_window((0, 0), window=self.report_scrollable_frame, anchor="nw")
        self.report_canvas.configure(yscrollcommand=self.report_scrollbar.set)
        
        # Área para relatório
        self.report_text = scrolledtext.ScrolledText(self.report_scrollable_frame, 
                                                    height=20, width=80)
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botão para salvar relatório
        self.save_report_btn = ttk.Button(self.report_scrollable_frame, text="Salvar Relatório", 
                                         command=self.save_report)
        self.save_report_btn.pack(pady=(0, 10))
        
        self.report_canvas.pack(side="left", fill="both", expand=True)
        self.report_scrollbar.pack(side="right", fill="y")
        
    def select_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.current_pdf_path = file_path
            self.file_label.config(text=os.path.basename(file_path))
            self.validate_btn.config(state='normal')
            self.status_var.set(f"Arquivo selecionado: {os.path.basename(file_path)}")
            
            # Limpar abas
            self.clear_tabs()
            
    def clear_tabs(self):
        self.info_text.delete(1.0, tk.END)
        self.validation_results_text.delete(1.0, tk.END)
        self.content_text.delete(1.0, tk.END)
        self.report_text.delete(1.0, tk.END)
        
    def validate_pdf(self):
        if not self.current_pdf_path:
            messagebox.showerror("Erro", "Nenhum arquivo PDF selecionado!")
            return
            
        # Executar validação em thread separada
        self.status_var.set("Validando PDF...")
        self.progress_var.set("Iniciando validação...")
        self.validate_btn.config(state='disabled')
        self.progress_bar.start()
        
        thread = threading.Thread(target=self._validate_pdf_thread)
        thread.daemon = True
        thread.start()
        
    def _validate_pdf_thread(self):
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(self.current_pdf_path):
                self.root.after(0, lambda: self.show_error("Arquivo não encontrado!"))
                return
                
            # Verificar se é realmente um arquivo PDF
            if not self.current_pdf_path.lower().endswith('.pdf'):
                self.root.after(0, lambda: self.show_error("Arquivo não é um PDF válido!"))
                return
                
            # Abrir PDF
            with open(self.current_pdf_path, 'rb') as file:
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                except Exception as e:
                    self.root.after(0, lambda: self.show_error(f"PDF corrompido ou inválido: {str(e)}"))
                    return
                
                # Coletar informações básicas
                self.pdf_info = {
                    'filename': os.path.basename(self.current_pdf_path),
                    'file_size': os.path.getsize(self.current_pdf_path),
                    'pages': len(pdf_reader.pages),
                    'metadata': pdf_reader.metadata,
                    'is_encrypted': pdf_reader.is_encrypted,
                    'creation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Realizar validações
                self.validation_results = self.perform_validations(pdf_reader)
                
                # Extrair conteúdo
                content = self.extract_content(pdf_reader)
                
                # Atualizar UI na thread principal
                self.root.after(0, self.update_ui_with_results, content)
                
        except PermissionError:
            self.root.after(0, lambda: self.show_error("Sem permissão para acessar o arquivo!"))
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Erro ao processar PDF: {str(e)}"))
            
    def perform_validations(self, pdf_reader):
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'checks': {}
        }
        
        # Verificar se o PDF pode ser lido
        try:
            if pdf_reader.is_encrypted:
                results['errors'].append("PDF está criptografado e não pode ser validado")
                results['is_valid'] = False
                return results
                
            # Verificar número de páginas
            if len(pdf_reader.pages) == 0:
                results['errors'].append("PDF não contém páginas")
                results['is_valid'] = False
            elif len(pdf_reader.pages) > 1000:
                results['warnings'].append("PDF tem muitas páginas (>1000)")
                
            # Verificar tamanho do arquivo
            file_size_mb = self.pdf_info['file_size'] / (1024 * 1024)
            if file_size_mb > 100:
                results['warnings'].append(f"Arquivo muito grande ({file_size_mb:.1f} MB)")
            elif file_size_mb < 0.001:  # Menos de 1KB
                results['warnings'].append("Arquivo muito pequeno (possivelmente corrompido)")
                
            # Verificar metadados
            if not pdf_reader.metadata:
                results['warnings'].append("PDF não possui metadados")
            else:
                if 'Title' not in pdf_reader.metadata:
                    results['warnings'].append("PDF não possui título")
                if 'Author' not in pdf_reader.metadata:
                    results['warnings'].append("PDF não possui autor")
                    
            # Verificar se páginas podem ser lidas
            readable_pages = 0
            empty_pages = 0
            for i, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        readable_pages += 1
                    else:
                        empty_pages += 1
                except Exception as e:
                    results['warnings'].append(f"Página {i+1} não pode ser lida: {str(e)}")
                    empty_pages += 1
                    
            results['checks']['readable_pages'] = readable_pages
            results['checks']['empty_pages'] = empty_pages
            results['checks']['total_pages'] = len(pdf_reader.pages)
            
            if readable_pages == 0:
                results['errors'].append("Nenhuma página contém texto legível")
                results['is_valid'] = False
            elif empty_pages > len(pdf_reader.pages) * 0.5:
                results['warnings'].append(f"Muitas páginas vazias ({empty_pages}/{len(pdf_reader.pages)})")
                
        except Exception as e:
            results['errors'].append(f"Erro durante validação: {str(e)}")
            results['is_valid'] = False
            
        return results
        
    def extract_content(self, pdf_reader):
        content = []
        
        for i, page in enumerate(pdf_reader.pages):
            try:
                text = page.extract_text()
                if text.strip():
                    content.append(f"--- PÁGINA {i+1} ---\n{text}\n")
            except:
                content.append(f"--- PÁGINA {i+1} ---\n[Conteúdo não pode ser extraído]\n")
                
        return content
        
    def update_ui_with_results(self, content):
        # Parar barra de progresso
        self.progress_bar.stop()
        self.progress_var.set("")
        
        # Atualizar aba de informações
        self.update_info_tab()
        
        # Atualizar aba de validação
        self.update_validation_tab()
        
        # Atualizar aba de conteúdo
        self.update_content_tab(content)
        
        # Atualizar aba de relatório
        self.update_report_tab()
        
        # Atualizar status
        status = "✅ PDF válido" if self.validation_results['is_valid'] else "❌ PDF inválido"
        self.status_var.set(status)
        self.validate_btn.config(state='normal')
        
    def update_info_tab(self):
        info_text = f"""INFORMAÇÕES DO PDF
{'='*50}

Nome do arquivo: {self.pdf_info['filename']}
Tamanho: {self.pdf_info['file_size']:,} bytes ({self.pdf_info['file_size']/1024/1024:.2f} MB)
Número de páginas: {self.pdf_info['pages']}
Criptografado: {'Sim' if self.pdf_info['is_encrypted'] else 'Não'}
Data de análise: {self.pdf_info['creation_date']}

METADADOS:
{'='*20}"""

        if self.pdf_info['metadata']:
            for key, value in self.pdf_info['metadata'].items():
                if value:
                    info_text += f"\n{key}: {value}"
        else:
            info_text += "\nNenhum metadado encontrado"
            
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_text)
        
    def update_validation_tab(self):
        validation_text = f"""RESULTADOS DA VALIDAÇÃO
{'='*40}

Status: {'✅ VÁLIDO' if self.validation_results['is_valid'] else '❌ INVÁLIDO'}

ERROS ENCONTRADOS:
{'='*20}"""
        
        if self.validation_results['errors']:
            for error in self.validation_results['errors']:
                validation_text += f"\n❌ {error}"
        else:
            validation_text += "\nNenhum erro encontrado"
            
        validation_text += f"""

AVISOS:
{'='*10}"""
        
        if self.validation_results['warnings']:
            for warning in self.validation_results['warnings']:
                validation_text += f"\n⚠️ {warning}"
        else:
            validation_text += "\nNenhum aviso"
            
        validation_text += f"""

ESTATÍSTICAS:
{'='*15}"""
        
        for key, value in self.validation_results['checks'].items():
            validation_text += f"\n{key.replace('_', ' ').title()}: {value}"
            
        self.validation_results_text.delete(1.0, tk.END)
        self.validation_results_text.insert(1.0, validation_text)
        
    def update_content_tab(self, content):
        content_text = "CONTEÚDO DO PDF\n" + "="*20 + "\n\n"
        
        if content:
            content_text += "\n".join(content)
        else:
            content_text += "Nenhum conteúdo pode ser extraído."
            
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(1.0, content_text)
        
    def update_report_tab(self):
        report_text = f"""RELATÓRIO DE VALIDAÇÃO
{'='*30}

Data/Hora: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Arquivo: {self.pdf_info['filename']}

RESUMO EXECUTIVO:
{'='*20}
Status: {'VÁLIDO' if self.validation_results['is_valid'] else 'INVÁLIDO'}
Total de páginas: {self.pdf_info['pages']}
Páginas legíveis: {self.validation_results['checks'].get('readable_pages', 0)}
Tamanho do arquivo: {self.pdf_info['file_size']/1024/1024:.2f} MB

DETALHES TÉCNICOS:
{'='*20}"""

        for key, value in self.pdf_info.items():
            if key != 'metadata':
                report_text += f"\n{key.replace('_', ' ').title()}: {value}"
                
        report_text += f"""

PROBLEMAS IDENTIFICADOS:
{'='*25}"""

        if self.validation_results['errors']:
            for error in self.validation_results['errors']:
                report_text += f"\nERRO: {error}"
                
        if self.validation_results['warnings']:
            for warning in self.validation_results['warnings']:
                report_text += f"\nAVISO: {warning}"
                
        if not self.validation_results['errors'] and not self.validation_results['warnings']:
            report_text += "\nNenhum problema identificado."
            
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report_text)
        
    def save_report(self):
        if not self.current_pdf_path:
            messagebox.showerror("Erro", "Nenhum PDF foi analisado!")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Salvar relatório",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.report_text.get(1.0, tk.END))
                messagebox.showinfo("Sucesso", f"Relatório salvo em: {file_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar relatório: {str(e)}")
                
    def show_error(self, message):
        # Parar barra de progresso
        self.progress_bar.stop()
        self.progress_var.set("")
        
        messagebox.showerror("Erro", message)
        self.status_var.set("Erro durante validação")
        self.validate_btn.config(state='normal')

def main():
    root = tk.Tk()
    app = PDFValidator(root)
    root.mainloop()

if __name__ == "__main__":
    main() 