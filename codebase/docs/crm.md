# 交叉參考矩陣 (CRM)

> 記錄各文件、程式碼與設定檔之間的交叉參考關係。

## 1. 規格 → 實作

| 規格章節 | 規格檔案 | 實作檔案 |
| :--- | :--- | :--- |
| 1. 專案檔案結構 | `specbase/工作流程規格書.md` | 整個專案目錄結構 |
| 2. 步驟 0：初始化檔案 | `specbase/工作流程規格書.md` | `.crewai/.crew/AGENTS.md`, `.crewai/fetch_open_data.py` |
| 3. 步驟 1-2：自動化管線 | `specbase/工作流程規格書.md` | `.crewai/run_tour_pipeline.py` |
| 矩陣目錄樹結構 | `specbase/工作流程規格書.md` | `specbase/導賞目標建築矩陣.md`, `.crewai/矩陣/**/*.md` |

## 2. 程式模組 → 文件

| 程式模組 | 檔案 | 相關文件 |
| :--- | :--- | :--- |
| `fetch_open_data.py` | `.crewai/fetch_open_data.py` | srs.md (FR-01), setup.md, configuration.md |
| `run_tour_pipeline.py` | `.crewai/run_tour_pipeline.py` | srs.md (FR-02~FR-08), pdr.md, backend-api.md, configuration.md |
| `build_mdbook.py` | `codebase/site/scripts/build_mdbook.py` | cicd.md, quick-start.md |
| `ci-cd.yml` | `.github/workflows/ci-cd.yml` | cicd.md, configuration.md |
| `pyproject.toml` | `.crewai/pyproject.toml` | setup.md, configuration.md |
| `sonar-project.properties` | `sonar-project.properties` | cicd.md, configuration.md |
| `book.toml` | `codebase/site/book.toml` | configuration.md, cicd.md |

## 3. CrewAI 代理人 → 任務 → 輸出

| 代理人 | 任務 | 輸出 | 手冊章節 |
| :--- | :--- | :--- | :--- |
| 香港官方檔案研究員 | t1 | 研究報告 + 官方檔案連結 | 二、四、六 |
| 首席事實查核與信譽評估員 | t2 | CL 評級表 + 狀態確認 | 三、四 |
| 文化導賞故事編劇 | t3 | 導賞解說文稿 | 五 |
| 導賞手冊總編輯 | t4 | 完整六段式 Markdown 手冊 | 一～六 |

## 4. CI/CD Job → 依賴 → 觸發

| Job | 觸發 | 依賴 | 輸出 |
| :--- | :--- | :--- | :--- |
| `auto_merge` | push | — | `dev`/`main` 更新 |
| `codeql` | push / dispatch | — | 安全分析報告 |
| `sonarqube` | push / dispatch | — | 品質掃描報告 |
| `build` | dispatch | — | Pages artifact |
| `deploy` | dispatch | `build` + `codeql` + `sonarqube` | GitHub Pages 部署 |

## 5. 資料流

| 來源 | 處理 | 輸出 | 更新 |
| :--- | :--- | :--- | :--- |
| CSDI KML | `fetch_open_data.py` | `.crewai/data/declared_monuments.json` | — |
| RVD XML | `fetch_open_data.py` | `.crewai/data/buildings_{urban,nt}.json` | — |
| 矩陣子檔案 | `parse_and_sort_building_matrix()` | buildings list | — |
| buildings list | `execute_crew_with_fallback()` | 手冊 Markdown | — |
| 手冊 Markdown | `update_matrix_entry()` | 矩陣狀態 + 連結 | `.crewai/矩陣/**/*.md` |
| 手冊 + 矩陣 | `auto_git_commit_and_push()` | Git commit | `origin/dev-001` |
| dev-001 | CI/CD `auto_merge` | dev/main | — |
| main | CI/CD `build` + `deploy` | GitHub Pages | `https://mcc-mak.github.io/hk-tour-guide/` |
