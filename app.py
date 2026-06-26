"""
app.py — 主入口 / 仪表板（浅色主题）
"""
import streamlit as st
from datetime import datetime, timedelta
import plotly.graph_objects as go

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import database as db
import style
import auth

# ── 页面配置 ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="个人笔记系统",
    page_icon="📓",
    layout="wide",
    initial_sidebar_state="expanded",
)

auth.require_login()

# ── 初始化数据库 ──────────────────────────────────────────────────
db.init_db()

# ── 全局样式（浅色主题） ──────────────────────────────────────────
style.apply_global_style()
style.inject_sidebar_toggle_fallback()

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
    backend_label = "☁️ Supabase" if db._IS_PG else "💾 SQLite"
    st.caption(f"v1.2  ·  {backend_label}")
    auth.show_logout()

# ── 主内容 ────────────────────────────────────────────────────────
style.sidebar_menu_hint()
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
