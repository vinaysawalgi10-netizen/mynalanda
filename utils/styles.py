import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* Main Theme Dark Overrides */
        .stApp {
            background-color: #0c1827;
            color: #e0f2fe;
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }

        /* Top Navigation Header Bar */
        .mynalanda-header {
            background: linear-gradient(90deg, #0b1d33 0%, #152c48 100%);
            padding: 18px 28px;
            border-bottom: 3px solid #00b0ff;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            gap: 20px;
        }

        .mynalanda-brand {
            display: flex;
            align-items: center;
            gap: 16px;
            flex-shrink: 0;
        }

        .mynalanda-title {
            font-size: 32px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: 0.5px;
            margin: 0;
            padding: 0;
            white-space: nowrap !important;
            word-break: keep-all !important;
            background: linear-gradient(90deg, #ffffff 0%, #00e5ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .mynalanda-subtitle {
            font-size: 12px;
            color: #90caf9;
            margin-top: 2px;
            white-space: nowrap;
        }

        .mynalanda-info {
            display: flex;
            align-items: center;
            gap: 24px;
            font-size: 13px;
            color: #90caf9;
            flex-wrap: nowrap;
        }

        .mynalanda-info-item {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .mynalanda-info-label {
            font-size: 11px;
            color: #78909c;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .mynalanda-info-val {
            font-size: 13px;
            font-weight: 600;
            color: #ffffff;
            white-space: nowrap;
        }

        /* Metric / KPI Cards */
        .kpi-card {
            background: radial-gradient(circle at center, #10263f 0%, #0c1c2e 100%);
            border: 1px solid #1e3a5f;
            border-radius: 12px;
            padding: 18px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
            margin-bottom: 15px;
        }
        .kpi-value {
            font-size: 38px;
            font-weight: 800;
            color: #00e5ff;
            margin: 5px 0;
            text-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
        }
        .kpi-label {
            font-size: 13px;
            font-weight: 600;
            color: #90caf9;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }

        /* Dark Card Container */
        .dark-card {
            background: #0f2238;
            border: 1px solid #1a365d;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }

        .dark-card-header {
            font-size: 16px;
            font-weight: 700;
            color: #00b0ff;
            border-bottom: 1px solid #1a3a60;
            padding-bottom: 8px;
            margin-bottom: 12px;
        }

        /* Star rating badge */
        .star-rating {
            color: #ffd700;
            font-size: 18px;
            letter-spacing: 2px;
        }

        /* Progress indicator bar */
        .progress-bar-container {
            background-color: #1a365d;
            border-radius: 6px;
            height: 10px;
            width: 100%;
            overflow: hidden;
            margin-top: 6px;
        }
        .progress-bar-fill-teal {
            background: linear-gradient(90deg, #00b0ff, #00e5ff);
            height: 100%;
        }
        .progress-bar-fill-yellow {
            background: linear-gradient(90deg, #ffb300, #ffd54f);
            height: 100%;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #09131f !important;
            border-right: 1px solid #152c48;
        }

        /* Table Styling Overrides */
        div[data-testid="stDataFrame"] {
            background-color: #0d1f33;
            border-radius: 8px;
            border: 1px solid #1a3a60;
        }
        </style>
    """, unsafe_allow_html=True)
