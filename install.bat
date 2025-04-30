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