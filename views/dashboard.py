import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from database import (
    fetch_dashboard_kpis,
    fetch_performance_landscape,
    fetch_section_column_chart,
    fetch_top_teacher_rankings,
    fetch_conditionally_formatted_teachers
)

def create_semi_circular_gauge(title, value, min_val=0, max_val=100, range_1=40, range_2=70, suffix="%", benchmark_target=75.0):
    """
    Renders an interactive semi-circular gauge indicator with multi-tier color zones,
    threshold target line, and rich hover tooltips.
    """
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        delta = {'reference': benchmark_target, 'position': "bottom", 'font': {'size': 11, 'color': '#69f0ae' if value >= benchmark_target else '#ffb300'}},
        number = {'suffix': suffix, 'font': {'color': '#ffffff', 'size': 26, 'family': 'Segoe UI'}},
        title = {'text': f"<b>{title}</b>", 'font': {'color': '#90caf9', 'size': 13, 'family': 'Segoe UI'}},
        gauge = {
            'axis': {
                'range': [min_val, max_val],
                'tickwidth': 1,
                'tickcolor': "#455a64",
                'tickfont': {'color': '#90caf9', 'size': 10}
            },
            'bar': {'color': "#00e5ff", 'thickness': 0.28},
            'bgcolor': "#091726",
            'bordercolor': "#162f4d",
            'steps': [
                {'range': [min_val, range_1], 'color': 'rgba(255, 23, 68, 0.25)'},
                {'range': [range_1, range_2], 'color': 'rgba(255, 179, 0, 0.25)'},
                {'range': [range_2, max_val], 'color': 'rgba(0, 230, 118, 0.25)'}
            ],
            'threshold': {
                'line': {'color': "#ffffff", 'width': 3},
                'thickness': 0.8,
                'value': benchmark_target
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=190,
        margin=dict(l=15, r=15, t=35, b=10),
        hovermode="closest"
    )
    return fig

def render_dashboard_tab():
    # ── 1. Interactive Slicers & Dynamic Filters ──────────────────────────────
    f1, f2, f3 = st.columns([1.2, 1, 1])
    with f1:
        section_filter = st.selectbox(
            "⚡ Section / Department Slicer",
            ["All Sections", "Sec1", "Sec2", "Sec3"],
            help="Filter all KPIs, gauges, charts, and tables dynamically by school section."
        )
    with f2:
        top_n_rank = st.selectbox(
            "🏆 Top Rankings Count",
            [5, 10, 15, 20],
            index=1,
            help="Adjust how many top teachers to display in the ranking bar chart."
        )
    with f3:
        table_limit = st.selectbox(
            "📋 Table Records Limit",
            [15, 25, 50, 100],
            index=1,
            help="Select the number of rows to display in the conditionally formatted table."
        )

    kpis = fetch_dashboard_kpis(section_filter)
    overall_avg = round((kpis['avg_int_bm'] + kpis['avg_ext_bm'] + (kpis['avg_compliance'] * 10)) / 3.0, 1)

    # ── 2. KPI Cards (Total Score, Average Score, Counts) ───────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value" style="color: #00e5ff;">{kpis['total_teachers']}</div>
                <div class="kpi-label">Total Faculty ({section_filter})</div>
            </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value" style="color: #69f0ae;">{overall_avg}%</div>
                <div class="kpi-label">Overall Average Score</div>
            </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value" style="color: #ff3d00;">{kpis['attrition_risk']}</div>
                <div class="kpi-label">Attrition Risk Count</div>
            </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value" style="color: #ffd740;">{kpis['late_count_instances']}</div>
                <div class="kpi-label">Late Counts (Dec Peak)</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 3. Gauges & Progress Indicators (Interactive with Tooltips) ────────────
    st.markdown('<div class="dark-card-header">🎯 Key Performance Gauges & Benchmark Progress</div>', unsafe_allow_html=True)
    g1, g2, g3, g4 = st.columns(4)

    with g1:
        fig1 = create_semi_circular_gauge("Internal BM Score", kpis['avg_int_bm'], min_val=20, max_val=100, range_1=50, range_2=75, suffix="%", benchmark_target=70.0)
        st.plotly_chart(fig1, use_container_width=True)

    with g2:
        fig2 = create_semi_circular_gauge("External BM Score", kpis['avg_ext_bm'], min_val=20, max_val=100, range_1=45, range_2=70, suffix="%", benchmark_target=65.0)
        st.plotly_chart(fig2, use_container_width=True)

    with g3:
        fig3 = create_semi_circular_gauge("Compliance Score", kpis['avg_compliance'], min_val=0, max_val=10, range_1=4.0, range_2=7.0, suffix="/10", benchmark_target=7.5)
        st.plotly_chart(fig3, use_container_width=True)

    with g4:
        fig4 = create_semi_circular_gauge("Co-Curricular Index", kpis['avg_cca'], min_val=0, max_val=10, range_1=4.0, range_2=7.0, suffix="/10", benchmark_target=7.0)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 4. Bar Charts & Column Charts with Rich Tooltips ────────────────────────
    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown('<div class="dark-card-header">📊 Section-wise Benchmark Comparison (Column Chart)</div>', unsafe_allow_html=True)
        df_sec = fetch_section_column_chart()
        fig_col = px.bar(
            df_sec,
            x="Section",
            y=["Int BM", "Ext BM", "Compliance Score (x10)"],
            barmode="group",
            color_discrete_sequence=["#00e5ff", "#ffd740", "#7c4dff"]
        )
        fig_col.update_traces(
            hovertemplate="<b>Section:</b> %{x}<br><b>Metric:</b> %{data.name}<br><b>Score:</b> %{y:.1f}<extra></extra>"
        )
        fig_col.update_layout(
            paper_bgcolor='#0a1826',
            plot_bgcolor='#0a1826',
            height=280,
            margin=dict(l=10, r=10, t=20, b=20),
            xaxis=dict(tickfont=dict(color='#90caf9', size=12), title=None),
            yaxis=dict(gridcolor='#162e4a', tickfont=dict(color='#90caf9'), title="Score / Percentage"),
            legend=dict(font=dict(color='#90caf9', size=11), title=None, orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_col, use_container_width=True)

    with ch2:
        st.markdown(f'<div class="dark-card-header">🏆 Top {top_n_rank} Teacher Rankings (Bar Chart)</div>', unsafe_allow_html=True)
        df_rank = fetch_top_teacher_rankings(top_n_rank, section_filter)
        fig_rank = px.bar(
            df_rank,
            y="Teacher",
            x="OverallScore",
            orientation="h",
            color="OverallScore",
            color_continuous_scale="Viridis"
        )
        fig_rank.update_traces(
            hovertemplate="<b>Teacher:</b> %{y}<br><b>Overall Score:</b> %{x:.1f}/100<extra></extra>"
        )
        fig_rank.update_layout(
            paper_bgcolor='#0a1826',
            plot_bgcolor='#0a1826',
            height=280,
            margin=dict(l=10, r=10, t=20, b=20),
            xaxis=dict(gridcolor='#162e4a', tickfont=dict(color='#90caf9'), range=[0, 100], title="Calculated Overall Score (%)"),
            yaxis=dict(tickfont=dict(color='#90caf9', size=11), autorange="reversed", title=None),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_rank, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 5. Line Chart: Performance Landscape (Jan to Dec) ─────────────────────
    st.markdown('<div class="dark-card-header">📈 Annual Academic Performance Landscape (Jan – Dec Line Chart)</div>', unsafe_allow_html=True)
    df_perf = fetch_performance_landscape()
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=df_perf['Month'],
        y=df_perf['Performance Score'],
        mode='lines+markers',
        fill='tozeroy',
        line=dict(color='#00e5ff', width=3, shape='spline'),
        fillcolor='rgba(0, 229, 255, 0.12)',
        marker=dict(size=8, color='#ffffff', line=dict(color='#00e5ff', width=2)),
        hovertemplate="<b>Month:</b> %{x}<br><b>Academic Score:</b> %{y:.1f}%<br><i>Growth Index: Positive</i><extra></extra>"
    ))
    fig_line.update_layout(
        paper_bgcolor='#0a1826',
        plot_bgcolor='#0a1826',
        height=240,
        margin=dict(l=20, r=20, t=10, b=30),
        xaxis=dict(showgrid=True, gridcolor='#162e4a', tickfont=dict(color='#90caf9', size=11), title="Evaluation Month"),
        yaxis=dict(showgrid=True, gridcolor='#162e4a', tickfont=dict(color='#90caf9'), range=[30, 95], title="Score (%)"),
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 6. Table with Conditional Formatting ──────────────────────────────────
    st.markdown(f'<div class="dark-card-header">📋 Faculty Benchmark & Risk Evaluations ({section_filter} - Top {table_limit} Rows)</div>', unsafe_allow_html=True)
    df_table = fetch_conditionally_formatted_teachers(section_filter, limit=table_limit)

    styled_df = df_table.style.background_gradient(
        cmap="YlGnBu",
        subset=["Int BM Score", "Ext BM Score"]
    ).format({
        "Int BM Score": "{:.1f}%",
        "Ext BM Score": "{:.1f}%",
        "Compliance Score": "{:.1f}/10",
        "Risk Score": "{:.2f}"
    })

    st.dataframe(styled_df, use_container_width=True, height=340)
