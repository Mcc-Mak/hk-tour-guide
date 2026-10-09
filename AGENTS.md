# AGENTS.md

Guidance for OpenCode sessions working in this repo.

## Project state

Spec (`specbase/工作流程規格書.md`) is the **authoritative design**: read it in full before any work. Step 0 + pipeline files have been implemented per spec (`specbase/導賞目標建築矩陣.md`, `.crewai/矩陣/`, `.crewai/fetch_open_data.py`, `.crewai/run_tour_pipeline.py`, `.crewai/pyproject.toml`, `.crewai/_stubs/`, `.crewai/.crew/AGENTS.md`). `.crewai/requirements.txt` is superseded by `.crewai/pyproject.toml` (kept for spec traceability). The spec still governs any further changes — do not deviate from its file layout, agent roster, or output structure without owner consent.

## Git

- Working branch: `dev-001`. The planned pipeline hardcodes `push origin dev-001`; remote also has `main` and `dev`. Do not assume `main` is the active branch.
- `origin` is a credential-less HTTPS remote (`https://Mcc-Mak@github.com/Mcc-Mak/hk-guided-tour.git`); auth is handled via a credential helper, not an embedded token. Do not embed tokens in the remote URL.
- The planned `.crewai/run_tour_pipeline.py` auto-runs `git add` + `commit` + `push origin dev-001` after **each** generated handbook. Expect many automated commits on `dev-001`; do not be alarmed or rebase them away.

## Planned architecture (from spec)

Python + CrewAI. Core dependency is `crewai` (pinned in `.crewai/pyproject.toml` — see Setup below). Intended entrypoints:
- `.crewai/fetch_open_data.py` — downloads HK open data into `.crewai/data/` (CSDI KML for declared monuments, RVD XML for buildings).
- `.crewai/run_tour_pipeline.py` — main pipeline: parses `.crewai/矩陣/**/*.md` (TOC tree), shows a startup TUI (run all / run only 🌚 unstarted / priority first then rest / quit), runs a 4-agent crew per building, writes handbooks to `codebase/建築/`, dynamically updates the matrix sub-file's 歷史檔案（連結）column + status to 🌕, then auto-commits.
- `codebase/建築/` — generated handbooks in category subdirectories: `codebase/建築/法定古蹟/NNNNN-名稱.md`, `codebase/建築/樓宇/市區/NNNNN-名稱.md`, and `codebase/建築/樓宇/新界/NNNNN-名稱.md`, where NNNNN = matrix `編號 {N}` zero-padded to 5 digits. Non-ASCII path: enforce UTF-8 in all file ops.
- `specbase/導賞目標建築矩陣.md` — **root TOC index file** linking to `.crewai/矩陣/**/*.md` sub-files. Does NOT contain building rows directly.
- `.crewai/矩陣/` — **TOC tree sub-files** containing the actual building matrix rows, split by category into subdirectories to control file size. Each file's rows are sorted by `(name, address)` in Unicode codepoint order, then assigned per-file N starting from 1 (NOT globally unique — disambiguated by sub-directory):
  - `.crewai/矩陣/法定古蹟/建築.md` — 173 rows (CSDI KML, N=1–173)
  - `.crewai/矩陣/樓宇/市區建築.md` — 12,381 rows (RVD Urban, N=1–12,381)
  - `.crewai/矩陣/樓宇/新界建築.md` — 7,656 rows (RVD NT, N=1–7,656)
  - Total: **20,210 buildings**. 21 CSDI monuments also in RVD are excluded from RVD to avoid duplicates. Markdown table cells with `|` characters are escaped as `\|`.
- `codebase/site/` — mdBook site configuration (`book.toml`, `scripts/build_mdbook.py`, `theme/`). GitHub Pages deployment is currently disabled (`.github/workflows/deploy-mdbook.yml` has only `workflow_dispatch` trigger).

There is no test suite, lint, or typecheck config yet — none should be assumed.

## Setup & environment (verified)

