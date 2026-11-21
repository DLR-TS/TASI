# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment setup

This project uses `uv`, not raw `pip`, and expects to run from a project-local `.venv` — never install into a global/system Python (editable installs there have gone stale/broken before). Set up with:

```
uv sync --extra all --group test --group dev
```

Extras (`geo`, `io`, `visualization`, `wms`, `database`, `performance`, `osi`, or `all`) are optional and lazily gated via `has_extra()` — e.g. `tasi.io` raises `ImportError` immediately if the `io` extra isn't installed. If you're touching `tasi.io`, `tasi.smos`, or anything geo-related, you need at least `--extra all` (or `io`+`geo`).

On Windows, invoke the venv's interpreter directly: `.venv/Scripts/python.exe`.

## Running tests

`pytest` config (`testpaths = ["src/tests"]`, `addopts = "--doctest-modules"`) is in `pyproject.toml`. Run with `uv run pytest src/tests` or `.venv/Scripts/python.exe -m pytest src/tests`.

**Locally, several test files hang** because they need infrastructure CI has but a local sandbox usually doesn't: `src/tests/dlr/*`, `src/tests/io/test_orm/*` (needs a real Postgres DB — `psycopg` will block on `connect()` with no timeout), and anything using `DatasetTestCase` from `src/tests/__init__.py` (`test_geo.py`, `test_indexing.py`, `test_manipulation.py` — downloads a real DLR-UT dataset over the network). When testing locally without that infra, scope pytest to the files you're actually changing, or add `pytest-timeout` (`--timeout=60 --timeout-method=thread`) to bound a hang rather than trusting `--ignore` alone.

## Data model

`Trajectory`, `Pose`, and `*Dataset` are pandas DataFrames with a MultiIndex on both axes:
- Rows: `(timestamp, id)`.
- Columns: `(attribute, subfield)`, e.g. `tj.position.easting`, `tj.velocity.northing`, `tj.dimension.length`, `tj.acceleration.easting`.

**Pandas index-alignment gotcha**: combining two *different* trajectories arithmetically (e.g. `challenger.position.easting - ego.position.easting`) aligns on the full `(timestamp, id)` index. Since ego/challenger carry different `id` values, this silently produces a doubled-length, all-NaN result instead of an elementwise diff — not an error, just wrong. Always convert each side to `.to_numpy()` before combining values across two different trajectories.

## tasi.smos (surrogate measures of safety)

`SMOS` (scalar, one value per interaction) and `TimeSeriesSMOS` (one value per timestep) in `src/tasi/smos/base.py` are the two base classes. Every metric follows the same pattern: its own module in `src/tasi/smos/`, a `classmethod estimate(cls, ego: Trajectory, challenger: Trajectory, ...) -> <Metric>`, exported from `src/tasi/smos/__init__.py`. See `src/tasi/smos/pet.py` for the canonical example and `src/tests/smos/conftest.py` for the shared synthetic test fixtures.

Ground rules for adding or extending SMoS metrics (correctness must come from cited literature, not from other SMoS libraries; one metric per PR; hand-derived unit test values; real-data examples only from DLR-UT/DLR-HT, never highD) are in @PLAN.md — read it before starting SMoS work.

Known pre-existing bug: `PET.estimate(..., position=...)` throws a shape-mismatch error whenever the position reference resolves to a 3-column (easting/northing/altitude) `Position`, since the shapely intersection point is 2D. Doesn't surface with real DLR-loaded data (no altitude column there), but will with any synthetically-built `Position`-based reference.
