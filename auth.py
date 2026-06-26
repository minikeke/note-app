"""
auth.py — 简单密码登录保护
- 密码从 st.secrets["app_password"] 或环境变量 APP_PASSWORD 读取
- 未设置密码时跳过登录（本地模式不受影响）
- 登录状态存储在 st.session_state["authenticated"]
"""
import streamlit as st
import os


def _get_password():
    """从 secrets 或环境变量获取密码，未设置返回 None。"""
    # 1. Streamlit secrets（云端）
    try:
        pwd = st.secrets.get("app_password", "")
        if pwd:
            return pwd
    except Exception:
        pass
    # 2. 环境变量（本地）
    return os.environ.get("APP_PASSWORD", "") or None


def _init_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False


def _login_page(password):
    """渲染登录页面，验证通过后设置状态。"""
    # 居中卡片样式
    st.markdown("""
    <style>
    .login-wrapper {
        max-width: 380px;
        margin: 80px auto 0;
        padding: 40px 36px;
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.08);
        text-align: center;
    }
    .login-icon { font-size: 3rem; margin-bottom: 8px; }
    .login-title { font-size: 1.3rem; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
    .login-sub { font-size: 0.85rem; color: #64748b; margin-bottom: 24px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-wrapper">
        <div class="login-icon">📓</div>
        <div class="login-title">个人笔记系统</div>
        <div class="login-sub">请输入密码以继续</div>
    </div>
    """, unsafe_allow_html=True)

    # 用空列做居中
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        pwd_input = st.text_input("密码", type="password", label_visibility="collapsed",
                                  placeholder="请输入密码")
        if st.button("🔓 登录", type="primary", use_container_width=True):
            if pwd_input == password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("密码错误")


def require_login():
    """在每个页面开头调用。未登录时显示登录表单并阻止后续渲染。"""
    _init_state()
    password = _get_password()

    # 未配置密码 → 跳过登录（本地开发模式）
    if not password:
        return

    # 已登录 → 正常渲染
    if st.session_state.authenticated:
        return

    # 未登录 → 显示登录页，阻止后续内容
    _login_page(password)
    st.stop()


def show_logout():
    """在侧边栏底部显示退出按钮，仅当密码已配置且已登录时显示。"""
    password = _get_password()
    if not password or not st.session_state.get("authenticated", False):
        return
    st.markdown("---")
    if st.button("🚪 退出登录", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
