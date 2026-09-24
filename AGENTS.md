# AGENTS.md

Guidance for OpenCode sessions working in this repo.

## Project state

Spec (`工作流程規格書.md`) is the **authoritative design**: read it in full before any work. Step 0 + pipeline files have been implemented per spec (`導賞目標建築矩陣.md`, `矩陣/`, `fetch_open_data.py`, `run_tour_pipeline.py`, `pyproject.toml`, `_stubs/`, `.crew/AGENTS.md`). `requirements.txt` is superseded by `pyproject.toml` (kept for spec traceability). The spec still governs any further changes — do not deviate from its file layout, agent roster, or output structure without owner consent.

## Git

- Working branch: `dev-001`. The planned pipeline hardcodes `push origin dev-001`; remote also has `main` and `dev`. Do not assume `main` is the active branch.
- `origin` is a credential-less HTTPS remote (`https://Mcc-Mak@github.com/Mcc-Mak/hk-guided-tour.git`); auth is handled via a credential helper, not an embedded token. Do not embed tokens in the remote URL.
- The planned `run_tour_pipeline.py` auto-runs `git add` + `commit` + `push origin dev-001` after **each** generated handbook. Expect many automated commits on `dev-001`; do not be alarmed or rebase them away.

## Planned architecture (from spec)

Python + CrewAI. Core dependency is `crewai` (pinned in `pyproject.toml` — see Setup below). Intended entrypoints:
- `fetch_open_data.py` — downloads HK open data into `data/` (CSDI KML for declared monuments, RVD XML for buildings).
- `run_tour_pipeline.py` — main pipeline: parses `矩陣/*.md` (TOC tree), shows a startup TUI (run all / run only 🌚 unstarted / quit), runs a 4-agent crew per building, writes handbooks to `建築/`, dynamically updates the matrix sub-file's 歷史檔案（連結）column + status to 🌕, then auto-commits.
- `建築/` — generated handbooks in category subdirectories: `建築/法定古蹟/NNNNN-名稱.md` and `建築/樓宇/NNNNN-名稱.md`, where NNNNN = matrix `編號 {N}` zero-padded to 5 digits. Non-ASCII path: enforce UTF-8 in all file ops.
- `導賞目標建築矩陣.md` — **root TOC index file** linking to `矩陣/*.md` sub-files. Does NOT contain building rows directly.
- `矩陣/` — **TOC tree sub-files** containing the actual building matrix rows, split by category to control file size. Each file's rows are sorted by `(name, address)` in Unicode codepoint order, then assigned per-file N starting from 1 (NOT globally unique — disambiguated by sub-directory):
  - `法定古蹟.md` — 173 rows (CSDI KML, N=1–173)
  - `樓宇-市區.md` — 12,381 rows (RVD Urban, N=1–12,381)
  - `樓宇-新界.md` — 7,656 rows (RVD NT, N=1–7,656)
  - Total: **20,210 buildings**. 21 CSDI monuments also in RVD are excluded from RVD to avoid duplicates. Markdown table cells with `|` characters are escaped as `\|`.

There is no test suite, lint, or typecheck config yet — none should be assumed.

## Setup & environment (verified)

- System Python is **externally-managed (PEP 668)** — `pip install` into it is refused. This project uses **`uv`** (available at `/usr/bin/uv`) as the package manager. Run `uv sync` to create `.venv/` and install all dependencies. `.venv/` is gitignored; `uv.lock` should be committed.
- `pyproject.toml` pins **`crewai==1.15.22`** (owner-confirmed). This version exports `LLM`, which `run_tour_pipeline.py` imports. The `verbose=` parameter on `Crew`/`Agent` is accepted (not removed) in 1.15.22 — no spec deviation needed.
- **musllinux stub packages.** crewai 1.x transitively requires `lancedb`, `chromadb`, `onnxruntime`, and `google-re2`, none of which have musllinux wheels. The `_stubs/` directory contains local stub packages for all four. `pyproject.toml` declares them as direct deps and uses `[tool.uv.sources]` to redirect to the local paths. The stubs satisfy install-time resolution but raise `NotImplementedError` if called — safe because this project never uses crewai's Memory/RAG/Flow features. Pattern adapted from `/workplace/mcp/crewai-mcp-server/_stubs/`.
- crewai 1.15.22 **installs and imports successfully** on this Alpine/musllinux sandbox. `from crewai import Agent, Crew, Process, Task, LLM` works. `run_tour_pipeline.py` imports cleanly. The parser smoke-test passes (20,210 buildings, correct Unicode-codepoint sort order, pipe-escaping verified).
- Full pipeline *execution* (CrewAI crew kickoff with LLM calls) still requires both `HKOAI_API_KEY` and `OPENCODE_API_KEY` env vars to be set — see LLM configuration below.

