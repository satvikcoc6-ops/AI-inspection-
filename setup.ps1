$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path '.venv/Scripts/python.exe')) {
    $bundledPython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
    if (Test-Path $bundledPython) { & $bundledPython -m venv .venv } else { py -3.12 -m venv .venv }
    if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.12, then retry setup.ps1.' }
}
& .venv/Scripts/python.exe -m ensurepip --upgrade
& .venv/Scripts/python.exe -m pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cpu
if ($LASTEXITCODE -ne 0) { throw 'PyTorch installation failed.' }
& .venv/Scripts/python.exe -m pip install -r requirements-lock.txt --extra-index-url https://download.pytorch.org/whl/cpu
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
& .venv/Scripts/python.exe tools/doctor.py
if ($LASTEXITCODE -ne 0) { throw 'Model verification failed. See the error above.' }
Write-Host 'Setup complete. Double-click START_DASHBOARD.cmd.'
