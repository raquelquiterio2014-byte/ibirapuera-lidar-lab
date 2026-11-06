# V1 validation — 2026-10-27

Executed in the delivery environment (Linux, Python 3.12):

- Complete real source LAZ read in 250,000-point chunks.
- Header: 4,987,651 points; half-open ROI: 665,333 points.
- 5 m grid: 1,600 occupied cells; 1,235 cells with class-2 ground support.
- Output class totals equal grid totals; ground totals agree.
- Preview capped at 100,000 points and contained within ROI.
- Unit tests check boundary handling and real-data consistency.
- Streamlit AppTest passed initial rendering, ground-only class filtering, empty class selection and ground coverage selection without application exceptions.
- Python compilation passed.

Not yet tested: Windows launch, visual browser/GPU rendering, your 8 GB notebook's performance or fresh Windows dependency installation. Initial display is 30,000 points, adjustable to 100,000. Processing is local; the app does not upload data.

The earlier feasibility count (665,403) included outer boundaries. The production half-open definition excludes 70 east/north boundary points, yielding 665,333. This is a boundary convention, not a data revision.

Known provenance issues: missing embedded CRS, LAS version discrepancy between AWS and external index, unresolved vertical reference and codes 19/20. These are disclosed in the interface.

## V1.1 checks — 2026-10-30

Streamlit AppTest passed all five navigation pages, the ground/vegetation/structures/all-classes presets and elevation colouring without exceptions. Both existing data/boundary tests passed; compilation passed. Local server startup succeeded. A visual browser screenshot could not be completed because the test environment has no installed Playwright Chromium binary. Browser/GPU rendering and online basemap tile availability must be checked on the user's computer. Original source and audit outputs were preserved.

## V1.1.2 Forest Edition
Wallpaper options (trees, lake, solid forest green) and all navigation pages passed Streamlit AppTest. Existing data tests passed. Real source photographs were inspected, with authors, capture dates and CC0 terms recorded in assets/PHOTO_CREDITS.md. Visual browser rendering remains to be checked on Windows; automated Chromium download in the delivery environment failed. Scientific data and outputs are unchanged.
