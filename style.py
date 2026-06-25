"""style.py — 全局样式注入

所有页面统一导入本模块，确保侧边栏、折叠按钮、主题等样式一致。
"""
import streamlit as st
import streamlit.components.v1 as components

GLOBAL_CSS = """
<style>
/* ===== 隐藏 Streamlit 默认装饰（保留 header，否则展开按钮会被一起隐藏） ===== */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] a,
header[data-testid="stHeader"] img,
header[data-testid="stHeader"] .st-emotion-cache-15ecox0,
header[data-testid="stHeader"] .st-emotion-cache-zq5wmm {
    display: none !important;
}

/* ===== 主内容区（浅色主题） ===== */
.stApp {
    background-color: #f5f6fa;
}
.stMainBlockContainer {
    color: #1e293b;
}
h1, h2, h3 { color: #1e293b !important; }
p, li { color: #334155; }

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
section[data-testid="stSidebar"] button[kind="header"] {
    background: rgba(255,255,255,.15) !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] button[kind="secondary"] {
    color: #1e293b !important;
}

/* ===== 侧边栏折叠按钮始终可见且醒目 ===== */
/* 折叠按钮容器：只要 sidebar 处于收起状态，就强制显示 */
section[data-testid="stSidebarUserContent"],
div[data-testid="stSidebarCollapsedControl"],
button[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    opacity: 1 !important;
    visibility: visible !important;
}

button[data-testid="stSidebarCollapsedControl"],
div[data-testid="stSidebarCollapsedControl"] {
    background: #2563eb !important;
    color: #ffffff !important;
    border-radius: 0 10px 10px 0 !important;
    padding: 10px 8px 10px 12px !important;
    box-shadow: 2px 2px 8px rgba(37,99,235,.35) !important;
    top: 12px !important;
    left: 0 !important;
    position: fixed !important;
    z-index: 999999 !important;
    transition: transform .15s ease, background .15s ease !important;
    width: 40px !important;
    height: 40px !important;
    align-items: center !important;
    justify-content: center !important;
}
button[data-testid="stSidebarCollapsedControl"]:hover,
div[data-testid="stSidebarCollapsedControl"]:hover {
    transform: scale(1.05) !important;
    background: #1d4ed8 !important;
}
button[data-testid="stSidebarCollapsedControl"] svg,
div[data-testid="stSidebarCollapsedControl"] svg,
button[data-testid="stSidebarCollapsedControl"] path,
div[data-testid="stSidebarCollapsedControl"] path,
button[data-testid="stSidebarCollapsedControl"] *,
div[data-testid="stSidebarCollapsedControl"] * {
    fill: #ffffff !important;
    color: #ffffff !important;
    stroke: #ffffff !important;
    width: 22px !important;
    height: 22px !important;
}

/* 兜底：当 sidebar 被收起时，左侧保留一条可点击的蓝色热区 */
.stApp:has(section[data-testid="stSidebar"][aria-expanded="false"])::before {
    content: "";
    position: fixed;
    left: 0; top: 0; bottom: 0;
    width: 6px;
    background: #2563eb;
    z-index: 9999;
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

/* ===== 通用事件/笔记卡片 ===== */
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

/* ===== 1_日程安排：日历样式 ===== */
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

/* ===== 2_随笔笔记：笔记列表样式 ===== */
.note-card {
    background:#ffffff; border:1px solid #e2e8f0;
    border-radius:10px; padding:14px 16px; margin-bottom:10px;
    cursor:pointer; transition:border-color .2s;
    box-shadow: 0 1px 5px rgba(0,0,0,.05);
}
.note-card:hover { border-color:#2563eb; }
.note-card.pinned { border-left:4px solid #f59e0b; }
.nc-title  { font-weight:700; font-size:1rem; color:#1e293b; }
.nc-snippet{ color:#64748b; font-size:.85rem; margin:4px 0; }
.nc-meta   { color:#94a3b8; font-size:.78rem; }
.tag-chip  {
    display:inline-block; background:#eff6ff; border-radius:5px;
    padding:2px 9px; margin:2px 3px; font-size:.78rem; color:#2563eb; font-weight:500;
}

/* ===== 3_项目管理：看板样式 ===== */
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

/* ===== 4_数据导出：导出卡片样式 ===== */
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
"""


def apply_global_style():
    """注入全局 CSS，确保所有页面样式一致。"""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def sidebar_menu_hint():
    """当侧边栏收起时，在页面顶部显示展开提示。"""
    st.markdown(
        """
        <div style="margin: -1rem 0 1rem 0; padding: .5rem .9rem; background: #eff6ff; border-left: 4px solid #2563eb; border-radius: 8px; color: #1e40af; font-size: .9rem;">
            ☰ 左上角蓝色按钮可展开菜单
        </div>
        """,
        unsafe_allow_html=True,
    )


_TOGGLE_BUTTON_JS = """
<script>
(function() {
    if (window.__sidebarToggleInstalled) return;
    window.__sidebarToggleInstalled = true;

    var btn = document.createElement('button');
    btn.id = 'custom-sidebar-toggle';
    btn.innerHTML = '☰';
    btn.setAttribute('aria-label', '展开菜单');
    btn.style.cssText = 'position:fixed; top:12px; left:0; z-index:999999; width:42px; height:42px; background:#2563eb; color:#fff; border:none; border-radius:0 10px 10px 0; font-size:22px; line-height:42px; text-align:center; box-shadow:2px 2px 8px rgba(37,99,235,.35); cursor:pointer; display:none; align-items:center; justify-content:center; padding:0;';

    btn.onclick = function() {
        var realBtn = document.querySelector('[data-testid="stSidebarCollapsedControl"]');
        if (realBtn) {
            realBtn.click();
        } else {
            var evt = new KeyboardEvent('keydown', {
                key: '[', code: 'BracketLeft', keyCode: 219, which: 219, bubbles: true
            });
            document.dispatchEvent(evt);
        }
    };

    function updateVisibility() {
        var sidebar = document.querySelector('section[data-testid="stSidebar"]');
        var expanded = false;
        if (sidebar) {
            expanded = sidebar.getAttribute('aria-expanded') !== 'false';
        }
        btn.style.display = expanded ? 'none' : 'flex';
        btn.setAttribute('aria-label', expanded ? '菜单已展开' : '展开菜单');
    }

    updateVisibility();
    setInterval(updateVisibility, 400);

    document.body.appendChild(btn);
})();
</script>
"""


def inject_sidebar_toggle_fallback():
    """注入一个始终可见的 JS 兜底按钮，防止 Streamlit 折叠按钮被隐藏。"""
    components.html(_TOGGLE_BUTTON_JS, height=0, scrolling=False)
