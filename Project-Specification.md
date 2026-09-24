# 香港導賞團專案：CrewAI 自動化工作流程規格書（歷史檔案欄位完全由 CrewAI 輸出版）

本規格書已精確定位您的核心要求：**「歷史檔案（連結）」欄位不再寫死在靜態矩陣中，而是完全交由 CrewAI 執行期中的研究員代理人（Official Archives Researcher）與總編輯代理人動態搜集、驗證，並以標準 Markdown 超連結格式（例如 `[官方檔案名稱](URL)`）寫入最終生成的 Markdown 導賞手冊中。**

---

## 📁 1. 專案檔案結構總覽

```text
hk-tour-automation/
├── AGENTS.md                   # 代理人角色、CL 評級與 Emoji 狀態標準
├── BUILDING_MATRIX.md          # 目標建築矩陣對照表（歷史檔案連結欄位留白交由 CrewAI 動態產出）
├── fetch_open_data.py          # 香港開放資料下載腳本
├── run_tour_pipeline.py        # 執行管線、5位數命名、啟動選單 TUI 與 Git 自動化主程式
├── data/                       # 下載之香港開放資料原始檔 (XML/JSON)
└── 建築/                       # 自動生成的 Markdown 導賞手冊儲存目錄（格式：00001-建築名稱.md）
    ├── 00001-舊中區警署.md
    └── ...

```

---

## 📝 2. 步驟 0：初始化檔案

### `AGENTS.md`

