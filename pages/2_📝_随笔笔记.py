"""
随笔笔记页面 — Markdown 编辑 + 标签 + 搜索
"""
import streamlit as st
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import database as db
import style
import auth

st.set_page_config(page_title="随笔笔记", page_icon="📝", layout="wide", initial_sidebar_state="expanded")
auth.require_login()
db.init_db()

style.apply_global_style()
style.inject_sidebar_toggle_fallback()

# ── 侧边栏 ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 📓 我的笔记本")
    st.markdown("---")
    st.page_link("app.py",                   label="🏠 仪表板"  )
    st.page_link("pages/1_📅_日程安排.py",   label="📅 日程安排")
    st.page_link("pages/2_📝_随笔笔记.py",   label="📝 随笔笔记")
    st.page_link("pages/3_🚀_项目管理.py",   label="🚀 项目管理")
    auth.show_logout()
    st.markdown("---")

    # 标签筛选
    all_tags = db.get_all_tags()
    st.markdown("**🏷 标签筛选**")
    if all_tags:
        selected_tag = st.radio("选择标签", ["全部"] + all_tags, label_visibility="collapsed")
        filter_tag = "" if selected_tag == "全部" else selected_tag
    else:
        filter_tag = ""
        st.caption("暂无标签")

# ── state ─────────────────────────────────────────────────────────
if "active_note_id" not in st.session_state: st.session_state.active_note_id = None
if "note_mode"      not in st.session_state: st.session_state.note_mode      = "list"   # list | edit | view

# ── 刷新帮助函数 ─────────────────────────────────────────────────
def open_note(nid):
    st.session_state.active_note_id = nid
    st.session_state.note_mode      = "view"

def new_note():
    st.session_state.active_note_id = None
    st.session_state.note_mode      = "edit"

style.sidebar_menu_hint()
st.title("📝 随笔笔记")

# ── 搜索栏 ────────────────────────────────────────────────────────
search_col, btn_col = st.columns([5, 1])
with search_col:
    search_q = st.text_input("🔍 搜索笔记", placeholder="标题或内容关键词", label_visibility="collapsed")
with btn_col:
    if st.button("✏️ 新建笔记", type="primary", use_container_width=True):
        new_note()

notes = db.get_notes(search=search_q, tag=filter_tag)

# ══════════════════ 列表 ＋ 详情/编辑 ═════════════════════════════
list_col, detail_col = st.columns([2, 3], gap="large")

# ── 笔记列表 ─────────────────────────────────────────────────────
with list_col:
    st.markdown(f"共 **{len(notes)}** 条笔记")
    if not notes:
        st.info("没有找到符合条件的笔记。")
    for note in notes:
        snippet  = (note["content"] or "").replace("\n", " ")[:60]
        tag_html = "".join(
            f'<span class="tag-chip">#{t.strip()}</span>'
            for t in note["tags"].split(",") if t.strip()
        )
        pin_icon = "📌 " if note["pinned"] else ""
        is_active = note["id"] == st.session_state.active_note_id
        border_extra = "border-color:#4f8ef7;" if is_active else ""
        st.markdown(f"""
        <div class="note-card {'pinned' if note['pinned'] else ''}" style="{border_extra}">
            <div class="nc-title">{pin_icon}{note['title']}</div>
            <div class="nc-snippet">{snippet or '（无内容）'}</div>
            <div>{tag_html}</div>
            <div class="nc-meta">{note['updated_at'][:16]}</div>
        </div>""", unsafe_allow_html=True)

        bcol1, bcol2, bcol3 = st.columns([2, 1, 1])
        with bcol1:
            if st.button("📖 查看", key=f"view_{note['id']}", use_container_width=True):
                open_note(note["id"])
                st.rerun()
        with bcol2:
            if st.button("✏️", key=f"edit_{note['id']}", use_container_width=True):
                st.session_state.active_note_id = note["id"]
                st.session_state.note_mode      = "edit"
                st.rerun()
        with bcol3:
            if st.button("🗑", key=f"del_{note['id']}", use_container_width=True):
                db.delete_note(note["id"])
                if st.session_state.active_note_id == note["id"]:
                    st.session_state.active_note_id = None
                    st.session_state.note_mode = "list"
                st.rerun()

# ── 详情 / 编辑区 ────────────────────────────────────────────────
with detail_col:
    mode = st.session_state.note_mode
    nid  = st.session_state.active_note_id

    if mode == "list":
        st.markdown("""
        <div style='text-align:center;padding:60px 20px;color:#4b5563'>
            <div style='font-size:3rem'>📝</div>
            <div style='margin-top:12px;font-size:1rem'>从左侧选择一条笔记查看，或点击「新建笔记」</div>
        </div>""", unsafe_allow_html=True)

    elif mode == "view" and nid:
        note = db.get_note(nid)
        if note:
            c1v, c2v = st.columns([4, 1])
            with c1v:
                st.subheader(("📌 " if note["pinned"] else "") + note["title"])
            with c2v:
                if st.button("✏️ 编辑", use_container_width=True):
                    st.session_state.note_mode = "edit"
                    st.rerun()

            # 标签
            if note["tags"]:
                tags_html = "".join(
                    f'<span class="tag-chip">#{t.strip()}</span>'
                    for t in note["tags"].split(",") if t.strip()
                )
                st.markdown(tags_html, unsafe_allow_html=True)

            st.caption(f"创建: {note['created_at'][:16]}  ·  更新: {note['updated_at'][:16]}")
            st.markdown("---")
            # Markdown 渲染
            st.markdown(note["content"] or "*（空笔记）*")

    elif mode == "edit":
        existing = db.get_note(nid) if nid else None

        st.subheader("新建笔记" if not existing else "编辑笔记")

        with st.form("note_form", clear_on_submit=False):
            title   = st.text_input("标题 *", value=existing["title"] if existing else "")
            content = st.text_area(
                "内容（支持 Markdown）",
                value=existing["content"] if existing else "",
                height=380,
            )
            tags_val = existing["tags"] if existing else ""
            tags    = st.text_input("标签（逗号分隔）", value=tags_val, placeholder="学习, 工作, 想法")
            pinned  = st.checkbox("📌 置顶", value=bool(existing["pinned"]) if existing else False)

            sc1, sc2 = st.columns(2)
            save_btn = sc1.form_submit_button("💾 保存", use_container_width=True, type="primary")
            cancel_btn = sc2.form_submit_button("✕ 取消", use_container_width=True)

            if save_btn:
                if not title.strip():
                    st.error("标题不能为空")
                else:
                    clean_tags = ",".join(t.strip() for t in tags.split(",") if t.strip())
                    if existing:
                        db.update_note(nid, title=title, content=content, tags=clean_tags, pinned=int(pinned))
                        st.success("已保存")
                    else:
                        new_id = db.add_note(title, content, clean_tags, int(pinned))
                        st.session_state.active_note_id = new_id
                    st.session_state.note_mode = "view"
                    st.rerun()

            if cancel_btn:
                st.session_state.note_mode = "view" if nid else "list"
                st.rerun()
