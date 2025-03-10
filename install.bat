@REM Python -m venv venv
CALL python.exe -m pip install --upgrade pip
CALL pip install pandas
CALL pip install asteval
CALL pip install control
CALL pip install pyside6
@REM pyside6-uic main.ui -o ui_main.py