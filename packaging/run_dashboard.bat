@echo off
setlocal

set ROOT_DIR=%~dp0..
if not exist "%ROOT_DIR%\.venv\Scripts\activate.bat" (
  echo Embedded virtual environment not found at %ROOT_DIR%\.venv
  exit /b 1
)

call "%ROOT_DIR%\.venv\Scripts\activate.bat"
streamlit run "%ROOT_DIR%\ngo_dashboard.py"