## Pipeline behavior gotcha

`parse_and_sort_building_matrix` reads sub-files in fixed order (`法定古蹟.md` → `樓宇-市區.md` → `樓宇-新界.md`) and sorts by `(file_order, N)` where N is per-file (each file starts from 1, NOT globally unique). Within each sub-file, rows are pre-sorted by `(name, address)` in Python Unicode codepoint order and assigned contiguous N from 1. The 5-digit file id uses the sub-file's `編號 {N}` (zero-padded), disambiguated by the category sub-directory (`法定古蹟/` or `樓宇/`). After each handbook is written, `update_matrix_entry()` updates that building's row in the correct `矩陣/*.md` sub-file (matched by **N value within the specified matrix_file**, not name): status → `🌕 已完成`, link → `` [`歷史檔案（連結）`](建築/{法定古蹟|樓宇}/NNNNN-名稱.md) ``.

## Handbook section structure (enforced)

The editor task (`t4`) specifies a fixed 6-section structure with mandatory subsections. All `建築/*-*.md` must follow:
1. 一、導賞概覽與地址資訊（建築基本資料表格 + 導賞路線建議）
2. 二、歷史脈絡與建築特色（建築風格與特色 + 歷史事件與背景）
3. 三、事實查核與可信度評級表（CL 1-5）
4. 四、歷史檔案狀態宣告（可信性等級 + 歷史檔案（連結））
5. 五、導賞員現場講稿（開場白 + 各站點 + 結語）
6. 六、參考資料來源（官方檔案 + 參考文獻清單）

Within section 二, historical events **must** be grouped under `#### {歷史時期/特徵}` subheadings, with each entry as `- {年份}：{歷史描述}`. This format is enforced in both the researcher task (`t1`) and editor task (`t4`).

## LLM configuration (from spec, non-obvious)

- Primary: `zai-org/GLM-5.2-FP8` via `https://litellm.services.hko.gov.hk`, env `HKOAI_API_KEY`.
- Fallback: `opencode-zen` via `https://api.opencode.ai/v1`, env `OPENCODE_API_KEY`.
- Pipeline tries primary, auto-falls back on failure. Both env vars must be set before running. Never commit these keys.
- **SSL bypass:** `run_tour_pipeline.py` monkey-patches `httpx.Client`/`AsyncClient` to default `verify=False` (before `from crewai import ...`). This is required because the HKO endpoint certificate is not trusted by the system CA store in this sandbox. Equivalent of `NODE_TLS_REJECT_UNAUTHORIZED=0`.
- **Timeout:** LLM timeout is 180s (not 60s) — GLM-5.2-FP8 uses reasoning tokens that require more time. Single CrewAI call takes ~48s.

## Content invariants (do not violate)

- **歷史檔案（連結） must never be hardcoded.** It is produced dynamically by the Official Archives Researcher + Chief Editor agents as standard Markdown links (`[name](URL)`). Do not pre-fill it in `導賞目標建築矩陣.md` or `矩陣/*.md` or template it statically. After each handbook is generated, `update_matrix_entry()` writes `` [`歷史檔案（連結）`](建築/{法定古蹟|樓宇}/NNNNN-名稱.md) `` into the matrix row in the correct `矩陣/*.md` sub-file.
- All handbook output is **Traditional Chinese (繁體中文)** Markdown with the fixed 6-section structure defined in the spec's editor task.
- CL ratings (1–5) and the 4 Emoji lifecycle states (🌚 未開始 / 🌒 進行中 / 🌗 審閱中 / 🌕 已完成) follow the spec's tables exactly.

## Naming collision — read before creating files

The spec's "Step 0" defines an `AGENTS.md` containing CrewAI agent roles + CL rating tables. That **collides with this OpenCode instruction file.** Do not overwrite this file with the spec's CrewAI-role content — that content lives in `.crew/AGENTS.md` (owner-confirmed).
