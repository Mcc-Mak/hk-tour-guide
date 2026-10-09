# Changelog

本專案遵循 [Semantic Versioning](https://semver.org/)。

## [0.3.0] — 2026-10-09

### Fixed
- 矩陣連結路徑修正：所有 `.crewai/矩陣/**/*.md` 子檔案中 2,160 條已完成項目的「歷史檔案（連結）」欄位，由 `](建築/...)` 修正為 `](codebase/建築/...)`，使其與規格書範例一致
- `run_tour_pipeline.py` 中 `update_matrix_entry()` 呼叫處同步修正連結路徑前綴

### Changed
- `specbase/工作流程規格書.md` LLM timeout 由 180s 修正為 600s（與實作一致）
- `specbase/工作流程規格書.md` 工作流程檔案結構由 `deploy-mdbook.yml` + `auto-merge.yml` 修正為單一 `ci-cd.yml`（與實作一致）
- `specbase/工作流程規格書.md` RVD XML 下載 URL 修正為實際使用的 `res.data.gov.hk` API 端點（`bnb-u.xml` / `bnb-nt.xml`）
- `specbase/工作流程規格書.md` LLM 配置段落擴充，新增三階段重試策略、Preflight 連線測試、CLI 旗標（`--priority-only` / `--priority-first`）說明

### Removed
- `run_tour_pipeline.py` 移除已棄用之死碼：`_detect_failed_agent()`、`_build_editor_task_with_context()`、`build_agents()` 的 `fallback_llm` / `fallback_indices` 參數（舊混合 LLM 重試策略遺留物）

## [0.2.0] — 2026-10-09

### Added
- `codebase/` 文件集：`toc.md`, `charter.md`, `user-stories.md`, `srs.md`, `prd.md`, `pdr.md`, `backend-api.md`, `db-schema.md`, `erd.md`, `quick-start.md`, `cicd.md`, `setup.md`, `configuration.md`, `rtm.md`, `crm.md`
- `CHANGELOG.md`（語意化版本）
- `AGENTS.md` 七步工作流程

### Changed
- `AGENTS.md` 文件路徑由 `codebase/docs/` 改為 `codebase/`
- SonarCloud project key 由 `Mcc-Mak_hk-tour-guide2` 修正為 `Mcc-Mak_hk-tour-guide`

## [0.1.0] — 2026-01-08

### Added
- CrewAI 自動化管線（`.crewai/run_tour_pipeline.py`）
- 4 代理人協作：研究員、查核員、編劇、總編輯
- LLM 三階段備援策略（GLM-5.2-FP8 ×2 → DeepSeek-V4-Flash ×1）
- 矩陣 TOC 樹結構（3 子檔案，20,210 棟建築）
- 啟動選單 TUI（4 種執行模式）
- `--priority-only` / `--priority-first` 旗標
- 六段式標準手冊結構
- Git 自動 commit + push
- CI/CD：`ci-cd.yml`（auto_merge + CodeQL + SonarQube + build + deploy）
- mdBook 網站建置與 GitHub Pages 部署
- 開放資料下載腳本（`.crewai/fetch_open_data.py`）
- musllinux stub 套件（lancedb, chromadb, onnxruntime, google-re2）
- `specbase/工作流程規格書.md`（權威設計規格）
- `specbase/導賞目標建築矩陣.md`（矩陣索引根節點）
