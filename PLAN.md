# PLAN: Extending `tasi.smos` with additional Surrogate Measures of Safety

This plan is written to be handed to Claude Code, one phase (or even one task) at a time, working directly in the `DLR-TS/TASI` repository. It is the outcome of a research pass on TASI's current state, comparable open-source tools, and community relevance for surrogate safety measures (SMoS) in traffic safety / automated-driving research. It replaces ad-hoc prompting with a fixed sequence of small, reviewable units of work.

## 0. Context (for Claude Code, read before starting any task)

- `tasi.smos` currently implements exactly one measure: `PET` (Post-Encroachment Time), in `src/tasi/smos/pet.py`.
- Its base class `SMOS` (`src/tasi/smos/base.py`) is a minimal Pydantic model with a single `value: float` field.
- The `PET.estimate(...)` pattern is the template for every new metric: a `classmethod estimate(...)` that takes `Trajectory` objects, does the computation, and returns a typed instance of the metric's own `SMOS` subclass.
- Every new metric is implemented as its own module in `src/tasi/smos/`, exported from `src/tasi/smos/__init__.py`, following that same pattern, so the public API stays consistent for users who already know `PET`.
- The comparable open-source tools identified during research are **SSMsOnPlane** (Yiru Jiao, TU Delft) and **CommonRoad-CriMe** (TU Munich). Neither is a good correctness reference to lean on automatically — see rule below.

## 1. Ground rules (apply to every phase)

1. **Correctness comes from the literature, not from other libraries.** Each metric's formula must be taken from a cited source (the original paper or an established review) and implemented directly from that definition. Do **not** use SSMsOnPlane or CommonRoad-CriMe output as a correctness oracle or cross-check during implementation — their code is not the specification, and their results are not to be assumed correct. Correctness is established through:
   - unit tests with **hand-derived / analytically computed** reference values on small synthetic trajectories (constant-velocity, constant-acceleration cases can be solved by hand or with basic kinematics — no external library needed), and
   - sanity checks on real trajectories (value ranges, units, edge cases such as zero relative velocity, parallel trajectories, no conflict point found, etc.).
2. **Real-data examples always use TASI's own datasets — DLR-UT or DLR-HT.** Never use highD (or any other third-party dataset that requires registration/is not freely redistributable) in examples, notebooks, or tests. `DLRUTDatasetManager` / the DLR-HT loader are the only real-world data sources used for demonstration and plausibility checks.
3. **One metric (or one clearly scoped infrastructure change) per Claude Code session/PR.** Small, independently reviewable diffs. Do not bundle multiple new metrics into one change.
4. **Every task ships with**: implementation, unit tests (hand-derived reference values + synthetic edge cases), docstrings, an `__init__.py` export, and a doc/example entry. No merge without green CI (pylint, pyright, pytest + coverage).
5. **SSMsOnPlane and CommonRoad-CriMe are only used once, at the very end (Phase 6), for a runtime/performance comparison** — not correctness. See Phase 6.

## 2. Phase overview

