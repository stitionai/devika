@echo off

rem Check if python is installed
python --version | findstr /R "Python 3\.[1-9][0-9]*\." >nul
if %errorlevel% neq 0 (
    echo Python is not installed, downloading Python 3.10.11...
    PowerShell.exe -Command "irm https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe -OutFile python-3.10.11-amd64.exe"
    echo Download of Python 3.10.11 completed.

    echo Installing Python 3.10.11...
    python-3.10.11-amd64.exe /quiet InstallAllUsers=1 InstallLauncherAllUsers=1 PrependPath=1 Include_test=0
    echo Python 3.10.11 has been installed successfully.
) else (
    echo Python already installed.
)

where bun >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing Bun. Accept Administrator request
    PowerShell.exe -Command "Start-Process PowerShell -Verb RunAs -ArgumentList '-Command', 'irm bun.sh/install.ps1 | iex' -Wait"
    echo Bun is installed.
) else (
    echo Bun is already installed.
)

where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing Uv. Accept Administrator request
    PowerShell.exe -Command "Start-Process PowerShell -Verb RunAs -ArgumentList '-Command', 'irm https://astral.sh/uv/install.ps1 | iex' -Wait"
    echo Uv is installed.
) else (
    echo Uv is already installed.
)

rem Check if the virtual environment exists
if not exist .venv (
    echo Creating virtual environment...
    uv venv
)

rem Activate the virtual environment
echo Activating virtual environment...
start cmd /k ".venv\Scripts\activate & echo Installing Python dependencies... & uv pip install -r requirements.txt & playwright install & echo Starting AI server... & python devika.py"

rem Navigate to the UI directory
cd ui/

rem Install frontend dependencies
echo Installing frontend dependencies...
bun install

rem Launch the UI
echo Launching UI...
bun run start

rem Deactivate the virtual environment
echo Deactivating virtual environment...
deactivate