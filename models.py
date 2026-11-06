"""Build measured-cell elevation grids from the original historical LAZ."""
from pathlib import Path
import csv
import io
import numpy as np
import laspy
from audit import ROOT, FILE, ROI, mask_roi

CELL = 5
MIN_POINTS = 3
SIZE = 40
CENTRES = (np.arange(SIZE) + 0.5) * CELL
MODEL = ROOT / 'outputs' / 'models.npz'


def build_models(source):
    counts = np.zeros(SIZE * SIZE, dtype=np.int64)
    maxima = np.full(counts.shape, -np.inf)
    ground_cells, ground_z = [], []
    with laspy.open(source) as reader:
        for points in reader.chunk_iterator(250_000):
            x, y, z = map(np.asarray, (points.x, points.y, points.z))
            valid = mask_roi(x, y) & np.isfinite(z) & ~np.asarray(points.withheld, dtype=bool)
            cells = (((y[valid] - ROI[1]) // CELL).astype(int) * SIZE
                     + ((x[valid] - ROI[0]) // CELL).astype(int))
            elevations = z[valid]
            np.add.at(counts, cells, 1)
            np.maximum.at(maxima, cells, elevations)
            ground = np.asarray(points.classification)[valid] == 2
            ground_cells.append(cells[ground])
            ground_z.append(elevations[ground])
    ids = np.concatenate(ground_cells) if ground_cells else np.empty(0, dtype=int)
    elevations = np.concatenate(ground_z) if ground_z else np.empty(0)
    ground_counts = np.bincount(ids, minlength=counts.size)
    order = np.argsort(ids)
    ends = np.cumsum(ground_counts)
    terrain = np.full(counts.shape, np.nan)
    for cell in np.flatnonzero(ground_counts >= MIN_POINTS):
        terrain[cell] = np.median(elevations[order[ends[cell]-ground_counts[cell]:ends[cell]]])
    surface = np.where(counts >= MIN_POINTS, maxima, np.nan)
    height = surface - terrain
    return {name: values.reshape(SIZE, SIZE) for name, values in
            dict(terrain=terrain, surface=surface, height=height,
                 counts=counts, ground_counts=ground_counts).items()}


def grid_csv(grids):
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(['easting_epsg31983_m', 'northing_epsg31983_m', 'all_count',
                     'ground_count', 'terrain_source_z_m', 'surface_source_z_m',
                     'surface_above_terrain_m'])
    for row, north in enumerate(CENTRES):
        for col, east in enumerate(CENTRES):
            values = [grids[name][row, col] for name in ('terrain', 'surface', 'height')]
            writer.writerow([ROI[0]+east, ROI[1]+north, grids['counts'][row,col],
                             grids['ground_counts'][row,col],
                             *(round(float(z), 3) if np.isfinite(z) else '' for z in values)])
    return stream.getvalue()


if __name__ == '__main__':
    grids = build_models(ROOT / 'data' / 'raw' / FILE)
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(MODEL, **grids)
    for name in ('terrain', 'surface', 'height'):
        print(f'{name}: {np.isfinite(grids[name]).sum():,} supported cells / {SIZE**2:,}')
