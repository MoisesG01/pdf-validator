@echo off
echo ========================================
echo    Gerando Executavel - Validador PDF
echo ========================================
echo.

echo 1. Instalando dependencias...
py -m pip install -r requirements.txt
py -m pip install pyinstaller

echo.
echo 2. Gerando executavel...
py -m PyInstaller pdf_validator.spec

echo.
echo 3. Verificando resultado...
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