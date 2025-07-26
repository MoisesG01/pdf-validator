@echo off
echo ========================================
echo    Gerando Executavel - Validador PDF
echo ========================================
echo.

REM 1. Cria e ativa ambiente virtual
if not exist .venv (
    py -m venv .venv
)
call .venv\Scripts\activate

echo 2. Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

echo.
echo 3. Gerando executavel...
py -m PyInstaller pdf_validator.spec

echo.
echo 4. Verificando resultado...
if exist "dist\Validador_PDF.exe" (
    echo ✅ Executavel criado com sucesso!
    echo 📁 Local: dist\Validador_PDF.exe
    echo 📏 Tamanho: 
    dir "dist\Validador_PDF.exe" | find "Validador_PDF.exe"
) else (
    echo ❌ Erro ao criar executavel!
)

echo.
echo ========================================
pause 