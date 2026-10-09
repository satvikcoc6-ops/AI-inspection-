import io
import json
from pathlib import Path
import sys
import zipfile
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app as api


@pytest.fixture(params=['local', 'cloud'])
def client(tmp_path,monkeypatch,request):
    monkeypatch.setattr(api,'DATA',tmp_path)
    if request.param == 'cloud':
        from types import SimpleNamespace
        objects = {}
        monkeypatch.setenv('VERCEL', '1')
        monkeypatch.setenv('BLOB_READ_WRITE_TOKEN', 'test-placeholder')
        def put(path, body, **kwargs):
            assert kwargs['access'] == 'private'
            objects[path] = body
        def get(path, **kwargs):
            assert kwargs['access'] == 'private'
            if path not in objects:
                raise api.cloud_storage.blob.BlobNotFoundError()
            return SimpleNamespace(content=objects[path])
        monkeypatch.setattr(api.cloud_storage.blob, 'put', put)
        monkeypatch.setattr(api.cloud_storage.blob, 'get', get)
        monkeypatch.setattr(api.cloud_storage.blob, 'list_objects',
                            lambda **kw: SimpleNamespace(blobs=[SimpleNamespace(pathname=p) for p in sorted(objects) if p.startswith(kw['prefix'])][:kw['limit']]))
    else:
        monkeypatch.delenv('VERCEL', raising=False)
    return TestClient(api.app)


@pytest.mark.parametrize('sample,expected',[('good',False),('bent',True),('scratch',False)])
def test_real_model_and_artifacts(client,sample,expected):
    path=api.ROOT/'references'/'examples'/f'{sample}.png'
    response=client.post('/api/inspect',files={'image':(path.name,path.read_bytes(),'image/png')})
    assert response.status_code==200,response.text
    result=response.json()
    baseline=json.loads((path.parent/f'{sample}_result'/'result.json').read_text())
    assert result['is_anomaly']==expected
    assert result['normalized_anomaly_score']==pytest.approx(baseline['normalized_anomaly_score'],abs=0.003)
    assert result['score_is_probability'] is False
    assert len(client.get('/api/history').json())==1
    from pypdf import PdfReader
    pdf=client.get(f"/api/inspections/{result['id']}/report.pdf")
    reader=PdfReader(io.BytesIO(pdf.content))
    assert len(reader.pages)==1
    assert result['decision'] in reader.pages[0].extract_text()
    bundle=client.get(f"/api/inspections/{result['id']}/results.zip")
    with zipfile.ZipFile(io.BytesIO(bundle.content)) as z:
        assert set(z.namelist())=={'input.png','heatmap.png','anomaly_map.npy','result.json','report.pdf'}


def test_invalid_image_and_asset(client):
    assert client.post('/api/inspect',files={'image':('bad.png',b'not an image')}).status_code==422
    assert client.get('/api/history').json()==[]
    assert client.get('/api/inspections/invalid/report.pdf').status_code==404
    assert client.get('/api/examples/unknown').status_code==404


def test_oversize_upload(client):
    assert client.post('/api/inspect',files={'image':('large.png',b'x'*(12*1024*1024+1))}).status_code==413


def test_model_failure_does_not_save_success(client,monkeypatch):
    def broken(_):
        raise RuntimeError('intentional test failure')
    monkeypatch.setattr(api.service,'predict',broken)
    path=api.ROOT/'references'/'examples'/'good.png'
    assert client.post('/api/inspect',files={'image':('good.png',path.read_bytes())}).status_code==503
    assert client.get('/api/history').json()==[]
