# 軟體需求規格書 (SRS)

## 1. 簡介

### 1.1 目的

本文件定義香港導賞團自動化管線系統的軟體需求，涵蓋功能需求、非功能需求及約束條件。

### 1.2 範圍

系統使用 CrewAI 多代理人架構，自動為 20,210 棟香港建築生成繁體中文導賞手冊，並透過 mdBook 發佈至 GitHub Pages。

### 1.3 定義與縮寫

| 縮寫 | 定義 |
| :--- | :--- |
| CL | Credibility Level，可信度評級（1-5） |
| TUI | Text User Interface，文字使用者介面 |
| AMO | Antiquities and Monuments Office，古物古蹟辦事處 |
| CSDI | Common Spatial Data Infrastructure，空間數據共享平台 |
| RVD | Rating and Valuation Department，差餉物業估價署 |
| LLM | Large Language Model，大型語言模型 |

## 2. 功能需求

### FR-01：開放資料下載

系統須從 CSDI 及 RVD 下載法定古蹟及樓宇資料，輸出至 `.crewai/data/` 目錄。

### FR-02：矩陣解析

系統須解析 `.crewai/矩陣/` 目錄下的 TOC 樹子檔案，依 `(子檔案順序, 編號 N)` 排序，支援 Markdown 表格中 `\|` 跳脫字元。

### FR-03：啟動選單 TUI

系統須提供四種執行模式：
1. 執行全部建築
2. 僅執行「🌚 未開始」項目
3. 優先建築先行，其後續接全部
4. 離開

### FR-04：CrewAI 多代理人執行

系統須依序執行 4 位代理人：
1. 香港官方檔案研究員 — 搜集歷史檔案並產出 Markdown 連結
2. 首席事實查核與信譽評估員 — 指派 CL 評級、推進狀態
3. 文化導賞故事編劇 — 撰寫繁體中文導賞稿
4. 導賞手冊總編輯 — 整合為六段式標準 Markdown 手冊

### FR-05：LLM 備援機制

系統須實作三階段重試策略：
- 第 1、2 次：GLM-5.2-FP8（完整 Crew）
- 第 3 次：DeepSeek-V4-Flash-0731-Coding（完整 Crew）
- 全部失敗時跳過該建築，不中斷管線

### FR-06：檔案命名與輸出

系統須將手冊輸出至 `codebase/建築/{法定古蹟|樓宇/市區|樓宇/新界}/NNNNN-名稱.md`，其中 NNNNN 為編號 N 零填補至 5 位。

### FR-07：矩陣更新

系統須於手冊生成後更新矩陣子檔案：狀態 → `🌕 已完成`，連結 → Markdown 超連結格式。

### FR-08：Git 自動化

系統須於每份手冊生成後自動 `git add` + `commit` + `push origin dev-001`。

### FR-09：CI/CD

系統須透過 GitHub Actions 實現：
- 自動合併 `dev-001` → `dev` → `main`
- CodeQL 安全分析
- SonarQube 程式碼品質分析
- 手動觸發 mdBook 建置與 GitHub Pages 部署（受 CodeQL + SonarQube 閘道保護）

## 3. 非功能需求

### NFR-01：效能

- 單次 CrewAI 呼叫逾時 600 秒
- LLM 連線預檢（max_tokens=1）於 10 秒內完成

### NFR-02：可靠性

- LLM 失敗不中斷管線（例外捕獲後 `continue`）
- 管線可中途停止並重新重新啟動（冪等性：已完成的建築狀態為 🌕，可透過模式 2 跳過）

### NFR-03：可維護性

- 程式碼遵循 PEP 8
- 依賴鎖定於 `uv.lock`
- musllinux stub 套件解決平台限制

### NFR-04：安全性

- API 金鑰僅透過環境變數傳遞，不寫入程式碼
- SonarQube 及 CodeQL 作為品質閘道

## 4. 約束條件

- Python 3.11+（externally-managed，須使用 `uv`）
- crewai==1.15.22（owner-confirmed pin）
- Alpine/musllinux 環境（部分依賴無原生 wheel，以 stub 替代）
- HKO LLM 端點需 SSL bypass（憑證未受系統信任）
