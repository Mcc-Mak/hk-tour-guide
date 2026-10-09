# 專案章程

## 專案名稱

香港導賞團（Hong Kong Guided Tour）

## 專案願景

以 CrewAI 多代理人協作架構，自動為香港 20,210 棟建築生成繁體中文導賞手冊，涵蓋法定古蹟及市區/新界樓宇，並以 mdBook 發佈至 GitHub Pages 供導賞員及公眾查閱。

## 專案目標

1. **自動化生成** — 使用 4 位 CrewAI 代理人（研究員、查核員、編劇、總編輯）依標準六段式結構生成每棟建築的導賞手冊。
2. **事實查核** — 每份手冊均附 CL 1-5 可信度評級表，過濾 AI 幻覺。
3. **動態歷史檔案** — 歷史檔案連結由研究員代理人動態搜集，以 Markdown 超連結格式呈現，絕不寫死。
4. **版本控制** — 每份手冊生成後自動 commit + push 至 `dev-001`，CI/CD 自動合併至 `dev` 及 `main`。
5. **品質把關** — CodeQL + SonarQube 雙品質閘道，mdBook 部署需兩者均通過。
6. **公開發佈** — mdBook 網站部署至 GitHub Pages：`https://mcc-mak.github.io/hk-tour-guide/`。

## 範圍

| 類別 | 資料來源 | 項目數 |
| :--- | :--- | :--- |
| 法定古蹟 | CSDI KML | 173 |
| 樓宇（市區） | RVD Urban XML | 12,381 |
| 樓宇（新界） | RVD NT XML | 7,656 |
| **合計** | | **20,210** |

## 關鍵關係人

| 角色 | 職責 |
| :--- | :--- |
| 專案負責人 (Mcc-Mak) | 需求決策、模型選擇、CI/CD 設定 |
| OpenCode 代理人 | 依 AGENTS.md 七步工作流程執行開發與維護 |
| CrewAI 代理人團隊 | 自動生成導賞手冊內容 |

## 技術棧

- **語言**: Python 3.12+
- **AI 框架**: CrewAI 1.15.22
- **LLM**: GLM-5.2-FP8（優先）、DeepSeek-V4-Flash-0731-Coding（備援）
- **套件管理**: uv
- **文件格式**: Markdown（繁體中文）
- **網站**: mdBook
- **CI/CD**: GitHub Actions（CodeQL + SonarQube + Pages Deploy）
- **版本控制**: Git（分支 `dev-001` → `dev` → `main`）
