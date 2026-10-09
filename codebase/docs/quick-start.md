# 快速上手

## 前置需求

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) 套件管理器
- `HKOAI_API_KEY` 環境變數（HKO LLM 端點金鑰）

## 1. 安裝依賴

```bash
cd .crewai
uv sync
```

## 2. 執行管線

### 互動模式（啟動選單 TUI）

```bash
uv run python .crewai/run_tour_pipeline.py 2>&1 | tee "tour-guide-research-$(date '+%Y%m%dT%H%M%S').log"
```

### 優先模式

```bash
# 僅處理優先建築
uv run python .crewai/run_tour_pipeline.py --priority-only

# 優先建築先行，其後續接全部未完成
uv run python .crewai/run_tour_pipeline.py --priority-first
```

## 3. 監控進度

```bash
# 即時日誌
tail -f /tmp/tour_pipeline.log

# 最近提交紀錄
git log --oneline -10

# 查看矩陣狀態
# 法定古蹟
grep "🌕" .crewai/矩陣/法定古蹟/建築.md | wc -l
# 市區樓宇
grep "🌕" .crewai/矩陣/樓宇/市區建築.md | wc -l
# 新界樓宇
grep "🌕" .crewai/矩陣/樓宇/新界建築.md | wc -l
```

## 4. 部署 mdBook 網站

1. 前往 GitHub Actions UI
2. 選擇「CI/CD」workflow
3. 點擊「Run workflow」（`workflow_dispatch`）
4. 等待 `build` + `codeql` + `sonarqube` + `deploy` 全部通過
5. 訪問 `https://mcc-mak.github.io/hk-tour-guide/`

> **注意：** 部署 job 依賴 CodeQL + SonarQube 均通過。若任一閘道失敗，部署不會執行。
