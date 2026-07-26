@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  set "PYTHON_LAUNCHER=py -3"
) else (
  set "PYTHON_LAUNCHER=python"
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/4] Creating virtual environment...
  %PYTHON_LAUNCHER% -m venv .venv
  if errorlevel 1 goto :error
)

echo [2/4] Installing dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :error
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo [3/4] Downloading and verifying Parquet data...
".venv\Scripts\python.exe" scripts\download_data.py
if errorlevel 1 goto :error

echo [4/4] Opening JupyterLab...
".venv\Scripts\python.exe" -m jupyter lab case3_antifraud.ipynb
exit /b 0

:error
echo.
echo Setup stopped because the previous step failed.
pause
exit /b 1
