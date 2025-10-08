@echo off
REM NGO Intelligence Platform - Windows One-Click Installer
REM This script provides the easiest way to install and run the platform on Windows

title NGO Intelligence Platform - Installer

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    🏛️  NGO Intelligence Platform  🏛️                      ║
echo ║                          One-Click Installer                                ║
echo ╠══════════════════════════════════════════════════════════════════════════════╣
echo ║  Automatic Setup  ^|  Dependencies  ^|  Verification  ^|  🎯 Ready    ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is available
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Please install Python 3.8+ first.
    echo Download from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python found
python --version

REM Check if we're in the right directory
if not exist "setup_platform.py" (
    echo setup_platform.py not found. Please run this script from the project directory.
    echo.
    pause
    exit /b 1
)

REM Run the setup
echo.
echo Starting automated setup...
python setup_platform.py --auto

REM Check if setup was successful
if %errorlevel% equ 0 (
    echo.
    echo Installation Complete!
    echo.
    echo Next steps:
    echo   1. Launch dashboard: start_platform.bat dashboard
    echo   2. Or run data collection: start_platform.bat data
    echo   3. Access dashboard at: http://localhost:8501
    echo.
    echo For more options, see QUICK_START_GUIDE.md
    echo.
    
    REM Ask if user wants to launch dashboard
    set /p response="Launch dashboard now? (y/n): "
    if /i "%response%"=="y" (
        echo Launching dashboard...
        start_platform.bat dashboard
    )
) else (
    echo Installation failed. Please check the error messages above.
    echo For help, see the troubleshooting guides in the project directory.
    echo.
    pause
    exit /b 1
)

echo.
pause
