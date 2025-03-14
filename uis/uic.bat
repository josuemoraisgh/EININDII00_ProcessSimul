@echo off
cd uis
CALL pyside6-uic main.ui -o ui_main.py
cd ..
cls
CALL "C:/Program Files/Python312/python.exe" c:/SourceCode/hrtSimulPython/main.py