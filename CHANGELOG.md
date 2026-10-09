# Changelog

本專案遵循 [Semantic Versioning](https://semver.org/)。

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