```markdown
# 香港導賞專案：CrewAI 代理人團隊與評估標準

## 1. 代理人團隊角色設定

### 代理人 1：香港官方檔案研究員 (Official Archives Researcher)
* **角色**: 歷史文獻與政府開放資料分析師
* **背景故事**: 擁有超過 15 年香港建築史與古物古蹟辦事處 (AMO) 檔案研究經驗，精通香港政府憲報與開放資料集（data.gov.hk）。
* **主要任務**: 負責從零搜集建築歷史檔案，並主動檢索最具公信力的官方檔案，**強制以 Markdown 超連結格式（例如 `[古物古蹟辦事處官方公告](https://...)`）作為「歷史檔案（連結）」的輸出內容**。

### 代理人 2：首席事實查核與信譽評估員 (Fact-Checker & Credibility Assessor)
* **角色**: 嚴格的事實審查與幻覺過濾專家
* **背景故事**: 資深香港歷史學家與資深新聞審查員，對未經證實的民間傳說持極高懷疑態度。
* **主要任務**: 指派 CL 1-5 可信度評級，並將專案狀態自動推進至 `🟢 已完成`。

### 代理人 3：文化導賞故事編劇 (Cultural Tour Playwright)
* **角色**: 繁體中文導賞解說資深撰稿人
* **背景故事**: 香港本土文化遺產導賞培訓師，擅長將歷史數據轉換為生動且符合香港在地語言習慣的導賞解說詞。
* **主要任務**: 將查核無誤的事實撰寫成引人入勝的導賞故事與腳本。

### 代理人 4：導賞手冊總編輯 (Handbook Chief Editor)
* **角色**: Markdown 排版與品質控制總監
* **背景故事**: 出版社高級編輯，嚴格把關導賞手冊的格式規範、結構排版與超連結宣告。
* **主要任務**: 整合所有內容，確保手冊結構完整、CL 表格正確，且由研究員產出的「歷史檔案（連結）」完全採用合法 Markdown 超連結格式呈現。

---

## 2. 可信度評級 (Credibility Level, CL) 標準

| 評級 | 分級名稱 | 定義與資料來源 |
| :--- | :--- | :--- |
| **CL 5** | **官方權威** | 古物古蹟辦事處 (AMO) 憲報紀錄、香港政府檔案處、法定古蹟官方公告。 |
| **CL 4** | **學術專著** | 本地大學建築系專題論文、香港皇家亞洲學會專刊、同儕審查之歷史文獻。 |
| **CL 3** | **主流媒體/NGO** | 具信譽之新聞媒體報導、活化歷史建築夥伴計劃官方報告。 |
| **CL 2** | **民間口述** | 街坊口述歷史紀錄、舊導賞員個人經驗分享。 |
| **CL 1** | **未經證實** | 都市傳說、民間風水傳聞（必須明確標註為傳說）。 |

---

## 3. 歷史檔案雙向評估標準

### A. 歷史檔案可信性（考證深度）
* **典範**：檔案、學術、口述、地圖或圖則互相印證，註釋與可信度評級 (CL) 極其完整。
* **完整**：多來源考證、具備歷史年表、建築特色說明、並列不同說法。
* **基礎**：標準結構大致完整，具備 3 個以上來源交叉比對。
* **種子**：具備基本資料與至少 1 個可靠來源。
* **待考**：資料出現明顯缺口或矛盾，需標註待進一步考證。

### B. 歷史檔案工作進度（專案生命週期 Emoji 狀態）
* **🔴 未開始**：【預設狀態】項目已列入矩陣排程，等待管線調用後由 CrewAI 自動啟動編撰。
* **🟡 進行中**：資料搜集、多方交叉比對與初稿撰寫作業進行中。
* **🟠 審閱中**：初稿已生成，總編輯正在進行格式校對與語氣複核。
* **🟢 已完成**：內容全面編撰、事實查核、檔案連結與參考清單均已到位。

```

### `BUILDING_MATRIX.md`

> *註：矩陣中的「歷史檔案（連結）」欄位統一預設為交由 CrewAI 動態產出的標示，實際內容由 AI 在生成手冊時填入 Markdown 連結。*

```markdown
# 導賞目標建築矩陣 (Building Matrix)

| 編號 {N} | 導賞專案類別 | 中文名稱 | 英文名稱 | 中文地址 | 英文地址 | 參考標籤 | 歷史檔案可信性 | 歷史檔案工作進度 | 歷史檔案（連結） |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 香港法定古蹟導賞團 | 前立法會大樓 | Former Legislative Council Building | 中環遮打道8號 | 8 Chater Road, Central | 前立法會大樓 | 典範 | 🔴 未開始 | *(由 CrewAI 動態產出 Markdown 連結)* |
| 2 | 香港法定古蹟導賞團 | 舊中區警署 | Former Central Police Station | 中環荷李活道10號 | 10 Hollywood Road, Central | 舊中區警署 | 典範 | 🔴 未開始 | *(由 CrewAI 動態產出 Markdown 連結)* |
| 3 | 香港樓宇導賞團 | 藍屋建築群 | Blue House Cluster | 灣仔石水渠街72-74號 | 72-74 Stone Nullah Lane, Wan Chai | 藍屋建築群 | 完整 | 🔴 未開始 | *(由 CrewAI 動態產出 Markdown 連結)* |
| 4 | 香港樓宇導賞團 | 雷生春 | Lui Seng Chun | 旺角荔枝角道119號 | 119 Lai Chi Kok Road, Mong Kok | 雷生春 | 種子 | 🔴 未開始 | *(由 CrewAI 動態產出 Markdown 連結)* |

```

### `fetch_open_data.py`

```python
#!/usr/bin/env python3
"""
香港開放資料下載腳本：從官方來源下載歷史建築與古蹟資料
"""
import os
import urllib.request

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

DATA_SOURCES = {
    "monuments_info.xml": "https://www.amo.gov.hk/filemanager/amo/common/form/declared_monuments_tc.xml",
    "historic_buildings.json": "https://api.data.gov.hk/v1/filter?q=%7B%22resource%22%3A%22http%3A%2F%2Fwww.amo.gov.hk%2Fdatagovhk%2Fmonument_tc.json%22%7D"
}

def download_open_data():
    print("⬇️ 開始下載香港開放資料集...")
    for filename, url in DATA_SOURCES.items():
        filepath = os.path.join(DATA_DIR, filename)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
                out_file.write(response.read())
            print(f"✅ 成功下載: {filename}")
        except Exception as e:
            print(f"⚠️ 下載 {filename} 失敗: {e}，建立本地參考備用檔。")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("<data><status>Local Fallback Reference</status></data>")

if __name__ == "__main__":
    download_open_data()

```

---

## 🛠️ 3. 步驟 1 與 2：具備前端啟動 TUI 與 CrewAI 動態 Markdown 連結的自動化管線 (`run_tour_pipeline.py`)

```python
#!/usr/bin/env python3
"""
香港導賞團自動化生成管線（含前端啟動 TUI 與 CrewAI Markdown 連結輸出）
- 多代理人協作 (CrewAI)
- LLM 優先調用 HKO/GLM-5.2-FP8，失敗時自動 Fallback 至 OpenCode-Zen
- 支援 5 位數編號檔案命名 (例如 00001-建築名稱.md)
- 內建矩陣排序 (導賞專案類別 -> 中文名稱 -> 中文地址)
- 啟動選單 TUI：於程式執行初期詢問整體執行範圍（全部執行 / 僅未開始項目 / 離開）
- 強制規定「歷史檔案（連結）」由 CrewAI 研究員及總編輯以 Markdown 語法動態產出
- 自動進行 Git Add, Commit 與 Push
"""

import os
import subprocess
from pathlib import Path
from crewai import Agent, Crew, Process, Task, LLM

# ==========================================
# 1. LLM 初始化配置 (含 Fallback 機制)
# ==========================================

def get_primary_llm() -> LLM:
    """初始化優先模型：HKO/GLM-5.2-FP8"""
    hko_api_key = os.getenv("HKOAI_API_KEY", "")
    return LLM(
        model="openai/zai-org/GLM-5.2-FP8",
        base_url="https://litellm.services.hko.gov.hk",
        api_key=hko_api_key if hko_api_key else "dummy_key",
        temperature=0.2,
        timeout=60
    )

def get_fallback_llm() -> LLM:
    """初始化 Fallback 免費模型：OpenCode-Zen"""
    return LLM(
        model="openai/opencode-zen",
        base_url="https://api.opencode.ai/v1",
        api_key=os.getenv("OPENCODE_API_KEY", "free-tier"),
        temperature=0.2,
        timeout=60
    )

def execute_crew_with_fallback(agents_builder_func, tasks_builder_func, inputs: dict) -> str:
    """執行 CrewAI 任務，具備自動 Fallback 機制"""
    try:
        print("🚀 正在嘗試使用優先模型: HKO/GLM-5.2-FP8...")
        primary_llm = get_primary_llm()
        agents = agents_builder_func(primary_llm)
        tasks = tasks_builder_func(agents, inputs)
        crew = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=False)
        result = crew.kickoff(inputs=inputs)
        print("✅ HKO/GLM-5.2-FP8 執行成功！")
        return str(result)
    except Exception as e:
        print(f"⚠️ 優先模型調用失敗: {e}")
        print("🔄 自動切換（Fallback）至免費模型: OpenCode-Zen...")
        try:
            fallback_llm = get_fallback_llm()
            agents = agents_builder_func(fallback_llm)
            tasks = tasks_builder_func(agents, inputs)
            crew = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=False)
            result = crew.kickoff(inputs=inputs)
            print("✅ OpenCode-Zen Fallback 執行成功！")
            return str(result)
        except Exception as fb_err:
            raise RuntimeError(f"❌ 所有 LLM 模型（含 Fallback）均調用失敗: {fb_err}")

