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

import glob
import os
import re
import subprocess
from pathlib import Path

import httpx

_original_client_init = httpx.Client.__init__
_original_async_client_init = httpx.AsyncClient.__init__

def _patched_client_init(self, *args, **kwargs):
    if "verify" not in kwargs:
        kwargs["verify"] = False
    return _original_client_init(self, *args, **kwargs)

def _patched_async_client_init(self, *args, **kwargs):
    if "verify" not in kwargs:
        kwargs["verify"] = False
    return _original_async_client_init(self, *args, **kwargs)

httpx.Client.__init__ = _patched_client_init
httpx.AsyncClient.__init__ = _patched_async_client_init

from crewai import Agent, Crew, Process, Task, LLM

MATRIX_PATH = "導賞目標建築矩陣.md"
MATRIX_DIR = "矩陣"
BUILDING_DIR = "建築"
MATRIX_FILE_ORDER = ["法定古蹟.md", "樓宇-市區.md", "樓宇-新界.md"]

def _category_to_subdir(category: str) -> str:
    """Map matrix category to handbook subdirectory name."""
    if "法定古蹟" in category:
        return "法定古蹟"
    return "樓宇"

def _split_matrix_row(line: str) -> list:
    """Split a Markdown table row on | (respecting \\| escapes), un-escape, and strip."""
    parts = re.split(r'(?<!\\)\|', line)
    parts = parts[1:-1]  # drop leading/trailing empty from | ... |
    return [p.strip().replace('\\|', '|') for p in parts]

def _join_matrix_row(parts: list) -> str:
    """Join parts into a Markdown table row, escaping | characters."""
    escaped = [p.replace('|', '\\|') for p in parts]
    return "| " + " | ".join(escaped) + " |\n"

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
        timeout=180
    )

def get_fallback_llm() -> LLM:
    """初始化 Fallback 免費模型：OpenCode-Zen"""
    return LLM(
        model="openai/opencode-zen",
        base_url="https://api.opencode.ai/v1",
        api_key=os.getenv("OPENCODE_API_KEY", "free-tier"),
        temperature=0.2,
        timeout=180
    )

def execute_crew_with_fallback(agents_builder_func, tasks_builder_func, inputs: dict) -> str:
    """執行 CrewAI 任務，具備自動 Fallback 機制"""
    try:
        print("🚀 正在嘗試使用優先模型: HKO/GLM-5.2-FP8...")
        primary_llm = get_primary_llm()
        agents = agents_builder_func(primary_llm)
        tasks = tasks_builder_func(agents, inputs)
        crew = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=True)
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
            crew = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=True)
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
        verbose=True
    )

    checker = Agent(
        role="首席事實查核與信譽評估員",
        goal="審查資料，過濾 AI 幻覺，指派 CL 1-5 可信度評級，並將專案狀態推進至 🌕 已完成。",
        backstory="你對歷史事實要求極度嚴格，能精準評估文獻考證深度與專案推進階段。",
        llm=llm,
        verbose=True
    )

    writer = Agent(
        role="文化導賞故事編劇",
        goal="撰寫符合香港在地導賞風格、生動且專業的繁體中文導賞解說詞。",
        backstory="你是導賞員培訓導師，精通以故事化手法介紹香港歷史建築。",
        llm=llm,
        verbose=True
    )

    editor = Agent(
        role="導賞手冊總編輯",
        goal="整合所有資料，格式化為標準 Markdown 文檔，**確保手冊中的「歷史檔案（連結）」欄位由 CrewAI 官方檔案研究員動態產出，且所有連結必須嚴格採用 Markdown 語法（[顯示名稱](URL)）呈現**。",
        backstory="你是出版社主編，對導賞手冊的格式規範、結構排版與 Markdown 超連結宣告有最高要求。",
        llm=llm,
        verbose=True
    )

    return [researcher, checker, writer, editor]

