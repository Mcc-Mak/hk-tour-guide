# 資料庫結構

> 本專案無傳統關聯式資料庫。資料以 Markdown 表格（矩陣子檔案）及 JSON 檔案（開放資料）形式儲存。以下記錄各資料實體的結構。

## 1. 矩陣子檔案（`.crewai/矩陣/**/*.md`）

### 1.1 表格結構

| 欄位順序 | 欄位名稱 | 類型 | 說明 |
| :---: | :--- | :--- | :--- |
| 1 | 編號 {N} | integer (string) | 子檔案內獨立遞增流水號，從 1 起 |
| 2 | 導賞專案類別 | string | `香港法定古蹟導賞團` 或 `香港樓宇導賞團` |
| 3 | 中文名稱 | string | 建築中文名稱 |
| 4 | 英文名稱 | string | 建築英文名稱 |
| 5 | 中文地址 | string | 建築中文地址 |
| 6 | 英文地址 | string | 建築英文地址 |
| 7 | 參考標籤 | string | 搜尋標籤（通常等同中文名稱） |
| 8 | 歷史檔案可信性 | enum | `典範` / `完整` / `基礎` / `種子` / `待考` |
| 9 | 歷史檔案工作進度 | enum | `🌚 未開始` / `🌒 進行中` / `🌗 審閱中` / `🌕 已完成` |
| 10 | 歷史檔案（連結） | markdown link | 由 CrewAI 動態產出，格式：`` [`歷史檔案（連結）`](codebase/建築/.../NNNNN-名稱.md) `` |

### 1.2 子檔案清單

| 檔案路徑 | 類別 | 資料來源 | 行數 |
| :--- | :--- | :--- | :--- |
| `.crewai/矩陣/法定古蹟/建築.md` | 法定古蹟 | CSDI KML | 173 |
| `.crewai/矩陣/樓宇/市區建築.md` | 樓宇（市區） | RVD Urban XML | 12,381 |
| `.crewai/矩陣/樓宇/新界建築.md` | 樓宇（新界） | RVD NT XML | 7,656 |

### 1.3 特殊處理

- Markdown 表格 cell 中的 `|` 字元以 `\|` 跳脫
- `_split_matrix_row()` / `_join_matrix_row()` 負責拆分與重組
- 排序鍵：`(子檔案順序, 編號 N)`，子檔案順序為 `法定古蹟 → 市區 → 新界`

## 2. 開放資料 JSON（`.crewai/data/`）

### 2.1 `declared_monuments.json`

```json
[
  {
    "name_zh": "前立法會大樓",
    "name_en": "Former Legislative Council Building",
    "address_zh": "中環遮打道8號",
    "address_en": "8 Chater Road, Central",
    "declared_date": "1984-00-00",
    "latitude": 22.2811,
    "longitude": 114.1593
  }
]
```

### 2.2 `buildings_urban.json` / `buildings_nt.json`

```json
[
  {
    "name_zh": "示例大廈",
    "name_en": "Example Building",
    "address_zh": "九龍尖沙咀彌敦道1號",
    "address_en": "1 Nathan Road, Tsim Sha Tsui, Kowloon",
    "district": "油尖旺區",
    "building_age": 50
  }
]
```

## 3. 手冊檔案（`codebase/建築/**/*.md`）

| 欄位 | 類型 | 說明 |
| :--- | :--- | :--- |
| 檔名 | `NNNNN-名稱.md` | NNNNN = 編號 N 零填補至 5 位 |
| 路徑 | `codebase/建築/{法定古蹟\|樓宇/市區\|樓宇/新界}/` | 依類別分類 |
| 格式 | Markdown（繁體中文） | 六段式標準結構 |
| 內容 | CrewAI 動態生成 | 含 CL 評級表、歷史檔案連結、導賞講稿 |
