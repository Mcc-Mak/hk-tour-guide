# 環境設定指南

## 1. 系統需求

| 項目 | 需求 |
| :--- | :--- |
| OS | Linux（Alpine/musllinux 已驗證） |
| Python | 3.11+ |
| uv | 最新版（`/usr/bin/uv` 或自行安裝） |
| Git | 任意版本 |

## 2. 複製專案

```bash
git clone https://github.com/Mcc-Mak/hk-tour-guide.git
cd hk-tour-guide
git checkout dev-001
```

## 3. 安裝依賴

```bash
cd .crewai
uv sync
```

此指令會：
1. 建立 `.venv/` 虛擬環境
2. 安裝 `crewai==1.15.22` 及所有依賴
3. 使用 `.crewai/_stubs/` 中的 stub 套件替代無 musllinux wheel 的依賴

### Stub 套件說明

| 套件 | 原因 | 是否實際使用 |
| :--- | :--- | :--- |
| `lancedb` | 無 musllinux wheel | 否（crewai Memory 功能未使用） |
| `chromadb` | 需 Rust 編譯 | 否（crewai RAG 功能未使用） |
| `onnxruntime` | 無 musllinux wheel | 否（chromadb 嵌入未使用） |
| `google-re2` | 需 C++ 編譯（abseil-cpp） | 否（crewai Flow CEL 未使用） |

## 4. 環境變數

```bash
export HKOAI_API_KEY="your-api-key-here"
```

| 變數 | 必要 | 說明 |
| :--- | :---: | :--- |
| `HKOAI_API_KEY` | 是 | HKO LLM 端點金鑰（GLM-5.2-FP8 + DeepSeek 共用） |

> **安全警告：** 絕不可將 API 金鑰寫入程式碼或提交至 Git。

## 5. 驗證安裝

```bash
# 測試 crewai import
uv run python -c "from crewai import Agent, Crew, Process, Task, LLM; print('OK')"

# 測試矩陣解析
uv run python -c "from run_tour_pipeline import parse_and_sort_building_matrix; print(len(parse_and_sort_building_matrix()))"
# 預期輸出: 20210
```

## 6. 下載開放資料（可選）

```bash
uv run python .crewai/fetch_open_data.py
```

輸出至 `.crewai/data/`：
- `declared_monuments.json`（173 項）
- `buildings_urban.json`（12,381 項）
- `buildings_nt.json`（7,656 項）

## 7. 常見問題

### Q: `uv sync` 失敗，提示 musllinux 不支援？

確認 `.crewai/pyproject.toml` 中的 `[tool.uv.sources]` 正確指向 `_stubs/` 目錄。stub 套件路徑為相對路徑。

### Q: LLM 連線失敗？

1. 確認 `HKOAI_API_KEY` 已設定
2. 確認網路可達 `https://litellm.services.hko.gov.hk`
3. SSL 問題已由 `run_tour_pipeline.py` 中的 httpx monkey-patch 處理（`verify=False`）

### Q: 管線執行中斷，如何恢復？

直接重新執行。已完成的建築狀態為 `🌕 已完成`，可選擇模式 2（僅執行未開始項目）跳過。
