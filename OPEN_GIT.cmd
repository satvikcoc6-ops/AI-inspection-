@echo off
cd /d "%~dp0"
set "PATH=%~dp0PortableGit\cmd;%PATH%"
echo Git for this project is ready. Type git --version to check it.
cmd /k
