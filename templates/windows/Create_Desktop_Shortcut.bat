@echo off
rem Creates "{{APP_NAME}}" shortcuts (Desktop + Start menu) with the app icon. Run once after unzipping;
rem run again if this folder is moved.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$d = '%~dp0'.TrimEnd('\');" ^
  "$ws = New-Object -ComObject WScript.Shell;" ^
  "foreach ($dir in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) {" ^
  "  $s = $ws.CreateShortcut((Join-Path $dir '{{APP_NAME}}.lnk'));" ^
  "  $s.TargetPath = (Join-Path $d 'python\pythonw.exe');" ^
  "  $s.Arguments = '-X utf8 -m {{PKG}}';" ^
  "  $s.WorkingDirectory = $d;" ^
  "  $s.IconLocation = (Join-Path $d '{{APP_FILE}}.ico') + ',0';" ^
  "  $s.Save() }"
if errorlevel 1 (
  echo Failed to create the shortcut. Please take a screenshot of this window.
) else (
  echo Done: "{{APP_NAME}}" shortcut created on the Desktop and in the Start menu.
)
pause
