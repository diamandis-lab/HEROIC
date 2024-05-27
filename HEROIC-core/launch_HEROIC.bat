

echo "Starting HEROIC EEG..."
set PATH_HEROIC=C:\Users\Lenovo\HEROIC\HEROIC-core

set d=%date:-=%
set t=%time::=%
set t=%t:.=%
set LOG_NAME=%d%_%t%.log


cd %PATH_HEROIC%


cmd /k "..\venv\bin\activate.bat & python main.py

