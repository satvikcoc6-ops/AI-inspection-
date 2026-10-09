"""Local dashboard API. Start with: python -m uvicorn app:app --host 127.0.0.1 --port 8000"""
import csv
import io
import json
import logging
import os
from pathlib import Path
import sqlite3
import time
import uuid
import zipfile
from datetime import datetime, timezone

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageOps, UnidentifiedImageError
from model_service import service, CHECKPOINT
from reports import make_report

ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get('AUTOINSPECT_DATA', str(ROOT/'data')))
DATA.mkdir(parents=True, exist_ok=True)
Image.MAX_IMAGE_PIXELS = 20_000_000
app = FastAPI(title='AutoInspect AI Pro', docs_url='/api/docs')
app.mount('/static', StaticFiles(directory=ROOT/'static'), name='static')


def connect():
    con = sqlite3.connect(DATA/'history.sqlite3', timeout=30)
    con.execute('CREATE TABLE IF NOT EXISTS inspections (id TEXT PRIMARY KEY, created_at TEXT, result TEXT)')
    return con


@app.get('/')
def home():
    return FileResponse(ROOT/'static'/'index.html')


@app.get('/api/health')
def health():
    return {'checkpoint_available': CHECKPOINT.is_file(), 'model_loaded': service.model is not None,
            'model': service.name, 'device': 'CPU', 'integrations': {'yolo': 'planned', 'genai': 'planned'}}


@app.get('/api/history')
def history():
    with connect() as con:
        rows = con.execute('SELECT result FROM inspections ORDER BY created_at DESC LIMIT 500').fetchall()
    return [json.loads(row[0]) for row in rows]


@app.get('/api/history.csv')
def history_csv():
    out = io.StringIO()
    fields=['id','created_at','image_name','decision','normalized_anomaly_score','duration_ms']
    writer=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore')
    writer.writeheader()
    for result in history():
        # Prevent spreadsheet formulas in uploaded filenames.
        result['image_name'] = "'"+result['image_name'] if result['image_name'].startswith(('=','+','-','@')) else result['image_name']
        writer.writerow(result)
    return Response(out.getvalue(),media_type='text/csv',headers={'Content-Disposition':'attachment; filename="inspections.csv"'})


@app.get('/api/examples/{name}')
def example(name: str):
    if name not in {'good','bent','scratch'}:
        raise HTTPException(404,'Unknown sample')
    return FileResponse(ROOT/'references'/'examples'/f'{name}.png')


@app.post('/api/inspect')
def inspect(image: UploadFile = File(...)):
    content=image.file.read(12*1024*1024+1)
    if len(content)>12*1024*1024:
        raise HTTPException(413,'Image must be smaller than 12 MB.')
    try:
        with Image.open(io.BytesIO(content)) as opened:
            if opened.width*opened.height>20_000_000:
                raise HTTPException(413,'Image must be below 20 megapixels.')
            original=ImageOps.exif_transpose(opened).convert('RGB')
            original.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(422,'Please upload a valid PNG, JPEG, or WebP image.')
    started=time.perf_counter()
    run_id=uuid.uuid4().hex
    folder=DATA/run_id
    try:
        result, overlay, heat=service.predict(original)
        folder.mkdir()
        original.save(folder/'input.png')
        overlay.save(folder/'heatmap.png')
        import numpy as np
        np.save(folder/'anomaly_map.npy',heat,allow_pickle=False)
        result.update(id=run_id,created_at=datetime.now(timezone.utc).isoformat(),
                      image_name=Path(image.filename or 'upload.png').name[:180],
                      duration_ms=round((time.perf_counter()-started)*1000),
                      note='Research prototype; not validated for automotive acceptance decisions.')
        (folder/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        make_report(folder,result)
        with zipfile.ZipFile(folder/'results.zip','w',zipfile.ZIP_DEFLATED) as archive:
            for name in ('input.png','heatmap.png','anomaly_map.npy','result.json','report.pdf'):
                archive.write(folder/name,name)
        with connect() as con:
            con.execute('INSERT INTO inspections VALUES (?,?,?)',(run_id,result['created_at'],json.dumps(result)))
        return result
    except Exception:
        logging.exception('Inspection failed')
        raise HTTPException(503,'The model could not finish this inspection. Check the server log and run tools/doctor.py.')


@app.get('/api/inspections/{run_id}/{asset}')
def download(run_id: str, asset: str):
    if len(run_id)!=32 or any(c not in '0123456789abcdef' for c in run_id):
        raise HTTPException(404,'Inspection not found')
    if asset not in {'input.png','heatmap.png','result.json','report.pdf','results.zip','anomaly_map.npy'}:
        raise HTTPException(404,'Unknown asset')
    path=DATA/run_id/asset
    if not path.is_file():
        raise HTTPException(404,'Result not found')
    return FileResponse(path,filename=f'{run_id[:8]}-{asset}' if asset not in {'input.png','heatmap.png'} else None)
