"""
数据导出页面
支持：
1. Markdown 周报/月报（可直接上传 IMA 知识库）
2. JSON 全量备份
3. CSV 日程/任务表格
"""
import streamlit as st
import json
import csv
import io
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import database as db

st.set_page_config(page_title="数据导出", page_icon="📤", layout="wide", initial_sidebar_state="expanded")
db.init_db()

st.markdown("""
<style>
section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #1e2a4a 0%, #2d3a6b 100%);
}
section[data-testid="stSidebar"] * {
    color: #e0e7ff !important;
}
section[data-testid="stSidebar"] a {
    color: #a5c8ff !important;
}
section[data-testid="stSidebar"] hr {
    border-color: #4a5888 !important;
}
section[data-testid="stSidebar"] button {
    color: #1e293b !important;
}
.stApp { background-color: #f5f6fa; }
.stMainBlockContainer { color: #1e293b; }
h1,h2,h3 { color: #1e293b !important; }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {visibility: hidden;}

.export-card {
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 20px 22px; margin-bottom: 14px;
    box-shadow: 0 1px 6px rgba(0,0,0,.06);
}
.export-card h4 { color: #1e293b; margin: 0 0 8px 0; font-size: 1rem; }
.export-card p  { color: #64748b; font-size: .86rem; margin: 0 0 12px 0; }

.ima-tip {
    background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px;
    padding: 14px 18px; margin-bottom: 16px;
}
.ima-tip p { color: #1d4ed8; font-size: .88rem; margin: 0; }
</style>
""", unsafe_allow_html=True)

# ── 侧边栏 ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 📓 我的笔记本")
    st.markdown("---")
    st.page_link("app.py",                   label="🏠 仪表板"  )
    st.page_link("pages/1_📅_日程安排.py",   label="📅 日程安排")
    st.page_link("pages/2_📝_随笔笔记.py",   label="📝 随笔笔记")
    st.page_link("pages/3_🚀_项目管理.py",   label="🚀 项目管理")
    st.page_link("pages/4_📤_数据导出.py",   label="📤 数据导出")

st.title("📤 数据导出 & IMA 同步")

# IMA 提示
st.markdown("""
<div class="ima-tip">
<p>💡 <b>如何同步到 IMA 知识库</b>：下载 Markdown 周报 → 打开 WorkBuddy 左侧「IMA 知识库」连接器 → 上传文件到对应知识库，即可用于后续报表和 AI 总结自动化。</p>
</div>
""", unsafe_allow_html=True)

# ──────────────── 时间范围选择 ────────────────────────────────────
st.subheader("⚙️ 选择导出范围")
range_col, _ = st.columns([2, 3])
with range_col:
    export_type = st.radio(
        "时间范围",
        ["本周", "上周", "本月", "上月", "自定义"],
        horizontal=True,
    )

today = datetime.now()
if export_type == "本周":
    start = today - timedelta(days=today.weekday())
    end   = start + timedelta(days=6)
elif export_type == "上周":
    start = today - timedelta(days=today.weekday() + 7)
    end   = start + timedelta(days=6)
elif export_type == "本月":
    start = today.replace(day=1)
    end   = today
elif export_type == "上月":
    first = today.replace(day=1)
    end   = first - timedelta(days=1)
    start = end.replace(day=1)
else:
    dc1, dc2 = st.columns(2)
    start = dc1.date_input("开始日期", value=today.replace(day=1))
    end   = dc2.date_input("结束日期", value=today)
    start = datetime.combine(start, datetime.min.time())
    end   = datetime.combine(end,   datetime.min.time())

start_str = start.strftime("%Y-%m-%d")
end_str   = end.strftime("%Y-%m-%d")
st.caption(f"导出范围：**{start_str}** 至 **{end_str}**")

# ── 拉数据 ────────────────────────────────────────────────────────
all_events  = db.get_events()
all_notes   = db.get_notes()
all_projects= db.get_projects("active") + db.get_projects("archived")

range_events = [e for e in all_events if start_str <= e["date"] <= end_str]

st.markdown("---")
left_col, right_col = st.columns(2, gap="large")

