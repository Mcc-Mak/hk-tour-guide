# Changelog

本專案遵循 [Semantic Versioning](https://semver.org/)。

## [0.5.0] — 2026-10-09

### Added
- GitHub issue #26「完成所有建築首次導賞手冊生成」— 20,210 棟建築導賞手冊生成追蹤（epic，無版本號）
- 82 個批次子議題（#27–#108）建立並連結至 #26，涵蓋法定古蹟 1 批次、市區 50 批次、新界 31 批次
- 82 個子議題已加入 GitHub 專案看板，依目前進度設定狀態（Todo / In Progress / Done）
- `run_tour_pipeline.py` 新增第 4 節「GitHub 議題與專案看板管理」：
  - `_get_batch_info()` 依建築分類與編號 N 計算所屬批次、子議題編號、N 範圍
  - `init_batch_progress()` 從已解析建築清單初始化批次進度字典
  - `update_batch_subissue()` 更新子議題 body 進度表，批次完成時自動關閉子議題
  - `_ensure_project_board_item()` 確保子議題已加入專案看板，回傳 item ID
  - `update_project_board_status()` 更新看板 Status 欄位（Todo / In Progress / Done）
  - `sync_batch_to_github()` 統一協調上述操作，非阻塞設計（失敗不中斷管線）
  - 主迴圈整合：每棟建築手冊生成並提交 Git 後，更新批次進度並同步至 GitHub

### Changed
- `codebase/` 文件集重組：14 份專案文件（charter, user-stories, srs, prd, pdr, backend-api, db-schema, erd, quick-start, cicd, setup, configuration, rtm, crm）由 `codebase/` 遷移至 `codebase/docs/`
- `codebase/toc.md` 連結路徑同步更新
- `AGENTS.md` 文件路徑更新（`codebase/X.md` → `codebase/docs/X.md`）
- `specbase/工作流程規格書.md` 檔案結構樹新增 `docs/` 子目錄
- `specbase/導賞目標建築矩陣.md` 目錄結構新增 `docs/` 子目錄
- `codebase/site/scripts/build_mdbook.py` 註解路徑修正

## [0.4.0] — 2026-10-09

### Fixed
- `specbase/導賞目標建築矩陣.md` 法定古蹟扣除數量由 3 項修正為 1 項（174→173）
- `specbase/導賞目標建築矩陣.md` 市區樓宇扣除數量由 17 項修正為 15 項（12,396→12,381）
- `specbase/工作流程規格書.md` CSDI/RVD 重複排除數量由 21 棟修正為 19 棟（15 市區 + 4 新界）

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
