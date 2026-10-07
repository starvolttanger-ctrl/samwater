@echo off
cd /d "%~dp0"
pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --onefile --windowed --name SAMWATER --collect-all customtkinter main.py
echo Done: dist\SAMWATER.exe
pause
