import PyPDF2

pdf_path = r'Teste_Montagem_Oxymag FDA_NS0084.pdf'

with open(pdf_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    for i, page in enumerate(reader.pages):
        print(f'--- Página {i+1} ---')
        text = page.extract_text()
        print(text)
        print('\n') 