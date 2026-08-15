import streamlit as st
from auth import register_user

def render_signup_page():
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
                        Create New Account
                    </h2>
                </div>
                <p style="color: #90caf9; font-size: 13px; margin: 0;">Join myNalanda Solutions</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("signup_form"):
            username = st.text_input("Choose Username", placeholder="e.g. john_doe").strip()
            email = st.text_input("Email Address", placeholder="e.g. john@mynalanda.com").strip()
            password = st.text_input("Password", type="password", placeholder="Choose password").strip()
            confirm_pass = st.text_input("Confirm Password", type="password", placeholder="Re-enter password").strip()

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Register Account", use_container_width=True)

            if submitted:
                if not username or not email or not password:
                    st.error("Please fill in all required fields!")
                elif password != confirm_pass:
                    st.error("Passwords do not match!")
                else:
                    success, msg, new_user = register_user(username, email, password, "User")
                    if success:
                        st.success("Account registered successfully! You can now log in.")
                    else:
                        st.error(msg)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("← Back to Login", use_container_width=True):
            st.session_state["auth_flow"] = "Login"
            st.rerun()
