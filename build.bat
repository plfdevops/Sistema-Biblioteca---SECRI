@echo off
pip install pyinstaller
pyinstaller --onefile --windowed --name Biblioteca --icon=biblioteca.ico main.py
echo.
echo Executavel gerado em: dist\Biblioteca.exe
pause
