# Validador de PDF - Desktop App

Uma aplicação desktop desenvolvida em Python com interface gráfica para validar e analisar arquivos PDF.

## Funcionalidades

- **Validação de PDF**: Verifica se o arquivo PDF é válido e pode ser lido
- **Análise de Informações**: Extrai metadados, número de páginas, tamanho do arquivo
- **Verificação de Conteúdo**: Analisa se as páginas contêm texto legível
- **Relatório Detalhado**: Gera relatórios completos da validação
- **Interface Gráfica**: Interface amigável com abas organizadas

## Requisitos

- Python 3.7 ou superior
- Bibliotecas listadas em `requirements.txt`

## Instalação

1. Clone ou baixe este repositório
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Uso

### Executar com Python:

```bash
python pdf_validator.py
```

### Executar com py (Windows):

```bash
py pdf_validator.py
```

### Como usar:

1. Clique em "Selecionar PDF" para escolher um arquivo PDF
2. Clique em "Validar PDF" para iniciar a análise
3. Visualize os resultados nas diferentes abas:
   - **Informações Básicas**: Metadados e informações gerais
   - **Validação**: Resultados da validação com erros e avisos
   - **Conteúdo**: Texto extraído do PDF
   - **Relatório**: Relatório completo que pode ser salvo

## Gerando Executável

Para criar um executável standalone (.exe) que não precisa do Python instalado:

### Método 1 - Script Automático (Recomendado):

```bash
build.bat
```

### Método 2 - Manual:

1. Instale o PyInstaller:

```bash
py -m pip install pyinstaller
```

2. Gere o executável:

```bash
py -m PyInstaller pdf_validator.spec
```

3. O executável será criado em `dist/Validador_PDF.exe`

### Vantagens do Executável:

- ✅ Não precisa do Python instalado
- ✅ Pode ser distribuído facilmente
- ✅ Funciona em qualquer Windows
- ✅ Arquivo único e portátil

## Validações Realizadas

- Verificação de arquivo criptografado
- Contagem de páginas
- Análise de tamanho do arquivo
- Verificação de metadados (título, autor)
- Extração e análise de texto das páginas
- Detecção de páginas vazias ou ilegíveis

## Estrutura do Projeto

```
pdf-validator/
├── pdf_validator.py    # Aplicação principal
├── pdf_validator.spec  # Configuração do PyInstaller
├── build.bat          # Script para gerar executável
├── requirements.txt    # Dependências
├── dist/              # Executável gerado
│   └── Validador_PDF.exe
└── README.md          # Este arquivo
```

## Tecnologias Utilizadas

- **tkinter**: Interface gráfica
- **PyPDF2**: Manipulação de arquivos PDF
- **threading**: Processamento assíncrono
- **json**: Manipulação de dados
- **datetime**: Timestamps
- **PyInstaller**: Geração de executável

## Limitações

- PDFs criptografados não podem ser validados
- Arquivos muito grandes podem demorar para processar
- Alguns PDFs com formatação complexa podem ter problemas na extração de texto

## Contribuição

Sinta-se à vontade para contribuir com melhorias e correções!
