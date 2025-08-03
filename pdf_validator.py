import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import PyPDF2
import pdfplumber
import os
import json
from datetime import datetime
import threading
import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

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
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título com ícone
        title_label = ttk.Label(main_frame, text="🧪 Validador de Testes", 
                               font=('Segoe UI', 20, 'bold'), foreground='#2d3a4a')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 30))
        
        # Botão para selecionar PDF
        self.select_btn = ttk.Button(main_frame, text="📂 Selecionar PDF", 
                                    command=self.select_pdf, style='Accent.TButton')
        self.select_btn.grid(row=1, column=0, sticky=tk.W, pady=(0, 10), ipadx=10, ipady=5)
        
        # Label para mostrar arquivo selecionado
        self.file_label = ttk.Label(main_frame, text="Nenhum arquivo selecionado", 
                                   foreground='#888', font=('Segoe UI', 11))
        self.file_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 10))
        
        # Botão para validar
        self.validate_btn = ttk.Button(main_frame, text="✅ Validar Testes", 
                                      command=self.validate_pdf, state='disabled', style='Success.TButton')
        self.validate_btn.grid(row=1, column=2, sticky=tk.E, pady=(0, 10), ipadx=10, ipady=5)
        
        # Barra de progresso
        self.progress_var = tk.StringVar()
        self.progress_var.set("")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var, font=('Segoe UI', 10))
        self.progress_label.grid(row=2, column=0, columnspan=3, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate', style='blue.Horizontal.TProgressbar')
        self.progress_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Notebook para abas
        self.notebook = ttk.Notebook(main_frame, style='Modern.TNotebook')
        self.notebook.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Aba de informações básicas
        self.info_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.info_frame, text="ℹ️ Informações")
        
        # Aba de validação
        self.validation_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.validation_frame, text="🔎 Validação")
        
        # Aba de conteúdo
        self.content_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.content_frame, text="📄 Conteúdo")
        
        # Aba de relatório
        self.report_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.report_frame, text="📊 Relatório")
        
        self.setup_info_tab()
        self.setup_validation_tab()
        self.setup_content_tab()
        self.setup_report_tab()
        
        # Barra de status (remover campo de PDF válido)
        self.status_var = tk.StringVar()
        self.status_var.set("")
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                                   relief=tk.SUNKEN, anchor=tk.W, font=('Segoe UI', 10), background='#e9ecef')
        self.status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(20, 0))
        
        # Estilos customizados
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Accent.TButton', font=('Segoe UI', 12, 'bold'), foreground='white', background='#0078d7')
        style.map('Accent.TButton', background=[('active', '#005fa3')])
        style.configure('Success.TButton', font=('Segoe UI', 12, 'bold'), foreground='white', background='#28a745')
        style.map('Success.TButton', background=[('active', '#218838')])
        style.configure('blue.Horizontal.TProgressbar', troughcolor='#e9ecef', background='#0078d7', thickness=8)
        style.configure('Modern.TNotebook.Tab', font=('Segoe UI', 12, 'bold'), padding=[10, 5])
        style.configure('TNotebook', tabposition='n')
        style.configure('TFrame', background='#f8fafc')
        style.configure('TLabel', background='#f8fafc')
        style.configure('TNotebook.Tab', background='#e9ecef', foreground='#2d3a4a')
        style.map('TNotebook.Tab', background=[('selected', '#0078d7')], foreground=[('selected', 'white')])
        
    def setup_info_tab(self):
        # Frame com scroll moderno
        self.info_canvas = tk.Canvas(self.info_frame, highlightthickness=0, bg='#f8fafc')
        self.info_scrollbar = ttk.Scrollbar(self.info_frame, orient="vertical", command=self.info_canvas.yview)
        self.info_scrollable_frame = ttk.Frame(self.info_canvas, padding=0)
        self.info_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.info_canvas.configure(scrollregion=self.info_canvas.bbox("all"))
        )
        self.info_canvas.create_window((0, 0), window=self.info_scrollable_frame, anchor="nw")
        self.info_canvas.configure(yscrollcommand=self.info_scrollbar.set)
        self.info_canvas.pack(side="left", fill="both", expand=True)
        self.info_scrollbar.pack(side="right", fill="y")
        # Área de texto
        self.info_text = tk.Text(self.info_scrollable_frame, height=20, width=80, font=('Segoe UI', 12), bg='#f8fafc', relief=tk.FLAT, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.info_text.config(state=tk.DISABLED)
        
    def setup_validation_tab(self):
        self.validation_canvas = tk.Canvas(self.validation_frame, highlightthickness=0, bg='#f8fafc')
        self.validation_scrollbar = ttk.Scrollbar(self.validation_frame, orient="vertical", command=self.validation_canvas.yview)
        self.validation_scrollable_frame = ttk.Frame(self.validation_canvas, padding=0)
        self.validation_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.validation_canvas.configure(scrollregion=self.validation_canvas.bbox("all"))
        )
        self.validation_canvas.create_window((0, 0), window=self.validation_scrollable_frame, anchor="nw")
        self.validation_canvas.configure(yscrollcommand=self.validation_scrollbar.set)
        self.validation_canvas.pack(side="left", fill="both", expand=True)
        self.validation_scrollbar.pack(side="right", fill="y")
        self.validation_results_text = tk.Text(self.validation_scrollable_frame, height=20, width=80, font=('Segoe UI', 12), bg='#f8fafc', relief=tk.FLAT, wrap=tk.WORD)
        self.validation_results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.validation_results_text.config(state=tk.DISABLED)
        
    def setup_content_tab(self):
        self.content_canvas = tk.Canvas(self.content_frame, highlightthickness=0, bg='#f8fafc')
        self.content_scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.content_canvas.yview)
        self.content_scrollable_frame = ttk.Frame(self.content_canvas, padding=0)
        self.content_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all"))
        )
        self.content_canvas.create_window((0, 0), window=self.content_scrollable_frame, anchor="nw")
        self.content_canvas.configure(yscrollcommand=self.content_scrollbar.set)
        self.content_canvas.pack(side="left", fill="both", expand=True)
        self.content_scrollbar.pack(side="right", fill="y")
        self.content_text = tk.Text(self.content_scrollable_frame, height=20, width=80, font=('Segoe UI', 12), bg='#f8fafc', relief=tk.FLAT, wrap=tk.WORD)
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.content_text.config(state=tk.DISABLED)
        
    def setup_report_tab(self):
        # Frame para relatório com scrollbar vertical automática
        self.report_canvas = tk.Canvas(self.report_frame, highlightthickness=0, bg='#f8fafc')
        self.report_scrollbar = ttk.Scrollbar(self.report_frame, orient="vertical", command=self.report_canvas.yview)
        self.report_scrollable_frame = ttk.Frame(self.report_canvas, padding=0)
        self.report_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.report_canvas.configure(scrollregion=self.report_canvas.bbox("all"))
        )
        self.report_canvas.create_window((0, 0), window=self.report_scrollable_frame, anchor="nw")
        self.report_canvas.configure(yscrollcommand=self.report_scrollbar.set)
        self.report_canvas.pack(side="left", fill="both", expand=True)
        self.report_scrollbar.pack(side="right", fill="y")
        self.report_scrollable_frame.grid_columnconfigure(0, weight=1)
        self.report_scrollable_frame.grid_rowconfigure(0, weight=1)
        
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
                
                # Extrair conteúdo usando pdfplumber
                content = self.extract_content(self.current_pdf_path)
                # Extrair texto completo para validações avançadas
                full_text = "\n".join(content)
                self.header_info = self.extract_header_info(full_text)
                adv_results = self.perform_advanced_validations(full_text, os.path.basename(self.current_pdf_path))
                self.advanced_results = adv_results
                
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
        
    def extract_content(self, pdf_path):
        content = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        content.append(f"--- PÁGINA {i+1} ---\n{text}\n")
                    else:
                        content.append(f"--- PÁGINA {i+1} ---\n[Conteúdo não pode ser extraído]\n")
                except Exception as e:
                    content.append(f"--- PÁGINA {i+1} ---\n[Erro ao extrair: {str(e)}]\n")
        return content
        
    def extract_header_info(self, pdf_text):
        info = {}
        m = re.search(r'Equipamento de Teste Nome\s*:\s*(.*)', pdf_text)
        if m:
            info['equipamento_teste'] = m.group(1).strip()
        m = re.search(r'Nr\. Serie\s*:\s*(\d+)', pdf_text)
        if m:
            info['nr_serie_teste'] = m.group(1).strip()
        m = re.search(r'Equipamento Testado Nome\s*:\s*(.*)', pdf_text)
        if m:
            info['equipamento_testado'] = m.group(1).strip()
        m = re.search(r'Equipamento Testado Nome\s*:\s*.*\nNr\. Serie\s*:\s*(\d+)', pdf_text)
        if m:
            info['nr_serie_testado'] = m.group(1).strip()
        m = re.search(r'Data Calibra[çc][aã]o\s*:\s*(\d{2}/\d{2}/\d{4})', pdf_text)
        if m:
            info['data_calibracao'] = m.group(1).strip()
        return info
        
    def perform_advanced_validations(self, pdf_text, filename):
        results = {
            'all_tests_ok': True,
            'failed_tests': [],
            'missing_alarm_ok': [],
            'serial_match': True,
            'serial_info': '',
            'calibration_valid': True,
            'calibration_info': '',
            'total_tests': 0,
            'expected_tests': 0,
            'all_tests_present': True,
            'not_performed_tests': [],  # <-- NOVO
            'attention_tests': [],      # <-- NOVO
            'annotation_requests': [],  # <-- NOVO
            'missing_annotation': [],    # <-- NOVO
            'annotation_results': []     # <-- NOVO
        }
        # 1. Testes OK/NOK
        test_blocks = re.findall(r'(Teste (\d+) de (\d+)[\s\S]+?)(?=Teste \d+ de \d+|$)', pdf_text)
        test_numbers = set()
        expected_tests = 0

        for idx, (block, test_num, test_total) in enumerate(test_blocks):
            test_id = f"{test_num} de {test_total}"
            test_numbers.add(int(test_num))
            expected_tests = int(test_total)
            # Verifica parâmetros NOK
            for line in block.splitlines():
                if re.search(r'OK/NOK', line):
                    continue
                nok_match = re.findall(r'([\w\s]+)\s+[^\n]*NOK', line, re.IGNORECASE)
                for param in nok_match:
                    results['all_tests_ok'] = False
                    results['failed_tests'].append(f"{test_id}: {param.strip()}")
                # NOVO: Verifica se algum valor min/max está fora do limite, mas o teste está OK
                param_match = re.match(
                    r'([\w\s]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+OK',
                    line
                )
                if param_match:
                    param_name = param_match.group(1).strip()
                    min_val = float(param_match.group(2).replace(',', '.'))
                    max_val = float(param_match.group(3).replace(',', '.'))
                    media_val = float(param_match.group(4).replace(',', '.'))
                    lim_min = float(param_match.group(5).replace(',', '.'))
                    lim_max = float(param_match.group(6).replace(',', '.'))
                    if min_val < lim_min or max_val > lim_max:
                        results['attention_tests'].append(f"{test_id}: {param_name} (Min: {min_val}, Max: {max_val}, Média aprovada: {media_val}, Limites: {lim_min}-{lim_max})")
            # NOVO: Verifica se o teste não foi realizado
            if 'Teste não realizado' in block:
                results['not_performed_tests'].append(test_id)
            # --- ANOTAÇÃO REFINADA ---
            # Procura por solicitações de anotação
            annotation_requests = re.findall(r'anotar\s+([^.\n]+)', block, re.IGNORECASE)
            
            for request in annotation_requests:
                request_clean = request.strip()
                annotated_values = []
                
                # Busca mais específica - apenas em seções OBS e próximas à solicitação
                search_context = ""
                
                # 1. Primeiro, procura em seções OBS específicas
                obs_sections = re.findall(r'OBS:\s*(.*?)(?=\n[A-Z]|\nTeste|\n\n|$)', block, re.DOTALL | re.IGNORECASE)
                for obs_section in obs_sections:
                    search_context += obs_section + " "
                
                # 2. Se não encontrou nada nas OBS, procura no contexto próximo à palavra "anotar"
                if not search_context.strip():
                    # Encontra a posição da palavra "anotar" e pega algumas linhas antes e depois
                    lines = block.split('\n')
                    for i, line in enumerate(lines):
                        if 'anotar' in line.lower():
                            # Pega 2 linhas antes e 3 linhas depois
                            start = max(0, i-2)
                            end = min(len(lines), i+4)
                            context_lines = lines[start:end]
                            search_context = " ".join(context_lines)
                            break
                
                # 3. Se ainda não tem contexto, usa todo o bloco mas com filtros mais rigorosos
                if not search_context.strip():
                    search_context = block
                
                # Busca por padrões específicos apenas no contexto selecionado
                
                # 1. Procura por concentração (apenas em contexto de anotação)
                conc_patterns = [
                    r'Concentração\s*[:=]?\s*([0-9]+[.,]?[0-9]*)\s*%',
                    r'Conc\s*[:=]?\s*([0-9]+[.,]?[0-9]*)\s*%',
                    r'([0-9]+[.,]?[0-9]*)\s*%\s*O2',
                    r'O2\s*[:=]?\s*([0-9]+[.,]?[0-9]*)\s*%'
                ]
                
                for pattern in conc_patterns:
                    matches = re.findall(pattern, search_context, re.IGNORECASE)
                    if matches:
                        for match in matches:
                            # Verifica se não é um valor de parâmetro de tabela
                            if not self._is_parameter_table_value(match, block):
                                annotated_values.append(f"Concentração {match}%")
                        if annotated_values:
                            break
                
                # 2. Procura por complacência dinâmica
                if not annotated_values:
                    comp_dyn_patterns = [
                        r'Complacência\s+Din\.?\s*[:=]?\s*([0-9]+[.,]?[0-9]*)\s*mL/cmH2O',
                        r'Din\.?\s*[:=]?\s*([0-9]+[.,]?[0-9]*)\s*mL/cmH2O',
                        r'Dinâmica\s*[:=]?\s*([0-9]+[.,]?[0-9]*)\s*mL/cmH2O'
                    ]
                    
                    for pattern in comp_dyn_patterns:
                        matches = re.findall(pattern, search_context, re.IGNORECASE)
                        if matches:
                            for match in matches:
                                if not self._is_parameter_table_value(match, block):
                                    annotated_values.append(f"Complacência Din. {match}mL/cmH2O")
                            if annotated_values:
                                break
                
                # 3. Procura por complacência estática
                if not annotated_values:
                    comp_est_patterns = [
                        r'Estática\s*[:=]?\s*([0-9]+[.,]?[0-9]*)\s*mL/cmH2O',
                        r'Est\.?\s*[:=]?\s*([0-9]+[.,]?[0-9]*)\s*mL/cmH2O',
                        r'Complacência\s+Est\.?\s*[:=]?\s*([0-9]+[.,]?[0-9]*)\s*mL/cmH2O'
                    ]
                    
                    for pattern in comp_est_patterns:
                        matches = re.findall(pattern, search_context, re.IGNORECASE)
                        if matches:
                            for match in matches:
                                if not self._is_parameter_table_value(match, block):
                                    annotated_values.append(f"Estática {match}mL/cmH2O")
                            if annotated_values:
                                break
                
                # 4. Procura por outros valores numéricos próximos à solicitação
                if not annotated_values:
                    # Procura por números próximos à palavra "anotar"
                    context_pattern = r'anotar[^0-9]*([0-9]+[.,]?[0-9]*)'
                    context_matches = re.findall(context_pattern, search_context, re.IGNORECASE)
                    if context_matches:
                        for match in context_matches:
                            if not self._is_parameter_table_value(match, block):
                                annotated_values.append(f"Valor {match}")
                
                # Monta o resultado
                if annotated_values:
                    valor_anotado = " | ".join(annotated_values)
                else:
                    valor_anotado = "NÃO ANOTADO"
                    results['missing_annotation'].append(f"{test_id}: {request_clean}")
                
                results['annotation_results'].append(f"{test_id}: {request_clean} -> {valor_anotado}")
            
            # --- FIM ANOTAÇÃO REFINADA ---
            # Verifica se é teste de alarme e se tem 'Teste OK!!' ou 'NOK' (case-insensitive)
            if 'OBS:' in block:
                obs_block = block.split('OBS:')[1] if 'OBS:' in block else ''
                if (re.search(r'verificar ocorrência|alarme', obs_block, re.IGNORECASE)
                    and not re.search(r'Teste\s*OK!!', obs_block, re.IGNORECASE)
                    and not re.search(r'NOK', obs_block, re.IGNORECASE)):
                    results['missing_alarm_ok'].append(test_id)
        results['total_tests'] = len(test_numbers)
        results['expected_tests'] = expected_tests
        results['all_tests_present'] = (len(test_numbers) == expected_tests)
        # 2. Número de série
        serial_in_file = ''
        serial_in_pdf = ''
        m = re.search(r'NS(\d+)', filename)
        if m:
            serial_in_file = m.group(1).lstrip('0')
        m2 = re.search(r'Equipamento Testado Nome\s*:\s*.*\nNr\. Serie\s*:\s*(\d+)', pdf_text)
        if m2:
            serial_in_pdf = m2.group(1).lstrip('0')
        results['serial_info'] = f"No arquivo: {serial_in_file} | No PDF: {serial_in_pdf}"
        if serial_in_file and serial_in_pdf and serial_in_file != serial_in_pdf:
            results['serial_match'] = False
        # 3. Data de calibração
        calib_match = re.search(r'Data Calibra[çc][aã]o\s*:\s*(\d{2}/\d{2}/\d{4})', pdf_text)
        from datetime import datetime
        calib_ok = True
        calib_info = ''
        if calib_match:
            calib_str = calib_match.group(1)
            try:
                calib_date = datetime.strptime(calib_str, '%d/%m/%Y')
                now = datetime.now()
                if calib_date <= now:
                    calib_ok = False
                calib_info = f"Data calibração: {calib_str} (Válida: {'Sim' if calib_ok else 'Não'})"
            except Exception as e:
                calib_ok = False
                calib_info = f"Data calibração inválida: {calib_str}"
        else:
            calib_ok = False
            calib_info = "Data calibração não encontrada"
        results['calibration_valid'] = calib_ok
        results['calibration_info'] = calib_info
        return results
    
    def _is_parameter_table_value(self, value, block):
        """
        Verifica se um valor encontrado é de uma tabela de parâmetros
        """
        # Procura por linhas que seguem o padrão de tabela de parâmetros
        # (muitos números separados por espaços + OK no final)
        lines = block.split('\n')
        for line in lines:
            # Padrão de tabela de parâmetros: texto + 5 números + OK
            if re.match(r'^\s*[\w\s]+\s+[\d\.,]+\s+[\d\.,]+\s+[\d\.,]+\s+[\d\.,]+\s+[\d\.,]+\s+OK', line):
                # Verifica se o valor está nesta linha
                if value in line:
                    return True
        return False
        
    def update_ui_with_results(self, content):
        # Parar barra de progresso
        self.progress_bar.stop()
        self.progress_var.set("")
        
        # Atualizar abas
        self.update_info_tab()
        self.update_validation_tab()
        self.update_content_tab(content)
        self.update_report_tab()
        
        # Não mostrar mais status de PDF válido/invalidado
        self.status_var.set("")
        self.validate_btn.config(state='normal')
        
    def update_info_tab(self):
        info_text = f"""INFORMAÇÕES DO PDF\n{'='*50}\n\nNome do arquivo: {self.pdf_info['filename']}\nTamanho: {self.pdf_info['file_size']:,} bytes ({self.pdf_info['file_size']/1024/1024:.2f} MB)\nNúmero de páginas: {self.pdf_info['pages']}\nCriptografado: {'Sim' if self.pdf_info['is_encrypted'] else 'Não'}\nData de análise: {self.pdf_info['creation_date']}\n\nMETADADOS:\n{'='*20}"""
        if self.pdf_info['metadata']:
            for key, value in self.pdf_info['metadata'].items():
                if value:
                    info_text += f"\n{key}: {value}"
        else:
            info_text += "\nNenhum metadado encontrado"
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_text)
        self.info_text.config(state=tk.DISABLED)
        
    def update_validation_tab(self):
        validation_text = f"""RESULTADOS DA VALIDAÇÃO\n{'='*40}\n\nStatus: {'✅ VÁLIDO' if self.validation_results['is_valid'] else '❌ INVÁLIDO'}\n\nERROS ENCONTRADOS:\n{'='*20}"""
        if self.validation_results['errors']:
            for error in self.validation_results['errors']:
                validation_text += f"\n❌ {error}"
        else:
            validation_text += "\nNenhum erro encontrado"
        validation_text += f"\n\nAVISOS:\n{'='*10}"
        if self.validation_results['warnings']:
            for warning in self.validation_results['warnings']:
                validation_text += f"\n⚠️ {warning}"
        else:
            validation_text += "\nNenhum aviso"
        validation_text += f"\n\nESTATÍSTICAS:\n{'='*15}"
        for key, value in self.validation_results['checks'].items():
            validation_text += f"\n{key.replace('_', ' ').title()}: {value}"
        self.validation_results_text.config(state=tk.NORMAL)
        self.validation_results_text.delete(1.0, tk.END)
        self.validation_results_text.insert(1.0, validation_text)
        self.validation_results_text.config(state=tk.DISABLED)
        
    def update_content_tab(self, content):
        content_text = "CONTEÚDO DO PDF\n" + "="*20 + "\n\n"
        if content:
            content_text += "\n".join(content)
        else:
            content_text += "Nenhum conteúdo pode ser extraído."
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(1.0, content_text)
        self.content_text.config(state=tk.DISABLED)
        
    def update_report_tab(self):
        # Limpar frame
        for widget in self.report_scrollable_frame.winfo_children():
            widget.destroy()
        adv = getattr(self, 'advanced_results', None)
        # Painel principal centralizado e expandido
        panel = ttk.Frame(self.report_scrollable_frame, padding=30)
        panel.grid(row=0, column=0, sticky="nsew", pady=30)
        self.report_scrollable_frame.grid_rowconfigure(0, weight=1)
        self.report_scrollable_frame.grid_columnconfigure(0, weight=1)
        # Status geral
        if adv:
            if adv['all_tests_present'] and adv['all_tests_ok'] and not adv['missing_alarm_ok'] and not adv['not_performed_tests']:
                status_color = '#28a745'
                status_text = 'APROVADO!'
                status_icon = '✅'
                status_msg = f'Todos os {adv["expected_tests"]} testes foram realizados e aprovados.'
            else:
                status_color = '#dc3545'
                status_text = 'REPROVADO!'
                status_icon = '❌'
                status_msg = ''
                if not adv['all_tests_present']:
                    status_msg += f'Nem todos os testes foram realizados! ({adv["total_tests"]} de {adv["expected_tests"]})\n'
                if adv.get('not_performed_tests'):
                    status_msg += 'Testes não realizados:\n  - ' + '\n  - '.join(adv['not_performed_tests']) + '\n'
                if not adv['all_tests_ok']:
                    status_msg += 'Testes reprovados:\n  - ' + '\n  - '.join(adv['failed_tests']) + '\n'
            # Campo de atenção: se aprovado, mostrar só observação geral
            if adv.get('attention_tests'):
                if status_color == '#28a745':
                    status_msg += 'Atenção:\nExistem parâmetros com Min/Max fora dos limites, mas aprovados pela média.\nVeja detalhes abaixo.\n'
                else:
                    status_msg += 'Atenção: Parâmetros com Min/Max fora dos limites, mas aprovados pela média:\n  - ' + '\n  - '.join(adv['attention_tests']) + '\n'
        else:
            status_color = '#ffc107'
            status_text = 'ERRO'
            status_icon = '⚠️'
            status_msg = 'Não foi possível realizar validações avançadas.'
        # Caixa de status
        status_frame = tk.Frame(panel, bg=status_color, bd=0, relief=tk.RIDGE)
        status_frame.pack(fill=tk.X, pady=(0, 30), ipadx=10, ipady=10)
        tk.Label(status_frame, text=f'{status_icon} {status_text}', font=('Segoe UI', 28, 'bold'), bg=status_color, fg='white').pack(pady=(10, 0))
        tk.Label(status_frame, text=status_msg, font=('Segoe UI', 15), bg=status_color, fg='white', justify='center').pack(pady=(0, 10))
        # Detalhes
        if adv:
            details_frame = ttk.Frame(panel, padding=20)
            details_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
            # Número de série
            serial_ok = adv['serial_match']
            serial_icon = '✅' if serial_ok else '❌'
            serial_color = '#28a745' if serial_ok else '#dc3545'
            serial_label = tk.Label(details_frame, text=f'{serial_icon} Número de série: {adv["serial_info"]}', font=('Segoe UI', 13, 'bold'), fg='white', bg=serial_color, anchor='w')
            serial_label.pack(fill=tk.X, pady=6)
            # Data calibração
            calib_ok = adv['calibration_valid']
            calib_icon = '✅' if calib_ok else '❌'
            calib_color = '#28a745' if calib_ok else '#dc3545'
            calib_info = adv["calibration_info"]
            # Remover prefixos duplicados
            if calib_info.startswith("Data calibração: "):
                calib_info = calib_info.replace("Data calibração: ", "")
            elif calib_info.startswith("Data calibração inválida: "):
                calib_info = calib_info.replace("Data calibração inválida: ", "Inválida: ")
            elif calib_info == "Data calibração não encontrada":
                calib_info = "Não encontrada"
            calib_label = tk.Label(details_frame, text=f'{calib_icon} Data calibração Ventmeter: {calib_info}', font=('Segoe UI', 13, 'bold'), fg='white', bg=calib_color, anchor='w')
            calib_label.pack(fill=tk.X, pady=6)
            # Testes de alarme
            if adv['missing_alarm_ok']:
                alarm_label = tk.Label(details_frame, text=f'⚠️ Testes de alarme sem confirmação "Teste OK!!": {", ".join(adv["missing_alarm_ok"])}', font=('Segoe UI', 13), fg='#856404', bg='#fff3cd', anchor='w')
                alarm_label.pack(fill=tk.X, pady=6)
            # Parâmetros com atenção
            if adv['attention_tests']:
                attention_label = tk.Label(
                    details_frame,
                    text=f'⚠️ Atenção: Parâmetros com Min/Max fora dos limites, mas aprovados pela média:\n  - ' + '\n  - '.join(adv['attention_tests']),
                    font=('Segoe UI', 13),
                    fg='#856404',
                    bg='#fff3cd',
                    anchor='w',
                    justify='left'
                )
                attention_label.pack(fill=tk.X, pady=6)
            # Testes de anotação ausente
            if adv.get('missing_annotation'):
                missing_annot_label = tk.Label(
                    details_frame,
                    text=f'⚠️ Testes que solicitaram anotação mas não foi encontrado valor anotado:\n  - ' + '\n  - '.join(adv['missing_annotation']),
                    font=('Segoe UI', 13),
                    fg='#856404',
                    bg='#fff3cd',
                    anchor='w',
                    justify='left'
                )
                missing_annot_label.pack(fill=tk.X, pady=6)
            # Listagem de anotações
            if adv.get('annotation_results'):
                annotation_label = tk.Label(
                    details_frame,
                    text=f'📝 Testes que solicitaram anotação e valor encontrado:\n  - ' + '\n  - '.join(adv['annotation_results']),
                    font=('Segoe UI', 13),
                    fg='#005fa3',
                    bg='#e9ecef',
                    anchor='w',
                    justify='left'
                )
                annotation_label.pack(fill=tk.X, pady=6)
        # Botão para salvar relatório
        self.save_report_btn = ttk.Button(panel, text="Salvar Relatório", command=self.save_report, style='Accent.TButton')
        self.save_report_btn.pack(pady=(30, 10))
        
    def save_report(self):
        if not self.current_pdf_path:
            messagebox.showerror("Erro", "Nenhum PDF foi analisado!")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Salvar relatório",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if file_path.lower().endswith('.pdf'):
                    self.save_report_as_pdf(file_path)
                else:
                    report_text = self.generate_report_text()
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(report_text)
                messagebox.showinfo("Sucesso", f"Relatório salvo em: {file_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar relatório: {str(e)}")

    def save_report_as_pdf(self, file_path):
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.units import mm
        report_text = self.generate_report_text()
        header = getattr(self, 'header_info', {})
        adv = getattr(self, 'advanced_results', None)
        info = self.pdf_info
        # Montar o PDF
        doc = SimpleDocTemplate(file_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=20)
        styles = getSampleStyleSheet()
        elements = []
        # Título
        title_style = styles['Title']
        title_style.alignment = TA_CENTER
        elements.append(Paragraph("RELATÓRIO DE VALIDAÇÃO", title_style))
        elements.append(Spacer(1, 8))
        # Cabeçalho
        header_data = []
        if header:
            header_data = [
                ["<b>Equipamento de Teste</b>", header.get('equipamento_teste', '')],
                ["<b>Nº Série Equipamento de Teste</b>", header.get('nr_serie_teste', '')],
                ["<b>Equipamento Testado</b>", header.get('equipamento_testado', '')],
                ["<b>Nº Série Equipamento Testado</b>", header.get('nr_serie_testado', '')],
                ["<b>Data Calibração</b>", header.get('data_calibracao', '')],
            ]
            t = Table(header_data, hAlign='LEFT', colWidths=[70*mm, 90*mm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 11),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.whitesmoke, colors.lightgrey]),
                ('LINEBELOW', (0,-1), (-1,-1), 1, colors.grey),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 10))
        # Info do arquivo
        if info:
            file_data = [
                ["<b>Arquivo</b>", info.get('filename', '')],
                ["<b>Tamanho</b>", f"{info.get('file_size', 0)/1024/1024:.2f} MB"],
                ["<b>Páginas</b>", info.get('pages', 0)],
                ["<b>Data de análise</b>", info.get('creation_date', '')],
            ]
            t2 = Table(file_data, hAlign='LEFT', colWidths=[70*mm, 90*mm])
            t2.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.whitesmoke, colors.lightgrey]),
            ]))
            elements.append(t2)
            elements.append(Spacer(1, 10))
        # Status
        if adv:
            aprovado = adv['all_tests_present'] and adv['all_tests_ok'] and not adv['missing_alarm_ok'] and not adv['not_performed_tests']
            status = "APROVADO" if aprovado else "REPROVADO"
            status_color = colors.green if aprovado else colors.red
            status_style = styles['Heading2']
            elements.append(Spacer(1, 8))
            elements.append(Paragraph(f'<b>Status:</b> <font color="{status_color.hexval()}">{status}</font>', status_style))
            elements.append(Spacer(1, 8))
            # Testes não realizados
            if adv.get('not_performed_tests'):
                elements.append(Paragraph('<b>Testes não realizados:</b>', styles['Normal']))
                for t in adv['not_performed_tests']:
                    elements.append(Paragraph(f"- {t}", styles['Normal']))
                elements.append(Spacer(1, 4))
            # Testes reprovados
            if not adv['all_tests_ok']:
                elements.append(Paragraph('<b>Testes reprovados:</b>', styles['Normal']))
                for t in adv['failed_tests']:
                    elements.append(Paragraph(f"- {t}", styles['Normal']))
                elements.append(Spacer(1, 4))
            # Atenção
            if adv.get('attention_tests'):
                elements.append(Paragraph('<b>Atenção: Parâmetros com Min/Max fora dos limites, mas aprovados pela média:</b>', styles['Normal']))
                for t in adv['attention_tests']:
                    elements.append(Paragraph(f"- {t}", styles['Normal']))
                elements.append(Spacer(1, 4))
            # Número de série
            elements.append(Paragraph(f'<b>Número de série:</b> {adv.get("serial_info", "")}', styles['Normal']))
            # Data calibração
            elements.append(Paragraph(f'<b>Data calibração:</b> {adv.get("calibration_info", "")}', styles['Normal']))
            # Alarmes
            if adv.get('missing_alarm_ok'):
                elements.append(Paragraph('<b>Testes de alarme sem confirmação "Teste OK!!":</b>', styles['Normal']))
                for t in adv['missing_alarm_ok']:
                    elements.append(Paragraph(f"- {t}", styles['Normal']))
            # Testes de anotação ausente
            if adv.get('missing_annotation'):
                elements.append(Paragraph('<b>Testes que solicitaram anotação mas não foi encontrado valor anotado:</b>', styles['Normal']))
                for t in adv['missing_annotation']:
                    elements.append(Paragraph(f"- {t}", styles['Normal']))
            # Listagem de anotações
            if adv.get('annotation_results'):
                elements.append(Paragraph('<b>Testes que solicitaram anotação e valor encontrado:</b>', styles['Normal']))
                for t in adv['annotation_results']:
                    elements.append(Paragraph(f"- {t}", styles['Normal']))
                elements.append(Spacer(1, 4))
        doc.build(elements)
        
    def generate_report_text(self):
        adv = getattr(self, 'advanced_results', None)
        info = self.pdf_info
        header = getattr(self, 'header_info', {})
        lines = []
        lines.append(f"RELATÓRIO DE VALIDAÇÃO\n{'='*50}\n")
        if header:
            lines.append(f"Equipamento de Teste: {header.get('equipamento_teste', '')}")
            lines.append(f"Nº Série Equipamento de Teste: {header.get('nr_serie_teste', '')}")
            lines.append(f"Equipamento Testado: {header.get('equipamento_testado', '')}")
            lines.append(f"Nº Série Equipamento Testado: {header.get('nr_serie_testado', '')}")
            lines.append(f"Data Calibração: {header.get('data_calibracao', '')}")
            lines.append('')
        if info:
            lines.append(f"Arquivo: {info.get('filename', '')}")
            lines.append(f"Tamanho: {info.get('file_size', 0)/1024/1024:.2f} MB")
            lines.append(f"Páginas: {info.get('pages', 0)}")
            lines.append(f"Data de análise: {info.get('creation_date', '')}\n")
        if adv:
            aprovado = adv['all_tests_present'] and adv['all_tests_ok'] and not adv['missing_alarm_ok'] and not adv['not_performed_tests']
            lines.append(f"Status: {'APROVADO' if aprovado else 'REPROVADO'}\n")
            if adv.get('not_performed_tests'):
                lines.append('Testes não realizados:')
                for t in adv['not_performed_tests']:
                    lines.append(f"  - {t}")
            if not adv['all_tests_ok']:
                lines.append('Testes reprovados:')
                for t in adv['failed_tests']:
                    lines.append(f"  - {t}")
            if adv.get('attention_tests'):
                lines.append('Atenção: Parâmetros com Min/Max fora dos limites, mas aprovados pela média:')
                for t in adv['attention_tests']:
                    lines.append(f"  - {t}")
            lines.append(f"Número de série: {adv.get('serial_info', '')}")
            lines.append(f"Data calibração: {adv.get('calibration_info', '')}")
            if adv.get('missing_alarm_ok'):
                lines.append('Testes de alarme sem confirmação "Teste OK!!":')
                for t in adv['missing_alarm_ok']:
                    lines.append(f"  - {t}")
            if adv.get('missing_annotation'):
                lines.append('Testes que solicitaram anotação mas não foi encontrado valor anotado:')
                for t in adv['missing_annotation']:
                    lines.append(f"  - {t}")
            if adv.get('annotation_results'):
                lines.append('Testes que solicitaram anotação e valor encontrado:')
                for t in adv['annotation_results']:
                    lines.append(f"  - {t}")
        return '\n'.join(lines)
        
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