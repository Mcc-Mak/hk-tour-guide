# 需求追溯矩陣 (RTM)

> 追蹤 SRS 需求 → 實作檔案 → 驗證方式的對應關係。

| 需求 ID | 需求描述 | 實作檔案 | 驗證方式 |
| :--- | :--- | :--- | :--- |
| FR-01 | 開放資料下載（CSDI + RVD） | `.crewai/fetch_open_data.py` | 執行後檢查 `.crewai/data/*.json` 存在且項目數正確 |
| FR-02 | 矩陣 TOC 樹解析與排序 | `.crewai/run_tour_pipeline.py` `parse_and_sort_building_matrix()` | `len(result) == 20210`，排序順序正確 |
| FR-03 | 啟動選單 TUI（4 種模式） | `.crewai/run_tour_pipeline.py` `main()` | 互動執行，4 種模式均可正確篩選 |
| FR-04 | CrewAI 4 代理人執行 | `.crewai/run_tour_pipeline.py` `build_agents()` `build_tasks()` | 手冊生成且結構符合六段式 |
| FR-05 | LLM 三階段備援 | `.crewai/run_tour_pipeline.py` `execute_crew_with_fallback()` | GLM 失敗時自動切換 DeepSeek |
| FR-06 | 檔案命名與輸出 | `.crewai/run_tour_pipeline.py` `main()` | 檔名為 `NNNNN-名稱.md`，路徑正確 |
| FR-07 | 矩陣更新 | `.crewai/run_tour_pipeline.py` `update_matrix_entry()` | 生成後矩陣狀態為 🌕，連結正確 |
| FR-08 | Git 自動化 | `.crewai/run_tour_pipeline.py` `auto_git_commit_and_push()` | `git log` 可見自動提交 |
| FR-09a | CI/CD 自動合併 | `.github/workflows/ci-cd.yml` `auto_merge` job | push 後 `dev`/`main` 更新 |
| FR-09b | CodeQL 品質閘道 | `.github/workflows/ci-cd.yml` `codeql` job | CI run 通過 |
| FR-09c | SonarQube 品質閘道 | `.github/workflows/ci-cd.yml` `sonarqube` job | CI run 通過 |
| FR-09d | mdBook 部署 | `.github/workflows/ci-cd.yml` `build` + `deploy` jobs | GitHub Pages 可訪問 |
| NFR-01 | 效能（timeout 600s） | `.crewai/run_tour_pipeline.py` `get_primary_llm()` | LLM 逾時設定為 600 |
| NFR-02 | 可靠性（不中斷） | `.crewai/run_tour_pipeline.py` `main()` try/except | 單棟失敗後 `continue` |
| NFR-03 | 可維護性（uv 鎖定） | `.crewai/pyproject.toml` `uv.lock` | `uv sync` 可重現環境 |
| NFR-04 | 安全性（API 金鑰） | `.crewai/run_tour_pipeline.py` `os.getenv()` | 金鑰僅由環境變數讀取 |

## 使用者故事追溯

| US ID | 使用者故事 | 對應需求 | 驗收狀態 |
| :--- | :--- | :--- | :--- |
| US-01 | 導賞員查閱手冊 | FR-04, FR-06, FR-09d | ✅ |
| US-02 | 研究人員驗證歷史資料 | FR-04, FR-07 | ✅ |
| US-03 | 專案負責人監控進度 | FR-07, FR-08 | ✅ |
| US-04 | 開發者執行管線 | FR-03, FR-05 | ✅ |
| US-05 | 公眾瀏覽導賞資訊 | FR-09d | ✅ |
