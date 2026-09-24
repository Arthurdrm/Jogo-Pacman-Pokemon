@echo off
REM ============================================================
REM  Build do PokePacman.exe (Ash Ketchum Edition) para Windows
REM ============================================================

echo [1/3] Instalando dependencias...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

echo [2/3] Gerando executavel standalone (Onefile) com PyInstaller...
python -m PyInstaller --onefile --noconsole --name "PokePacman" main.py

echo [3/3] Concluido com sucesso!
echo ============================================================
echo   Executavel standalone gerado em: dist\PokePacman.exe
echo ============================================================
pause
