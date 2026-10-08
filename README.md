# 🇭🇰 香港導賞團

本專案用於管理香港建築導賞的目標對象及相關數據管線（Pipeline）。

---

## 📌 快速連結
> [!IMPORTANT]
> - **[導賞目標建築矩陣](導賞目標建築矩陣.md)**：詳細的導賞目標建築對照表與設定。

---

## 🛠 開發與監控

### 1. 即時日誌監控
> [!NOTE]
> 若要實時追蹤管線執行狀態，請執行以下指令：
> ```bash
> tail -f /tmp/tour_pipeline.log
> ```

### 2. 版本控制紀錄
> [!NOTE]
> 查看最近 10 筆提交紀錄，以確認更新進度：
> ```bash
> git log --oneline -10
> ```

---

## 🚀 快速上手

### 啟動管線（含日誌記錄）

> [!IMPORTANT]
> 執行前必須設定以下環境變數：
> - `HKOAI_API_KEY` — 香港政府 LLM 端點金鑰
> - `OPENCODE_API_KEY` — Big Pickle (OpenCode-Zen) 備用模型金鑰

```bash
uv run python run_tour_pipeline.py 2>&1 | tee "tour-guide-research-$(date '+%Y%m%dT%H%M%S').log"
```

指令說明：
- `uv run python run_tour_pipeline.py` — 以 `uv` 虛擬環境執行管線。
- `2>&1` — 合併 stdout 與 stderr，確保錯誤訊息亦寫入日誌。
- `| tee "..."` — 即時輸出至終端機，同時寫入帶時間戳的日誌檔案（例如 `tour-guide-research-20260108T143025.log`）。

### 優先模式（僅處理指定建築）

加入 `--priority-only` 旗標可跳過啟動選單 TUI，僅處理 `run_tour_pipeline.py` 中 `_PRIORITY_BUILDINGS` 所列的建築：

```bash
uv run python run_tour_pipeline.py --priority-only 2>&1 | tee "tour-guide-research-$(date '+%Y%m%dT%H%M%S').log"
```