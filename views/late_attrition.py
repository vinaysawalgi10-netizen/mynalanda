import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from database import (
    get_all_teacher_names,
    fetch_late_arrival_trend,
    fetch_attrition_table,
    fetch_attrition_risk_summary,
    fetch_top_attrition_reasons
)

def render_late_attrition_tab():
    # ── 1. Top Section Slicer ─────────────────────────────────────────────────
    s_col1, s_col2 = st.columns([1.2, 3])
    with s_col1:
        selected_section = st.selectbox(
            "⚡ Filter by Section",
            ["All Sections", "Sec1", "Sec2", "Sec3"],
            help="Dynamically filter all risk metrics, charts, and attrition records by section."
        )

    # ── 2. Attrition Overview KPI Cards (Dynamically Filtered) ────────────────
    df_risk = fetch_attrition_risk_summary(selected_section)
    risk_counts = dict(zip(df_risk['RiskLevel'], df_risk['Count']))

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value" style="color: #ff1744;">{risk_counts.get('High Risk', 0)}</div>
                <div class="kpi-label">High Risk (Score ≥ 3.0)</div>
            </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value" style="color: #ffb300;">{risk_counts.get('Medium Risk', 0)}</div>
                <div class="kpi-label">Medium Risk (Score = 2.0)</div>
            </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value" style="color: #00b0ff;">{risk_counts.get('Low Risk', 0)}</div>
                <div class="kpi-label">Low Risk (Score = 1.0)</div>
            </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value" style="color: #00e676;">{risk_counts.get('No Risk', 0)}</div>
                <div class="kpi-label">No Risk (Score = 0.0)</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 3. Visualizations Row: Donut Chart & Risk Reasons Bar Chart ───────────
    v1, v2 = st.columns(2)

    with v1:
        st.markdown(f'<div class="dark-card-header">🍩 Attrition Risk Distribution ({selected_section})</div>', unsafe_allow_html=True)
        fig_donut = px.pie(
            df_risk,
            names='RiskLevel',
            values='Count',
            hole=0.55,
            color='RiskLevel',
            color_discrete_map={
                'High Risk': '#ff1744',
                'Medium Risk': '#ffb300',
                'Low Risk': '#00b0ff',
                'No Risk': '#00e676'
            }
        )
        fig_donut.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate="<b>Risk Category:</b> %{label}<br><b>Faculty Count:</b> %{value}<br><b>Percentage:</b> %{percent}<extra></extra>"
        )
        fig_donut.update_layout(
            paper_bgcolor='#0a1826',
            plot_bgcolor='#0a1826',
            height=270,
            margin=dict(l=10, r=10, t=20, b=20),
            legend=dict(font=dict(color='#90caf9', size=11), title=None, orientation="h", y=-0.1)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with v2:
        st.markdown(f'<div class="dark-card-header">📊 Primary Risk Drivers & Reasons ({selected_section})</div>', unsafe_allow_html=True)
        df_reasons = fetch_top_attrition_reasons(5, selected_section)
        fig_reasons = px.bar(
            df_reasons,
            y='Reason',
            x='Count',
            orientation='h',
            color='Count',
            color_continuous_scale="Reds"
        )
        fig_reasons.update_traces(
            hovertemplate="<b>Reason:</b> %{y}<br><b>Affected Teachers:</b> %{x}<extra></extra>"
        )
        fig_reasons.update_layout(
            paper_bgcolor='#0a1826',
            plot_bgcolor='#0a1826',
            height=270,
            margin=dict(l=10, r=10, t=20, b=20),
            xaxis=dict(gridcolor='#162e4a', tickfont=dict(color='#90caf9'), title="Count of Teachers"),
            yaxis=dict(tickfont=dict(color='#90caf9', size=11), autorange="reversed", title=None),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_reasons, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 4. Monthly Late Arrival Trend Section (Full Width Above) ──────────────
    st.markdown('<div class="dark-card-header">📈 Late Arrival Trend (Jan – Dec Monthly Spline Chart)</div>', unsafe_allow_html=True)

    teacher_list = ["All Teachers"] + get_all_teacher_names(selected_section)
    sel_teacher = st.selectbox("Select Teacher to View Individual Late Trend", teacher_list, index=0)

    t_param = None if sel_teacher == "All Teachers" else sel_teacher
    df_late = fetch_late_arrival_trend(t_param)

    x_vals = [str(m) for m in df_late['month']]
    y_vals = [float(v) for v in pd.to_numeric(df_late['late_count'], errors='coerce').fillna(0)]

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='lines+markers',
        line=dict(color='#00e5ff', width=3, shape='spline'),
        fill='tozeroy',
        fillcolor='rgba(0, 229, 255, 0.10)',
        marker=dict(size=8, color='#00b0ff', line=dict(color='#ffffff', width=1.5)),
        name="Late Count",
        hovertemplate="<b>Month:</b> %{x}<br><b>Late Count:</b> %{y:.1f} instances<extra></extra>"
    ))

    fig_trend.update_layout(
        paper_bgcolor='#0a1826',
        plot_bgcolor='#0a1826',
        height=300,
        margin=dict(l=20, r=20, t=20, b=40),
        xaxis=dict(showgrid=True, gridcolor='#162e4a', tickfont=dict(color='#90caf9', size=11), title="Month (Calendar Year 2026)"),
        yaxis=dict(showgrid=True, gridcolor='#162e4a', tickfont=dict(color='#90caf9'), title="Late Count Instances", dtick=1),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 5. Filtered Attrition Summary Table Section (Full Width Below) ────────
    st.markdown(f'<div class="dark-card-header">📋 Attrition Summary & Filtered Data Table ({selected_section})</div>', unsafe_allow_html=True)

    c_filt, c_space = st.columns([1.2, 2])
    with c_filt:
        attrition_filter = st.selectbox(
            "Attrition Risk Level Filter",
            ["All", "High Risk (>2.0)", "Medium Risk (1.0 - 2.0)", "Low Risk (0.0 - 1.0)", "No Risk (0.0)"]
        )

    df_attr = fetch_attrition_table(attrition_filter, selected_section)

    st.dataframe(
        df_attr[['Teacher Name', 'Section', 'Attr. Score', 'Attrition Explanation']],
        use_container_width=True,
        height=340,
        column_config={
            "Teacher Name": st.column_config.TextColumn("Teacher Name", width="medium"),
            "Section": st.column_config.TextColumn("Section", width="small"),
            "Attr. Score": st.column_config.NumberColumn("Attr. Score", format="%.2f", width="small"),
            "Attrition Explanation": st.column_config.TextColumn("Attrition Explanation", width="large")
        }
    )
