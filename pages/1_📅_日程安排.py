"""
日程安排页面（浅色主题）
"""
import streamlit as st
from datetime import datetime, date, timedelta
import calendar
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import database as db

st.set_page_config(page_title="日程安排", page_icon="📅", layout="wide", initial_sidebar_state="expanded")
db.init_db()

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

/* ===== 日历网格 ===== */
.cal-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 5px;
}
.cal-header {
    text-align: center;
    font-weight: 700;
    color: #64748b;
    padding: 6px 0;
    font-size: .82rem;
    letter-spacing: .04em;
}
.cal-day {
    min-height: 68px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 6px 8px;
    cursor: pointer;
    transition: border-color .15s, box-shadow .15s;
}
.cal-day:hover { border-color: #2563eb; box-shadow: 0 2px 8px rgba(37,99,235,.12); }
.cal-day.today {
    border-color: #2563eb;
    background: #eff6ff;
    box-shadow: 0 0 0 2px rgba(37,99,235,.2);
}
.cal-day.other  { opacity: .4; }
.cal-day.selected { border-color: #7c3aed; background: #f5f3ff; }
.day-num {
    font-weight: 700;
    font-size: .9rem;
    color: #1e293b;
}
.cal-day.today .day-num { color: #2563eb; }
.day-dot {
    width: 7px; height: 7px; border-radius: 50%;
    display: inline-block; margin: 1px 2px;
}

/* ===== 事件卡片 ===== */
.ev-card {
    background: #ffffff;
    border-left: 4px solid #2563eb;
    border-radius: 8px;
    padding: 11px 15px;
    margin-bottom: 9px;
    box-shadow: 0 1px 6px rgba(0,0,0,.06);
}
.ev-title { font-weight: 700; font-size: .97rem; color: #1e293b; }
.ev-meta  { color: #64748b; font-size: .82rem; margin-top: 4px; }
.ev-note  { color: #475569; font-size: .82rem; margin-top: 4px; background: #f8fafc; border-radius: 4px; padding: 4px 8px; }

/* ===== 通用 ===== */
h1, h2, h3 { color: #1e293b !important; }
p, li  { color: #334155; }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {visibility: hidden;}

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

# ── session state ─────────────────────────────────────────────────
if "cal_year"  not in st.session_state: st.session_state.cal_year  = datetime.now().year
if "cal_month" not in st.session_state: st.session_state.cal_month = datetime.now().month
if "sel_date"  not in st.session_state: st.session_state.sel_date  = datetime.now().strftime("%Y-%m-%d")
if "show_add"  not in st.session_state: st.session_state.show_add  = False
if "edit_ev"   not in st.session_state: st.session_state.edit_ev   = None

st.title("📅 日程安排")

col_cal, col_detail = st.columns([3, 2], gap="large")

# ══════════════════ 日历列 ═══════════════════════════════════════
with col_cal:
    # 月份导航栏
    nav1, nav2, nav3 = st.columns([1, 4, 1])
    with nav1:
        if st.button("◀", key="prev_month"):
            m = st.session_state.cal_month - 1
            if m < 1:
                m = 12
                st.session_state.cal_year -= 1
            st.session_state.cal_month = m
    with nav2:
        st.markdown(
            f"<h3 style='text-align:center;margin:0;color:#1e293b'>"
            f"{st.session_state.cal_year}年 {st.session_state.cal_month}月</h3>",
            unsafe_allow_html=True,
        )
    with nav3:
        if st.button("▶", key="next_month"):
            m = st.session_state.cal_month + 1
            if m > 12:
                m = 1
                st.session_state.cal_year += 1
            st.session_state.cal_month = m

    # 本月事件
    month_str = f"{st.session_state.cal_year:04d}-{st.session_state.cal_month:02d}"
    events_this_month = db.get_events(month_str)
    events_by_date: dict = {}
    for ev in events_this_month:
        events_by_date.setdefault(ev["date"], []).append(ev)

    today_str = datetime.now().strftime("%Y-%m-%d")

    # 绘制日历
    cal_obj = calendar.Calendar(firstweekday=0)
    days_in_month = list(cal_obj.itermonthdates(st.session_state.cal_year, st.session_state.cal_month))

    WEEKDAYS = ["一","二","三","四","五","六","日"]
    header_html = "".join(f'<div class="cal-header">{d}</div>' for d in WEEKDAYS)

    cells_html = ""
    for d in days_in_month:
        d_str    = d.strftime("%Y-%m-%d")
        is_cur   = d.month == st.session_state.cal_month
        is_today = d_str == today_str
        is_sel   = d_str == st.session_state.sel_date
        cls = "cal-day"
        if not is_cur:  cls += " other"
        if is_today:    cls += " today"
        if is_sel:      cls += " selected"
        dot_html = ""
        if d_str in events_by_date:
            for ev in events_by_date[d_str][:4]:
                dot_html += f'<span class="day-dot" style="background:{ev["color"]}"></span>'
        cells_html += f"""
        <div class="{cls}">
            <div class="day-num">{d.day}</div>
            <div style="margin-top:3px">{dot_html}</div>
        </div>"""

    st.markdown(f'<div class="cal-grid">{header_html}{cells_html}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # 交互日期选择器
    sel = st.date_input(
        "📌 选择查看日期",
        value=datetime.strptime(st.session_state.sel_date, "%Y-%m-%d").date(),
        key="date_picker",
    )
    if sel:
        st.session_state.sel_date  = sel.strftime("%Y-%m-%d")
        st.session_state.cal_year  = sel.year
        st.session_state.cal_month = sel.month

    # 月度日程汇总
    st.markdown("---")
    month_label = f"{st.session_state.cal_month}月 所有日程"
    st.markdown(f"#### {month_label}")
    if events_this_month:
        for ev in events_this_month:
            d_label  = datetime.strptime(ev["date"], "%Y-%m-%d").strftime("%m/%d")
            time_str = ev["start_time"] or "全天"
            dot = f'<span style="display:inline-block;width:9px;height:9px;border-radius:50%;background:{ev["color"]};margin-right:5px;vertical-align:middle"></span>'
            st.markdown(
                f'{dot}<b>{d_label}</b> &nbsp;{time_str}&nbsp; {ev["title"]}',
                unsafe_allow_html=True,
            )
    else:
        st.caption("本月暂无日程")

# ══════════════════ 详情 & 新增列 ════════════════════════════════
with col_detail:
    sel_str   = st.session_state.sel_date
    sel_label = datetime.strptime(sel_str, "%Y-%m-%d").strftime("%Y年%m月%d日 %A")
    # 将英文星期替换为中文
    en_to_zh  = {"Monday":"周一","Tuesday":"周二","Wednesday":"周三",
                  "Thursday":"周四","Friday":"周五","Saturday":"周六","Sunday":"周日"}
    for en, zh in en_to_zh.items():
        sel_label = sel_label.replace(en, zh)

    st.subheader(f"🗓️ {sel_label}")

    # 新增按钮
    btn_label = "✕ 收起表单" if st.session_state.show_add else "➕ 新增日程"
    if st.button(btn_label, type="primary", use_container_width=True):
        st.session_state.show_add = not st.session_state.show_add
        st.session_state.edit_ev  = None

    # 新增表单
    if st.session_state.show_add:
        with st.form("add_event_form", clear_on_submit=True):
            st.markdown("##### ✏️ 填写日程信息")
            title    = st.text_input("标题 *", placeholder="如：部门例会")
            ev_date  = st.date_input("日期", value=datetime.strptime(sel_str, "%Y-%m-%d").date())
            c1f, c2f = st.columns(2)
            st_time  = c1f.text_input("开始时间", placeholder="09:00")
            en_time  = c2f.text_input("结束时间", placeholder="10:00")
            location = st.text_input("地点", placeholder="会议室/线上")
            note     = st.text_area("备注", height=72)
            color    = st.color_picker("颜色标签", value="#2563eb")
            s1, s2   = st.columns(2)
            submitted = s1.form_submit_button("💾 保存日程", use_container_width=True)
            cancel    = s2.form_submit_button("✕ 取消",     use_container_width=True)
            if submitted:
                if not title.strip():
                    st.error("⚠️ 标题不能为空")
                else:
                    db.add_event(title.strip(), ev_date.strftime("%Y-%m-%d"),
                                 st_time, en_time, location, note, color)
                    st.success("✅ 日程已保存！")
                    st.session_state.show_add = False
                    st.rerun()
            if cancel:
                st.session_state.show_add = False
                st.rerun()

    # 当日事件
    day_events = db.get_events_by_date(sel_str)
    st.markdown("<br>", unsafe_allow_html=True)

    if day_events:
        st.markdown(f"**当日共 {len(day_events)} 个日程**")
        for ev in day_events:
            time_str = f"{ev['start_time']} – {ev['end_time']}" if ev['start_time'] else "全天"
            loc_html = f"&nbsp; 📍 {ev['location']}" if ev['location'] else ""
            note_html= f"<div class='ev-note'>📄 {ev['note']}</div>" if ev['note'] else ""
            st.markdown(f"""
            <div class="ev-card" style="border-left-color:{ev['color']}">
                <div class="ev-title">{ev['title']}</div>
                <div class="ev-meta">🕐 {time_str}{loc_html}</div>
                {note_html}
            </div>""", unsafe_allow_html=True)
            if st.button(f"🗑 删除「{ev['title']}」", key=f"del_ev_{ev['id']}"):
                db.delete_event(ev["id"])
                st.rerun()
            st.markdown("")
    else:
        st.info("📭 这天没有日程，点击上方「新增日程」添加。")
