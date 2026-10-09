# 後端 API 文件

> 本專案無傳統 REST API 後端服務。以下記錄管線的 CLI 介面、LLM 端點及 CI/CD 觸發介面。

## 1. CLI 介面

### 1.1 管線執行

```bash
uv run python .crewai/run_tour_pipeline.py [FLAGS] 2>&1 | tee "tour-guide-research-$(date '+%Y%m%dT%H%M%S').log"
```

| 旗標 | 說明 |
| :--- | :--- |
| （無） | 顯示啟動選單 TUI（4 種模式） |
| `--priority-only` | 跳過 TUI，僅處理 `_PRIORITY_BUILDINGS` 中的建築 |
| `--priority-first` | 跳過 TUI，優先建築先行，其後續接全部未完成項目 |

### 1.2 開放資料下載

```bash
uv run python .crewai/fetch_open_data.py
```

無旗標。下載 CSDI KML + RVD XML 至 `.crewai/data/`。

### 1.3 mdBook 建置

```bash
python3 codebase/site/scripts/build_mdbook.py   # 產生 book-src/
mdbook build codebase/site                       # 編譯至 codebase/site/book/
```

## 2. LLM 端點

### 2.1 端點資訊

| 項目 | 值 |
| :--- | :--- |
| Base URL | `https://litellm.services.hko.gov.hk` |
| 認證 | Bearer token（環境變數 `HKOAI_API_KEY`） |
| 協定 | OpenAI-compatible Chat Completions API |
| SSL | 需 `verify=False`（端點憑證未受系統信任） |

### 2.2 模型

| 模型 | 用途 | 參數 |
| :--- | :--- | :--- |
| `zai-org/GLM-5.2-FP8` | 優先模型 | temperature=0.2, max_tokens=16000, timeout=600s |
| `deepseek-ai/DeepSeek-V4-Flash-0731-Coding` | 備援模型 | 同上 |

### 2.3 Chat Completions 請求範例

```http
POST /chat/completions HTTP/1.1
Host: litellm.services.hko.gov.hk
Authorization: Bearer ${HKOAI_API_KEY}
Content-Type: application/json

{
  "model": "zai-org/GLM-5.2-FP8",
  "messages": [{"role": "user", "content": "OK"}],
  "max_tokens": 1,
  "temperature": 0.0,
  "stream": false
}
```

### 2.4 連線預檢

`preflight_llm_check()` 以 `max_tokens=1` 發送最小化請求：
- HTTP 200 → 連線正常
- 非 200 → 跳過該模型，記錄錯誤訊息

## 3. CI/CD 觸發介面

### 3.1 自動觸發（push to dev-001）

Push 至 `dev-001` 或 `dev` 時自動觸發以下 job：

| Job | 說明 |
| :--- | :--- |
| `auto_merge` | `dev-001` → `dev` → `main`（`--no-ff --allow-unrelated-histories`） |
| `codeql` | CodeQL 安全分析（Python） |
| `sonarqube` | SonarQube 程式碼品質掃描 |

### 3.2 手動觸發（workflow_dispatch）

透過 GitHub Actions UI 手動觸發，執行以下 job：

| Job | 依賴 | 說明 |
| :--- | :--- | :--- |
| `build` | — | 產生 book-src、安裝 mdBook、建置靜態網站、上傳 artifact |
| `deploy` | `build` + `codeql` + `sonarqube` | 部署至 GitHub Pages |
