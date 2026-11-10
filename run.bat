@echo off
REM ROCCA — Control Cadena Cárnica SDE (Windows CMD wrapper)
REM Ejecuta el script de PowerShell.
REM Uso: run.bat [--no-build]

setlocal

if "%~1"=="--no-build" (
    powershell -ExecutionPolicy Bypass -File "%~dp0run.ps1" -NoBuild
) else (
    powershell -ExecutionPolicy Bypass -File "%~dp0run.ps1"
)

endlocal
