import streamlit as st
import base64, os
from PIL import Image

# Determine base dir and logo path
base_dir = os.path.dirname(os.path.abspath(__file__))
logo_file_path = os.path.join(base_dir, "assets", "mynalanda_logo.png")

# Page configuration
page_icon_obj = Image.open(logo_file_path) if os.path.exists(logo_file_path) else "🎓"
st.set_page_config(
    page_title="myNalanda - Analytics Dashboard",
    page_icon=page_icon_obj,
    layout="wide",
    initial_sidebar_state="expanded"
)

from database import init_db
from utils.styles import apply_custom_css
from views.login import render_login_page
from views.signup import render_signup_page
from views.forgot_password import render_forgot_password_page
from views.dashboard import render_dashboard_tab
from views.teacher import render_teacher_tab
from views.late_attrition import render_late_attrition_tab

# Load logo as base64 for inline embedding (works everywhere without a web server)
def _get_logo_b64():
    if os.path.exists(logo_file_path):
        with open(logo_file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

_LOGO_B64 = _get_logo_b64()
_LOGO_SRC = f"data:image/png;base64,{_LOGO_B64}" if _LOGO_B64 else ""

# Store logo URL in session state so login, signup, forgot_password can use it
st.session_state["logo_url"] = _LOGO_SRC

# Initialize DB & Styles
init_db()
apply_custom_css()

# Session state initialization
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None
if "auth_flow" not in st.session_state:
    st.session_state["auth_flow"] = "Login"
if "current_tab" not in st.session_state:
    st.session_state["current_tab"] = "Dashboard"

# ─────────────────────────────────────────────────────────────────────────────
# AUTHENTICATION FLOW
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state["authenticated"]:
    if st.session_state["auth_flow"] == "Login":
        render_login_page()
    elif st.session_state["auth_flow"] == "Signup":
        render_signup_page()
    elif st.session_state["auth_flow"] == "ForgotPassword":
        render_forgot_password_page()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP (Authenticated - All Pages Visible to All Users)
# ─────────────────────────────────────────────────────────────────────────────
else:
    user = st.session_state["user"]
    username = user.get("username", "User") if isinstance(user, dict) else "User"

    # ── Top Header Bar ────────────────────────────────────────────────────────
    _icon_html = (
        f'<img src="{_LOGO_SRC}" style="height:48px; width:48px; object-fit:cover; border-radius:8px; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">'
        if _LOGO_SRC else
        '<div style="font-size:38px;line-height:1;">🎓</div>'
    )
    st.markdown(f"""
        <div class="mynalanda-header">
            <div class="mynalanda-brand">
                {_icon_html}
                <div>
                    <div class="mynalanda-title">myNalanda</div>
                    <div class="mynalanda-subtitle">Skills Analytics &amp; Academic Intelligence Platform</div>
                </div>
            </div>
            <div class="mynalanda-info">
                <div class="mynalanda-info-item">
                    <span class="mynalanda-info-label">Logged in as</span>
                    <span class="mynalanda-info-val" style="color: #00e5ff;">
                        {username}
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        _sidebar_icon = (
            f'<img src="{_LOGO_SRC}" style="height:36px; width:36px; object-fit:cover; border-radius:6px;">'
            if _LOGO_SRC else
            '<div style="font-size:28px;line-height:1;">🎓</div>'
        )
        st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: center;
                        gap: 10px; padding: 12px 0 4px 0;">
                {_sidebar_icon}
                <h2 style="color: #00e5ff; margin: 0; font-weight: 800;
                           font-size: 24px; white-space: nowrap;">myNalanda</h2>
            </div>
            <div style="text-align: center; color: #90caf9; font-size: 11px; margin-bottom: 12px;">
                School Analytics Portal
            </div>
            <hr style="border-color: #162c48; margin-top: 0px; margin-bottom: 15px;">
        """, unsafe_allow_html=True)

        nav_options = ["Dashboard", "Teacher", "Late Count & Attrition"]

        if st.session_state["current_tab"] not in nav_options:
            st.session_state["current_tab"] = nav_options[0]

        selected_nav = st.radio(
            "Navigation",
            nav_options,
            index=nav_options.index(st.session_state["current_tab"]),
            key="nav_radio"
        )
        st.session_state["current_tab"] = selected_nav

        st.markdown("<hr style='border-color: #162c48; margin: 20px 0 15px 0;'>",
                    unsafe_allow_html=True)

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.session_state["auth_flow"] = "Login"
            st.session_state["current_tab"] = "Dashboard"
            st.rerun()

        st.markdown("""
            <div style="margin-top: 30px; font-size: 11px; color: #546e7a; text-align: center;">
                © myNalanda Solutions &amp; Services Pvt. Ltd.<br>2026
            </div>
        """, unsafe_allow_html=True)

    # ── Render Selected Page ──────────────────────────────────────────────────
    tab = st.session_state["current_tab"]

    if tab == "Dashboard":
        render_dashboard_tab()
    elif tab == "Teacher":
        render_teacher_tab()
    elif tab == "Late Count & Attrition":
        render_late_attrition_tab()
