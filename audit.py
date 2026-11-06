"""Reproducible, bounded-memory audit of one historical GeoSampa tile."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import urllib.request
import collections
import numpy as np
import laspy

ROOT = Path(__file__).resolve().parent
FILE = 'MDS_color_3316-132.laz'
URL = 'https://laz-m3dc-pmsp.s3.sa-east-1.amazonaws.com/' + FILE
ROI = (330750., 7390400., 330950., 7390600.)
LABELS = {2: 'Ground', 5: 'High vegetation', 6: 'Building', 9: 'Water',
          19: 'Unresolved source code 19', 20: 'Unresolved source code 20'}

def download(path):
    """Download atomically, preserving an existing input."""
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.part')
    try:
        with urllib.request.urlopen(URL, timeout=60) as response, temp.open('wb') as out:
            while block := response.read(1024 * 1024):
                out.write(block)
        with laspy.open(temp) as reader:
            if reader.header.point_count <= 0:
                raise ValueError('Empty point cloud')
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)

def mask_roi(x, y):
    # Half-open bounds avoid duplicate points when adjoining study areas are added.
    a, b, c, d = ROI
    return (x >= a) & (x < c) & (y >= b) & (y < d)

def build_audit(path, output, preview_limit=100000):
    if preview_limit < 1:
        raise ValueError('preview_limit must be positive')
    output.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    all_counts, roi_counts = collections.Counter(), collections.Counter()
    density = np.zeros((40, 40), dtype=np.int64)
    ground = np.zeros_like(density)
    # Priority reservoir: a reproducible uniform sample, bounded by preview_limit.
    rng = np.random.default_rng(42)
    sample = np.empty((0, 7), dtype=np.float64)
    keys = np.empty(0)
    lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
    with laspy.open(path) as reader:
        h = reader.header
        crs = h.parse_crs()
        header = dict(version=str(h.version), point_format=h.point_format.id,
                      point_count=h.point_count, scales=h.scales.tolist(),
                      bounds_min=h.mins.tolist(), bounds_max=h.maxs.tolist(),
                      embedded_crs=crs.to_string() if crs else None)
        has_rgb = {'red', 'green', 'blue'}.issubset(h.point_format.dimension_names)
        for p in reader.chunk_iterator(250000):
            classes = np.asarray(p.classification)
            all_counts.update(map(int, classes))
            x, y, z = np.asarray(p.x), np.asarray(p.y), np.asarray(p.z)
            m = mask_roi(x, y)
            if not m.any():
                continue
            xyz = np.column_stack((x[m], y[m], z[m]))
            cls = classes[m]
            lo = np.minimum(lo, xyz.min(axis=0)); hi = np.maximum(hi, xyz.max(axis=0))
            roi_counts.update(map(int, cls))
            col = ((xyz[:, 0] - ROI[0]) // 5).astype(int)
            row = ((xyz[:, 1] - ROI[1]) // 5).astype(int)
            np.add.at(density, (row, col), 1)
            np.add.at(ground, (row[cls == 2], col[cls == 2]), 1)
            rgb = (np.column_stack((p.red[m], p.green[m], p.blue[m]))
                   if has_rgb else np.zeros((len(cls), 3), dtype=np.uint16))
            values = np.column_stack((xyz, cls, rgb))
            sample = np.concatenate((sample, values))
            keys = np.concatenate((keys, rng.random(len(values))))
            if len(keys) > preview_limit:
                keep = np.argpartition(keys, preview_limit - 1)[:preview_limit]
                sample, keys = sample[keep], keys[keep]
    count = sum(roi_counts.values())
    if not count:
        raise ValueError('No points intersect the study area; check input and CRS.')
    report = dict(project='Ibirapuera LiDAR Lab', version='1.0.0',
        generated_utc=datetime.now(timezone.utc).isoformat(), source_url=URL,
        input_file=path.name, bytes=path.stat().st_size, sha256=digest.hexdigest(),
        header=header, working_crs='EPSG:31983',
        crs_basis='External OpenTopography tile index; not embedded in inspected AWS file',
        acquisition='2017 collection; exact tile acquisition date unverified',
        vertical_reference='Unresolved; do not label Z as orthometric or ellipsoidal height',
        roi=dict(bounds=list(ROI), boundary_rule='min inclusive, max exclusive', area_m2=40000,
                 point_count=count, density_all_returns_per_m2=count/40000,
                 bounds_min=lo.tolist(), bounds_max=hi.tolist()),
        tile_classes=dict(sorted(all_counts.items())), roi_classes=dict(sorted(roi_counts.items())),
        coverage=dict(cell_size_m=5, cells=1600, occupied_cells=int((density>0).sum()),
                      empty_cells=int((density==0).sum()),
                      ground_supported_cells=int((ground>0).sum()),
                      note='An occupied 5 m cell does not prove complete coverage or accuracy.'),
        preview=dict(points=len(sample), seed=42, method='uniform random priority reservoir'),
        limitations=['Historical educational study; no field validation.',
                      'Codes 19 and 20 remain unresolved; no modern ASPRS meaning assumed.',
                      'Point density is not spatial resolution or positional accuracy.',
                      'No terrain interpolation, tree inventory or change detection in V1.'])
    (output/'audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    np.savez_compressed(output/'preview.npz', points=sample[:, :4], rgb=sample[:, 4:].astype(np.uint16) if has_rgb else np.empty((0, 3), dtype=np.uint16), coverage=density, ground=ground)
    return report

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download', action='store_true')
    args = parser.parse_args()
    path = ROOT/'data/raw'/FILE
    if args.download:
        download(path)
    if not path.exists():
        parser.error('Input missing. Run: python audit.py --download')
    report = build_audit(path, ROOT/'outputs')
    print(json.dumps(dict(roi=report['roi'], coverage=report['coverage']), indent=2))

if __name__ == '__main__':
    main()
