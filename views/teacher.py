import streamlit as st
import plotly.graph_objects as go
from database import get_all_teacher_names, fetch_teacher_full_profile, add_new_teacher
from utils.pdf_generator import generate_teacher_pdf

def render_star_rating(stars: int):
    full_stars = "★" * stars
    empty_stars = "☆" * (3 - stars) if stars <= 3 else ""
    return f"<span class='star-rating'>{full_stars}{empty_stars}</span>"

def render_teacher_tab():
    # --------------------------------------------------------------------------
    # MANAGEMENT PANEL: Add New Teacher & Download Excel
    # --------------------------------------------------------------------------
    with st.expander("➕ Add New Teacher to Database", expanded=False):
        st.markdown("""
            <div style="font-size: 13px; color: #90caf9; margin-bottom: 10px;">
                Fill in the details below to register a new teacher. All evaluation records 
                (benchmark scores, attrition, stakeholder ratings) will be seeded with default values automatically.
            </div>
        """, unsafe_allow_html=True)

        fa1, fa2 = st.columns(2)
        with fa1:
            new_name = st.text_input("Full Name *", placeholder="e.g. Anita K. Sharma")
            new_dob = st.text_input("Date of Birth", placeholder="e.g. 15 Jun 1990")
            new_qual = st.selectbox("Qualifications", [
                "MA, BEd", "MSc, BEd", "BA, BEd", "BSc, BEd", "MCom, BEd", "MA, MEd", "MSc, PhD", "Other"
            ])
            new_exp_school = st.number_input("Experience (Current School, years)", min_value=0, max_value=40, value=1)

        with fa2:
            new_section = st.selectbox("Section", ["Sec1", "Sec2", "Sec3"])
            new_subjects = st.selectbox("Subject(s)", [
                "Maths-VI-X", "English-IX-XII", "Science-VI-VIII", "Social Studies-VIII-X",
                "Hindi-VI-X", "Computer-VI-XII", "Physics-XI-XII", "Chemistry-XI-XII",
                "Biology-IX-XII", "Economics-XI-XII", "History-VIII-X", "Geography-IX-XII",
                "Political Science-XI-XII", "Art & Craft-VI-X", "English-VI-VIII", "Hindi-VI-VII"
            ])
            new_cpw = st.number_input("Classes per Week", min_value=10, max_value=40, value=25)
            new_exp_prev = st.number_input("Experience (Previous School, years)", min_value=0, max_value=30, value=0)

        if st.button("✅ Add Teacher", use_container_width=True, type="primary"):
            if not new_name.strip():
                st.error("Teacher name is required.")
            else:
                success, msg = add_new_teacher(
                    new_name.strip(), new_dob, new_qual,
                    new_exp_school, new_exp_prev if new_exp_prev > 0 else None,
                    new_section, new_cpw, new_subjects
                )
                if success:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")
    # --------------------------------------------------------------------------
    # TEACHER PROFILE VIEWER (With Section & Teacher Slicers)
    # --------------------------------------------------------------------------
    c_sec, c_select, c_pdf = st.columns([1, 2, 1.2])
    with c_sec:
        sel_section = st.selectbox("Filter by Section", ["All Sections", "Sec1", "Sec2", "Sec3"])
    
    teacher_names = get_all_teacher_names(sel_section)
    if not teacher_names:
        st.warning("No teachers found in the selected section.")
        return

    with c_select:
        selected_teacher = st.selectbox("Select Teacher Name", teacher_names, index=0)

    profile = fetch_teacher_full_profile(selected_teacher)
    if not profile:
        st.warning("No details found for the selected teacher.")
        return

    with c_pdf:
        st.write("")  # Spacer
        pdf_bytes = generate_teacher_pdf(profile)
        st.download_button(
            label="📄 Download Report (PDF)",
            data=pdf_bytes,
            file_name=f"Teacher_Report_{selected_teacher.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Top Row: Avatar / Info / Leaves + Basic Info Box
    r1_col1, r1_col2 = st.columns([1.2, 1.8])

    with r1_col1:
        st.markdown(f"""
            <div class="dark-card">
                <div style="display: flex; gap: 15px; align-items: center; margin-bottom: 15px;">
                    <div style="width: 70px; height: 70px; border-radius: 50%; background: linear-gradient(135deg, #00b0ff, #00e5ff);
                                display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: 800; color: #0c1827;">
                        {selected_teacher[0]}
                    </div>
                    <div>
                        <h3 style="color: #ffffff; margin: 0; font-size: 20px;">{selected_teacher}</h3>
                        <p style="color: #00b0ff; margin: 0; font-size: 13px;">Section: {profile['section']} | {profile['subjects']}</p>
                    </div>
                </div>
                <div style="background: #091726; padding: 12px; border-radius: 8px; border: 1px solid #162f4d;">
                    <div style="display: flex; justify-content: space-between; font-size: 13px; color: #90caf9; margin-bottom: 5px;">
                        <span>Late (Current Month): <b style="color: #ffffff;">{profile['late_current_month']}</b></span>
                        <span>Unplanned Leaves: <b style="color: #ffffff;">{profile['unplanned_leaves']}</b></span>
                    </div>
                    <div style="font-size: 12px; color: #78909c;">Leave Balance Indicator</div>
                    <div style="display: flex; gap: 4px; margin-top: 5px;">
                        {"".join(['<div style="width: 10px; height: 10px; border-radius: 50%; background-color: #00e5ff;"></div>' for _ in range(12)])}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with r1_col2:
        st.markdown(f"""
            <div class="dark-card">
                <div class="dark-card-header">Basic Information</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13px; color: #e0f2fe;">
                    <div>• <b>Date of Birth:</b> {profile['dob']}</div>
                    <div>• <b>Qualifications:</b> {profile['qualifications']}</div>
                    <div>• <b>Experience (Current School):</b> {profile['experience_school']} years</div>
                    <div>• <b>Experience (Previous):</b> {profile['experience_prev'] if profile['experience_prev'] > 0 else 'NA'} years</div>
                    <div>• <b>Section:</b> {profile['section']}</div>
                    <div>• <b>Classes per Week:</b> {profile['classes_per_week']}</div>
                    <div style="grid-column: span 2;">• <b>Subjects &amp; Classes:</b> {profile['subjects']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Middle Row
    m1, m2, m3 = st.columns([1, 1.2, 1.2])

    with m1:
        st.markdown(f"""
            <div class="dark-card" style="min-height: 220px;">
                <div class="dark-card-header">Compliance Score</div>
                <div style="margin-bottom: 15px;">
                    <span style="font-size: 13px; color: #90caf9;">Training (Hours):</span>
                    <span style="font-size: 20px; font-weight: 700; color: #00e5ff; float: right;">{profile['training_hours']} / 50</span>
                </div>
                <div>
                    <span style="font-size: 13px; color: #90caf9;">Assignment Correction:</span>
                    <span style="float: right;">{render_star_rating(profile['assignment_stars'])}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with m2:
        int_notes_html = "".join([f"<li style='margin-bottom: 4px;'><b>{n.split(':')[0]}:</b> {n.split(':')[1] if ':' in n else ''}</li>" for n in profile['int_bm_notes']])
        st.markdown(f"""
            <div class="dark-card" style="min-height: 220px;">
                <div class="dark-card-header">Teaching Delivery Score (Int. BM)</div>
                <ul style="font-size: 12px; color: #90caf9; padding-left: 18px; margin-bottom: 10px;">
                    {int_notes_html}
                </ul>
                <div style="margin-top: 10px;">
                    <span style="font-size: 11px; color: #78909c;">Scale (0-100)</span>
                    <div style="font-size: 22px; font-weight: 800; color: #ffffff;">{profile['int_bm_score']}</div>
                    <div class="progress-bar-container">
                        <div class="progress-bar-fill-teal" style="width: {profile['int_bm_score']}%;"></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with m3:
        ext_notes_html = "".join([f"<li style='margin-bottom: 4px;'><b>{n.split(':')[0]}:</b> {n.split(':')[1] if ':' in n else ''}</li>" for n in profile['ext_bm_notes']])
        st.markdown(f"""
            <div class="dark-card" style="min-height: 220px;">
                <div class="dark-card-header">Teaching Delivery Score (Ext. BM)</div>
                <ul style="font-size: 12px; color: #90caf9; padding-left: 18px; margin-bottom: 10px;">
                    {ext_notes_html}
                </ul>
                <div style="margin-top: 10px;">
                    <span style="font-size: 11px; color: #78909c;">Scale (0-100)</span>
                    <div style="font-size: 22px; font-weight: 800; color: #ffffff;">{profile['ext_bm_score']}</div>
                    <div class="progress-bar-container">
                        <div class="progress-bar-fill-yellow" style="width: {profile['ext_bm_score']}%;"></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Bottom Row
    b1, b2, b3 = st.columns(3)

    with b1:
        st.markdown(f"""
            <div class="dark-card">
                <div class="dark-card-header">Contribution to Co-curricular Activities</div>
                <p style="font-size: 13px; color: #90caf9; margin-bottom: 4px;">No. of Activities: <b style="color: #ffffff;">{profile['co_curricular_count']} / 12</b></p>
                <p style="font-size: 13px; color: #90caf9; margin-bottom: 4px;">Quality of Contribution:</p>
                <div style="font-size: 16px; font-weight: 700; color: #00e5ff;">{profile['co_curricular_quality']}</div>
            </div>
        """, unsafe_allow_html=True)

    with b2:
        st.markdown(f"""
            <div class="dark-card">
                <div class="dark-card-header">Alignment with Stakeholders</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 12px; color: #90caf9;">
                    <div>Head: {render_star_rating(profile['head_stars'])}</div>
                    <div>Peer: {render_star_rating(profile['peer_stars'])}</div>
                    <div>Student: {render_star_rating(profile['student_stars'])}</div>
                    <div>Parent: {render_star_rating(profile['parent_stars'])}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with b3:
        exp_list = "".join([f"<li>{e}</li>" for e in profile['expectations']])
        st.markdown(f"""
            <div class="dark-card">
                <div class="dark-card-header">Expectations from HOD / Principal</div>
                <ul style="font-size: 12px; color: #90caf9; padding-left: 16px; margin: 0;">
                    {exp_list}
                </ul>
            </div>
        """, unsafe_allow_html=True)

    # Teacher Score Overview Chart
    st.markdown("""
        <div class="dark-card-header" style="margin-top: 10px;">
            Teacher Score Overview
        </div>
    """, unsafe_allow_html=True)

    categories = ['Teaching Delivery Score (Int. BM)', 'Teaching Delivery Score (Ext. BM)', 'Compliance Score']
    scores_vals = [profile['int_bm_score'], profile['ext_bm_score'], profile['compliance_score'] * 10]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        y=categories,
        x=scores_vals,
        orientation='h',
        marker=dict(color=['#00b0ff', '#00e5ff', '#3f51b5'], line=dict(color='#1a365d', width=1)),
        text=[f"{val:.1f}" for val in scores_vals],
        textposition='auto',
        textfont=dict(color='#ffffff', size=12, family='Segoe UI'),
        hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>"
    ))

    fig_bar.update_layout(
        paper_bgcolor='#0a1826',
        plot_bgcolor='#0a1826',
        height=200,
        margin=dict(l=20, r=20, t=10, b=20),
        xaxis=dict(showgrid=True, gridcolor='#162e4a', range=[0, 100], tickfont=dict(color='#90caf9')),
        yaxis=dict(showgrid=False, tickfont=dict(color='#90caf9', size=11))
    )
    st.plotly_chart(fig_bar, use_container_width=True)
