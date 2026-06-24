"""
app.py — 主入口 / 仪表板（浅色主题）
"""
import streamlit as st
from datetime import datetime, timedelta
import plotly.graph_objects as go

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import database as db

# ── 页面配置 ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="个人笔记系统",
    page_icon="📓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 初始化数据库 ──────────────────────────────────────────────────
db.init_db()

# ── 全局样式（浅色主题） ──────────────────────────────────────────
st.markdown("""
<style>
/* ===== 侧边栏 ===== */
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

/* ===== 主内容区 ===== */
.stApp {
    background-color: #f5f6fa;
}
.stMainBlockContainer {
    color: #1e293b;
}

/* ===== 统计卡片 ===== */
.stat-card {
    background: #ffffff;
    border: 1px solid #dde1f0;
    border-radius: 14px;
    padding: 22px 18px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(79,142,247,.08);
}
.stat-icon   { font-size: 1.7rem; }
.stat-number {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.2;
}
.stat-label  { color: #64748b; font-size: .88rem; margin-top: 5px; font-weight: 500; }

/* ===== 事件卡片 ===== */
.event-row {
    background: #ffffff;
    border-left: 4px solid #2563eb;
    border-radius: 8px;
    padding: 11px 15px;
    margin-bottom: 9px;
    box-shadow: 0 1px 6px rgba(0,0,0,.06);
}
.event-title { font-weight: 700; font-size: 1rem; color: #1e293b; }
.event-meta  { color: #64748b; font-size: .83rem; margin-top: 3px; }

/* ===== 笔记预览卡片 ===== */
.note-preview {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 9px;
    box-shadow: 0 1px 5px rgba(0,0,0,.05);
}
.note-title   { font-weight: 700; font-size: .97rem; color: #1e293b; margin-bottom: 4px; }
.note-snippet { color: #64748b; font-size: .85rem; }
.note-tag {
    display: inline-block; background: #eff6ff; color: #2563eb;
    border-radius: 5px; padding: 1px 9px; font-size: .76rem;
    margin: 2px 3px 0 0; font-weight: 500;
}

/* ===== 标题 ===== */
h1, h2, h3 { color: #1e293b !important; }

/* ===== 隐藏 Streamlit 默认装饰 ===== */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── 侧边栏 ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 📓 我的笔记本")
    st.markdown("---")

    today_str_display = datetime.now().strftime("%Y年%m月%d日")
    weekday_map = ["周一","周二","周三","周四","周五","周六","周日"]
    weekday = weekday_map[datetime.now().weekday()]
    st.markdown(f"**{today_str_display}  {weekday}**")
    st.markdown("")

    st.page_link("app.py",                   label="🏠 仪表板"  )
    st.page_link("pages/1_📅_日程安排.py",   label="📅 日程安排")
    st.page_link("pages/2_📝_随笔笔记.py",   label="📝 随笔笔记")
    st.page_link("pages/3_🚀_项目管理.py",   label="🚀 项目管理")

    st.markdown("---")
    st.caption("v1.1  ·  SQLite 本地存储")

# ── 主内容 ────────────────────────────────────────────────────────
st.title("🏠 今日概览")

stats = db.get_stats()
today = datetime.now().strftime("%Y-%m-%d")
today_events = db.get_events_by_date(today)
recent_notes = db.get_notes()[:5]

# ── 统计卡片行 ────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

def stat_card(col, number, label, icon):
    with col:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-icon">{icon}</div>
            <div class="stat-number">{number}</div>
            <div class="stat-label">{label}</div>
        </div>""", unsafe_allow_html=True)

stat_card(c1, stats["today_events"],    "今日日程",   "📅")
stat_card(c2, stats["total_notes"],     "笔记总数",   "📝")
stat_card(c3, stats["active_projects"], "进行中项目", "🚀")
stat_card(c4, stats["todo_tasks"],      "待完成任务", "✅")

st.markdown("<br>", unsafe_allow_html=True)

# ── 下方两列 ──────────────────────────────────────────────────────
left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("📅 今日日程")
    if today_events:
        for ev in today_events:
            time_str = f"{ev['start_time']}–{ev['end_time']}" if ev['start_time'] else "全天"
            loc_str  = f"&nbsp; 📍 {ev['location']}" if ev['location'] else ""
            st.markdown(f"""
            <div class="event-row" style="border-left-color:{ev['color']}">
                <div class="event-title">{ev['title']}</div>
                <div class="event-meta">🕐 {time_str}{loc_str}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("今天没有日程安排，去 📅 日程安排 页面添加吧！")

    # 任务进度饼图
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📊 任务状态分布")
    todo_n, doing_n, done_n = stats["todo_tasks"], stats["doing_tasks"], stats["done_tasks"]
    total = todo_n + doing_n + done_n
    if total > 0:
        fig = go.Figure(go.Pie(
            labels=["待办", "进行中", "已完成"],
            values=[todo_n, doing_n, done_n],
            hole=.55,
            marker_colors=["#ef4444", "#f59e0b", "#22c55e"],
            textinfo="label+percent",
            textfont_size=13,
        ))
        fig.update_layout(
            paper_bgcolor="rgba(255,255,255,0)",
            plot_bgcolor ="rgba(255,255,255,0)",
            margin=dict(t=10, b=10, l=10, r=10),
            font_color="#334155",
            showlegend=True,
            legend=dict(font=dict(color="#334155")),
            height=260,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("还没有任务，去 🚀 项目管理 创建吧！")

with right:
    st.subheader("📝 最近笔记")
    if recent_notes:
        for note in recent_notes:
            snippet = (note["content"] or "")[:80].replace("\n", " ")
            tags_html = ""
            if note["tags"]:
                for t in note["tags"].split(","):
                    t = t.strip()
                    if t:
                        tags_html += f'<span class="note-tag">#{t}</span>'
            pin = "📌 " if note["pinned"] else ""
            st.markdown(f"""
            <div class="note-preview">
                <div class="note-title">{pin}{note['title']}</div>
                <div class="note-snippet">{snippet or '（无内容）'}</div>
                <div style="margin-top:7px">{tags_html}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("还没有笔记，去 📝 随笔笔记 页面创建吧！")

    # 未来 7 天日程预告
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🗓️ 未来 7 天")
    week_events_exist = False
    for i in range(1, 8):
        d = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        evs = db.get_events_by_date(d)
        if evs:
            week_events_exist = True
            d_label = (datetime.now() + timedelta(days=i)).strftime("%m/%d %a")
            st.markdown(f"**{d_label}**")
            for ev in evs:
                t = ev['start_time'] or "全天"
                st.markdown(f"- `{t}` {ev['title']}")
    if not week_events_exist:
        st.info("未来 7 天暂无日程")
