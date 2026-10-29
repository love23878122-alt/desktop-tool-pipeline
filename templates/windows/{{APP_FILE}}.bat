@echo off
rem Start {{APP_NAME}} (desktop window, no console)
cd /d "%~dp0"
start "" "%~dp0python\pythonw.exe" -X utf8 -m {{PKG}}
