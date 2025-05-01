@REM Python -m venv venv
CALL python.exe -m pip install --upgrade pip
CALL pip install pandas
CALL pip install pyserial
CALL pip install asteval
CALL pip install control
CALL pip install pyside6
CALL pip install openpyxl
CALL pip install xlrd
CALL pip install qtawesome
CALL pip install PyOpenGL 
CALL pip install pyinstaller
CALL pip uninstall pymodbus
CALL pip install pymodbus==3.3.0
CALL pip install PyOpenGL-accelerate

@REM pyside6-uic main.ui -o ui_main.py
@REM pyinstaller --onefile --add-data "db/banco.db;db" --windowed --name processSimul main.py

@REM pip install nuitka
@REM No menu Iniciar, busque por “x64 Native Tools Command Prompt for VS 2022” (ou equivalente à sua versão).
@REM python -m nuitka --standalone --onefile --output-dir=py_build --experimental=use_pefile --experimental=use_pefile_recurse --experimental=use_pefile_fullrecurse --enable-plugin=pyside6 --windows-console-mode=disable --include-data-file="db/banco.db=db/banco.db" --jobs=4 --output-filename=processSimul.exe main.py
