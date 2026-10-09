# Verification — 10 October 2026 (Asia/Kolkata)

Environment: Windows, Python 3.12.14, torch 2.6.0+cpu, torchvision 0.21.0+cpu, anomalib 2.6.0. Exact dependency versions are saved in `requirements-lock.txt`.

## Real checkpoint inference

| Sample | Supplied score | Repaired runtime score | Decision |
| --- | ---: | ---: | --- |
| good | 0.43523818 | 0.43523723 | NORMAL |
| bent | 0.89841497 | 0.89841461 | REVIEW |
| scratch | 0.47052062 | 0.47052032 | NORMAL (known missed defect) |

Maximum observed score difference is below 0.000001. Weights were not retrained or changed. Decisions are preserved.

The saved checkpoint's torchvision Resize interpolation used a string incompatible with torchvision 0.21; the loader maps it to the equivalent enum. The original preprocessing transform is used rather than its export variant, preserving resize antialiasing. Using the export transform changed scores and even the scratch decision; this was caught and corrected before delivery.

## Automated checks

`python -m pytest -q --tb=short`: **6 passed**, 3 upstream nonfatal warnings, 15.62 seconds.

- Real checkpoint inference and saved-output regression on all three samples.
- Successful inspections create SQLite records and downloadable PDF and ZIP files.
- PDFs contain the decision and fit on one page.
- ZIP includes input PNG, heatmap PNG, raw anomaly NumPy array, result JSON, and report PDF.
- Invalid image and unknown assets return useful errors.
- Oversized upload returns HTTP 413.
- Simulated model failure returns HTTP 503 and does not create a success record.

`pip check`: no broken requirements. Python compilation and JavaScript syntax checks passed.

## Browser verification

Verified through the Codex browser against the running local FastAPI server:

- Bent sample → run → heatmap, REVIEW, score 0.898.
- Original / heatmap switching.
- History search, NORMAL / REVIEW filter, and reopening a saved inspection.
- Upload a real good.png file from disk → run → NORMAL.
- Downloaded a PDF through the dashboard link.
- History survives a page reload.
- Desktop layout inspected at a 1440-pixel responsive breakpoint; no page horizontal overflow.
- Compact layout checked at the normal embedded-browser width.

The sample PDF was rendered with Poppler and visually reviewed: one page, legible text, correct metadata, both images visible, no clipping or overlapping content. `output/dashboard-preview.jpg` records the inspected dashboard; `output/pdf/sample-inspection-report.pdf` is the reviewed example report.

No full training dataset was supplied; dataset-wide metrics were not re-evaluated. YOLO and GenAI are extension contracts only. The requested ponytail skill was not available.
