"""Private Blob artifacts and immutable history entries for Vercel deployments."""
import json
import mimetypes
import os
import time
from concurrent.futures import ThreadPoolExecutor
from vercel import blob


def enabled():
    return bool(os.environ.get('VERCEL'))


def require_store():
    if not os.environ.get('BLOB_READ_WRITE_TOKEN'):
        raise RuntimeError('Connect the private Blob store with a read-write token enabled.')


def read(path):
    require_store()
    return blob.get(path, access='private', use_cache=False).content


def save(folder, result):
    require_store()
    for path in folder.iterdir():
        blob.put(f'inspections/{result["id"]}/{path.name}', path.read_bytes(),
                 access='private', content_type=mimetypes.guess_type(path.name)[0] or 'application/octet-stream')
    # Publish history last, so incomplete uploads never appear as completed runs.
    key = f'history/{9999999999999-int(time.time()*1000):013d}-{result["id"]}.json'
    blob.put(key, json.dumps(result).encode(), access='private', content_type='application/json')


def history():
    require_store()
    entries = blob.list_objects(prefix='history/', limit=500).blobs
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda item: json.loads(read(item.pathname)), entries))
    return sorted(results, key=lambda item: item['created_at'], reverse=True)