| Phase | Goal | Depends on |
|---|---|---|
| 0 | Infrastructure: extend `SMOS` base for time-series-valued metrics, add shared synthetic test fixtures | — |
| 1 | Longitudinal car-following metrics: TTC, MTTC, DRAC, THW | Phase 0 |
| 2 | Geometric conflict metrics: TAdv, TTC2D, ACT (reuse/extend PET's intersection logic) | Phase 0 |
| 3 | Aggregated severity indices: TET, TIT, CPI | Phase 1 (needs TTC time series) |
| 4 | Mixed-traffic / VRU-specific metrics using DLR-UT | Phase 1–2 |
| 5 | Real-data plausibility notebooks on DLR-UT / DLR-HT | after each of Phase 1–4 has ≥1 metric merged |
| 6 | Performance benchmark vs. SSMsOnPlane / CommonRoad-CriMe (speed only) + community visibility (JOSS, README, awesome-lists) | after Phase 1–4 substantially done |

## 3. Phase 0 — Infrastructure

**Task 0.1 — Extend the `SMOS` base class**

Prompt for Claude Code:

> Read `src/tasi/smos/base.py`, `src/tasi/smos/pet.py`, and the `Trajectory` class under `src/tasi/trajectory/`. `PET` is scalar (one value per pair of trajectories). Several upcoming metrics (TTC, DRAC, THW) are time-series-valued: one value per timestep of an interaction. Design and implement an extension to `SMOS` (or a sibling base class, e.g. `TimeSeriesSMOS`) that supports this without breaking `PET`. Keep the same `estimate(...)`-classmethod convention. Do not implement any new metric in this task — infrastructure only.

**Task 0.2 — Shared test fixtures**

Prompt for Claude Code:

> Add a pytest fixture module (e.g. `tests/smos/conftest.py` or `tests/fixtures/trajectories.py`) providing synthetic two-participant `Trajectory` pairs for the three canonical conflict geometries used by SMoS literature: (a) car-following / rear-end (collinear, closing speed), (b) crossing/turning (paths intersect at an angle), (c) no-conflict / diverging paths. Each fixture must expose exact, hand-computable kinematics (constant velocity or constant acceleration, documented in a comment) so that later unit tests can assert exact expected values.

## 4. Phase 1 — Longitudinal core metrics

Implement one per task, each as its own module `src/tasi/smos/<name>.py`, using the car-following fixture from Task 0.2.

| Task | Metric | Definition source | Notes |
|---|---|---|---|
| 1.1 | **TTC** (Time-to-Collision) | Hayward (1972) | Baseline metric; implement first, fully vectorized (numpy), no per-timestep Python loops |
| 1.2 | **THW** (Time Headway) | standard traffic-flow definition | Simplest metric; good second task to confirm the Phase 0 base class works |
| 1.3 | **MTTC** (Modified TTC) | Ozbay et al. (2008) | Extends TTC with acceleration term; reuse TTC's structure where sensible |
| 1.4 | **DRAC** (Deceleration Rate to Avoid Crash) | Cooper (1984) | |

Each task's prompt should follow this template:

> Implement `<Metric>(TimeSeriesSMOS)` in `src/tasi/smos/<metric>.py`, following the `estimate(...)` pattern from `pet.py` (or `ttc.py` once it exists). Definition: `<insert formula and citation>`. Use vectorized numpy operations over the trajectories' position/velocity arrays — no Python-level loops over timesteps. Add unit tests in `tests/smos/test_<metric>.py` using the Phase-0 fixtures with hand-derived expected values, plus edge cases (zero relative velocity, diverging trajectories, single-timestep trajectories). Export from `src/tasi/smos/__init__.py`. Add a docstring with the formula and citation, and a short entry in the Sphinx docs.

## 5. Phase 2 — Geometric conflict metrics

These extend PET's intersection-point logic rather than the car-following fixture.

| Task | Metric | Definition source |
|---|---|---|
| 2.1 | Extract shared intersection-point logic from `pet.py` into a reusable helper (e.g. `_conflict_point()` in `base.py` or a new `geometry.py`) | refactor, no new metric |
| 2.2 | **TAdv** (Time Advantage) | SMoS literature (e.g. Hydén, 1987 conflict-technique context) |
| 2.3 | **TTC2D** / generalized TTC for non-collinear paths | Allen et al. / Sultan-style generalization |
| 2.4 | **ACT** (Anticipated Collision Time) | SMoS review literature |

Task 2.1 must land before 2.2–2.4 to avoid duplicating PET's geometry code.

## 6. Phase 3 — Aggregated severity indices

Only start once at least TTC (Task 1.1) exists, since these build on a TTC time series.

| Task | Metric | Definition source |
|---|---|---|
| 3.1 | **TET** (Time-Exposed TTC) | Minderhoud & Bovy (2001) |
| 3.2 | **TIT** (Time-Integrated TTC) | Minderhoud & Bovy (2001) |
| 3.3 | **CPI** (Crash Potential Index) | Cunto & Saccomanno (2008) |

## 7. Phase 4 — Mixed-traffic / VRU-specific metrics

Uses DLR-UT specifically (it is the only dataset with pedestrians/cyclists).

| Task | Description |
|---|---|
| 4.1 | Minimum vehicle–VRU distance over time as a standalone SMoS |
| 4.2 | VRU-adapted PET/encroachment-time variant (different spatial tolerance than vehicle–vehicle) |
| 4.3 | Document, per metric already implemented, whether its underlying kinematic assumptions (e.g. bounded deceleration) still hold for pedestrians/cyclists; flag any that don't rather than silently misapplying them |

## 8. Phase 5 — Real-data plausibility checks (not correctness validation)

For each metric merged in Phases 1–4, once there are at least 3–4 metrics implemented, add a notebook under `doc/examples/` that:

- loads a sample from **DLR-UT or DLR-HT** via `DLRUTDatasetManager` (or the equivalent DLR-HT loader),
- computes the metric(s) on real interactions,
- checks plausibility: value ranges are physically sensible, distributions look reasonable, no NaNs/infs on well-formed input, known-safe interactions produce "safe" values and known-close interactions produce "critical" values.

This step is about catching implementation bugs and unrealistic outputs on real data — it is explicitly **not** a cross-check against another library's numbers.

## 9. Phase 6 — Benchmarking and community visibility (final phase)

**Task 6.1 — Performance benchmark (speed only, not correctness)**

Prompt for Claude Code:

> Once Phases 1–4 cover a reasonable set of metrics, write a benchmark script/notebook that measures **runtime only** — TASI's `tasi.smos` implementations vs. equivalent metrics in SSMsOnPlane and, where applicable, CommonRoad-CriMe — on the same input: a trajectory sample from **DLR-UT or DLR-HT**, converted into whatever input format each comparison library expects. Report wall-clock time and scaling behavior (e.g. number of trajectory pairs vs. runtime). Do **not** compare or reconcile the numeric output values between libraries — this benchmark is about speed, not correctness.

**Task 6.2 — Visibility**

- README table listing which SMoS TASI supports (with badges).
- Short paper submission to JOSS (Journal of Open Source Software).
- Listing in relevant "awesome" lists (e.g. awesome-traffic-safety) and linking from the ICTCT SMoS Library context.
- Leave 2–3 missing metrics tagged as "good first issue" to invite external contributions.

## 10. Suggested execution order

1. Phase 0 (0.1, 0.2)
2. TTC (1.1) → THW (1.2) → MTTC (1.3) → DRAC (1.4)
3. Geometry refactor (2.1) → TAdv (2.2) or TTC2D (2.3)
4. First plausibility notebook (Phase 5) once 3–4 metrics exist — don't wait until everything is done
5. Remaining Phase 2/3/4 metrics as needed
6. Phase 6 once the metric set feels reasonably complete
