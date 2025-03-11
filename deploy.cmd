@echo off

:: Setup
:: -----

:: Echo deployment info
echo Deployment started
echo Current directory: %CD%

:: Check if we are in the correct directory
IF NOT EXIST requirements.txt (
  echo Error: requirements.txt not found.
  exit /b 1
)

:: Main
:: ----

:: 1. Install Python packages
echo Installing Python packages...
call %PYTHONPATH%\python.exe -m pip install -r requirements.txt
IF !ERRORLEVEL! NEQ 0 (
  echo Failed to install Python packages. Error: !ERRORLEVEL!
  exit /b !ERRORLEVEL!
)
echo Python packages installed successfully.

:: 2. Make startup script executable (for Linux-based App Service)
if exist app_service_startup.sh (
  echo Making app_service_startup.sh executable...
  :: This will only work on Linux-based App Service plans
  call chmod +x app_service_startup.sh
)

echo Deployment completed successfully. 