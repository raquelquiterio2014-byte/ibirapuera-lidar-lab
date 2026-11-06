# Ibirapuera LiDAR Lab
For the final integrated release, see [V6 Forest Edition](V6.md).

For the current release, see [V2 Point Cloud Explorer](V2.md).


**V1.1 — Guided Data Audit | by Raquel Cruz**

An independent educational project exploring historical public airborne LiDAR over a 200 × 200 m portion of Ibirapuera Park, São Paulo, Brazil. It is separate from Taquaral Geo3D. The source collection is from 2017; the exact flight date of this tile is unverified.

## Start in PyCharm on Windows

1. Extract the ZIP completely (do not run inside the ZIP).
2. Open the `ibirapuera-lidar-lab` folder as a PyCharm project.
3. Select a **64-bit Python 3.11 or 3.12** interpreter and create a virtual environment.
4. In the PyCharm terminal, run:

```powershell
python -m pip install -r requirements.txt
python main.py
```

Streamlit opens the local application in your browser, normally at http://localhost:8501. If it does not open automatically, use the URL printed in the terminal. Stop the app with Ctrl+C. All processing is local; no API key, QGIS, GPU or paid service is needed. Internet is needed to install packages or restore the source download, not to explore bundled outputs.

In the sidebar, use **Project version** to open any dedicated screen from V1 to V6. Choose **V2 · Point Cloud Explorer** to access source RGB, custom class filters and interactive HTML export. The integrated view is also available from the same selector.

This repository includes the audit outputs, models and a 100,000-point preview. Download the original LAZ (about 31 MB) from its provider to rebuild the audit or verify all original release files:

```powershell
python audit.py --download
```

If `python` points to the wrong interpreter, run these commands with the Python executable from your PyCharm virtual environment. A missing module usually means the packages were installed in a different interpreter.

## What V1 delivers

- Streaming audit in 250,000-point chunks; SHA-256 provenance.
- Full input and study-area class counts.
- 5 m occupancy and ground-support grids (counts, not interpolated terrain).
- Reproducible bounded-memory uniform preview (seed 42).
- Browser-based class filtering, 3D inspection and JSON export.

The source contains 4,987,651 points. Study area bounds in externally assigned EPSG:31983 are X [330750, 330950), Y [7390400, 7390600). Half-open boundaries prevent duplicate boundary points in future adjacent crops. See `outputs/audit.json` for current computed counts; do not use preview counts as totals.

## Scientific limitations

The AWS input reports LAS 1.0, point format 3, and has no embedded CRS. The OpenTopography index describes this tile as LAS 1.2 in SIRGAS 2000 / UTM 23S. The application assigns EPSG:31983 from that external index; it does not pretend that this was read from the input header. AWS and OpenTopography copies should not be assumed byte-identical.

Vertical reference is unresolved: source Z is shown in metres without claiming orthometric or ellipsoidal altitude. A 0.01 m storage scale is not accuracy. Source classes 19 and 20 are intentionally unresolved. Class labels 2/5/6 are supplied classifications, not independently validated ground truth. Occupancy at 5 m is only a coarse coverage diagnostic. No biomass, flood forecast, individual-tree inventory or terrain model is claimed. No field measurements were used.

Orthophotos from 2017/2020 were checked during feasibility research but are not bundled. Their specific reuse conditions and native tile metadata remain pending. V1 does not download or display them.

## Sources and attribution

- São Paulo City Hall / GeoSampa, Mapa 3D Digital da Cidade: https://registry.opendata.aws/pmsp-lidar/
- Original LAZ: https://laz-m3dc-pmsp.s3.sa-east-1.amazonaws.com/MDS_color_3316-132.laz
- Collection documentation and external tile index: https://portal.opentopography.org/datasetMetadata?otCollectionID=OT.062020.31983.1
- Tile index: https://opentopography.s3.sdsc.edu/pc-bulk/BR17_SaoPaulo/BR17_SaoPaulo_TileIndex.zip
- Inspection report: https://portal.opentopography.org/lasReport?opentopoID=OTLAS.062020.31983.1

Source retrieved/inspected on 2026-10-27. Collection citation: São Paulo City Hall (PMSP) (2024), *Sao Paulo, Brazil Lidar Survey 2017*, distributed by OpenTopography, https://doi.org/10.5069/G9NV9GD1. Publication year is not acquisition year.

The AWS registry declares **GNU GPL v3.0** for the dataset. See `SOURCE_NOTICE.md` and the bundled license. Project source code is also distributed under GPL-3.0-or-later. This statement does not assign a license to unrelated orthophotos or third-party dependencies.

## Validation

```powershell
python -m unittest discover -s tests
```

See `docs/VALIDATION.md` for checks actually performed in the delivery environment. Windows and your notebook's performance must still be checked locally.

## Next versions

V2: richer point-cloud exploration; V3: supported terrain/surface grids; V4: height above ground; V5: licensed, aligned historical imagery comparison; V6: reproducible final learning release. These are planned, not implemented in V1.

## V1.1 interface update

Navigation now uses five pages: 3D Explorer, Study Location, Data Coverage, Sources & Limits and Version Roadmap. The default view shows classified ground, tall vegetation and built structures; unresolved source codes remain available under All source classes and included in full audit counts.

Choose a landscape preset, viewpoint and display detail to explore. Source elevation means source Z, not height above ground. Study Location uses an OpenStreetMap basemap and the exact transformed study boundary. Tiles need internet; offline coordinate bounds remain available. No camera or live imagery module is planned.

### Updating on Windows
Stop the running app with Ctrl+C. Extract this complete package into a separate folder, open it in PyCharm and select your existing project interpreter or create a new environment. Install requirements and run `python main.py`. Keep the existing V1 folder as a backup.

### Six-version roadmap
V1 (including V1.1): audited data and guided learning interface. V2: expanded cloud exploration, RGB and exports. V3: terrain/surface models with support masks. V4: heights above ground and profiles where supported. V5: historical imagery comparison, conditional on source terms and alignment. V6: final reproducible learning release.

## V1.1.2 — Forest Edition
Dark forest-green theme with real Ibirapuera photographs as local wallpaper. Open the sidebar to choose trees (default), lake or solid green. Photos are decorative historical views; see assets/PHOTO_CREDITS.md. No live image module. The data and audit calculations are unchanged. The wallpaper works offline.

Stop the previous server (Ctrl+C), extract this complete package into a new folder and run `python main.py` from that folder after selecting the Python environment with the requirements installed.
