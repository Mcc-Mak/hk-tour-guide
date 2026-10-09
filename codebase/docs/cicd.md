# CI/CD 文件

## Workflow 檔案

`.github/workflows/ci-cd.yml`

## 觸發條件

| 事件 | 觸發條件 |
| :--- | :--- |
| `push` | push 至 `dev-001` 或 `dev` |
| `workflow_dispatch` | 手動觸發（GitHub Actions UI） |

## Jobs

### 1. `auto_merge`

- **觸發**: `push` 事件
- **權限**: `contents: write`
- **步驟**:
  1. Checkout（`fetch-depth: 0`）
  2. 配置 Git 使用者
  3. 若來源為 `dev-001`：`git merge origin/dev-001 --no-ff --allow-unrelated-histories` → push to `dev`
  4. `git merge origin/dev --no-ff --allow-unrelated-histories` → push to `main`
- **認證**: 預設 `GITHUB_TOKEN`（其 push 不觸發級聯 workflow，故兩步合併在同一 job）

### 2. `codeql`

- **觸發**: `push` 或 `workflow_dispatch`
- **權限**: `security-events: write`, `contents: read`, `actions: read`
- **步驟**:
  1. Checkout
  2. Initialize CodeQL（`v4`，language: `python`，排除 `_stubs`、`__pycache__`、`site-packages`）
  3. Autobuild
  4. Perform CodeQL Analysis

### 3. `sonarqube`

- **觸發**: `push` 或 `workflow_dispatch`
- **步驟**:
  1. Checkout（`fetch-depth: 0`）
  2. SonarQube Scan（action pin: `SonarSource/sonarqube-scan-action@fd88b7d7ccbaefd23d8f36f73b59db7a3d246602`）
- **Secrets**: `SONAR_TOKEN`, `SONAR_HOST_URL`
- **專案設定**: `sonar-project.properties`

### 4. `build`

- **觸發**: 僅 `workflow_dispatch`
- **權限**: `contents: read`
- **步驟**:
  1. Checkout
  2. Setup Python 3.12
  3. `python3 codebase/site/scripts/build_mdbook.py` — 產生 `book-src/`
  4. Install mdBook（`peaceiris/actions-mdbook@ee69d230fe19748b7abf22df32acaa93833fad08`）
  5. `mdbook build codebase/site`
  6. Upload Pages artifact（`codebase/site/book`）

### 5. `deploy`

- **觸發**: 僅 `workflow_dispatch`
- **依賴**: `build` + `codeql` + `sonarqube`（三者均須通過）
- **權限**: `pages: write`, `id-token: write`
- **環境**: `github-pages`
- **步驟**:
  1. Deploy to GitHub Pages（`actions/deploy-pages@v4`）

## 並行控制

```yaml
concurrency:
  group: ci-cd
  cancel-in-progress: false
```

同一時間僅允許一個 CI/CD run，不取消進行中的 run。

## 品質閘道

| 閘道 | 保護範圍 |
| :--- | :--- |
| CodeQL | 安全性分析（Python） |
| SonarQube | 程式碼品質掃描 |
| 兩者均須通過 | mdBook 部署才會執行 |

## SonarCloud 設定

| 項目 | 值 |
| :--- | :--- |
| Organization | `mcc-mak` |
| Project Key | `Mcc-Mak_hk-tour-guide` |
| Project Name | `hk-tour-guide` |
| Sources | `codebase`, `.crewai` |
| Exclusions | `__pycache__`, `_stubs`, `site-packages` |
| Python Version | 3.12 |
| Analysis Method | CI-based（Automatic Analysis 已停用） |