# ══════════════ Markdown 周报/月报 ═══════════════════════════════
with left_col:
    st.markdown('<div class="export-card"><h4>📄 Markdown 报告（推荐上传 IMA）</h4>'
                '<p>生成结构化 Markdown，包含日程汇总、笔记摘要、项目进度，可直接上传 IMA 知识库供 AI 检索分析。</p></div>',
                unsafe_allow_html=True)

    def build_markdown_report(start_str, end_str, events, notes, projects):
        lines = []
        lines.append(f"# 📓 个人笔记系统报告")
        lines.append(f"\n**报告时段**：{start_str} ～ {end_str}  \n**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}")

        # 日程汇总
        lines.append("\n---\n## 📅 日程安排")
        if events:
            lines.append(f"\n本期共 **{len(events)}** 个日程：\n")
            cur_date = ""
            for ev in sorted(events, key=lambda x: x["date"]):
                if ev["date"] != cur_date:
                    cur_date = ev["date"]
                    lines.append(f"\n### {cur_date}")
                t = f"{ev['start_time']}–{ev['end_time']}" if ev["start_time"] else "全天"
                loc = f"  📍 {ev['location']}" if ev["location"] else ""
                note= f"\n  > {ev['note']}" if ev["note"] else ""
                lines.append(f"- **{ev['title']}** ({t}){loc}{note}")
        else:
            lines.append("\n本期无日程记录。")

        # 笔记摘要（取最近10条）
        lines.append("\n---\n## 📝 笔记摘要（最近 10 条）")
        recent = sorted(notes, key=lambda x: x["updated_at"], reverse=True)[:10]
        if recent:
            for n in recent:
                tags = " ".join(f"`#{t.strip()}`" for t in n["tags"].split(",") if t.strip()) if n["tags"] else ""
                snippet = (n["content"] or "").replace("\n", " ")[:120]
                lines.append(f"\n### {'📌 ' if n['pinned'] else ''}{n['title']}  {tags}")
                lines.append(f"\n{snippet}{'...' if len(n['content'] or '') > 120 else ''}")
                lines.append(f"\n*更新于 {n['updated_at'][:16]}*")
        else:
            lines.append("\n暂无笔记。")

        # 项目进度
        lines.append("\n---\n## 🚀 项目进度")
        if projects:
            for proj in projects:
                tasks = db.get_tasks(proj["id"])
                total = len(tasks)
                done  = sum(1 for t in tasks if t["status"] == "done")
                doing = sum(1 for t in tasks if t["status"] == "doing")
                todo  = total - done - doing
                pct   = int(done / total * 100) if total else 0
                bar   = "█" * (pct // 10) + "░" * (10 - pct // 10)
                lines.append(f"\n### {proj['name']}")
                if proj["description"]:
                    lines.append(f"\n{proj['description']}")
                lines.append(f"\n进度：`{bar}` {pct}%  （待办 {todo} / 进行中 {doing} / 完成 {done}）")
                if proj["deadline"]:
                    lines.append(f"\n⏰ 截止：{proj['deadline']}")
                if tasks:
                    lines.append("\n**任务清单：**")
                    for t in tasks:
                        icon = {"todo": "⬜", "doing": "🔄", "done": "✅"}.get(t["status"], "⬜")
                        lines.append(f"- {icon} {t['title']}")
        else:
            lines.append("\n暂无项目。")

        lines.append("\n---\n*由「个人笔记系统」自动生成*")
        return "\n".join(lines)

    md_content = build_markdown_report(start_str, end_str, range_events, all_notes, all_projects)

    # 预览
    with st.expander("👁️ 预览报告内容", expanded=False):
        st.markdown(md_content)

    filename_md = f"笔记报告_{start_str}_{end_str}.md"
    st.download_button(
        label="⬇️ 下载 Markdown 报告",
        data=md_content.encode("utf-8"),
        file_name=filename_md,
        mime="text/markdown",
        use_container_width=True,
        type="primary",
    )

    # ── JSON 全量备份 ──────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="export-card"><h4>🗂️ JSON 全量备份</h4>'
                '<p>导出所有数据的 JSON 格式，可用于程序自动处理、导入其他工具，或结构化写入 IMA。</p></div>',
                unsafe_allow_html=True)

    def build_json_backup():
        all_tasks_map = {}
        for proj in all_projects:
            all_tasks_map[proj["id"]] = db.get_tasks(proj["id"])
        data = {
            "export_time": datetime.now().isoformat(),
            "events":   all_events,
            "notes":    all_notes,
            "projects": [
                {**proj, "tasks": all_tasks_map.get(proj["id"], [])}
                for proj in all_projects
            ],
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    json_content = build_json_backup()
    filename_json = f"笔记备份_{today.strftime('%Y%m%d')}.json"
    st.download_button(
        label="⬇️ 下载 JSON 备份",
        data=json_content.encode("utf-8"),
        file_name=filename_json,
        mime="application/json",
        use_container_width=True,
    )


# ══════════════ CSV 导出 ════════════════════════════════════════
with right_col:
    st.markdown('<div class="export-card"><h4>📊 CSV 日程表</h4>'
                '<p>导出筛选时间段内的日程数据为 CSV，适合导入 Excel / 钉钉日历 / 自动化报表工具。</p></div>',
                unsafe_allow_html=True)

    def build_csv_events(events):
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["date","title","start_time","end_time","location","note"])
        writer.writeheader()
        for ev in events:
            writer.writerow({
                "date":       ev["date"],
                "title":      ev["title"],
                "start_time": ev["start_time"] or "",
                "end_time":   ev["end_time"] or "",
                "location":   ev["location"] or "",
                "note":       ev["note"] or "",
            })
        return buf.getvalue()

    csv_events = build_csv_events(range_events)
    st.download_button(
        label=f"⬇️ 下载日程 CSV（{len(range_events)} 条）",
        data=csv_events.encode("utf-8-sig"),  # utf-8-sig 让 Excel 正确显示中文
        file_name=f"日程_{start_str}_{end_str}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # ── CSV 任务导出 ────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="export-card"><h4>📋 CSV 任务列表</h4>'
                '<p>导出所有项目的任务清单为 CSV，包含项目名、状态、优先级、截止日期。</p></div>',
                unsafe_allow_html=True)

    def build_csv_tasks():
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["project","title","status","priority","due_date","description"])
        writer.writeheader()
        for proj in all_projects:
            for t in db.get_tasks(proj["id"]):
                writer.writerow({
                    "project":     proj["name"],
                    "title":       t["title"],
                    "status":      {"todo":"待办","doing":"进行中","done":"已完成"}.get(t["status"], t["status"]),
                    "priority":    {"high":"高","medium":"中","low":"低"}.get(t["priority"], t["priority"]),
                    "due_date":    t["due_date"] or "",
                    "description": t["description"] or "",
                })
        return buf.getvalue()

    csv_tasks = build_csv_tasks()
    st.download_button(
        label="⬇️ 下载任务 CSV",
        data=csv_tasks.encode("utf-8-sig"),
        file_name=f"任务列表_{today.strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # ── 自动化脚本提示 ──────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🤖 自动化集成方案")

    with st.expander("查看 IMA 自动上传脚本（Python）", expanded=False):
        st.code("""
# ima_sync.py — 每日自动将报告上传到 IMA 知识库
# 需要先在 WorkBuddy 中开启 IMA 连接器并获取 API Token

import requests, json
from datetime import datetime, timedelta

IMA_API = "https://ima.qq.com/api/v1/document/upload"
IMA_TOKEN = "YOUR_IMA_TOKEN"  # 替换为你的 Token
KB_ID = "YOUR_KB_ID"          # 替换为你的知识库 ID

def upload_to_ima(file_path: str, doc_title: str):
    with open(file_path, "rb") as f:
        resp = requests.post(
            IMA_API,
            headers={"Authorization": f"Bearer {IMA_TOKEN}"},
            data={"kb_id": KB_ID, "title": doc_title},
            files={"file": f},
        )
    return resp.json()

if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    # 先用 note_app 生成报告，再上传
    result = upload_to_ima(f"笔记报告_{today}.md", f"笔记系统日报 {today}")
    print(result)
""", language="python")

    with st.expander("查看定时任务配置（Windows 任务计划）", expanded=False):
        st.code("""
# 每天早上 8 点自动生成并上传报告
# 在 PowerShell 以管理员身份运行：

$action  = New-ScheduledTaskAction -Execute "python" `
           -Argument "C:/path/to/ima_sync.py"
$trigger = New-ScheduledTaskTrigger -Daily -At "08:00"
Register-ScheduledTask -TaskName "IMA_笔记同步" `
    -Action $action -Trigger $trigger -RunLevel Highest
""", language="powershell")
