# 2D Knapsack GA

Desktop application for experimenting with two-dimensional knapsack packing.
It loads rectangular tasks from `.txt`, runs a genetic optimizer, optionally compares the result with exhaustive search on small tasks, and visualizes layouts, generations, and statistics.

## Run

```powershell
.\.venv\Scripts\Activate.ps1
python -m knapsack2d.ui.app
```

## Tests

```powershell
$env:QT_QPA_PLATFORM='offscreen'
python -m pytest -q
```

## Documentation

- `docs/README.md`
- `docs/ui-guide.md`
- `docs/optimization-pipeline.md`
- `docs/variation-and-evolution.md`
- `docs/task-format.md`