# ==========================================
# 2. 定義 CrewAI Agents 與 Tasks
# ==========================================

def build_agents(llm: LLM):
    researcher = Agent(
        role="香港官方檔案研究員",
        goal="搜集目標建築的官方歷史檔案、建築風格與背景，並自主挖掘、驗證最具公信力的官方檔案，**強制以 Markdown 超連結格式（例如 `[官方檔案名稱](URL)`）輸出「歷史檔案（連結）」**。",
        backstory="你是一位資深香港歷史研究員，精通香港開放資料集、古物古蹟辦事處 (AMO) 資料與官方文獻。",
        llm=llm,
        verbose=False
    )
    
    checker = Agent(
        role="首席事實查核與信譽評估員",
        goal="審查資料，過濾 AI 幻覺，指派 CL 1-5 可信度評級，並將專案狀態推進至 🟢 已完成。",
        backstory="你對歷史事實要求極度嚴格，能精準評估文獻考證深度與專案推進階段。",
        llm=llm,
        verbose=False
    )
    
    writer = Agent(
        role="文化導賞故事編劇",
        goal="撰寫符合香港在地導賞風格、生動且專業的繁體中文導賞解說詞。",
        backstory="你是導賞員培訓導師，精通以故事化手法介紹香港歷史建築。",
        llm=llm,
        verbose=False
    )
    
    editor = Agent(
        role="導賞手冊總編輯",
        goal="整合所有資料，格式化為標準 Markdown 文檔，**確保手冊中的「歷史檔案（連結）」欄位由 CrewAI 官方檔案研究員動態產出，且所有連結必須嚴格採用 Markdown 語法（[顯示名稱](URL)）呈現**。",
        backstory="你是出版社主編，對導賞手冊的格式規範、結構排版與 Markdown 超連結宣告有最高要求。",
        llm=llm,
        verbose=False
    )
    
    return [researcher, checker, writer, editor]

