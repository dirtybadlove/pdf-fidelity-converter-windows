@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo First run: preparing the local Python environment...
  py -3 -m venv .venv 2>nul
  if errorlevel 1 python -m venv .venv
  if errorlevel 1 goto :setup_error
  ".venv\Scripts\python.exe" -m pip install --upgrade pip
  if errorlevel 1 goto :setup_error
  ".venv\Scripts\python.exe" -m pip install -e .
  if errorlevel 1 goto :setup_error
)

".venv\Scripts\python.exe" -m pdf_content_converter
exit /b %errorlevel%

:setup_error
echo.
echo Setup failed. Please check that Python 3 and internet access are available.
pause
exit /b 1

