import streamlit as st
from auth import reset_password

def render_forgot_password_page():
    logo_src = st.session_state.get("logo_url", "")
    icon_html = f'<img src="{logo_src}" style="height: 48px; width: 48px; object-fit: cover; border-radius: 8px; vertical-align: middle;">' if logo_src else '<div style="font-size: 38px; line-height: 1;">🎓</div>'

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    c_left, c_center, c_right = st.columns([1, 1.8, 1])

    with c_center:
        st.markdown(f"""
            <div style="background: #0d1e30; border: 1px solid #1c3d64; border-radius: 16px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin-bottom: 20px; text-align: center;">
                <div style="display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 6px;">
                    {icon_html}
                    <h2 style="color: #ffffff; font-size: 32px; font-weight: 800; margin: 0; background: linear-gradient(90deg, #ffffff, #00e5ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                        Reset Password
                    </h2>
                </div>
                <p style="color: #90caf9; font-size: 13px; margin: 0;">myNalanda Account Recovery</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("forgot_form"):
            username = st.text_input("Registered Username", placeholder="Enter your username").strip()
            new_pass = st.text_input("New Password", type="password", placeholder="Enter new password").strip()
            confirm_pass = st.text_input("Confirm New Password", type="password", placeholder="Re-enter new password").strip()

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            reset_submitted = st.form_submit_button("Reset Password", use_container_width=True)

            if reset_submitted:
                if not username or not new_pass:
                    st.error("Please provide your username and new password!")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match!")
                else:
                    success, msg = reset_password(username, new_pass)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("← Back to Login", use_container_width=True):
            st.session_state["auth_flow"] = "Login"
            st.rerun()