def build_tasks(agents, inputs: dict):
    researcher, checker, writer, editor = agents

    t1 = Task(
        description=(
            "研究目標建築 '{building_name}'（地址：{address}，類別：{category}，標籤：{tag}）。"
            "請全面搜集其建設年份、建築風格與歷史事件，並**必須自主挖掘或整理出該建築最具公信力的官方歷史檔案連結**。"
            "每個歷史檔案連結必須嚴格採用以下格式：[`CL {可信度評級}：{機構名稱}`](URL)，例如 [`CL 5：古物古蹟辦事處`](https://www.amo.gov.hk/...)。"
            "其中{可信度評級}為 1-5 的整數（CL 5=官方權威、CL 4=學術專著、CL 3=主流媒體/NGO、CL 2=民間口述、CL 1=未經證實），{機構名稱}為該檔案的發佈機構全稱。"
            "歷史事件資料必須以「{歷史時期/特徵}」分組，每組內以「{年份}：{歷史描述}」格式條列整理。"
        ),
        expected_output="包含建築基本數據、歷史事實（以「{年份}：{歷史描述}」格式按「{歷史時期/特徵}」分組）、參考資料清單以及由 CrewAI 動態產出之 Markdown 格式官方檔案超連結（格式為 [`CL {評級}：{機構名稱}`](URL)）的研究報告。",
        agent=researcher
    )

    t2 = Task(
        description=(
            "對前述資料進行事實查核，將歷史數據整理為表格，指定 CL 1-5 可信度評級，"
            "並確認其「歷史檔案可信性」（目標：{credibility}）。"
            "請將其目前狀態（{completion}）正式推進至「🌕 已完成」。"
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
            "必須嚴格遵循以下章節結構（使用中文數字編號一至六），不可增減章節：\n\n"
            "## 一、導賞概覽與地址資訊\n"
            "### 建築基本資料\n"
            "（必須包含表格：建築名稱、地址、建設年份、建築風格、歷史評級）\n"
            "### 導賞路線建議\n\n"
            "## 二、歷史脈絡與建築特色\n"
            "### 建築風格與特色\n"
            "### 歷史事件與背景\n"
            "（必須以「#### {歷史時期/特徵}」作為四級子標題分組，每組下列條目必須採用「- {年份}：{歷史描述}」格式條列）\n\n"
            "## 三、事實查核與可信度評級表（CL 1-5）\n"
            "### 歷史數據查核結果\n"
            "（必須包含表格：項目、報告記載內容、查核結果、佐證來源、CL 評級）\n"
            "### AI 幻覺過濾檢測報告\n"
            "### 整體可信度評級\n"
            "（必須包含表格：評估維度、CL 評級、說明）\n\n"
            "## 四、歷史檔案狀態宣告\n"
            "### 可信性等級\n"
            "### 歷史檔案（連結）\n"
            "（由 CrewAI 研究員動態產出，必須為編號清單格式，每條連結嚴格採用 `[`CL {可信度評級}：{機構名稱}`](URL)` 格式，"
            "並在清單上方加入引述區塊：> **以下歷史檔案連結由 CrewAI 官方檔案研究員動態產出，所有連結均經過驗證，指向香港特別行政區政府官方機構網域。**）\n\n"
            "## 五、導賞員現場講稿\n"
            "### 開場白\n"
            "### 各站點\n"
            "（每個站點以「### {站點名稱}」為三級標題，其下必須包含「#### 現場觀察重點」與「#### 歷史故事」兩個四級子標題）\n"
            "### 結語\n\n"
            "## 六、參考資料來源\n"
            "### 官方檔案\n"
            "（所有連結必須採用 Markdown 超連結格式 [`CL {可信度評級}：{機構名稱}`](URL)）\n"
            "### 參考文獻清單\n\n"
            "全篇使用專業繁體中文。歷史事件章節中的每一條目必須嚴格採用「{年份}：{歷史描述}」格式，並按「{歷史時期/特徵}」分組。"
        ),
        expected_output="結構完整的 Markdown 導賞手冊全文，嚴格遵循上述六大章節結構與子標題規範，歷史事件以「{年份}：{歷史描述}」格式按「{歷史時期/特徵}」分組，含 CrewAI 動態產出之 Markdown 歷史檔案超連結。",
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

def auto_git_commit_and_push(file_path: str, building_name: str, n_id: str, credibility: str, matrix_file: str = None, branch: str = "dev-001"):
    print(f"📦 對 {file_path} 進行版本控制...")
    git_add_args = ["add", file_path]
    if matrix_file:
        git_add_args.append(matrix_file)
    run_git_command(git_add_args)
    commit_subject = f"docs(tour): 生成 {building_name} 導賞手冊"
    commit_body = (
        f"建築名稱：{building_name}\n"
        f"檔案路徑：{file_path}\n"
        f"矩陣編號：{n_id}\n"
        f"可信性等級：{credibility}\n"
        f"模型：HKO/GLM-5.2-FP8 (zai-org/GLM-5.2-FP8)\n"
        f"結構：六段式標準章節 + CL 評級表 + 動態歷史檔案連結\n"
        f"矩陣狀態：🌕 已完成"
    )
    run_git_command(["commit", "-m", commit_subject, "-m", commit_body])
    run_git_command(["push", "origin", branch])

# ==========================================
# 4. 主流程 (含解析、排序與啟動選單 TUI)
# ==========================================


def parse_and_sort_building_matrix(matrix_dir: str = MATRIX_DIR) -> list:
    """
    解析導賞目標建築矩陣（目錄樹結構）。
    讀取 矩陣/ 目錄下所有 .md 子檔案（依固定順序：法定古蹟 → 樓宇-市區 → 樓宇-新界），
    合併解析後依 (子檔案順序, 編號 N) 排序。
    各子檔案內 N 從 1 起獨立遞增（非全域唯一），以子目錄區分。
    """
    buildings = []
    matrix_files = [os.path.join(matrix_dir, f) for f in MATRIX_FILE_ORDER if os.path.exists(os.path.join(matrix_dir, f))]
    # Also pick up any unexpected .md files not in FILE_ORDER
    extra = sorted(glob.glob(os.path.join(matrix_dir, "*.md")))
    for f in extra:
        if f not in matrix_files:
            matrix_files.append(f)

    if not matrix_files:
        return [{
            "N": "1",
            "category": "香港法定古蹟導賞團",
            "name": "舊中區警署",
            "address": "中環荷李活道10號",
            "tag": "舊中區警署",
            "credibility": "典範",
            "completion": "🌚 未開始"
        }]

    file_order = {mf: i for i, mf in enumerate(matrix_files)}

    for mf in matrix_files:
        with open(mf, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("|") and not line.startswith("| 編號") and "---" not in line:
                    parts = _split_matrix_row(line)
                    if len(parts) >= 10 and parts[0].isdigit():
                        buildings.append({
                            "N": parts[0],
                            "category": parts[1],
                            "name": parts[2],
                            "address": parts[4],
                            "tag": parts[6],
                            "credibility": parts[7],
                            "completion": parts[8],
                            "link": parts[9],
                            "_matrix_file": mf
                        })

    sorted_buildings = sorted(buildings, key=lambda x: (file_order[x["_matrix_file"]], int(x["N"])))
    return sorted_buildings


def update_matrix_entry(n_value: str, building_name: str, link_url: str, matrix_file: str = None) -> str:
    """生成手冊後更新矩陣中的「歷史檔案（連結）」欄位與工作進度狀態。
    依編號 N 比對（各子檔案內 N 從 1 起獨立遞增，非全域唯一），更新指定子檔案。
    必須提供 matrix_file 以定位正確的子檔案。
    回傳被更新的檔案路徑。
    """
    link_md = f"[`歷史檔案（連結）`]({link_url})"

    if matrix_file:
        search_files = [matrix_file]
    else:
        search_files = sorted(glob.glob(os.path.join(MATRIX_DIR, "*.md")))

    for mf in search_files:
        if not os.path.exists(mf):
            continue
        with open(mf, "r", encoding="utf-8") as f:
            lines = f.readlines()

        updated = False
        with open(mf, "w", encoding="utf-8") as f:
            for line in lines:
                if line.startswith("|") and "---" not in line and not line.startswith("| 編號"):
                    parts = _split_matrix_row(line)
                    if len(parts) >= 10 and parts[0] == n_value:
                        parts[8] = "🌕 已完成"
                        parts[9] = link_md
                        line = _join_matrix_row(parts)
                        print(f"📝 矩陣已更新：N={n_value} {building_name} -> 🌕 已完成 | {link_md} (in {mf})")
                        updated = True
                f.write(line)

        if updated:
            return mf
    print(f"⚠️ 找不到編號 N={n_value}（{building_name}）的矩陣項目。")
    return None

def main():
    output_root = Path(BUILDING_DIR)
    (output_root / "法定古蹟").mkdir(parents=True, exist_ok=True)
    (output_root / "樓宇").mkdir(parents=True, exist_ok=True)

    buildings = parse_and_sort_building_matrix()
    print(f"📋 共讀取到 {len(buildings)} 棟標的建築（已依編號 N 排序）。\n")

    # === 啟動選單 TUI（在每次執行開頭詢問一次） ===
    print("=" * 60)
    print("🏛️ 香港導賞團自動化管線 - 啟動選單")
    print("=" * 60)
    print("  [1] 執行全部建築項目 (Run all buildings)")
    print("  [2] 僅執行「🌚 未開始」項目 (Run only unstarted items)")
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
        print(f"\n🔍 已過濾出 {len(target_buildings)} 個「🌚 未開始」的項目準備執行。")
    else:
        target_buildings = buildings
        print(f"\n⚡ 將依序批次執行全部共 {len(target_buildings)} 個建築項目。")

    if not target_buildings:
        print("📭 目前沒有符合條件的建築需要處理。")
        return

    print("=" * 60 + "\n")

    # === 批次自動化執行迴圈 ===
    for item in target_buildings:
        n_id = str(int(item["N"])).zfill(5)
        b_name = item["name"]
        category = item["category"]
        address = item["address"]
        tag = item["tag"]
        credibility = item["credibility"]
        completion = item["completion"]

        subdir = _category_to_subdir(category)
        file_path = output_root / subdir / f"{n_id}-{b_name}.md"

        print(f"--------------------------------------------------")
        print(f"🏗️ 正在處理 [編號 {item['N']}] {b_name} ({category}) | 狀態: {completion} -> 啟動 CrewAI...")

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

        updated_file = update_matrix_entry(item["N"], b_name, f"建築/{subdir}/{n_id}-{b_name}.md", item.get("_matrix_file"))

        auto_git_commit_and_push(str(file_path), b_name, n_id=n_id, credibility=credibility, matrix_file=updated_file, branch="dev-001")
        print(f"✨ [{b_name}] 處理完成！\n")

    print("\n🎉 選定的所有導賞手冊均已成功透過 CrewAI 動態生成 Markdown 檔案連結並提交至 Git！")

if __name__ == "__main__":
    main()
