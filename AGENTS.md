# AGENTS.md

Guidance for OpenCode sessions working in this repo.

## Project state

Spec (`Project-Specification.md`) is the **authoritative design**: read it in full before any work. Step 0 + pipeline files have been implemented per spec (`BUILDING_MATRIX.md`, `fetch_open_data.py`, `run_tour_pipeline.py`, `pyproject.toml`, `_stubs/`, `.crew/AGENTS.md`). `requirements.txt` is superseded by `pyproject.toml` (kept for spec traceability). The spec still governs any further changes — do not deviate from its file layout, agent roster, or output structure without owner consent.

## Git

- Working branch: `dev-001`. The planned pipeline hardcodes `push origin dev-001`; remote also has `main` and `dev`. Do not assume `main` is the active branch.
- `origin` is a credential-less HTTPS remote (`https://Mcc-Mak@github.com/Mcc-Mak/hk-guided-tour.git`); auth is handled via a credential helper, not an embedded token. Do not embed tokens in the remote URL.
- The planned `run_tour_pipeline.py` auto-runs `git add` + `commit` + `push origin dev-001` after **each** generated handbook. Expect many automated commits on `dev-001`; do not be alarmed or rebase them away.

## Planned architecture (from spec)

Python + CrewAI. Core dependency is `crewai` (pinned in `pyproject.toml` — see Setup below). Intended entrypoints:
- `fetch_open_data.py` — downloads HK open data into `data/` (XML/JSON).
- `run_tour_pipeline.py` — main pipeline: parses `BUILDING_MATRIX.md`, shows a startup TUI (run all / run only 🔴 unstarted / quit), runs a 4-agent crew per building, writes handbooks to `建築/`, then auto-commits.
- `建築/` — generated handbooks named `NNNNN-建築名稱.md` (5-digit zero-padded id). Non-ASCII path: enforce UTF-8 in all file ops.
- `BUILDING_MATRIX.md` — target building matrix; the 歷史檔案（連結）column is intentionally blank (see invariant below).

There is no test suite, lint, or typecheck config yet — none should be assumed.

## Setup & environment (verified)

- System Python is **externally-managed (PEP 668)** — `pip install` into it is refused. This project uses **`uv`** (available at `/usr/bin/uv`) as the package manager. Run `uv sync` to create `.venv/` and install all dependencies. `.venv/` is gitignored; `uv.lock` should be committed.
- `pyproject.toml` pins **`crewai==1.15.22`** (owner-confirmed). This version exports `LLM`, which `run_tour_pipeline.py` imports. The `verbose=` parameter on `Crew`/`Agent` is accepted (not removed) in 1.15.22 — no spec deviation needed.
- **musllinux stub packages.** crewai 1.x transitively requires `lancedb`, `chromadb`, `onnxruntime`, and `google-re2`, none of which have musllinux wheels. The `_stubs/` directory contains local stub packages for all four. `pyproject.toml` declares them as direct deps and uses `[tool.uv.sources]` to redirect to the local paths. The stubs satisfy install-time resolution but raise `NotImplementedError` if called — safe because this project never uses crewai's Memory/RAG/Flow features. Pattern adapted from `/workplace/mcp/crewai-mcp-server/_stubs/`.
- crewai 1.15.22 **installs and imports successfully** on this Alpine/musllinux sandbox. `from crewai import Agent, Crew, Process, Task, LLM` works. `run_tour_pipeline.py` imports cleanly. The parser smoke-test passes (4 buildings, correct Unicode-codepoint sort order).
- Full pipeline *execution* (CrewAI crew kickoff with LLM calls) still requires both `HKOAI_API_KEY` and `OPENCODE_API_KEY` env vars to be set — see LLM configuration below.

## Pipeline behavior gotcha

`parse_and_sort_building_matrix` sorts rows by `(category, name, address)` using **Python Unicode codepoint order**, not Chinese stroke/pinyin order. Consequence: `香港樓宇導賞團` (樓 U+6A13) sorts *before* `香港法定古蹟導賞團` (法 U+6CD5), so the runtime order is matrix rows N=3,4,1,2. `main()` assigns the 5-digit file id via `enumerate(..., start=1)`, **not** the matrix `編號 {N}` — so output filenames (`00001-藍屋建築群.md`, …) are renumbered by sort order and diverge from the matrix's own `N` column. This is per-spec; don't "fix" it without owner consent.

## LLM configuration (from spec, non-obvious)

- Primary: `zai-org/GLM-5.2-FP8` via `https://litellm.services.hko.gov.hk`, env `HKOAI_API_KEY`.
- Fallback: `opencode-zen` via `https://api.opencode.ai/v1`, env `OPENCODE_API_KEY`.
- Pipeline tries primary, auto-falls back on failure. Both env vars must be set before running. Never commit these keys.

## Content invariants (do not violate)

- **歷史檔案（連結） must never be hardcoded.** It is produced dynamically by the Official Archives Researcher + Chief Editor agents as standard Markdown links (`[name](URL)`). Do not pre-fill it in `BUILDING_MATRIX.md` or template it statically.
- All handbook output is **Traditional Chinese (繁體中文)** Markdown with the fixed 6-section structure defined in the spec's editor task.
- CL ratings (1–5) and the 4 Emoji lifecycle states (🔴 未開始 / 🟡 進行中 / 🟠 審閱中 / 🟢 已完成) follow the spec's tables exactly.

## Naming collision — read before creating files

The spec's "Step 0" defines an `AGENTS.md` containing CrewAI agent roles + CL rating tables. That **collides with this OpenCode instruction file.** Do not overwrite this file with the spec's CrewAI-role content — that content lives in `.crew/AGENTS.md` (owner-confirmed).
