@echo off
setlocal enabledelayedexpansion

for %%i in ("%~dp0..") do set ROOT_DIR=%%~fi
if "%1"=="" (
    set BUNDLE_NAME=ngo_intel_bundle
) else (
    set BUNDLE_NAME=%1
)
set BUNDLE_DIR=%ROOT_DIR%\%BUNDLE_NAME%
set TMP_DIR=%ROOT_DIR%\.bundle_tmp
set VENV_DIR=%TMP_DIR%\venv_bundle

echo ==> Preparing bundle workspace
if exist "%BUNDLE_DIR%" rmdir /s /q "%BUNDLE_DIR%"
if exist "%TMP_DIR%" rmdir /s /q "%TMP_DIR%"
if exist "%ROOT_DIR%\%BUNDLE_NAME%.zip" del "%ROOT_DIR%\%BUNDLE_NAME%.zip"
mkdir "%BUNDLE_DIR%\scripts"
mkdir "%TMP_DIR%"

echo ==> Creating isolated virtual environment
python -m venv "%VENV_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r "%ROOT_DIR%\requirements.txt"
python -m pip freeze > "%TMP_DIR%\requirements.lock"
call "%VENV_DIR%\Scripts\deactivate.bat"

echo ==> Copying project files
copy "%ROOT_DIR%\README.md" "%BUNDLE_DIR%\"
copy "%ROOT_DIR%\requirements.txt" "%BUNDLE_DIR%\"
copy "%TMP_DIR%\requirements.lock" "%BUNDLE_DIR%\"
copy "%ROOT_DIR%\ngo_dashboard.py" "%BUNDLE_DIR%\"
copy "%ROOT_DIR%\master_scraper.py" "%BUNDLE_DIR%\"
copy "%ROOT_DIR%\master_scraper_data.py" "%BUNDLE_DIR%\"
copy "%ROOT_DIR%\master_scraper_viz.py" "%BUNDLE_DIR%\"

if not exist "%BUNDLE_DIR%\data" mkdir "%BUNDLE_DIR%\data"
robocopy "%ROOT_DIR%\data\demo_data" "%BUNDLE_DIR%\data\demo_data" /E /NFL /NDL /NJH /NJS /NC /NS
robocopy "%ROOT_DIR%\scripts" "%BUNDLE_DIR%\scripts_tmp" /E /NFL /NDL /NJH /NJS /NC /NS
if exist "%BUNDLE_DIR%\scripts" rmdir /s /q "%BUNDLE_DIR%\scripts"
ren "%BUNDLE_DIR%\scripts_tmp" scripts

if exist "%ROOT_DIR%\viz" (
  robocopy "%ROOT_DIR%\viz" "%BUNDLE_DIR%\viz" /E /NFL /NDL /NJH /NJS /NC /NS
)

if exist "%ROOT_DIR%\auth" (
  robocopy "%ROOT_DIR%\auth" "%BUNDLE_DIR%\auth" /E /NFL /NDL /NJH /NJS /NC /NS
  if exist "%BUNDLE_DIR%\auth\bluesky\config\auth.json" del "%BUNDLE_DIR%\auth\bluesky\config\auth.json"
)

echo ==> Embedding virtual environment
xcopy "%VENV_DIR%" "%BUNDLE_DIR%\.venv\" /E /I /Q
rmdir /s /q "%TMP_DIR%"

echo ==> Creating launch scripts
copy "%ROOT_DIR%\packaging\run_dashboard.sh" "%BUNDLE_DIR%\scripts\run_dashboard.sh"
copy "%ROOT_DIR%\packaging\run_dashboard.bat" "%BUNDLE_DIR%\scripts\run_dashboard.bat"

echo ==> Creating zip archive
cd /d "%ROOT_DIR%"
if exist %BUNDLE_NAME%.zip del %BUNDLE_NAME%.zip
python -m zipfile -c %BUNDLE_NAME%.zip %BUNDLE_NAME%

echo Bundle ready at %ROOT_DIR%\%BUNDLE_NAME%.zip
