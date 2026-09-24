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
