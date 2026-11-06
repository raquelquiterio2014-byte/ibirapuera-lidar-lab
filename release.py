"""Verify the bundled inputs and regenerate model products."""
import argparse
import hashlib
import json
from pathlib import Path
from models import ROOT

MANIFEST = ROOT / 'outputs' / 'release_manifest.json'
FILES = ('data/raw/MDS_color_3316-132.laz', 'outputs/audit.json',
         'outputs/preview.npz', 'outputs/models.npz')


def digest(path: Path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def verify():
    expected = json.loads(MANIFEST.read_text(encoding='utf-8'))
    return {name: (ROOT / name).is_file() and digest(ROOT / name) == expected.get(name)
            for name in FILES}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true', help='Record checksums after rebuilding outputs.')
    if parser.parse_args().record:
        MANIFEST.write_text(json.dumps({name: digest(ROOT / name) for name in FILES}, indent=2),
                            encoding='utf-8')
    checks = verify()
    for name, ok in checks.items():
        print(f'{"OK" if ok else "MISMATCH"}  {name}')
    raise SystemExit(0 if all(checks.values()) else 1)
