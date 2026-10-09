"""Preserve scikit-image's runtime import stubs stripped by Python bundlers."""
import json
from pathlib import Path
import tempfile


def preserve_lazy_stubs():
    import lazy_loader
    if getattr(lazy_loader.attach_stub, '_autoinspect_compat', False):
        return
    original = lazy_loader.attach_stub

    def attach_stub(package_name, filename):
        source = Path(filename)
        stub = source if source.suffix == '.pyi' else source.with_suffix('.pyi')
        if not stub.exists() and package_name.startswith('skimage'):
            saved = json.loads(Path(__file__).with_name('runtime_stubs.json').read_text(encoding='utf-8'))
            if package_name in saved:
                cache = Path(tempfile.gettempdir())/'autoinspect-stubs'
                cache.mkdir(parents=True, exist_ok=True)
                stub = cache/f'{package_name}.pyi'
                stub.write_text(saved[package_name], encoding='utf-8')
                return original(package_name, str(stub))
        return original(package_name, filename)

    attach_stub._autoinspect_compat = True
    lazy_loader.attach_stub = attach_stub
