# 組態參考

## 1. 環境變數

| 變數 | 必要 | 預設值 | 說明 |
| :--- | :---: | :--- | :--- |
| `HKOAI_API_KEY` | 是 | — | HKO LLM 端點金鑰 |

## 2. LLM 組態（`run_tour_pipeline.py`）

### 2.1 優先模型

| 參數 | 值 |
| :--- | :--- |
| model | `openai/zai-org/GLM-5.2-FP8` |
| base_url | `https://litellm.services.hko.gov.hk` |
| temperature | 0.2 |
| max_tokens | 16000 |
| timeout | 600 秒 |
| max_retries | 0 |
| stream | false |

### 2.2 備援模型

| 參數 | 值 |
| :--- | :--- |
| model | `openai/deepseek-ai/DeepSeek-V4-Flash-0731-Coding` |
| base_url | `https://litellm.services.hko.gov.hk` |
| temperature | 0.2 |
| max_tokens | 16000 |
| timeout | 600 秒 |
| max_retries | 0 |
| stream | false |

### 2.3 SSL

```python
httpx.Client.__init__ → verify=False  # HKO 端點憑證未受系統信任
httpx.AsyncClient.__init__ → verify=False
```

## 3. 管線常數

| 常數 | 值 | 說明 |
| :--- | :--- | :--- |
| `REPO_ROOT` | 專案根目錄 | `Path(__file__).resolve().parent.parent` |
| `MATRIX_DIR` | `.crewai/矩陣` | 矩陣子檔案目錄 |
| `BUILDING_DIR` | `codebase/建築` | 手冊輸出目錄 |
| `MATRIX_FILE_ORDER` | `["法定古蹟/建築.md", "樓宇/市區建築.md", "樓宇/新界建築.md"]` | 子檔案讀取順序 |
| Git branch | `dev-001` | 自動 push 目標分支 |

### 3.1 優先建築（`_PRIORITY_BUILDINGS`）

```python
_PRIORITY_BUILDINGS = {
    "新界建築.md": frozenset({
        5847, 5907–5924, 6157, 6294, 6796, 6797, 6903, 7582, 7594, 7600, 7653,
    }),
}
```

## 4. CI/CD Secrets

| Secret | 用途 |
| :--- | :--- |
| `SONAR_TOKEN` | SonarCloud 認證 |
| `SONAR_HOST_URL` | SonarCloud 主機 URL |

## 5. 專案設定檔

| 檔案 | 說明 |
| :--- | :--- |
| `.crewai/pyproject.toml` | Python 專案定義、依賴、uv sources |
| `.crewai/uv.lock` | 依賴鎖定檔 |
| `sonar-project.properties` | SonarQube 掃描設定 |
| `codebase/site/book.toml` | mdBook 網站設定 |
| `.github/workflows/ci-cd.yml` | CI/CD workflow 定義 |
| `.gitignore` | Git 忽略規則 |

## 6. SonarQube 設定（`sonar-project.properties`）

| 屬性 | 值 |
| :--- | :--- |
| `sonar.projectKey` | `Mcc-Mak_hk-tour-guide` |
| `sonar.organization` | `mcc-mak` |
| `sonar.projectName` | `hk-tour-guide` |
| `sonar.sources` | `codebase,.crewai` |
| `sonar.exclusions` | `**/__pycache__/**,**/_stubs/**,**/site-packages/**` |
| `sonar.python.version` | 3.12 |

## 7. mdBook 設定（`codebase/site/book.toml`）

| 屬性 | 值 |
| :--- | :--- |
| title | 香港建築導賞手冊 |
| language | zh-Hant |
| src | book-src |
| git-repository-url | `https://github.com/Mcc-Mak/hk-tour-guide` |
| search | 啟用（limit=30, boolean-and, boost-title=2） |