def build_tasks(agents, inputs: dict):
    researcher, checker, writer, editor = agents
    
    t1 = Task(
        description=(
            "研究目標建築 '{building_name}'（地址：{address}，類別：{category}，標籤：{tag}）。"
            "請全面搜集其建設年份、建築風格與歷史事件，並**必須自主挖掘或整理出該建築最具公信力的官方歷史檔案連結，並強制以 Markdown 格式（例如 [官方文獻名稱](網址)）作為「歷史檔案（連結）」的輸出內容**。"
        ),
        expected_output="包含建築基本數據、歷史事實、參考資料清單以及由 CrewAI 動態產出之 Markdown 格式官方檔案超連結的研究報告。",
        agent=researcher
    )
    
    t2 = Task(
        description=(
            "對前述資料進行事實查核，將歷史數據整理為表格，指定 CL 1-5 可信度評級，"
            "並確認其「歷史檔案可信性」（目標：{credibility}）。"
            "請將其目前狀態（{completion}）正式推進至「🟢 已完成」。"
        ),
        expected_output="含 CL 評級表與狀態推進確認之報告。",
        agent=checker
    )
    
    t3 = Task(
        description="根據已查核資料，編寫適合導賞員現場口述的繁體中文導賞稿（包含現場觀察重點與歷史故事）。",
        expected_output="流暢且專業的繁體中文導賞解說文稿。",
        agent=writer
    )
    
    t4 = Task(
        description=(
            "將以上所有內容匯整為一份標準 Markdown 格式手冊。\n"
            "必須包含以下章節：\n"
            "1. 導賞概覽與地址資訊\n"
            "2. 歷史脈絡與建築特色\n"
            "3. 事實查核與可信度評級表 (CL 1-5)\n"
            "4. 歷史檔案狀態宣告（包含可信性等級、已更新之完成度 🟢 已完成，以及由 CrewAI 研究員動態產出之「歷史檔案（連結）」，**必須為標準 Markdown 超連結格式 [名稱](URL)**）\n"
            "5. 導賞員現場講稿\n"
            "6. 參考資料來源（列出官方檔案與參考文獻清單，所有網址均需採用 Markdown 語法）\n"
            "全篇使用專業繁體中文。"
        ),
        expected_output="結構完整的 Markdown 導賞手冊全文（含 CrewAI 動態產出之 Markdown 歷史檔案超連結）。",
        agent=editor
    )
    
    return [t1, t2, t3, t4]

# ==========================================
# 3. Git 自動化控制
# ==========================================

def run_git_command(args: list):
    result = subprocess.run(["git"] + args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"⚠️ Git 提示 (git {' '.join(args)}): {result.stderr.strip()}")
    else:
        print(f" Git: git {' '.join(args)}")

def auto_git_commit_and_push(file_path: str, building_name: str, branch: str = "dev-001"):
    print(f"📦 對 {file_path} 進行版本控制...")
    run_git_command(["add", file_path])
    commit_msg = f"docs(tour): 自動化生成 {building_name} 之導賞手冊 (含 CrewAI 動態 Markdown 檔案連結)"
    run_git_command(["commit", "-m", commit_msg])
    run_git_command(["push", "origin", branch])

