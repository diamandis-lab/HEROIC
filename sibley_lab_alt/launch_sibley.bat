
@echo off
echo "Starting Sibley EEG..."
set PATH_SIBLEY=C:\Users\Lenovo\sibley_38\sibley

set d=%date:-=%
set t=%time::=%
set t=%t:.=%
set LOG_NAME=%d%_%t%.log


cd %PATH_SIBLEY%
cmd /k "..\Scripts\activate.bat & python .\main.py > ..\session_logs\%LOG_NAME% 2>&1"

