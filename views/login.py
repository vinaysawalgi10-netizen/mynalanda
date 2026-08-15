import streamlit as st
from auth import authenticate_user, user_exists, register_user

def render_login_page():
    logo_src = st.session_state.get("logo_url", "")
    icon_html = f'<img src="{logo_src}" style="height: 52px; width: 52px; object-fit: cover; border-radius: 8px; vertical-align: middle;">' if logo_src else '<div style="font-size: 44px; line-height: 1;">🎓</div>'

    # Centered container layout with tight spacing and padding
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    c_left, c_center, c_right = st.columns([1, 1.8, 1])

    with c_center:
        # Header Branding
        st.markdown(f"""
            <div style="background: #0d1e30; border: 1px solid #1c3d64; border-radius: 16px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin-bottom: 20px;">
                <div style="display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 8px;">
                    {icon_html}
                    <h1 style="color: #ffffff; font-size: 40px; font-weight: 800; margin: 0; padding: 0; background: linear-gradient(90deg, #ffffff 0%, #00e5ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                        myNalanda
                    </h1>
                </div>
                <div style="text-align: center; color: #90caf9; font-size: 13px; font-weight: 500;">
                    Skills Analytics & Academic Intelligence Platform
                </div>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", value="", placeholder="Enter your username").strip()
            password = st.text_input("Password", type="password", value="", placeholder="Enter your password").strip()

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            submit_button = st.form_submit_button("Sign In", use_container_width=True)

            if submit_button:
                if not username or not password:
                    st.error("Please enter both a username and password!")
                else:
                    if user_exists(username):
                        user = authenticate_user(username, password)
                        if user:
                            st.session_state["authenticated"] = True
                            st.session_state["user"] = user
                            st.session_state["current_tab"] = "Dashboard"
                            st.success(f"Welcome back, {username}! Logging in...")
                            st.rerun()
                        else:
                            st.error("Username exists, but the password provided is incorrect!")
                    else:
                        default_email = f"{username.lower()}@mynalanda.com"
                        success, msg, new_user = register_user(username, default_email, password, "User")
                        if success and new_user:
                            st.session_state["authenticated"] = True
                            st.session_state["user"] = new_user
                            st.session_state["current_tab"] = "Dashboard"
                            st.success(f"Account created! Welcome {username}. Logging in...")
                            st.rerun()
                        else:
                            st.error(msg)

        # Quick action links
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Signup", use_container_width=True):
                st.session_state["auth_flow"] = "Signup"
                st.rerun()
        with c2:
            if st.button("Forgot Password?", use_container_width=True):
                st.session_state["auth_flow"] = "ForgotPassword"
                st.rerun()