# ==========================================
# 4. 主流程 (含解析、排序與啟動選單 TUI)
# ==========================================

def parse_and_sort_building_matrix(matrix_path: str = "BUILDING_MATRIX.md") -> list:
    """
    解析 BUILDING_MATRIX.md 並依序以：
    1. 導賞專案類別
    2. 中文名稱
    3. 中文地址
    進行排序
    """
    buildings = []
    if not os.path.exists(matrix_path):
        return [{
            "N": "1", 
            "category": "香港法定古蹟導賞團", 
            "name": "舊中區警署", 
            "address": "中環荷李活道10號", 
            "tag": "舊中區警署",
            "credibility": "典範",
            "completion": "🔴 未開始"
        }]
        
    with open(matrix_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("|") and not line.startswith("| 編號") and "---" not in line:
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 9:
                    buildings.append({
                        "N": parts[0],
                        "category": parts[1],
                        "name": parts[2],
                        "address": parts[4],
                        "tag": parts[6],
                        "credibility": parts[7],
                        "completion": parts[8]
                    })
                    
    # 依照要求排序：導賞專案類別、中文名稱、中文地址
    sorted_buildings = sorted(
        buildings, 
        key=lambda x: (x["category"], x["name"], x["address"])
    )
    return sorted_buildings

def main():
    output_dir = Path("建築")
    output_dir.mkdir(exist_ok=True)
    
    buildings = parse_and_sort_building_matrix()
    print(f"📋 共讀取到 {len(buildings)} 棟標的建築（已依規則排序）。\n")
    
    # === 啟動選單 TUI（在每次執行開頭詢問一次） ===
    print("=" * 60)
    print("🏛️ 香港導賞團自動化管線 - 啟動選單")
    print("=" * 60)
    print("  [1] 執行全部建築項目 (Run all buildings)")
    print("  [2] 僅執行「🔴 未開始」項目 (Run only unstarted items)")
    print("  [3] 離開程式 (Quit)")
    print("-" * 60)
    
    while True:
        mode_choice = input("請選擇執行模式 [1/2/3]: ").strip()
        if mode_choice in ['1', '2', '3']:
            break
        print("⚠️ 輸入無效，請重新輸入 1, 2 或 3。")
        
    if mode_choice == '3':
        print("🛑 使用者選擇離開。程式結束。")
        return
    elif mode_choice == '2':
        target_buildings = [b for b in buildings if "未開始" in b["completion"]]
        print(f"\n🔍 已過濾出 {len(target_buildings)} 個「🔴 未開始」的項目準備執行。")
    else:
        target_buildings = buildings
        print(f"\n⚡ 將依序批次執行全部共 {len(target_buildings)} 個建築項目。")
        
    if not target_buildings:
        print("📭 目前沒有符合條件的建築需要處理。")
        return
        
    print("=" * 60 + "\n")
    
    # === 批次自動化執行迴圈 ===
    for idx, item in enumerate(target_buildings, start=1):
        n_id = str(idx).zfill(5)
        b_name = item["name"]
        category = item["category"]
        address = item["address"]
        tag = item["tag"]
        credibility = item["credibility"]
        completion = item["completion"]
        
        file_path = output_dir / f"{n_id}-{b_name}.md"
        
        print(f"--------------------------------------------------")
        print(f"🏗️ 正在處理 [{n_id}] {b_name} ({category}) | 狀態: {completion} -> 啟動 CrewAI...")
        
        inputs = {
            "building_name": b_name,
            "category": category,
            "address": address,
            "tag": tag,
            "credibility": credibility,
            "completion": completion
        }
        
        content = execute_crew_with_fallback(build_agents, build_tasks, inputs)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📄 手冊已成功寫入: {file_path}")
        
        auto_git_commit_and_push(str(file_path), b_name, branch="dev-001")
        print(f"✨ [{b_name}] 處理完成！\n")

    print("\n🎉 選定的所有導賞手冊均已成功透過 CrewAI 動態生成 Markdown 檔案連結並提交至 Git！")

if __name__ == "__main__":
    main()

```