- System Python is **externally-managed (PEP 668)** — `pip install` into it is refused. This project uses **`uv`** (available at `/usr/bin/uv`) as the package manager. Run `uv sync` (from `.crewai/`) to create `.venv/` and install all dependencies. `.venv/` is gitignored; `uv.lock` should be committed.
- `.crewai/pyproject.toml` pins **`crewai==1.15.22`** (owner-confirmed). This version exports `LLM`, which `.crewai/run_tour_pipeline.py` imports. The `verbose=` parameter on `Crew`/`Agent` is accepted (not removed) in 1.15.22 — no spec deviation needed.
- **musllinux stub packages.** crewai 1.x transitively requires `lancedb`, `chromadb`, `onnxruntime`, and `google-re2`, none of which have musllinux wheels. The `.crewai/_stubs/` directory contains local stub packages for all four. `.crewai/pyproject.toml` declares them as direct deps and uses `[tool.uv.sources]` to redirect to the local paths. The stubs satisfy install-time resolution but raise `NotImplementedError` if called — safe because this project never uses crewai's Memory/RAG/Flow features. Pattern adapted from `/workplace/mcp/crewai-mcp-server/_stubs/`.
- crewai 1.15.22 **installs and imports successfully** on this Alpine/musllinux sandbox. `from crewai import Agent, Crew, Process, Task, LLM` works. `.crewai/run_tour_pipeline.py` imports cleanly. The parser smoke-test passes (20,210 buildings, correct Unicode-codepoint sort order, pipe-escaping verified).
- Full pipeline *execution* (CrewAI crew kickoff with LLM calls) requires only `HKOAI_API_KEY` env var to be set — see LLM configuration below.

## Pipeline behavior gotcha

`parse_and_sort_building_matrix` reads sub-files in fixed order (`法定古蹟/建築.md` → `樓宇/市區建築.md` → `樓宇/新界建築.md`) and sorts by `(file_order, N)` where N is per-file (each file starts from 1, NOT globally unique). Within each sub-file, rows are pre-sorted by `(name, address)` in Python Unicode codepoint order and assigned contiguous N from 1. The 5-digit file id uses the sub-file's `編號 {N}` (zero-padded), disambiguated by the category sub-directory (`法定古蹟/` or `樓宇/市區/` or `樓宇/新界/`). After each handbook is written, `update_matrix_entry()` updates that building's row in the correct `.crewai/矩陣/**/*.md` sub-file (matched by **N value within the specified matrix_file**, not name): status → `🌕 已完成`, link → `` [`歷史檔案（連結）`](codebase/建築/{法定古蹟|樓宇/市區|樓宇/新界}/NNNNN-名稱.md) ``.

## Handbook section structure (enforced)

The editor task (`t4`) specifies a fixed 6-section structure with mandatory subsections. All `codebase/建築/*-*.md` must follow:
1. 一、導賞概覽與地址資訊（建築基本資料表格 + 導賞路線建議）
2. 二、歷史脈絡與建築特色（建築風格與特色 + 歷史事件與背景）
3. 三、事實查核與可信度評級表（CL 1-5）
4. 四、歷史檔案狀態宣告（可信性等級 + 歷史檔案（連結））
5. 五、導賞員現場講稿（開場白 + 各站點 + 結語）
6. 六、參考資料來源（官方檔案 + 參考文獻清單）

Within section 二, historical events **must** be grouped under `#### {歷史時期/特徵}` subheadings, with each entry as `- {年份}：{歷史描述}`. This format is enforced in both the researcher task (`t1`) and editor task (`t4`).

## LLM configuration (from spec, non-obvious)

- Primary: `zai-org/GLM-5.2-FP8` via `https://litellm.services.hko.gov.hk`, env `HKOAI_API_KEY`.
- Fallback: `deepseek-ai/DeepSeek-V4-Flash-0731-Coding` via `https://litellm.services.hko.gov.hk` (same endpoint, same key). Replaced the previous OpenCode-Zen/Big Pickle fallback which was locked to the OpenCode app free tier and could not be called from an external script.
- Pipeline tries primary (2×), auto-falls back on failure. Only `HKOAI_API_KEY` must be set. Never commit this keys.
- **SSL bypass:** `.crewai/run_tour_pipeline.py` monkey-patches `httpx.Client`/`AsyncClient` to default `verify=False` (before `from crewai import ...`). This is required because the HKO endpoint certificate is not trusted by the system CA store in this sandbox. Equivalent of `NODE_TLS_REJECT_UNAUTHORIZED=0`.
- **Timeout:** LLM timeout is 600s — GLM-5.2-FP8 uses reasoning tokens that require more time. Single CrewAI call takes ~48s.

## LLM failure hypothesis & retry strategy (current)

### Observed failure pattern (from `/tmp/tour-guide-research.log`, 149MB)

