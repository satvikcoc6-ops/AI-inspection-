"""Create a portable source bundle without virtualenvs, caches, or inspection data."""
from pathlib import Path
import zipfile

root=Path(__file__).resolve().parents[1]
destination=root/'output'/'AutoInspect_Hackathon.zip'
files=['app.py','cloud_storage.py','model_service.py','reports.py','integrations.py','predict.py',
       'runtime_compat.py','runtime_stubs.json','SKIMAGE_LICENSE.txt',
       'requirements.txt','requirements-lock.txt','README.md','VALIDATION.md',
       'setup.ps1','START_DASHBOARD.cmd','OPEN_GIT.cmd','.gitignore',
       '.python-version','.vercelignore','vercel.json','uv.toml']
with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as archive:
    for name in files:
        archive.write(root/name,'AutoInspect_AI_Pro/'+name)
    for directory in ('static','references','tests','tools'):
        for path in (root/directory).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                archive.write(path,'AutoInspect_AI_Pro/'+path.relative_to(root).as_posix())
    for name in ('dashboard-preview.jpg','pdf/sample-inspection-report.pdf'):
        archive.write(root/'output'/name,'AutoInspect_AI_Pro/output/'+name)
print(destination)
