@echo off
cd uis
CALL pyside6-uic main.ui -o ui_main.py
CALL pyside6-uic dialog_value.ui -o ui_dialog_value.py
CALL pyside6-uic dialog_func.ui -o ui_dialog_func.py
CALL pyside6-uic dialog_tfunc.ui -o ui_dialog_tfunc.py
cd ..
cls
REM CALL "C:/Program Files/Python312/python.exe" c:/SourceCode/0II2/EININDII07_hrtSimulPython/main.py