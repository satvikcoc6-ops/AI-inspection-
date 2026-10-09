@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run powershell -ExecutionPolicy Bypass -File setup.ps1 first.
  pause
  exit /b 1
)
echo AutoInspect dashboard: http://127.0.0.1:8000
echo Keep this window open. Press Ctrl+C to stop the dashboard.
".venv\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8000
pause
