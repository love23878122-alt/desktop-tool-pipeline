@echo off
rem Same as {{APP_FILE}}.bat but keeps a console open so error messages stay visible
cd /d "%~dp0"
"%~dp0python\python.exe" -X utf8 -m {{PKG}}
echo.
echo Exit code: %ERRORLEVEL%
pause
