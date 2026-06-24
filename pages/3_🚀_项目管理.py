"""
项目管理页面 — 看板式任务管理
"""
import streamlit as st
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import database as db

st.set_page_config(page_title="项目管理", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")
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

.proj-card {
    background:#ffffff; border:1px solid #e2e8f0; border-radius:12px;
    padding:16px; margin-bottom:10px; cursor:pointer; transition:border-color .2s;
    box-shadow: 0 1px 6px rgba(0,0,0,.06);
}
.proj-card:hover { border-color:#7c3aed; box-shadow: 0 3px 12px rgba(124,58,237,.1); }
.proj-card.active-proj { border-color:#7c3aed; background:#faf5ff; }
.proj-name { font-weight:700; font-size:1.05rem; color:#1e293b; }
.proj-desc { color:#64748b; font-size:.85rem; margin:4px 0; }
.proj-meta { color:#94a3b8; font-size:.78rem; }

.task-card {
    background:#ffffff; border:1px solid #e2e8f0; border-radius:8px;
    padding:10px 12px; margin-bottom:8px;
    box-shadow: 0 1px 4px rgba(0,0,0,.05);
}
.task-title { font-weight:600; font-size:.9rem; color:#1e293b; }
.task-desc  { color:#64748b; font-size:.82rem; margin-top:3px; }
.task-due   { color:#94a3b8; font-size:.78rem; margin-top:4px; }

.priority-high   { border-left:3px solid #ef4444; }
.priority-medium { border-left:3px solid #f59e0b; }
.priority-low    { border-left:3px solid #22c55e; }

.kanban-header {
    text-align:center; padding:9px; border-radius:8px;
    font-weight:700; font-size:.9rem; margin-bottom:10px;
}
.progress-bar {
    background:#e2e8f0; border-radius:4px; height:7px; overflow:hidden; margin-top:6px;
}
.progress-fill {
    background:linear-gradient(90deg,#2563eb,#7c3aed); height:100%;
    border-radius:4px; transition:width .4s;
}
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

# ── state ─────────────────────────────────────────────────────────
if "active_proj_id"  not in st.session_state: st.session_state.active_proj_id  = None
if "show_new_proj"   not in st.session_state: st.session_state.show_new_proj   = False
if "show_new_task"   not in st.session_state: st.session_state.show_new_task   = False

st.title("🚀 项目管理")

proj_col, kanban_col = st.columns([1, 3], gap="large")

# ══════════════════ 项目列表 ══════════════════════════════════════
with proj_col:
    st.subheader("📁 项目")

    if st.button("➕ 新建项目", type="primary", use_container_width=True):
        st.session_state.show_new_proj = not st.session_state.show_new_proj

    if st.session_state.show_new_proj:
        with st.form("new_proj_form", clear_on_submit=True):
            pname = st.text_input("项目名称 *")
            pdesc = st.text_area("项目描述", height=70)
            pcol  = st.color_picker("颜色", "#7c5cfc")
            pdead = st.date_input("截止日期（可选）", value=None)
            psub  = st.form_submit_button("创建", use_container_width=True)
            if psub:
                if not pname.strip():
                    st.error("项目名称不能为空")
                else:
                    dead_str = pdead.strftime("%Y-%m-%d") if pdead else ""
                    pid = db.add_project(pname.strip(), pdesc.strip(), pcol, dead_str)
                    st.session_state.active_proj_id = pid
                    st.session_state.show_new_proj  = False
                    st.success("项目已创建！")
                    st.rerun()

    projects = db.get_projects("active")
    archived = db.get_projects("archived")

    if not projects and not archived:
        st.info("还没有项目，点上方按钮创建吧！")
    else:
        for proj in projects:
            tasks = db.get_tasks(proj["id"])
            total = len(tasks)
            done  = sum(1 for t in tasks if t["status"] == "done")
            pct   = int(done / total * 100) if total else 0
            is_active = proj["id"] == st.session_state.active_proj_id
            border_extra = "border-color:#7c5cfc;" if is_active else ""
            st.markdown(f"""
            <div class="proj-card {'active-proj' if is_active else ''}" style="{border_extra}">
                <span style="display:inline-block;width:10px;height:10px;border-radius:50%;
                    background:{proj['color']};margin-right:6px;vertical-align:middle"></span>
                <span class="proj-name">{proj['name']}</span>
                <div class="proj-desc">{proj['description'] or ''}</div>
                <div class="proj-meta">{total} 个任务  ·  完成 {pct}%</div>
                <div class="progress-bar"><div class="progress-fill" style="width:{pct}%"></div></div>
                {"<div class='proj-meta' style='margin-top:5px'>⏰ " + proj['deadline'] + "</div>" if proj['deadline'] else ""}
            </div>""", unsafe_allow_html=True)

            pc1, pc2, pc3 = st.columns([3, 1, 1])
            with pc1:
                if st.button("打开", key=f"open_{proj['id']}", use_container_width=True):
                    st.session_state.active_proj_id = proj["id"]
                    st.session_state.show_new_task  = False
                    st.rerun()
            with pc2:
                if st.button("归档", key=f"arc_{proj['id']}", use_container_width=True):
                    db.update_project(proj["id"], status="archived")
                    if st.session_state.active_proj_id == proj["id"]:
                        st.session_state.active_proj_id = None
                    st.rerun()
            with pc3:
                if st.button("🗑", key=f"dproj_{proj['id']}", use_container_width=True):
                    db.delete_project(proj["id"])
                    if st.session_state.active_proj_id == proj["id"]:
                        st.session_state.active_proj_id = None
                    st.rerun()

        if archived:
            with st.expander(f"归档项目 ({len(archived)})"):
                for proj in archived:
                    st.markdown(f"- {proj['name']}")
                    if st.button("恢复", key=f"restore_{proj['id']}"):
                        db.update_project(proj["id"], status="active")
                        st.rerun()

# ══════════════════ 看板 ══════════════════════════════════════════
with kanban_col:
    pid = st.session_state.active_proj_id
    if not pid:
        st.markdown("""
        <div style='text-align:center;padding:80px 20px;color:#64748b'>
            <div style='font-size:3.5rem'>🚀</div>
            <div style='font-size:1rem;margin-top:12px;font-weight:500'>从左侧选择一个项目查看看板</div>
        </div>""", unsafe_allow_html=True)
    else:
        proj = db.get_project(pid)
        if not proj:
            st.warning("项目不存在")
        else:
            # 项目标题
            st.subheader(proj["name"])
            if proj["description"]:
                st.caption(proj["description"])
            if proj["deadline"]:
                st.caption(f"⏰ 截止日期: {proj['deadline']}")

            # 新增任务
            if st.button("➕ 添加任务", type="primary"):
                st.session_state.show_new_task = not st.session_state.show_new_task

            if st.session_state.show_new_task:
                with st.form("new_task_form", clear_on_submit=True):
                    t_title = st.text_input("任务标题 *")
                    t_desc  = st.text_area("描述", height=70)
                    tc1, tc2 = st.columns(2)
                    t_pri   = tc1.selectbox("优先级", ["high","medium","low"],
                                            format_func=lambda x: {"high":"🔴 高","medium":"🟡 中","low":"🟢 低"}[x])
                    t_due   = tc2.date_input("截止日期（可选）", value=None)
                    t_sub   = st.form_submit_button("添加任务", use_container_width=True)
                    if t_sub:
                        if not t_title.strip():
                            st.error("任务标题不能为空")
                        else:
                            due_str = t_due.strftime("%Y-%m-%d") if t_due else ""
                            db.add_task(pid, t_title.strip(), t_desc.strip(), t_pri, due_str)
                            st.session_state.show_new_task = False
                            st.rerun()

            # 拉任务
            all_tasks = db.get_tasks(pid)
            todo_tasks  = [t for t in all_tasks if t["status"] == "todo"]
            doing_tasks = [t for t in all_tasks if t["status"] == "doing"]
            done_tasks  = [t for t in all_tasks if t["status"] == "done"]

            PRIORITY_LABEL = {"high":"🔴 高","medium":"🟡 中","low":"🟢 低"}

            def task_card(task, next_status, next_label, prev_status=None, prev_label=None):
                pri_cls = f"priority-{task['priority']}"
                st.markdown(f"""
                <div class="task-card {pri_cls}">
                    <div class="task-title">{task['title']}</div>
                    {"<div class='task-desc'>" + task['description'] + "</div>" if task['description'] else ""}
                    <div class="task-due">
                        {PRIORITY_LABEL.get(task['priority'], '')}
                        {"  ⏰ " + task['due_date'] if task['due_date'] else ""}
                    </div>
                </div>""", unsafe_allow_html=True)

                btn_cols = [st.columns(3)]
                cols = st.columns(3)
                with cols[0]:
                    if prev_status and st.button(f"◀ {prev_label}", key=f"prev_{task['id']}", use_container_width=True):
                        db.update_task(task["id"], status=prev_status)
                        st.rerun()
                with cols[1]:
                    if st.button(f"{next_label} ▶", key=f"next_{task['id']}", use_container_width=True):
                        db.update_task(task["id"], status=next_status)
                        st.rerun()
                with cols[2]:
                    if st.button("🗑", key=f"dtask_{task['id']}", use_container_width=True):
                        db.delete_task(task["id"])
                        st.rerun()

            # 三列看板
            kb_todo, kb_doing, kb_done = st.columns(3, gap="medium")

            with kb_todo:
                st.markdown(f'<div class="kanban-header" style="background:#fef2f2;color:#dc2626;border:1px solid #fecaca">📋 待办 ({len(todo_tasks)})</div>', unsafe_allow_html=True)
                if todo_tasks:
                    for t in todo_tasks:
                        task_card(t, next_status="doing", next_label="开始", prev_status=None, prev_label=None)
                else:
                    st.caption("暂无待办任务")

            with kb_doing:
                st.markdown(f'<div class="kanban-header" style="background:#fffbeb;color:#d97706;border:1px solid #fde68a">⚡ 进行中 ({len(doing_tasks)})</div>', unsafe_allow_html=True)
                if doing_tasks:
                    for t in doing_tasks:
                        task_card(t, next_status="done", next_label="完成", prev_status="todo", prev_label="退回")
                else:
                    st.caption("暂无进行中任务")

            with kb_done:
                st.markdown(f'<div class="kanban-header" style="background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0">✅ 已完成 ({len(done_tasks)})</div>', unsafe_allow_html=True)
                if done_tasks:
                    for t in done_tasks:
                        task_card(t, next_status="todo", next_label="重开", prev_status="doing", prev_label="进行中")
                else:
                    st.caption("暂无已完成任务")

            # 统计
            total = len(all_tasks)
            if total:
                done_n = len(done_tasks)
                pct = int(done_n / total * 100)
                st.markdown("---")
                st.markdown(f"**整体进度：{done_n}/{total} 任务完成（{pct}%）**")
                st.progress(pct / 100)
