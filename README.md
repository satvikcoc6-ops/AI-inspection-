# AutoInspect AI Pro

A local hackathon dashboard using the supplied **trained PatchCore checkpoint**. Upload a component image, run AI, compare the original with its anomaly overlay, review its normalized score and decision, and download a PDF or complete results bundle.

## Run on this computer

Double-click **START_DASHBOARD.cmd**, then open **http://127.0.0.1:8000**. Keep the terminal window open while using the dashboard. It runs only on this computer. No GPU, account, or API key is needed.

If dependencies need installation:

```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1
```

The setup script uses Python 3.12, creates an isolated `.venv`, installs a matched CPU pair (`torch==2.6.0`, `torchvision==0.21.0`), installs the dashboard requirements, and checks all three samples. Internet is needed for first installation. Once installed, inference and reports work offline; fonts fall back to local system fonts.

Manual startup:

```powershell
.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000
```

## Demo flow

1. Select **Normal nut**, then **Run AI inspection**.
2. View its score and NORMAL decision. Switch between heatmap and original.
3. Select **Bent nut**, then run again to demonstrate REVIEW and its anomaly response.
4. Download **PDF report** or **All results** (input, overlay, raw anomaly array, JSON, PDF).
5. Open **Inspection history**, filter/search saved inspections, reopen a result, or export CSV.
6. Show **Model & integrations** to explain the model and future provider contracts.

The scratch sample is a documented model miss. Use it to explain the need for human review and representative validation, not to claim scratch detection.

## What was fixed

- The original dashboard expected `predict.py` and the checkpoint beside `app.py`, although the supplied projects were separate. Model assets now have an explicit project-relative location.
- Its field lookup omitted the predictor's `normalized_anomaly_score` and `status`, so it displayed “See JSON” instead of the actual output. The API and dashboard now share an explicit result schema.
- Every original inspection spawned a new process and reloaded the checkpoint. The model now stays cached and inference is serialized for consistent CPU execution.
- CPU dependencies are pinned together; CUDA is unnecessary. The original environment versions are preserved in `references/evaluation.json` for provenance.
- Checkpoint resize interpolation strings are adapted to torchvision enums. Inference uses the checkpoint's original preprocessing transform, preserving antialiasing and the supplied sample decisions.
- SQLite history persists across server restarts. Reports and images remain downloadable from `data/<inspection-id>/`.
- Invalid and oversized uploads return useful errors. Failed predictions do not create successful history entries. Filenames are rendered as text and escaped in PDF output.
- No public Gradio sharing tunnel is created.

## Architecture

- `app.py`: FastAPI routes, uploads, SQLite persistence, exports and downloads.
- `model_service.py`: original Anomalib checkpoint, original preprocessing and postprocessing, CPU inference, fixed-scale heatmap overlay.
- `reports.py`: one-page PDF inspection report.
- `static/`: responsive dashboard; no frontend build process required.
- `integrations.py`: typed `DefectDetector` and `ExplanationProvider` contracts for future YOLO and GenAI providers. Neither integration is active or simulated.
- `references/`: copies of supplied model, examples, evaluation and provenance files. The Downloads folders are untouched.
- `tools/doctor.py`: real-model diagnostics.
- `requirements-lock.txt`: exact installed environment (including testing tools); use after installing the CPU PyTorch pair for reproducibility on Windows/Python 3.12.
- `/api/docs`: interactive API documentation.

History and generated files stay on the local disk. Back up `data/` to retain inspections. The history API displays the most recent 500 records; CSV exports that same window. The first prediction includes model import/load time and takes longer than later runs.

## Validation

```powershell
.venv\Scripts\python.exe -m pip install pytest httpx pypdf
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe tools/doctor.py
```

Tests run real inference on good, bent and scratch samples; compare scores with supplied saved outputs; verify decisions, history, PDF content, ZIP assets, upload errors and failure handling. See `VALIDATION.md` for the actual observed results.

## Model scope and attribution

PatchCore with ResNet18 layer2/layer3 features, 1% coreset, three neighbors; 220 normal MVTec AD metal-nut training images. The supplied custom held-out evaluation reports image AUROC 0.983 and F1 0.964 (28 validation, 87 test images). This project does not independently reproduce those dataset-wide metrics or retrain the checkpoint.

The normalized score is **not a probability or physical defect severity**. NORMAL means below the model anomaly threshold; REVIEW means anomaly detected. Neither certifies automotive acceptance or identifies defect categories. Arbitrary car photos are outside the model's training domain.

MVTec AD and supplied sample derivatives: **CC BY-NC-SA 4.0**, educational/noncommercial use. Retain the attribution and applicable terms in `references/README.md`. Anomalib: Apache-2.0. Checkpoints contain serialized Python objects; this app loads only the fixed, supplied local checkpoint and does not accept model uploads.

## Documentation used

- [Anomalib PatchCore reference](https://anomalib.readthedocs.io/en/lib-v2.5.1/markdown/guides/reference/models/image/patchcore.html)
- [Anomalib postprocessing](https://anomalib.readthedocs.io/en/latest/markdown/guides/how_to/models/post_processor.html)
- [Official PyTorch version pairs](https://pytorch.org/get-started/previous-versions/)

The requested “ponytail” skill was not found among installed skills or the supplied folders, so it was not used.