Analysis of pipeline execution logs reveals a consistent pattern:

- **Successes**: All 4 agents run in sequence (1→2→3→4), each appearing 3× in the log (12 total appearances = 1 success path through 4 agents × 3 crew-level retries when earlier buildings consumed retries). A successful building produces a handbook.
- **Failures occur at only 2 points** — never at agents 2 or 3:
  - **Agent 1 failure** (香港官方檔案研究員): GLM-5.2-FP8 returns `content=None` or empty string immediately. Affected buildings include 02336–02341 (all named 啟鑽苑, 6 duplicate-name entries), 02344, 02345. These fail across all 3 retries, suggesting a prompt-specific issue (likely the duplicate building name confusing the model, or the research prompt triggering a reasoning-token exhaustion that leaves `content` empty).
  - **Agent 4 failure** (導賞手冊總編輯): Agents 1–3 succeed, but the editor agent — which has the longest and most structurally complex prompt (6-section Markdown template with nested subsections) — gets `content=None`. Affected buildings include pre-02330, 02334, 02347. The editor prompt's length and structural complexity likely cause GLM-5.2-FP8 to exhaust `max_tokens` on reasoning tokens, leaving no budget for `content`.
- **Root cause hypothesis**: GLM-5.2-FP8 is a reasoning model. For certain prompts (long/complex like agent 4's, or involving duplicate names like agent 1's), the model spends its entire `max_tokens` budget on `reasoning_content` and returns an empty or None `content` field. CrewAI's `OpenAICompletion._handle_completion()` (line 2277) does `message.content or ""`, which becomes `""`, triggering the `ValueError("Invalid response from LLM call - None or empty.")` in `agent_utils.py` (lines 413-419, 537-543).
- **Proof**: Direct OpenAI SDK calls with simple prompts return `message.content` properly populated (with `reasoning_content` also present). The issue only manifests with CrewAI's complex prompts (tools + multi-turn ReAct formatting + long structured system prompts).

### Three-attempt retry strategy

`execute_crew_with_fallback()` implements a 3-attempt strategy (replaces the old 3× GLM + full-crew fallback):

| Attempt | Strategy | Agents | LLM |
|---------|----------|--------|-----|
| 1 (normal) | Full crew | All 4 | GLM-5.2-FP8 |
| 2 (retry) | Full crew | All 4 | GLM-5.2-FP8 |
| 3 (fallback) | Full crew | All 4 | DeepSeek-V4-Flash-0731-Coding |

**Attempt 3 logic**: Rebuild the **entire crew** with **all 4 agents** using DeepSeek-V4-Flash-0731-Coding (same HKO endpoint, same `HKOAI_API_KEY`). No mixed LLMs, no agent-failure detection — just a clean full-crew retry with a different model.

**Failure safety**: If attempt 3 (DeepSeek-V4-Flash) also fails — for any reason (quota exhaustion, connection failure, empty content, exception) — `execute_crew_with_fallback()` raises a `RuntimeError`. The main loop's `try/except` catches it and **continues to the next building** (`continue`). DeepSeek-V4-Flash failure **never breaks pipeline continuity**.

## Content invariants (do not violate)

- **歷史檔案（連結） must never be hardcoded.** It is produced dynamically by the Official Archives Researcher + Chief Editor agents as standard Markdown links (`[name](URL)`). Do not pre-fill it in `specbase/導賞目標建築矩陣.md` or `.crewai/矩陣/**/*.md` or template it statically. After each handbook is generated, `update_matrix_entry()` writes `` [`歷史檔案（連結）`](codebase/建築/{法定古蹟|樓宇/市區|樓宇/新界}/NNNNN-名稱.md) `` into the matrix row in the correct `.crewai/矩陣/**/*.md` sub-file.
- All handbook output is **Traditional Chinese (繁體中文)** Markdown with the fixed 6-section structure defined in the spec's editor task.
- CL ratings (1–5) and the 4 Emoji lifecycle states (🌚 未開始 / 🌒 進行中 / 🌗 審閱中 / 🌕 已完成) follow the spec's tables exactly.

## Naming collision — read before creating files

The spec's "Step 0" defines an `AGENTS.md` containing CrewAI agent roles + CL rating tables. That **collides with this OpenCode instruction file.** Do not overwrite this file with the spec's CrewAI-role content — that content lives in `.crewai/.crew/AGENTS.md` (owner-confirmed).
